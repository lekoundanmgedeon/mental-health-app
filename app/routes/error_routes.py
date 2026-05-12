"""Error handlers."""

from flask import Blueprint, render_template

error_bp = Blueprint("errors", __name__)


@error_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html", title="Page not found"), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html", title="Server error"), 500
