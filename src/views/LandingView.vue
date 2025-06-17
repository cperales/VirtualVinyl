<template>
	<div class="login-container">
		<div class="vinyl-record">
			<div class="vinyl-center">
				<div class="vinyl-label">
                                        <h1 class="app-title">Virtual Vinyl</h1>
					<p class="app-subtitle">Vintage Playlist Creator</p>
				</div>
			</div>
		</div>

                <div class="login-card">
                        <h2>Connect Your Music</h2>
                        <p>Sign in with Spotify or TIDAL to discover your top tracks and create vintage playlists</p>
                        <button @click="handleSpotifyLogin" class="spotify-btn">
                                <span class="spotify-icon">♪</span>
                                Connect with Spotify
                        </button>
                        <button @click="handleTidalLogin" class="tidal-btn">
                                <span class="tidal-icon">♪</span>
                                Connect with TIDAL
                        </button>
                </div>
        </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSpotify } from '../composables/useSpotify'

const router = useRouter()
const { login, isAuthenticated, handleCallback } = useSpotify()

const handleSpotifyLogin = async () => {
        const success = await login()
        if (success) {
                router.push('/home')
        }
}

const handleTidalLogin = () => {
        alert('TIDAL login not yet implemented')
}

onMounted(async () => {
	// Check if we're returning from Spotify auth
	const callbackHandled = await handleCallback()

	if (callbackHandled || isAuthenticated.value) {
		router.push('/home')
	}
})
</script>

<style scoped>
.login-container {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	min-height: 100vh;
	padding: 2rem;
	background: radial-gradient(circle at center, #3d2817 0%, #1a0f08 100%);
}

.vinyl-record {
	width: 300px;
	height: 300px;
	border-radius: 50%;
	background: linear-gradient(45deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 3rem;
	box-shadow:
		0 0 30px rgba(0, 0, 0, 0.5),
		inset 0 0 20px rgba(255, 255, 255, 0.1);
	position: relative;
	animation: spin 20s linear infinite;
}

.vinyl-record::before {
	content: '';
	position: absolute;
	width: 280px;
	height: 280px;
	border-radius: 50%;
	background: repeating-conic-gradient(from 0deg,
			transparent 0deg,
			transparent 2deg,
			rgba(255, 255, 255, 0.05) 2deg,
			rgba(255, 255, 255, 0.05) 4deg);
}

.vinyl-center {
	width: 120px;
	height: 120px;
	border-radius: 50%;
	background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1;
}

.vinyl-label {
	text-align: center;
	color: #F5DEB3;
}

.app-title {
	font-family: 'Bebas Neue', cursive;
	font-size: 1.5rem;
	margin: 0;
	letter-spacing: 2px;
}

.app-subtitle {
	font-family: 'Crimson Text', serif;
	font-size: 0.8rem;
	margin: 0;
	font-style: italic;
}

.login-card {
	background: rgba(139, 69, 19, 0.9);
	padding: 3rem;
	border-radius: 15px;
	text-align: center;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	backdrop-filter: blur(10px);
	border: 2px solid rgba(245, 222, 179, 0.3);
}

.login-card h2 {
	font-family: 'Bebas Neue', cursive;
	color: #F5DEB3;
	font-size: 2rem;
	margin-bottom: 1rem;
	letter-spacing: 1px;
}

.login-card p {
	font-family: 'Crimson Text', serif;
	color: #F5DEB3;
	margin-bottom: 2rem;
	line-height: 1.6;
}

.spotify-btn {
	background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
	color: white;
	border: none;
	padding: 1rem 2rem;
	border-radius: 50px;
	font-family: 'Bebas Neue', cursive;
	font-size: 1.1rem;
	letter-spacing: 1px;
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin: 0 auto;
	transition: all 0.3s ease;
}

.spotify-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(29, 185, 84, 0.4);
}

.spotify-icon {
        font-size: 1.3rem;
}

.tidal-btn {
        background: linear-gradient(135deg, #0d273d 0%, #112d5c 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-family: 'Bebas Neue', cursive;
        font-size: 1.1rem;
        letter-spacing: 1px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem auto 0;
        transition: all 0.3s ease;
}

.tidal-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(17, 45, 92, 0.4);
}

.tidal-icon {
        font-size: 1.3rem;
}

@keyframes spin {
	from {
		transform: rotate(0deg);
	}

	to {
		transform: rotate(360deg);
	}
}
</style>
