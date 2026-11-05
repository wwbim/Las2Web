"""
Command-Line Interface (CLI) for Las2Web.
Provides headless batch conversion using PotreeConverter 2.x.
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.core.converter import ConversionTask, is_supported_file
from src.core.server import open_in_bim_scope


def main():
    parser = argparse.ArgumentParser(
        description="Las2Web - Minimal Point Cloud to Potree 2.x Converter CLI"
    )
    parser.add_argument(
        "input",
        help="Path to point cloud input file (.las or .laz)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Target output directory (defaults to <filename>_potree beside input)",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=["poisson", "poisson_average", "random"],
        default="poisson",
        help="Point sampling method (default: poisson)",
    )
    parser.add_argument(
        "--encoding",
        choices=["UNCOMPRESSED", "BROTLI"],
        default="UNCOMPRESSED",
        help="Octree binary chunk encoding (default: UNCOMPRESSED)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Automatically launch local CORS server and open BIM-Scope 3D viewer upon completion",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not is_supported_file(input_path):
        print(
            f"Error: Unsupported format {input_path.suffix}. Expected .las or .laz",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"=== Las2Web Point Cloud Conversion ===")
    print(f"Source file:   {input_path}")
    task = ConversionTask(
        input_file=input_path,
        output_dir=args.output,
        method=args.method,
        encoding=args.encoding,
    )
    print(f"Output folder: {task.output_dir}")
    print(f"Method:        {args.method}")
    print(f"Encoding:      {args.encoding}")
    print("---------------------------------------")

    def on_progress(percent: int, message: str):
        print(f"[{percent:3d}%] {message}")

    def on_log(line: str):
        # Only print significant lines to keep CLI output clean
        if any(k in line for k in ("Indexed", "Chunking", "closing", "duration", "total points")):
            print(f"  {line}")

    result = task.run(on_progress=on_progress, on_log=on_log)

    print("---------------------------------------")
    if result["success"]:
        print(f"Success! Converted in {result['elapsed_seconds']:.2f} seconds.")
        print(f"Output files located at: {result['output_dir']}")
        if args.preview:
            print("Starting local CORS server and launching BIM-Scope viewer...")
            url = open_in_bim_scope(result["output_dir"])
            print(f"Viewer URL: {url}")
            print("Press Ctrl+C to stop local preview server.")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nServer stopped.")
    else:
        print(f"Conversion Failed: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
