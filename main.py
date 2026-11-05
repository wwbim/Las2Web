"""
Las2Web - Unified Entry Point.
Launches the PyQt6 GUI when started with no arguments,
or executes headless command-line conversion when arguments are supplied.
"""

import sys
from pathlib import Path

# Fix for Windows --windowed executable when launched with CLI arguments
if sys.platform == "win32":
    import ctypes
    # Try attaching to parent console if invoked from terminal
    if ctypes.windll.kernel32.AttachConsole(-1):
        try:
            sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")
            sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        except Exception:
            pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def run_gui():
    from PyQt6.QtWidgets import QApplication
    from src.gui.main_window import MainWindow
    from src.gui.style import APP_STYLESHEET

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


def main():
    # If arguments are passed (and not just script name / gui flag), route to CLI
    args = sys.argv[1:]
    if args and not (len(args) == 1 and args[0].lower() in ("--gui", "-g")):
        from cli import main as cli_main

        cli_main()
    else:
        run_gui()


if __name__ == "__main__":
    main()
