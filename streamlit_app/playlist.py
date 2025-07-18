class PlaylistManager:
    """Manage track selection for playlist creation."""

    def __init__(self):
        self.selected_tracks = []

    def toggle_track(self, track):
        """Add or remove track from selection, max 10 tracks."""
        existing = next((t for t in self.selected_tracks if t['id'] == track['id']), None)
        if existing:
            self.selected_tracks = [t for t in self.selected_tracks if t['id'] != track['id']]
        elif len(self.selected_tracks) < 10:
            self.selected_tracks.append(track)
