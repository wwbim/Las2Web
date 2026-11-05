"""
PyInstaller Build Script for Las2Web.
Generates a standalone, portable Windows executable with PotreeConverter bundled.
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"


def build():
    print("=== Building Las2Web Portable Executable ===")

    # Ensure PotreeConverter is downloaded first
    from src.core.downloader import ensure_potree_converter

    converter_exe = ensure_potree_converter()
    converter_dir = converter_exe.parent

    print(f"PotreeConverter found at: {converter_dir}")

    # PyInstaller arguments
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name=Las2Web",
        f"--add-data={converter_dir};bin/PotreeConverter",
        str(BASE_DIR / "main.py"),
    ]

    print("Executing PyInstaller:")
    print(" ".join(pyinstaller_cmd))

    ret = subprocess.run(pyinstaller_cmd, cwd=str(BASE_DIR))
    if ret.returncode == 0:
        print("\nBuild completed successfully!")
        print(f"Executable directory: {DIST_DIR / 'Las2Web'}")
    else:
        print(f"\nBuild failed with exit code {ret.returncode}", file=sys.stderr)
        sys.exit(ret.returncode)


if __name__ == "__main__":
    build()
