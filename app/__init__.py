"""Application factory and extension initialization for the finance app."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

_DEFAULT_DB_FILENAME: Final[str] = "finance.db"


def _default_database_uri() -> str:
    """Return a default SQLite URI stored in a user-writable directory."""

    storage_dir_override = os.getenv("FINANCE_APP_STORAGE_DIR")
    if storage_dir_override:
        target = Path(storage_dir_override).expanduser()
        db_file = target if target.suffix else target / _DEFAULT_DB_FILENAME
    else:
        db_file = Path.home() / "FinanceTrackerData" / _DEFAULT_DB_FILENAME

    db_file.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_file.resolve(strict=False).as_posix()}"


def _normalize_database_uri(raw_uri: str | None) -> str:
    """Normalize *raw_uri* and ensure SQLite targets are writable paths."""

    if not raw_uri:
        return _default_database_uri()

    candidate = raw_uri.strip()
    if not candidate:
        return _default_database_uri()

    if "://" not in candidate:
        db_file = Path(candidate).expanduser()
        if db_file.is_dir():
            db_file /= _DEFAULT_DB_FILENAME
        db_file.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_file.resolve(strict=False).as_posix()}"

    try:
        url = make_url(candidate)
    except ArgumentError:
        return _default_database_uri()

    if url.drivername.startswith("sqlite") and url.database and url.database != ":memory:":
        db_path = Path(url.database).expanduser().resolve(strict=False)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = url.set(database=db_path.as_posix())
        return str(url)

    return candidate


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the financial data tracker."""

    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    config: dict[str, object] = {
        "SECRET_KEY": os.getenv("FLASK_SECRET_KEY", "change-me"),
        "SQLALCHEMY_DATABASE_URI": _normalize_database_uri(os.getenv("DATABASE_URL")),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
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

