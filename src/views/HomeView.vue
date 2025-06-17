<template>
	<div class="home-container">
                <header class="home-header">
                        <div class="header-content">
				<h1 class="page-title">Your Vinyl Collection</h1>
				<div class="user-info" v-if="user">
					<span>Welcome, {{ user.display_name }}</span>
					<button @click="handleLogout" class="logout-btn">Sign Out</button>
				</div>
                        </div>
                </header>
                <p v-if="playerError" class="player-error">{{ playerError }}</p>

		<main class="main-content">
			<!-- Search Section -->
			<div class="search-section">
				<div class="search-container">
					<input v-model="searchQuery" @input="handleSearchInput" placeholder="Search for songs on Spotify..."
						class="search-input" />
					<button v-if="searchQuery" @click="clearSearchInput" class="clear-search-btn">
						✕
					</button>
				</div>
			</div>

			<div class="selection-info">
				<p v-if="!searchQuery">Select up to 10 tracks to create your vintage playlist</p>
				<p v-else>Search results - Select up to 10 tracks to create your vintage playlist</p>
				<div class="selection-counter">
					{{ selectedTracks.length }}/10 selected
				</div>
				<button v-if="selectedTracks.length > 0" @click="showPlaylistDialog = true" class="create-playlist-btn">
					Create Playlist
				</button>
			</div>

			<!-- Display current tracks (search results or top tracks) -->
			<div class="tracks-grid" v-if="currentTracks.length && !isSearching">
				<div v-for="track in currentTracks" :key="track.id" class="vinyl-card"
					:class="{ selected: isSelected(track) }">
					<div class="vinyl-cover">
						<img :src="track.album.images[0]?.url" :alt="track.album.name" class="album-art" />
						<div class="vinyl-overlay">
							<div class="vinyl-actions">
								<button @click="handlePlayTrack(track)" class="action-btn play-btn"
									:title="'Play ' + track.name">
									<span v-if="currentTrack?.id === track.id && isPlaying">⏸</span>
									<span v-else>▶</span>
								</button>
								<button @click="toggleSelection(track)" class="action-btn select-btn"
									:class="{ selected: isSelected(track) }"
									:title="isSelected(track) ? 'Remove from playlist' : 'Add to playlist'">
									<span v-if="isSelected(track)">✓</span>
									<span v-else>+</span>
								</button>
							</div>
						</div>
					</div>
					<div class="track-info">
						<h3 class="track-name">{{ track.name }}</h3>
						<p class="artist-name">{{track.artists.map(a => a.name).join(', ')}}</p>
						<p class="album-name">{{ track.album.name }}</p>
					</div>
				</div>
			</div>

			<!-- Loading states -->
			<div v-else-if="isSearching" class="loading">
				<div class="loading-vinyl"></div>
				<p>Searching for tracks...</p>
			</div>

			<div v-else-if="!topTracks.length && !searchQuery" class="loading">
				<div class="loading-vinyl"></div>
				<p>Loading your music collection...</p>
			</div>

			<!-- No results message -->
			<div v-else-if="searchQuery && !currentTracks.length && !isSearching" class="no-results">
				<p>No tracks found for "{{ searchQuery }}"</p>
				<p>Try a different search term</p>
			</div>
		</main>

		<!-- Music Player -->
		<div v-if="currentTrack" class="music-player">
			<div class="player-content">
				<div class="player-track-info">
					<img :src="currentTrack.album.images[0]?.url" :alt="currentTrack.album.name"
						class="player-artwork" />
					<div class="player-details">
						<h4 class="player-track-name">{{ currentTrack.name }}</h4>
						<p class="player-artist-name">{{currentTrack.artists.map(a => a.name).join(', ')}}</p>
					</div>
				</div>

				<div class="player-controls">
					<button @click="handlePlayPause" class="player-btn">
						<span v-if="isPlaying">⏸</span>
						<span v-else>▶</span>
					</button>
					<button @click="stopTrack" class="player-btn">
						⏹
					</button>
				</div>

				<div class="player-volume">
					<button @click="stopTrack" class="close-player-btn" title="Close player">
						✕
					</button>
				</div>
			</div>

		</div>

		<!-- Playlist Creation Dialog -->
		<div v-if="showPlaylistDialog" class="dialog-overlay" @click="showPlaylistDialog = false">
			<div class="dialog" @click.stop>
				<h3>Create New Playlist</h3>
				<input v-model="playlistName" placeholder="Enter playlist name..." class="playlist-input"
					@keyup.enter="handleCreatePlaylist" />
				<div class="dialog-actions">
					<button @click="showPlaylistDialog = false" class="cancel-btn">Cancel</button>
					<button @click="handleCreatePlaylist" class="confirm-btn">Create</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSpotify } from '../composables/useSpotify'

const router = useRouter()
const {
        user,
        topTracks,
        selectedTracks,
        searchResults,
        isSearching,
        currentTrack,
        isPlaying,
        playerError,
        logout,
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
} = useSpotify()

const showPlaylistDialog = ref(false)
const playlistName = ref('')
const searchQuery = ref('')
const searchTimeout = ref(null)

// Computed property to determine which tracks to display
const currentTracks = computed(() => {
	return searchQuery.value ? searchResults.value : topTracks.value
})

const handleLogout = () => {
	logout()
	router.push('/login')
}

const isSelected = (track) => {
	return selectedTracks.value.some(t => t.id === track.id)
}

const toggleSelection = (track) => {
	if (selectedTracks.value.length >= 10 && !isSelected(track)) {
		// Show feedback when trying to select more than 10 tracks
		alert('You can only select up to 10 tracks for your playlist.')
		return
	}
	toggleTrackSelection(track)
}

const handleCreatePlaylist = async () => {
	if (!playlistName.value.trim()) {
		alert('Please enter a playlist name.')
		return
	}

	if (selectedTracks.value.length === 0) {
		alert('Please select at least one track for your playlist.')
		return
	}

        try {
                const trackCount = selectedTracks.value.length
                const playlist = await createPlaylist(playlistName.value)
                if (playlist) {
                        showPlaylistDialog.value = false
                        playlistName.value = ''
                        alert(`Playlist "${playlist.name}" created successfully with ${trackCount} tracks!`)
                        if (playlist.external_urls && playlist.external_urls.spotify) {
                                window.open(playlist.external_urls.spotify, '_blank')
                        }
                } else {
                        alert('Failed to create playlist. Please try again.')
                }
        } catch (error) {
                console.error('Error creating playlist:', error)
                alert('An error occurred while creating the playlist. Please try again.')
        }
}

const handleSearchInput = () => {
	// Clear existing timeout
	if (searchTimeout.value) {
		clearTimeout(searchTimeout.value)
	}

	// Set new timeout with 500ms debounce
	searchTimeout.value = setTimeout(() => {
		if (searchQuery.value.trim()) {
			searchTracks(searchQuery.value)
		} else {
			clearSearch()
		}
	}, 500)
}

const clearSearchInput = () => {
	searchQuery.value = ''
	clearSearch()
	if (searchTimeout.value) {
		clearTimeout(searchTimeout.value)
	}
}

const handlePlayTrack = async (track) => {
        if (currentTrack.value?.id === track.id) {
                handlePlayPause()
        } else {
                await playTrack(track)
        }
}

const handlePlayPause = async () => {
        if (isPlaying.value) {
                await pauseTrack()
        } else {
                await resumeTrack()
        }
}



onMounted(async () => {
	await getCurrentUser()
	await getTopTracks()
})
</script>

<style scoped>
.home-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #2c1810 0%, #1a0f08 100%);
}

.home-header {
	background: rgba(139, 69, 19, 0.9);
	padding: 1.5rem 2rem;
	border-bottom: 2px solid rgba(245, 222, 179, 0.3);
}

.header-content {
	max-width: 1200px;
	margin: 0 auto;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-title {
	font-family: 'Bebas Neue', cursive;
	color: #F5DEB3;
	font-size: 2.5rem;
	margin: 0;
	letter-spacing: 2px;
}

.user-info {
	display: flex;
	align-items: center;
	gap: 1rem;
	color: #F5DEB3;
	font-family: 'Crimson Text', serif;
}

.logout-btn {
	background: rgba(245, 222, 179, 0.2);
	color: #F5DEB3;
	border: 1px solid rgba(245, 222, 179, 0.5);
	padding: 0.5rem 1rem;
	border-radius: 25px;
	font-family: 'Crimson Text', serif;
	cursor: pointer;
	transition: all 0.3s ease;
}

.logout-btn:hover {
	background: rgba(245, 222, 179, 0.3);
}

.main-content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 2rem;
}

.search-section {
	margin-bottom: 2rem;
}

.search-container {
	position: relative;
	max-width: 600px;
	margin: 0 auto;
}

.search-input {
	width: 100%;
	padding: 1rem 3rem 1rem 1.5rem;
	border: 2px solid rgba(245, 222, 179, 0.3);
	border-radius: 50px;
	background: rgba(139, 69, 19, 0.2);
	color: #F5DEB3;
	font-family: 'Crimson Text', serif;
	font-size: 1.1rem;
	backdrop-filter: blur(10px);
	transition: all 0.3s ease;
}

.search-input:focus {
	border-color: rgba(245, 222, 179, 0.8);
	background: rgba(139, 69, 19, 0.3);
	outline: none;
	box-shadow: 0 0 20px rgba(245, 222, 179, 0.2);
}

.search-input::placeholder {
	color: rgba(245, 222, 179, 0.6);
}

.clear-search-btn {
	position: absolute;
	right: 1rem;
	top: 50%;
	transform: translateY(-50%);
	background: rgba(245, 222, 179, 0.2);
	color: #F5DEB3;
	border: none;
	width: 2rem;
	height: 2rem;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.3s ease;
	font-size: 1rem;
}

.clear-search-btn:hover {
	background: rgba(245, 222, 179, 0.4);
	transform: translateY(-50%) scale(1.1);
}

.selection-info {
	text-align: center;
	margin-bottom: 3rem;
	color: #F5DEB3;
	font-family: 'Crimson Text', serif;
}

.selection-info p {
	font-size: 1.1rem;
	margin-bottom: 1rem;
}

.selection-counter {
	font-family: 'Bebas Neue', cursive;
	font-size: 1.5rem;
	margin-bottom: 1rem;
	color: #DEB887;
}

.create-playlist-btn {
	background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
	color: #F5DEB3;
	border: none;
	padding: 1rem 2rem;
	border-radius: 25px;
	font-family: 'Bebas Neue', cursive;
	font-size: 1.1rem;
	letter-spacing: 1px;
	cursor: pointer;
	transition: all 0.3s ease;
}

.create-playlist-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
}

.tracks-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 2rem;
	margin-top: 2rem;
}

.vinyl-card {
	cursor: pointer;
	transition: all 0.3s ease;
	text-align: center;
}

.vinyl-card:hover {
	transform: translateY(-5px);
}

.vinyl-card.selected {
	transform: translateY(-5px) scale(1.05);
}

.vinyl-cover {
	position: relative;
	width: 180px;
	height: 180px;
	margin: 0 auto 1rem;
	border-radius: 50%;
	overflow: hidden;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
	border: 4px solid #8B4513;
}

.album-art {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.vinyl-overlay {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.vinyl-card:hover .vinyl-overlay {
	opacity: 1;
}

.vinyl-actions {
	display: flex;
	gap: 1rem;
	align-items: center;
}

.action-btn {
	background: rgba(245, 222, 179, 0.9);
	color: #8B4513;
	border: none;
	width: 3rem;
	height: 3rem;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 1.2rem;
	font-weight: bold;
	transition: all 0.3s ease;
	backdrop-filter: blur(10px);
}

.action-btn:hover {
	transform: scale(1.1);
	background: rgba(245, 222, 179, 1);
}

.play-btn {
	font-size: 1rem;
}

.select-btn.selected {
	background: #1DB954;
	color: white;
}

.music-player {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: rgba(139, 69, 19, 0.95);
	backdrop-filter: blur(20px);
	border-top: 2px solid rgba(245, 222, 179, 0.3);
	padding: 1rem 2rem;
	z-index: 1000;
	animation: slideUp 0.3s ease-out;
}

.player-content {
	max-width: 1200px;
	margin: 0 auto;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 2rem;
}

.player-track-info {
	display: flex;
	align-items: center;
	gap: 1rem;
	flex: 1;
	min-width: 0;
}

.player-artwork {
	width: 60px;
	height: 60px;
	border-radius: 8px;
	object-fit: cover;
	border: 2px solid rgba(245, 222, 179, 0.3);
}

.player-details {
	min-width: 0;
	flex: 1;
}

.player-track-name {
	font-family: 'Bebas Neue', cursive;
	color: #F5DEB3;
	font-size: 1.2rem;
	margin: 0 0 0.2rem;
	letter-spacing: 1px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.player-artist-name {
	font-family: 'Crimson Text', serif;
	color: #DEB887;
	margin: 0;
	font-size: 0.9rem;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.player-controls {
	display: flex;
	gap: 0.5rem;
	align-items: center;
}

.player-btn {
	background: rgba(245, 222, 179, 0.2);
	color: #F5DEB3;
	border: 1px solid rgba(245, 222, 179, 0.5);
	width: 3rem;
	height: 3rem;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 1.2rem;
	transition: all 0.3s ease;
}

.player-btn:hover {
	background: rgba(245, 222, 179, 0.4);
	transform: scale(1.05);
}

.player-volume {
	display: flex;
	align-items: center;
}

.close-player-btn {
	background: rgba(245, 222, 179, 0.2);
	color: #F5DEB3;
	border: 1px solid rgba(245, 222, 179, 0.5);
	width: 2.5rem;
	height: 2.5rem;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 1rem;
	transition: all 0.3s ease;
}

.close-player-btn:hover {
	background: rgba(245, 222, 179, 0.4);
	transform: scale(1.05);
}

.dialog-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	animation: fadeIn 0.3s ease-out;
}

.dialog {
	background: #8B4513;
	padding: 2rem;
	border-radius: 15px;
	min-width: 300px;
	max-width: 500px;
	width: 90%;
	color: #F5DEB3;
	border: 2px solid rgba(245, 222, 179, 0.3);
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
	backdrop-filter: blur(10px);
	animation: slideInUp 0.3s ease-out;
}

.dialog h3 {
	font-family: 'Bebas Neue', cursive;
	margin: 0 0 1rem;
	font-size: 1.5rem;
	letter-spacing: 1px;
	text-align: center;
}

.playlist-input {
	width: 100%;
	padding: 0.8rem;
	border: 1px solid rgba(245, 222, 179, 0.5);
	border-radius: 8px;
	background: rgba(245, 222, 179, 0.1);
	color: #F5DEB3;
	font-family: 'Crimson Text', serif;
	margin-bottom: 1.5rem;
	font-size: 1rem;
	transition: all 0.3s ease;
}

.playlist-input:focus {
	border-color: rgba(245, 222, 179, 0.8);
	background: rgba(245, 222, 179, 0.2);
	box-shadow: 0 0 10px rgba(245, 222, 179, 0.3);
}

.playlist-input::placeholder {
	color: rgba(245, 222, 179, 0.6);
}

.dialog-actions {
	display: flex;
	gap: 1rem;
	justify-content: flex-end;
}

.cancel-btn,
.confirm-btn {
	padding: 0.7rem 1.5rem;
	border: none;
	border-radius: 25px;
	font-family: 'Crimson Text', serif;
	cursor: pointer;
	transition: all 0.3s ease;
	font-size: 0.9rem;
	font-weight: 600;
}

.cancel-btn {
	background: rgba(245, 222, 179, 0.2);
	color: #F5DEB3;
	border: 1px solid rgba(245, 222, 179, 0.5);
}

.cancel-btn:hover {
	background: rgba(245, 222, 179, 0.3);
	transform: translateY(-1px);
}

.confirm-btn {
	background: #1DB954;
	color: white;
}

.confirm-btn:hover {
	background: #1ed760;
	transform: translateY(-1px);
	box-shadow: 0 3px 10px rgba(29, 185, 84, 0.4);
}

.no-results {
	text-align: center;
	color: #F5DEB3;
	font-family: 'Crimson Text', serif;
	margin-top: 4rem;
}

.no-results p {
	margin-bottom: 0.5rem;
	font-size: 1.1rem;
}

.no-results p:first-child {
        font-size: 1.3rem;
        color: #DEB887;
}

.player-error {
        color: #ff8080;
        text-align: center;
        margin-top: 1rem;
        font-family: 'Crimson Text', serif;
}

@keyframes fadeIn {
	from {
		opacity: 0;
	}

	to {
		opacity: 1;
	}
}

@keyframes slideInUp {
	from {
		transform: translateY(30px);
		opacity: 0;
	}

	to {
		transform: translateY(0);
		opacity: 1;
	}
}

/* Responsive adjustments */
@media (max-width: 768px) {
	.player-content {
		flex-direction: column;
		gap: 1rem;
	}

	.player-track-info {
		justify-content: center;
	}

	.vinyl-actions {
		gap: 0.5rem;
	}

	.action-btn {
		width: 2.5rem;
		height: 2.5rem;
		font-size: 1rem;
	}
}
</style>
