from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path
from dotenv import load_dotenv
import os

# Initialize extensions

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the financial data tracker."""
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{Path(app.root_path).parent / 'finance.db'}",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "กรุณาเข้าสู่ระบบก่อนใช้งาน"
    login_manager.login_message_category = "warning"

    from .models import User  # noqa: WPS433 - imported for flask-login user loader

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Return the user associated with *user_id*."""
        if user_id and user_id.isdigit():
            return db.session.get(User, int(user_id))
        return None

    with app.app_context():
        db.create_all()

    from .auth import auth_bp
    from .views import views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)

    return app
