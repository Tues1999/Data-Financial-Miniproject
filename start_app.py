"""Entry point for packaging the Flask app as a desktop-friendly executable."""

from __future__ import annotations

import multiprocessing
import os
import socket
import sys
import threading
import webbrowser
from contextlib import closing
from typing import Final

from app import create_app

DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 5000
BROWSER_OPEN_DELAY: Final[float] = 1.5


def _is_port_available(port: int, host: str = DEFAULT_HOST) -> bool:
    """Return True if *port* is free on *host*."""

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def _pick_port(start_port: int, host: str = DEFAULT_HOST, search_range: int = 25) -> int:
    """Pick the first available port starting at *start_port*."""

    if _is_port_available(start_port, host):
        return start_port

    for offset in range(1, search_range + 1):
        candidate = start_port + offset
        if _is_port_available(candidate, host):
            return candidate

    return start_port


def _open_browser(url: str) -> None:
    """Open *url* in the default browser, ignoring failures."""

    try:
        webbrowser.open(url, new=1, autoraise=True)
    except Exception:
        pass

def main() -> None:
    """Launch the Flask application for desktop usage."""

    multiprocessing.freeze_support()

    host = os.getenv("HOST", DEFAULT_HOST)
    if not host.strip():
        host = DEFAULT_HOST
    try:
        default_port = int(os.getenv("PORT", DEFAULT_PORT))
    except ValueError:
        default_port = DEFAULT_PORT
    port = _pick_port(default_port, host=host)
    if port != default_port:
        print(
            f"พอร์ต {default_port} ถูกใช้งานอยู่ เปลี่ยนไปใช้พอร์ต {port} แทน",
        )

    app = create_app()

    url = f"http://{host}:{port}/"
    threading.Timer(BROWSER_OPEN_DELAY, _open_browser, args=(url,)).start()

    print("Starting local server. If your browser does not open automatically,")
    print(f"เปิดเบราว์เซอร์ที่ {url}")
    print("กด Ctrl+C เพื่อปิดแอปพลิเคชันเมื่อใช้งานเสร็จ")

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
