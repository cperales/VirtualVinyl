import importlib

import dash_app


def test_dash_app_layout():
    importlib.reload(dash_app)
    assert dash_app.app.layout is not None
