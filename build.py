"""
Automated Build & Packaging Pipeline for Las2Web.
Performs 100% of compilation, asset collection, and PyInstaller bundling inside
Windows %TEMP% to prevent Google Drive I/O sync locks and conflicts.
Outputs a 100% standalone portable folder and ZIP archive to Deliverables/.
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path

# Ensure stdout handles UTF-8 gracefully on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DELIVERABLES_DIR = PROJECT_ROOT / "Deliverables"
ICON_PATH = PROJECT_ROOT / "assets" / "las2web.ico"

# VC++ Runtime DLLs to guarantee 100% zero-dependency on target client machines
VC_RUNTIME_DLLS = [
    "msvcp140.dll",
    "msvcp140_1.dll",
    "msvcp140_2.dll",
    "msvcp140_atomic_wait.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "vcomp140.dll",
]


def ensure_vc_runtimes_in_dir(target_dir: Path):
    """Copy VC++ runtime DLLs from System32 into target directory if missing."""
    sys32 = Path("C:/Windows/System32")
    for dll in VC_RUNTIME_DLLS:
        src = sys32 / dll
        dst = target_dir / dll
        if src.is_file() and not dst.is_file():
            shutil.copy2(str(src), str(dst))


def build_package():
    print("========================================================")
    print("🚀 Las2Web Standalone Build & Packaging Pipeline")
    print("========================================================")
    print(f"Project Source: {PROJECT_ROOT}")

    # Ensure Deliverables directory exists
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ensure PotreeConverter is ready
    print("\n[Step 1/5] Checking PotreeConverter binary...")
    from src.core.downloader import ensure_potree_converter
    converter_exe = ensure_potree_converter()
    ensure_vc_runtimes_in_dir(converter_exe.parent)
    print(f"  ✓ PotreeConverter ready at: {converter_exe}")

    # 2. Setup isolated build environment in %TEMP%
    temp_build_root = Path(tempfile.mkdtemp(prefix="las2web_build_"))
    print(f"\n[Step 2/5] Creating isolated build environment in %TEMP%...")
    print(f"  ✓ Working directory: {temp_build_root}")

    try:
        staging_src = temp_build_root / "src_project"
        staging_src.mkdir(parents=True, exist_ok=True)

        # Copy necessary project files into staging area
        print("  ✓ Staging source code and dependencies to local drive...")
        shutil.copytree(str(PROJECT_ROOT / "src"), str(staging_src / "src"), dirs_exist_ok=True)
        shutil.copytree(str(PROJECT_ROOT / "assets"), str(staging_src / "assets"), dirs_exist_ok=True)
        shutil.copytree(str(PROJECT_ROOT / "bin"), str(staging_src / "bin"), dirs_exist_ok=True)
        shutil.copy2(str(PROJECT_ROOT / "main.py"), str(staging_src / "main.py"))
        shutil.copy2(str(PROJECT_ROOT / "cli.py"), str(staging_src / "cli.py"))

        dist_path = temp_build_root / "dist"
        work_path = temp_build_root / "build"
        spec_path = temp_build_root / "spec"

        # 3. Execute PyInstaller completely within %TEMP%
        print("\n[Step 3/5] Executing PyInstaller in isolated temp workspace...")
        converter_data = f"{staging_src / 'bin' / 'PotreeConverter'};bin/PotreeConverter"
        assets_data = f"{staging_src / 'assets'};assets"

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--windowed",
            "--name=Las2Web",
            f"--icon={staging_src / 'assets' / 'las2web.ico'}",
            f"--distpath={dist_path}",
            f"--workpath={work_path}",
            f"--specpath={spec_path}",
            f"--add-data={converter_data}",
            f"--add-data={assets_data}",
            str(staging_src / "main.py"),
        ]

        print("  Running PyInstaller command...")
        res = subprocess.run(cmd, cwd=str(staging_src), capture_output=True, text=True)
        if res.returncode != 0:
            print("  ❌ PyInstaller Compilation Error:", file=sys.stderr)
            print(res.stdout, file=sys.stderr)
            print(res.stderr, file=sys.stderr)
            sys.exit(res.returncode)

        built_app_dir = dist_path / "Las2Web"
        if not built_app_dir.is_dir():
            raise FileNotFoundError(f"Expected build output not found at: {built_app_dir}")

        # Inject VC++ runtimes into application root as well
        ensure_vc_runtimes_in_dir(built_app_dir)
        print("  ✓ Standalone executable compiled successfully with all runtimes bundled.")

        # 4. Create ZIP distribution archive
        print("\n[Step 4/5] Creating distribution ZIP package...")
        zip_temp_path = temp_build_root / "Las2Web_win64.zip"
        with zipfile.ZipFile(zip_temp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(built_app_dir):
                for file in files:
                    full_p = Path(root) / file
                    rel_p = Path("Las2Web") / full_p.relative_to(built_app_dir)
                    zf.write(full_p, str(rel_p))

        zip_size_mb = zip_temp_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Distribution archive created: {zip_size_mb:.2f} MB")

        # 5. Copy final deliverables to Deliverables/
        print("\n[Step 5/5] Deploying deliverables to project Deliverables/ folder...")
        target_app_dir = DELIVERABLES_DIR / "Las2Web"
        target_zip = DELIVERABLES_DIR / "Las2Web_win64.zip"

        shutil.copytree(str(built_app_dir), str(target_app_dir), dirs_exist_ok=True)
        shutil.copy2(str(zip_temp_path), str(target_zip))

        print(f"  ✓ Standalone App Folder: {target_app_dir}")
        print(f"  ✓ Portable ZIP Archive:  {target_zip} ({zip_size_mb:.2f} MB)")

    finally:
        # Clean up temporary build files from local drive
        print("\n🧹 Cleaning up temporary build workspace in %TEMP%...")
        shutil.rmtree(temp_build_root, ignore_errors=True)
        print("  ✓ Cleanup complete.")

    print("\n========================================================")
    print("✅ Build Finished Successfully! Deliverables ready for distribution.")
    print("========================================================")


if __name__ == "__main__":
    build_package()
