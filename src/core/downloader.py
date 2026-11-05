"""
PotreeConverter binary dependency manager for Las2Web.
Detects, downloads, and extracts PotreeConverter 2.1.5 for Windows x64.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path

POTREE_VERSION = "2.1.5"
POTREE_DOWNLOAD_URL = (
    f"https://github.com/potree/PotreeConverter/releases/download/{POTREE_VERSION}/"
    f"PotreeConverter_{POTREE_VERSION}_x64_windows.zip"
)


def get_base_dir() -> Path:
    """Get root directory of the application whether running from source or frozen binary."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def get_converter_path() -> Path | None:
    """
    Search for PotreeConverter.exe in local bin/ or system PATH.
    Returns Path if found and executable, else None.
    """
    base_dir = get_base_dir()
    exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else base_dir
    candidate_paths = [
        base_dir / "bin" / "PotreeConverter" / "PotreeConverter.exe",
        base_dir / "bin" / "PotreeConverter.exe",
        exe_dir / "bin" / "PotreeConverter" / "PotreeConverter.exe",
        exe_dir / "bin" / "PotreeConverter.exe",
        exe_dir / "PotreeConverter.exe",
    ]

    for p in candidate_paths:
        if p.is_file():
            return p

    # Check system PATH
    system_path = shutil.which("PotreeConverter.exe") or shutil.which("PotreeConverter")
    if system_path:
        return Path(system_path)

    return None


def download_potree_converter(progress_callback=None) -> Path:
    """
    Download and extract PotreeConverter to bin/PotreeConverter/ directory.
    Optional progress_callback receives (percent: int, message: str).
    Returns absolute Path to PotreeConverter.exe upon success.
    """
    base_dir = get_base_dir()
    bin_dir = base_dir / "bin"
    potree_dir = bin_dir / "PotreeConverter"
    bin_dir.mkdir(parents=True, exist_ok=True)

    zip_path = bin_dir / f"PotreeConverter_{POTREE_VERSION}.zip"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Las2Web"}
    req = urllib.request.Request(POTREE_DOWNLOAD_URL, headers=headers)

    if progress_callback:
        progress_callback(0, f"Connecting to {POTREE_DOWNLOAD_URL}...")

    with urllib.request.urlopen(req) as resp, open(zip_path, "wb") as out_file:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 64 * 1024

        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0 and progress_callback:
                percent = int(downloaded * 100 / total_size)
                mb_down = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                progress_callback(percent, f"Downloading: {mb_down:.1f} MB / {mb_total:.1f} MB ({percent}%)")

    if progress_callback:
        progress_callback(100, "Extracting PotreeConverter files...")

    # Extract archive
    temp_extract = bin_dir / "_temp_extract"
    if temp_extract.exists():
        shutil.rmtree(temp_extract, ignore_errors=True)
    temp_extract.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_extract)

    # Locate PotreeConverter.exe inside extracted structure
    found_exe = None
    for root, _, files in os.walk(temp_extract):
        if "PotreeConverter.exe" in files:
            found_exe = Path(root) / "PotreeConverter.exe"
            break

    if not found_exe:
        raise FileNotFoundError("PotreeConverter.exe was not found inside downloaded archive.")

    exe_dir = found_exe.parent
    if potree_dir.exists():
        shutil.rmtree(potree_dir, ignore_errors=True)

    shutil.move(str(exe_dir), str(potree_dir))

    # Clean up temp files
    shutil.rmtree(temp_extract, ignore_errors=True)
    if zip_path.exists():
        zip_path.unlink()

    target_exe = potree_dir / "PotreeConverter.exe"
    if not target_exe.is_file():
        raise FileNotFoundError(f"Failed to set up PotreeConverter at {target_exe}")

    if progress_callback:
        progress_callback(100, f"PotreeConverter {POTREE_VERSION} ready.")

    return target_exe


def ensure_potree_converter(progress_callback=None) -> Path:
    """Ensure PotreeConverter.exe is available; downloads if not present."""
    existing = get_converter_path()
    if existing:
        return existing
    return download_potree_converter(progress_callback)
