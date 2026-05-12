"""Application factory for Student MindCare."""

from pathlib import Path

from flask import Flask

from config import Config
from app.extensions import csrf, db, login_manager
from app.models.user import User
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.error_routes import error_bp
from app.routes.prediction_routes import prediction_bp
from app.routes.specialist_routes import specialist_bp
from app.services.specialist_service import seed_default_specialists


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    app.instance_path and __import__("pathlib").Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(specialist_bp)
    app.register_blueprint(error_bp)

    with app.app_context():
        db.create_all()
        seed_default_specialists()

    return app
