"""Helper script to package the project as a standalone executable."""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import PyInstaller.__main__  # type: ignore[import]
except ModuleNotFoundError as exc:  # pragma: no cover - fails fast for missing dep
    raise SystemExit(
        "PyInstaller ไม่ได้ถูกติดตั้ง กรุณารัน 'pip install -r requirements-dev.txt'",
    ) from exc

PROJECT_ROOT = Path(__file__).parent.resolve()
APP_NAME = "FinanceTracker"


def _build_command() -> list[str]:
    """Construct the PyInstaller command arguments."""

    data_separator = ";" if os.name == "nt" else ":"
    templates_dir = (PROJECT_ROOT / "app" / "templates").resolve()
    static_dir = (PROJECT_ROOT / "app" / "static").resolve()

    add_data_templates = f"{templates_dir}{data_separator}app/templates"
    add_data_static = f"{static_dir}{data_separator}app/static"

    command = [
        str(PROJECT_ROOT / "start_app.py"),
        "--name",
        APP_NAME,
        "--noconfirm",
        "--clean",
        "--add-data",
        add_data_templates,
        "--add-data",
        add_data_static,
    ]

    if os.name == "nt":
        command.append("--windowed")

    return command


def main() -> None:
    """Run PyInstaller with the predefined configuration."""

    print("Building executable with PyInstaller...")
    PyInstaller.__main__.run(_build_command())
    dist_dir = PROJECT_ROOT / "dist" / APP_NAME
    exe_name = f"{APP_NAME}.exe" if os.name == "nt" else APP_NAME
    print("สร้างไฟล์สำเร็จที่:")
    print(dist_dir / exe_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
