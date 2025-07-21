from . import app
from . import routes  # noqa: F401

if __name__ == '__main__':
    app.run(debug=True)
