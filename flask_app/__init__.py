import os
from flask import Flask
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'secret')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from .routes import bp  # noqa: E402
app.register_blueprint(bp)
