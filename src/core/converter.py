"""
Point cloud conversion engine wrapping PotreeConverter 2.x.
Provides in-place output path calculation, non-ASCII path virtualization,
subprocess management, and progress parsing.
"""

import os
import re
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Callable, Any

from .downloader import ensure_potree_converter

SUPPORTED_EXTENSIONS = {".las", ".laz"}


def is_supported_file(file_path: str | Path) -> bool:
    """Check if the given file has a supported point cloud extension."""
    path = Path(file_path)
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def get_default_output_dir(input_path: str | Path) -> Path:
    """
    Calculate default in-place output directory beside the source file:
    e.g., C:/data/scan.las -> C:/data/scan_potree
    """
    p = Path(input_path).resolve()
    return p.parent / f"{p.stem}_potree"


def _is_pure_ascii(text: str | Path) -> bool:
    """Check if path string contains only ASCII characters."""
    try:
        str(text).encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


class ConversionTask:
    """Encapsulates a single conversion process with non-ASCII path support."""

    def __init__(
        self,
        input_file: str | Path,
        output_dir: str | Path | None = None,
        method: str = "poisson",
        encoding: str = "UNCOMPRESSED",
        extra_args: list[str] | None = None,
    ):
        self.input_file = Path(input_file).resolve()
        if not self.input_file.is_file():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        self.output_dir = Path(output_dir).resolve() if output_dir else get_default_output_dir(self.input_file)
        self.method = method
        self.encoding = encoding
        self.extra_args = extra_args or []
        self.process: subprocess.Popen | None = None
        self._is_cancelled = False

    def cancel(self):
        """Cancel ongoing conversion subprocess."""
        self._is_cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def run(
        self,
        on_progress: Callable[[int, str], None] | None = None,
        on_log: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        """
        Execute conversion synchronously while streaming progress and logs.
        Handles non-ASCII paths transparently via temporary staging if needed.
        """
        start_time = time.time()
        converter_exe = ensure_potree_converter()

        # Check if paths need ASCII staging
        needs_staging = not (_is_pure_ascii(self.input_file) and _is_pure_ascii(self.output_dir))

        staging_dir: Path | None = None
        actual_input: Path = self.input_file
        actual_output: Path = self.output_dir

        if needs_staging:
            if on_log:
                on_log("[Info] Non-ASCII characters detected in path. Preparing staging environment...")
            temp_root = Path(tempfile.gettempdir()) / f"las2web_{int(time.time() * 1000)}"
            temp_root.mkdir(parents=True, exist_ok=True)
            staging_dir = temp_root

            staged_input = staging_dir / f"input{self.input_file.suffix}"
            staged_output = staging_dir / "output"

            # Try hardlink first (instant, 0 bytes disk cost)
            try:
                os.link(str(self.input_file), str(staged_input))
                if on_log:
                    on_log("[Info] Fast zero-copy link created for conversion.")
            except Exception:
                if on_log:
                    on_log("[Info] Copying file to local staging buffer...")
                shutil.copyfile(str(self.input_file), str(staged_input))

            actual_input = staged_input
            actual_output = staged_output

        actual_output.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(converter_exe),
            str(actual_input),
            "-o",
            str(actual_output),
            "-m",
            self.method,
            "--encoding",
            self.encoding,
        ]
        if self.extra_args:
            cmd.extend(self.extra_args)

        if on_log:
            on_log(f"Starting PotreeConverter engine...")
        if on_progress:
            on_progress(5, "Initializing PotreeConverter...")

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
        )

        progress = 5
        stage_weights = {
            "COUNTING": (5, 25),
            "CREATING CHUNKS": (25, 55),
            "INDEXING": (55, 90),
            "MERGING": (90, 98),
        }
        current_stage = "COUNTING"

        try:
            for raw_line in self.process.stdout:
                if self._is_cancelled:
                    break

                line = raw_line.strip()
                if not line:
                    continue

                if on_log:
                    on_log(line)

                upper_line = line.upper()
                for stage in stage_weights:
                    if stage in upper_line:
                        current_stage = stage
                        break

                pct_match = re.search(r"(\d{1,3})%", line)
                if pct_match:
                    pct = int(pct_match.group(1))
                    start_p, end_p = stage_weights.get(current_stage, (10, 90))
                    progress = int(start_p + (end_p - start_p) * (pct / 100.0))
                else:
                    if progress < 95:
                        progress = min(95, progress + 1)

                if on_progress:
                    on_progress(progress, line)

            self.process.wait()
            return_code = self.process.poll()
            elapsed = time.time() - start_time

            if self._is_cancelled:
                return {
                    "success": False,
                    "output_dir": self.output_dir,
                    "metadata_path": None,
                    "elapsed_seconds": elapsed,
                    "error": "Conversion was cancelled by user.",
                }

            staged_metadata = actual_output / "metadata.json"
            if return_code == 0 and staged_metadata.is_file():
                # If staging was used, move files to user's final output directory
                if needs_staging and staging_dir:
                    if on_log:
                        on_log("[Info] Finalizing output files to destination...")
                    if self.output_dir.exists():
                        shutil.rmtree(self.output_dir, ignore_errors=True)
                    self.output_dir.mkdir(parents=True, exist_ok=True)

                    for item in actual_output.iterdir():
                        dest = self.output_dir / item.name
                        if item.is_dir():
                            shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
                        else:
                            shutil.copy2(str(item), str(dest))

                final_metadata = self.output_dir / "metadata.json"
                if on_progress:
                    on_progress(100, "Conversion completed successfully!")
                return {
                    "success": True,
                    "output_dir": self.output_dir,
                    "metadata_path": final_metadata,
                    "elapsed_seconds": elapsed,
                    "error": None,
                }
            else:
                err_msg = f"PotreeConverter exited with code {return_code}. metadata.json not found."
                return {
                    "success": False,
                    "output_dir": self.output_dir,
                    "metadata_path": None,
                    "elapsed_seconds": elapsed,
                    "error": err_msg,
                }

        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "output_dir": self.output_dir,
                "metadata_path": None,
                "elapsed_seconds": elapsed,
                "error": str(e),
            }
        finally:
            # Clean up staging directory
            if staging_dir and staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)
