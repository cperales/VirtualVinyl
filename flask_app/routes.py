import uuid
from flask import render_template, session, request, redirect, url_for, Blueprint

from streamlit_app.spotify_client import SpotifyClient
from streamlit_app.tidal_client import TidalClient
from streamlit_app.playlist import PlaylistManager

bp = Blueprint('routes', __name__)


def get_spotify():
    if 'spotify' not in session:
        session['spotify'] = SpotifyClient()
    return session['spotify']


def get_tidal():
    if 'tidal' not in session:
        session['tidal'] = TidalClient()
    return session['tidal']


def get_playlist():
    if 'playlist' not in session:
        session['playlist'] = PlaylistManager()
    return session['playlist']


@bp.route('/')
def index():
    sp = get_spotify()
    td = get_tidal()
    pl = get_playlist()

    return render_template('index.html',
                           sp_authenticated=sp.is_authenticated(),
                           td_authenticated=td.is_authenticated(),
                           selected_tracks=pl.selected_tracks)


@bp.route('/login/spotify')
def login_spotify():
    sp = get_spotify()
    return redirect(sp.login_url())


@bp.route('/login/tidal')
def login_tidal():
    td = get_tidal()
    state = str(uuid.uuid4())
    return redirect(td.login_url(state))


@bp.route('/callback/spotify')
def callback_spotify():
    code = request.args.get('code')
    if code:
        sp = get_spotify()
        sp.handle_callback(code)
    return redirect(url_for('routes.index'))


@bp.route('/callback/tidal')
def callback_tidal():
    code = request.args.get('code')
    if code:
        td = get_tidal()
        td.handle_callback(code)
    return redirect(url_for('routes.index'))


@bp.route('/search')
def search():
    query = request.args.get('q', '')
    sp = get_spotify()
    pl = get_playlist()
    results = sp.search_tracks(query)
    return render_template('_tracks.html', tracks=results, selected=pl.selected_tracks)


@bp.route('/toggle', methods=['POST'])
def toggle():
    pl = get_playlist()
    track = {
        'id': request.form.get('id'),
        'uri': request.form.get('uri'),
        'name': request.form.get('name'),
        'artists': request.form.get('artists', ''),
    }
    pl.toggle_track(track)
    return render_template('_track.html', track=track, selected_tracks=pl.selected_tracks)


@bp.route('/create_playlist', methods=['POST'])
def create_playlist():
    name = request.form.get('name')
    service = request.form.get('service', 'spotify')
    pl = get_playlist()
    if service == 'spotify':
        sp = get_spotify()
        uris = [t['uri'] for t in pl.selected_tracks]
        playlist = sp.create_playlist(name, uris)
    else:
        td = get_tidal()
        ids = [t['id'] for t in pl.selected_tracks]
        # Dummy user id for example
        playlist = td.create_playlist('me', name, ids)
    pl.selected_tracks = []
    return redirect(url_for('routes.index'))
