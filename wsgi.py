"""
WSGI entry point for Gunicorn server.
This module exposes the Flask application instance as 'application' for WSGI servers.
"""
from app import app

# Gunicorn looks for 'application' by default
application = app

if __name__ == "__main__":
    application.run()
