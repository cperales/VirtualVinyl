import { ref, computed, onMounted } from 'vue'
import { SpotifyApi } from '@spotify/web-api-ts-sdk'

const CLIENT_ID = '766875441cc149e79ed8aff4fb1be351' // Replace with your Spotify Client ID
const REDIRECT_URI = 'https://famous-definite-sailfish.ngrok-free.app'
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

export function useSpotify() {
  const isAuthenticated = computed(() => !!spotifyApi.value)

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
    const state = urlParams.get('state')
    
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
      return true
    } catch (error) {
      // No valid session
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
    if (!spotifyApi.value) return false
    
    try {
      // Set current track for display
      currentTrack.value = track
      isPlaying.value = true
      
      // Note: For preview playback, we'll use the track's preview_url
      // Full playback requires Spotify Premium and Web Playback SDK
      return true
    } catch (error) {
      console.error('Error playing track:', error)
      return false
    }
  }

  const pauseTrack = () => {
    isPlaying.value = false
  }

  const resumeTrack = () => {
    if (currentTrack.value) {
      isPlaying.value = true
    }
  }

  const stopTrack = () => {
    currentTrack.value = null
    isPlaying.value = false
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
