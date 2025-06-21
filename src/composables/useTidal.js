import { ref, computed, onMounted } from 'vue'

const CLIENT_ID = '5KP5Sx04Viwj4FRQ'
const REDIRECT_URI = 'https://cperales.github.io/VirtualVinyl/tidal-callback'
const AUTH_URL = 'https://login.tidal.com/authorize'
const API_URL = 'https://api.tidal.com/v1'

const tidalApi = ref(null)
const user = ref(null)
const topTracks = ref([])
const selectedTracks = ref([])
const searchResults = ref([])
const isSearching = ref(false)
const currentTrack = ref(null)
const isPlaying = ref(false)

export function useTidal() {
  const isAuthenticated = computed(() => !!tidalApi.value?.accessToken)

  const login = async () => {
    try {
      const state = Math.random().toString(36).substring(7)
      localStorage.setItem('tidalState', state)
      
      const params = new URLSearchParams({
        client_id: CLIENT_ID,
        response_type: 'code',
        redirect_uri: REDIRECT_URI,
        state: state,
        scope: 'r_usr w_usr r_sub w_sub'
      })

      window.location.href = `${AUTH_URL}?${params.toString()}`
      return true
    } catch (error) {
      console.error('TIDAL Authentication failed:', error)
      return false
    }
  }

  const handleCallback = async () => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    const savedState = localStorage.getItem('tidalState')

    if (code && state === savedState) {
      try {
        const response = await fetch('https://auth.tidal.com/v1/oauth2/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            grant_type: 'authorization_code',
            code,
            client_id: CLIENT_ID,
            redirect_uri: REDIRECT_URI,
          }),
        })

        const data = await response.json()
        tidalApi.value = {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        }

        // Clean up URL and state
        localStorage.removeItem('tidalState')
        window.history.replaceState({}, document.title, window.location.pathname)

        await loadUserProfile()
        return true
      } catch (error) {
        console.error('Error handling TIDAL callback:', error)
        return false
      }
    }
    return false
  }

  const loadUserProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${tidalApi.value.accessToken}`,
        },
      })
      user.value = await response.json()
    } catch (error) {
      console.error('Error loading TIDAL user profile:', error)
    }
  }

  // Moved to the consolidated implementation below

  const searchTracks = async (query) => {
    if (!query) {
      searchResults.value = []
      return []
    }

    isSearching.value = true

    try {
      const response = await fetch(
        `${API_URL}/search/tracks?query=${encodeURIComponent(query)}&limit=50`,
        {
          headers: {
            'Authorization': `Bearer ${tidalApi.value.accessToken}`,
          },
        }
      )
      const data = await response.json()
      searchResults.value = data.items
      return data.items
    } catch (error) {
      console.error('Error searching TIDAL tracks:', error)
      return []
    } finally {
      isSearching.value = false
    }
  }

  const createPlaylist = async (name, description) => {
    if (!user.value || !tidalApi.value?.accessToken) {
      throw new Error('Must be authenticated to create a playlist')
    }

    try {
      const createResponse = await fetch(`${API_URL}/users/${user.value.id}/playlists`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tidalApi.value.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: name, // TIDAL API uses 'title' instead of 'name'
          description,
          visibility: 'PRIVATE', // Start as private, user can change later
        }),
      })

      if (!createResponse.ok) {
        const errorText = await createResponse.text()
        throw new Error(`Failed to create playlist: ${errorText}`)
      }

      const playlist = await createResponse.json()

      // Add tracks to playlist
      if (selectedTracks.value.length > 0) {
        const addTracksResponse = await fetch(`${API_URL}/playlists/${playlist.uuid}/items`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${tidalApi.value.accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            trackIds: selectedTracks.value.map(track => track.id),
            onDupes: 'SKIP' // Skip duplicates instead of failing
          }),
        })

        if (!addTracksResponse.ok) {
          console.error('Some tracks could not be added to the playlist')
          // We still continue as the playlist was created
        }

        // Verify which tracks were added successfully
        const playlistTracksResponse = await fetch(`${API_URL}/playlists/${playlist.uuid}/items`, {
          headers: {
            'Authorization': `Bearer ${tidalApi.value.accessToken}`,
          },
        })

        if (playlistTracksResponse.ok) {
          const { items } = await playlistTracksResponse.json()
          const addedTracks = items.map(item => item.track)
          console.log(`Successfully added ${addedTracks.length} tracks to playlist`)
        }
      }

      return {
        ...playlist,
        tracks: selectedTracks.value,
        url: `https://listen.tidal.com/playlist/${playlist.uuid}`
      }
    } catch (error) {
      console.error('Error creating TIDAL playlist:', error)
      throw error
    }
  }

  const toggleTrackSelection = (track) => {
    const index = selectedTracks.value.findIndex((t) => t.id === track.id)
    if (index > -1) {
      selectedTracks.value.splice(index, 1)
    } else if (selectedTracks.value.length < 10) {
      selectedTracks.value.push(track)
    }
  }

  const logout = () => {
    tidalApi.value = null
    user.value = null
    topTracks.value = []
    selectedTracks.value = []
    searchResults.value = []
  }

  return {
    isAuthenticated,
    user,
    login,
    handleCallback,
    logout,
    searchTracks,
    createPlaylist,
    toggleTrackSelection,
    topTracks,
    selectedTracks,
    searchResults,
    isSearching,
    currentTrack,
    isPlaying,
  }
}
