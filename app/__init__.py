"""Application factory and extension initialization for the finance app."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def _default_database_uri() -> str:
    """Return a default SQLite URI stored in a user-writable directory."""

    storage_dir_override = os.getenv("FINANCE_APP_STORAGE_DIR")
    if storage_dir_override:
        target = Path(storage_dir_override).expanduser()
        db_file = target if target.suffix else target / "finance.db"
    else:
        db_file = Path.home() / "FinanceTrackerData" / "finance.db"

    db_file.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_file.resolve().as_posix()}"


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the financial data tracker."""

    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    config: dict[str, object] = {
        "SECRET_KEY": os.getenv("FLASK_SECRET_KEY", "change-me"),
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", ""),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    if test_config:
        config.update(test_config)

    if not config.get("SQLALCHEMY_DATABASE_URI"):
        config["SQLALCHEMY_DATABASE_URI"] = _default_database_uri()

    app.config.update(config)

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

