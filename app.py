"""Flask entrypoint for hosting platforms like Vercel.

This exposes a module-level `app` variable so runtimes that search for
one of the common filenames (app.py, main.py, server.py, etc.) can
locate the Flask application.
"""

from app import create_app

app = create_app()
