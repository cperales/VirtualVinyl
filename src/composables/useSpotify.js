import { ref, computed, onMounted } from 'vue'
import { SpotifyApi } from '@spotify/web-api-ts-sdk'

const CLIENT_ID = '766875441cc149e79ed8aff4fb1be351' // Replace with your Spotify Client ID
const REDIRECT_URI = 'https://cperales.github.io/VirtualVinyl'
const SCOPES = [
  'user-read-private',
  'user-read-email',
  'user-top-read',
  'playlist-modify-public',
  'playlist-modify-private'
]

const spotifyApi = ref(null)
const user = ref(null)
const topTracks = ref([])
const selectedTracks = ref([])
const searchResults = ref([])
const isSearching = ref(false)
const currentTrack = ref(null)
const isPlaying = ref(false)
const playerReady = ref(false)
const playerError = ref('')
const deviceId = ref(null)
let player = null

export function useSpotify() {
  const isAuthenticated = computed(() => !!spotifyApi.value)

  const setupPlayer = () => {
    if (!window.Spotify || player) return
    player = new window.Spotify.Player({
      name: 'VirtualVinyl',
      getOAuthToken: cb => cb(spotifyApi.value.getAccessToken())
    })

    player.addListener('ready', ({ device_id }) => {
      deviceId.value = device_id
      playerReady.value = true
      spotifyApi.value.player.transferPlayback([device_id], true).catch(() => {})
    })

    const setError = ({ message }) => {
      playerError.value = message
    }

    player.addListener('initialization_error', setError)
    player.addListener('authentication_error', setError)
    player.addListener('account_error', () => {
      playerError.value = 'Premium account required'
    })

    player.connect()
  }

  	onMounted(() => {
		spotifyApi.value = SpotifyApi.withUserAuthorization(
			CLIENT_ID,
			REDIRECT_URI,
			SCOPES
			)
	})

  const login = async () => {
    try {
      // Use the SDK's built-in authorization code with PKCE flow
      
      // This will redirect to Spotify's authorization page
      await spotifyApi.value.authenticate()
      
      return true
    } catch (error) {
      console.error('Authentication failed:', error)
      return false
    }
  }

  const handleCallback = async () => {
    // Check if we're on the callback URL with authorization code
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    
    if (code) {
      try {
        // Initialize the API with user authorization using the callback
        spotifyApi.value = SpotifyApi.withUserAuthorization(
          CLIENT_ID,
          REDIRECT_URI,
          SCOPES
        )
        
        // The SDK should handle the callback automatically
        await spotifyApi.value.authenticate()
        setupPlayer()
        
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname)
        
        return true
      } catch (error) {
        console.error('Error handling callback:', error)
        return false
      }
    }
    
    // Check if we already have a valid session
    try {
      spotifyApi.value = SpotifyApi.withUserAuthorization(
        CLIENT_ID,
        REDIRECT_URI,
        SCOPES
      )
      
      // Try to get current user to validate existing session
      await spotifyApi.value.currentUser.profile()
      setupPlayer()
      return true
    } catch (error) {
      console.error('Session validation failed:', error)
      spotifyApi.value = null
      return false
    }
  }

  const logout = () => {
    spotifyApi.value = null
    user.value = null
    topTracks.value = []
    selectedTracks.value = []
    
    // Clear any stored tokens (SDK handles this internally)
    localStorage.removeItem('spotify-sdk')
  }

  const getCurrentUser = async () => {
    if (!spotifyApi.value) return null
    
    try {
      const profile = await spotifyApi.value.currentUser.profile()
      user.value = profile
      return profile
    } catch (error) {
      console.error('Error fetching user profile:', error)
      return null
    }
  }

  const getTopTracks = async () => {
    if (!spotifyApi.value) return []
    
    try {
      const response = await spotifyApi.value.currentUser.topItems('tracks', 'long_term', 50)
      topTracks.value = response.items
      return response.items
    } catch (error) {
      console.error('Error fetching top tracks:', error)
      return []
    }
  }

  const toggleTrackSelection = (track) => {
    const index = selectedTracks.value.findIndex(t => t.id === track.id)
    if (index > -1) {
      selectedTracks.value.splice(index, 1)
    } else if (selectedTracks.value.length < 10) {
      selectedTracks.value.push(track)
    }
  }

  const createPlaylist = async (name) => {
    if (!spotifyApi.value || !user.value || selectedTracks.value.length === 0) return null
    
    try {
      const playlist = await spotifyApi.value.playlists.createPlaylist(
        user.value.id,
        {
          name,
          description: 'Created with VirtualVinyl',
          public: false
        }
      )
      
      const trackUris = selectedTracks.value.map(track => track.uri)
      await spotifyApi.value.playlists.addItemsToPlaylist(playlist.id, trackUris)
      
      selectedTracks.value = []
      return playlist
    } catch (error) {
      console.error('Error creating playlist:', error)
      return null
    }
  }

  const searchTracks = async (query) => {
    if (!spotifyApi.value || !query.trim()) {
      searchResults.value = []
      return []
    }
    
    isSearching.value = true
    
    try {
      const response = await spotifyApi.value.search(query, ['track'], 'US', 50)
      searchResults.value = response.tracks.items
      return response.tracks.items
    } catch (error) {
      console.error('Error searching tracks:', error)
      searchResults.value = []
      return []
    } finally {
      isSearching.value = false
    }
  }

  const clearSearch = () => {
    searchResults.value = []
    isSearching.value = false
  }

  const playTrack = async (track) => {
    if (!spotifyApi.value || !deviceId.value) return false

    try {
      // Set current track for display
      currentTrack.value = track
      isPlaying.value = true
      await spotifyApi.value.player.startResumePlayback(deviceId.value, undefined, [track.uri])
      return true
    } catch (error) {
      console.error('Error playing track:', error)
      return false
    }
  }

  const pauseTrack = async () => {
    if (!spotifyApi.value || !deviceId.value) return
    await spotifyApi.value.player.pausePlayback(deviceId.value).catch(() => {})
    isPlaying.value = false
  }

  const resumeTrack = async () => {
    if (!spotifyApi.value || !deviceId.value || !currentTrack.value) return
    await spotifyApi.value.player.startResumePlayback(deviceId.value)
    isPlaying.value = true
  }

  const stopTrack = () => {
    currentTrack.value = null
    isPlaying.value = false
    if (spotifyApi.value && deviceId.value) {
      spotifyApi.value.player.pausePlayback(deviceId.value).catch(() => {})
    }
  }

  return {
    isAuthenticated,
    user,
    topTracks,
    selectedTracks,
    searchResults,
    isSearching,
    currentTrack,
    isPlaying,
    playerReady,
    playerError,
    login,
    logout,
    handleCallback,
    getCurrentUser,
    getTopTracks,
    toggleTrackSelection,
    createPlaylist,
    searchTracks,
    clearSearch,
    playTrack,
    pauseTrack,
    resumeTrack,
    stopTrack
  }
}
