import React, { useState, useEffect } from 'react';
import { Search, Music, Plus, X, Save } from 'lucide-react';

interface Track {
  id: string;
  uri: string;
  name: string;
  duration_ms: number;
  album: {
    name: string;
    images: { url: string }[];
  };
  artists: { name: string }[];
}

interface SpotifyUser {
  display_name: string;
}

const VirtualVinyl = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<SpotifyUser | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Track[]>([]);
  const [vinylTracks, setVinylTracks] = useState<Track[]>([]);
  const [playlistName, setPlaylistName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const API_BASE = 'http://localhost:5000';

  useEffect(() => {
    checkAuthStatus();
    // Check for auth success from callback
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
      setIsAuthenticated(true);
      fetchUser();
      window.history.replaceState({}, '', '/');
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/auth-status`, {
        credentials: 'include'
      });
      const data = await response.json();
      setIsAuthenticated(data.authenticated);
      if (data.authenticated) {
        fetchUser();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    }
  };

  const fetchUser = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/user`, {
        credentials: 'include'
      });
      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  };

  const handleLogin = () => {
    window.location.href = `${API_BASE}/login`;
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/api/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      setIsAuthenticated(false);
      setUser(null);
      setVinylTracks([]);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const searchTracks = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/search?q=${encodeURIComponent(searchQuery)}`,
        { credentials: 'include' }
      );
      const data = await response.json();
      setSearchResults(data.tracks?.items || []);
    } catch (error) {
      console.error('Search failed:', error);
    }
    setIsLoading(false);
  };

  const addToVinyl = (track: Track) => {
    if (vinylTracks.length >= 12) {
      alert('Maximum 12 tracks per vinyl!');
      return;
    }
    
    if (vinylTracks.find(t => t.id === track.id)) {
      alert('Track already in your vinyl!');
      return;
    }
    
    setVinylTracks([...vinylTracks, track]);
  };

  const removeFromVinyl = (trackId: string) => {
    setVinylTracks(vinylTracks.filter(t => t.id !== trackId));
  };

  const createPlaylist = async () => {
    if (vinylTracks.length < 8) {
      alert('Minimum 8 tracks required for a vinyl!');
      return;
    }
    
    if (!playlistName.trim()) {
      alert('Please enter a playlist name!');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/create-playlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: playlistName,
          track_uris: vinylTracks.map(t => t.uri)
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert(`Virtual Vinyl created successfully! Check your Spotify playlists.`);
        setVinylTracks([]);
        setPlaylistName('');
      } else {
        alert(data.error || 'Failed to create playlist');
      }
    } catch (error) {
      console.error('Failed to create playlist:', error);
    }
    setIsLoading(false);
  };

  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl text-center max-w-md">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-pink-500 to-violet-500 rounded-full flex items-center justify-center">
            <Music className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-4">VirtualVinyl</h1>
          <p className="text-white/80 mb-8">Create vinyl-style playlists from your favorite tracks</p>
          <button
            onClick={handleLogin}
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
          >
            Connect with Spotify
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Music className="w-8 h-8 text-white" />
            <h1 className="text-2xl font-bold text-white">VirtualVinyl</h1>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-white/80">Welcome, {user.display_name}!</span>
            )}
            <button
              onClick={handleLogout}
              className="bg-red-500/20 hover:bg-red-500/30 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          
          {/* Search Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-4">Search Tracks</h2>
            
            <div className="flex space-x-2 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/50" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchTracks()}
                  placeholder="Search for songs, artists, albums..."
                  className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-white/40"
                />
              </div>
              <button
                onClick={searchTracks}
                disabled={isLoading}
                className="bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white px-6 py-3 rounded-lg transition-colors"
              >
                Search
              </button>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {searchResults.map(track => (
                <div key={track.id} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {track.album.images[2] && (
                      <img
                        src={track.album.images[2].url}
                        alt={track.album.name}
                        className="w-12 h-12 rounded-lg"
                      />
                    )}
                    <div>
                      <p className="text-white font-medium">{track.name}</p>
                      <p className="text-white/60 text-sm">
                        {track.artists.map(a => a.name).join(', ')} • {formatDuration(track.duration_ms)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => addToVinyl(track)}
                    className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Vinyl Creation Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-4">
              Your Virtual Vinyl ({vinylTracks.length}/12)
            </h2>
            
            <div className="mb-4">
              <input
                type="text"
                value={playlistName}
                onChange={(e) => setPlaylistName(e.target.value)}
                placeholder="Enter playlist name..."
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-white/40"
              />
            </div>

            <div className="space-y-2 mb-6 max-h-64 overflow-y-auto">
              {vinylTracks.map((track, index) => (
                <div key={track.id} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-white/60 text-sm font-mono w-6">
                      {(index + 1).toString().padStart(2, '0')}
                    </span>
                    {track.album.images[2] && (
                      <img
                        src={track.album.images[2].url}
                        alt={track.album.name}
                        className="w-10 h-10 rounded-lg"
                      />
                    )}
                    <div>
                      <p className="text-white text-sm font-medium">{track.name}</p>
                      <p className="text-white/60 text-xs">
                        {track.artists.map(a => a.name).join(', ')}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFromVinyl(track.id)}
                    className="bg-red-500/20 hover:bg-red-500/40 text-red-300 p-2 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {vinylTracks.length === 0 && (
              <div className="text-center py-8 text-white/50">
                <Music className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Start building your vinyl by searching and adding tracks</p>
                <p className="text-sm mt-2">Minimum 8 tracks, maximum 12 tracks</p>
              </div>
            )}

            <div className="flex items-center justify-between text-white/60 text-sm mb-4">
              <span>Tracks: {vinylTracks.length} (8-12 required)</span>
              <span>
                Duration: {formatDuration(vinylTracks.reduce((acc, track) => acc + track.duration_ms, 0))}
              </span>
            </div>

            <button
              onClick={createPlaylist}
              disabled={vinylTracks.length < 8 || !playlistName.trim() || isLoading}
              className="w-full bg-gradient-to-r from-pink-500 to-violet-500 hover:from-pink-600 hover:to-violet-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2"
            >
              <Save className="w-5 h-5" />
              <span>{isLoading ? 'Creating...' : 'Create Virtual Vinyl'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VirtualVinyl;
