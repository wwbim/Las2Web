"""
Lightweight local HTTP static server with full CORS and HTTP Range support.
Enables web viewers like BIM-Scope (https://wwbim.github.io/BIM-Scope/)
to stream point cloud octree chunks (metadata.json, octree.bin, hierarchy.bin) directly.
"""

import os
import sys
import re
import socket
import threading
import webbrowser
from pathlib import Path
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote

DEFAULT_BIM_SCOPE_URL = "https://wwbim.github.io/BIM-Scope/"


class CORSAndRangeRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler with:
    1. Full permissive CORS headers (for remote web viewers like BIM-Scope).
    2. HTTP Byte Range support (mandatory for potree-core chunk streaming).
    """

    def end_headers(self):
        # Permissive CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Range, Origin, Content-Type, Accept, Authorization, X-Requested-With",
        )
        self.send_header(
            "Access-Control-Expose-Headers",
            "Content-Range, Content-Length, Accept-Ranges, Content-Type",
        )
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        """Respond to preflight CORS check."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def send_head(self):
        """Custom send_head adding support for HTTP 206 Partial Content (Range requests)."""
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            return super().send_head()

        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            total_size = fs[6]

            # Check for 'Range' header
            range_header = self.headers.get("Range")
            if range_header:
                match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                if match:
                    start_str, end_str = match.groups()
                    start = int(start_str)
                    end = int(end_str) if end_str else total_size - 1

                    if start >= total_size or end >= total_size or start > end:
                        self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                        self.send_header("Content-Range", f"bytes */{total_size}")
                        self.end_headers()
                        f.close()
                        return None

                    length = end - start + 1
                    f.seek(start)

                    self.send_response(HTTPStatus.PARTIAL_CONTENT)
                    self.send_header("Content-Type", self.guess_type(path))
                    self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
                    self.send_header("Content-Length", str(length))
                    self.end_headers()
                    return f

            # Regular full-file response
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(total_size))
            self.end_headers()
            return f
        except Exception:
            if f:
                f.close()
            raise

    def log_message(self, format, *args):
        """Silent logging for normal requests to avoid terminal spam."""
        pass


class LocalPointcloudServer:
    """Singleton-friendly background server serving a specified point cloud directory."""

    _instance: "LocalPointcloudServer | None" = None
    _lock = threading.Lock()

    def __init__(self, root_dir: Path | str, port: int = 0):
        self.root_dir = Path(root_dir).resolve()
        self.port = port
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.actual_port: int = 0

    def start(self) -> int:
        """Start the server in a daemon thread. Returns bound port."""
        if self.server:
            return self.actual_port

        handler = lambda *args, **kwargs: CORSAndRangeRequestHandler(
            *args, directory=str(self.root_dir), **kwargs
        )
        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), handler)
        self.actual_port = self.server.server_port

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self.actual_port

    def stop(self):
        """Shutdown the server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.thread = None


_global_server: LocalPointcloudServer | None = None


def serve_pointcloud(folder_path: Path | str, preferred_port: int = 9005) -> tuple[str, int]:
    """
    Ensure the point cloud folder is served via HTTP with CORS & Range support.
    Returns (url_to_metadata, port).
    """
    global _global_server
    path = Path(folder_path).resolve()
    if path.is_file():
        path = path.parent

    # If already running for this directory, reuse port
    if _global_server and _global_server.root_dir == path and _global_server.server:
        port = _global_server.actual_port
    else:
        if _global_server:
            _global_server.stop()
        _global_server = LocalPointcloudServer(path, port=preferred_port)
        try:
            port = _global_server.start()
        except OSError:
            # Fallback to random free port
            _global_server = LocalPointcloudServer(path, port=0)
            port = _global_server.start()

    metadata_url = f"http://127.0.0.1:{port}/metadata.json"
    return metadata_url, port


def open_in_bim_scope(
    folder_path: Path | str,
    viewer_base_url: str = DEFAULT_BIM_SCOPE_URL,
    preferred_port: int = 9005,
    auto_open_browser: bool = True,
) -> str:
    """
    Start local CORS server for the converted folder and open in BIM-Scope viewer.
    Returns the target browser URL.
    """
    metadata_url, _ = serve_pointcloud(folder_path, preferred_port=preferred_port)
    encoded_param = quote(metadata_url, safe="")
    target_url = f"{viewer_base_url.rstrip('/')}/?pointcloud={encoded_param}"

    if auto_open_browser:
        webbrowser.open(target_url)

    return target_url
