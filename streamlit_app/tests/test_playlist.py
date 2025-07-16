from streamlit_app.playlist import PlaylistManager


def test_toggle_adds_track():
    pm = PlaylistManager()
    pm.toggle_track({'id': '1'})
    assert len(pm.selected_tracks) == 1
    assert pm.selected_tracks[0]['id'] == '1'


def test_toggle_removes_track():
    pm = PlaylistManager()
    track = {'id': '1'}
    pm.toggle_track(track)
    pm.toggle_track(track)
    assert len(pm.selected_tracks) == 0


def test_limit_selection_to_10():
    pm = PlaylistManager()
    for i in range(12):
        pm.toggle_track({'id': str(i)})
    assert len(pm.selected_tracks) == 10
