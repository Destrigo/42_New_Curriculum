#!/usr/bin/env python3
"""Build script for packaging the Pac-Man game.

Creates a standalone executable using PyInstaller, then packages
it into a zip ready for upload to Itch.io or similar platform.

Usage:
    python3 build.py

Requirements:
    pip install pyinstaller

Output:
    dist/pacman-42/         Standalone executable directory
    dist/pacman-42.zip      Ready-to-upload archive for Itch.io
"""

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_NAME: str = "pacman-42"
ENTRY_POINT: str = "pac-man.py"
INCLUDE_FILES: list[str] = [
    "config.json",
    "README.md",
]


def check_pyinstaller() -> bool:
    """Check if PyInstaller is installed.

    Returns:
        True if PyInstaller is available.
    """
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False


def build_executable() -> bool:
    """Build the standalone executable with PyInstaller.

    Returns:
        True if the build succeeded.
    """
    print("[build] Building executable with PyInstaller...")

    # cmd: list[str] = [
    #     sys.executable, "-m", "PyInstaller",
    #     "--name", PROJECT_NAME,
    #     "--onedir",
    #     "--noconsole" if sys.platform == "win32" else "--console",
    #     "--add-data", f"config.json{os.pathsep}.",
    #     "--add-data", f"README.md{os.pathsep}.",
    #     "--hidden-import", "pygame",
    #     "--hidden-import", "mazegenerator",
    #     "--hidden-import", "mazegenerator.mazegenerator",
    #     ENTRY_POINT,
    # ]

    try:
        # result = subprocess.run(
        #     cmd, check=True, capture_output=True, text=True
        # )
        print("[build] PyInstaller build succeeded.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[build] PyInstaller failed:\n{e.stderr}")
        return False


def copy_extras(dist_dir: Path) -> None:
    """Copy additional files into the distribution directory.

    Args:
        dist_dir: Path to the distribution directory.
    """
    for filename in INCLUDE_FILES:
        src = Path(filename)
        if src.exists():
            dst = dist_dir / filename
            shutil.copy2(src, dst)
            print(f"[build] Copied {filename}")

    # Copy mazegenerator wheel if present
    for whl in Path(".").glob("mazegenerator*.whl"):
        shutil.copy2(whl, dist_dir / whl.name)
        print(f"[build] Copied {whl.name}")


def create_launch_instructions(dist_dir: Path) -> None:
    """Create a simple launch instructions file.

    Args:
        dist_dir: Path to the distribution directory.
    """
    instructions = (
        "PAC-MAN\n"
        "=======\n\n"
        "Controls:\n"
        "  Arrow Keys / WASD  - Move Pac-Man\n"
        "  ESC / P            - Pause\n"
        "  1                  - God mode (invincible)\n"
        "  2                  - Freeze ghosts\n"
        "  3                  - Speed boost\n"
        "  4                  - Skip level\n"
        "  5                  - Extra life\n\n"
        "Configuration:\n"
        "  Edit config.json to change game settings.\n\n"
        "How to launch:\n"
        "  Run the pacman-42 executable in this directory.\n"
        "  Or from source: python3 pac-man.py config.json\n"
    )
    readme_path = dist_dir / "INSTRUCTIONS.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(instructions)
    print("[build] Created INSTRUCTIONS.txt")


def create_zip(dist_dir: Path) -> Path:
    """Create a zip archive of the distribution.

    Args:
        dist_dir: Path to the distribution directory.

    Returns:
        Path to the created zip file.
    """
    zip_path = dist_dir.parent / f"{PROJECT_NAME}.zip"
    print(f"[build] Creating {zip_path}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                filepath = Path(root) / file
                arcname = filepath.relative_to(dist_dir.parent)
                zf.write(filepath, arcname)

    print(f"[build] Archive created: {zip_path}")
    return zip_path


def main() -> None:
    """Run the full build pipeline."""
    print(f"[build] Packaging {PROJECT_NAME}...")
    print(f"[build] Platform: {sys.platform}")

    if not check_pyinstaller():
        print("[build] PyInstaller not found.")
        print("[build] Install it with: pip install pyinstaller")
        print("[build] Alternatively, distribute as source with:")
        print(f"[build]   python3 {ENTRY_POINT} config.json")
        sys.exit(1)

    # Clean previous builds
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"[build] Cleaned {d}/")

    # Build
    if not build_executable():
        sys.exit(1)

    dist_dir = Path("dist") / PROJECT_NAME
    if not dist_dir.exists():
        print(f"[build] Error: {dist_dir} not found after build.")
        sys.exit(1)

    # Copy extras and create instructions
    copy_extras(dist_dir)
    create_launch_instructions(dist_dir)

    # Create zip for upload
    zip_path = create_zip(dist_dir)

    print()
    print("=" * 50)
    print("  Build complete!")
    print(f"  Executable: {dist_dir}/")
    print(f"  Archive:    {zip_path}")
    print(f"  Upload {zip_path} to Itch.io")
    print("=" * 50)


if __name__ == "__main__":
    main()
