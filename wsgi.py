"""WSGI entry point used by Gunicorn/Render/Railway."""

from app import create_app

app = create_app()
