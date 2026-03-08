#!/usr/bin/env python3
"""Build and package the Pac-Man game for Itch.io deployment.

Creates a standalone executable using PyInstaller, then packages
it into a zip ready for upload.

Usage:
    python3 build.py

Prerequisites:
    uv add pyinstaller

Output:
    dist/pacman-42/         Standalone executable directory
    dist/pacman-42.zip      Archive ready for Itch.io upload
"""

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional


PROJECT_NAME: str = "pacman-42"
ENTRY_POINT: str = "pac-man.py"
INCLUDE_FILES: list[str] = [
    "config.json",
    "README.md",
    ".itch.toml",
]


def check_pyinstaller() -> bool:
    """Check if PyInstaller is importable.

    Returns:
        True if PyInstaller is available.
    """
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False


def build_executable() -> bool:
    """Build the standalone executable with PyInstaller"""
    print("[build] Building executable with PyInstaller...")

    cmd: list[str] = [
        sys.executable, "-m", "PyInstaller",
        "--name", PROJECT_NAME,
        "--onedir",
        "--console",
        "--add-data", f"config.json{os.pathsep}.",
        "--add-data", f"README.md{os.pathsep}.",
        "--hidden-import", "pygame",
        "--hidden-import", "mazegenerator",
        "--hidden-import", "mazegenerator.mazegenerator",
        ENTRY_POINT,
    ]

    # if sys.platform == "win32":
    #     cmd[5] = "--noconsole"

    try:
        result = subprocess.run(cmd, check=True)
        print(result)
        print("[build] PyInstaller build succeeded.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[build] PyInstaller failed with code {e.returncode}")
        return False


def find_dist_dir() -> Optional[Path]:
    """Find the output directory created by PyInstaller.

    Returns:
        Path to the distribution directory, or None if not found.
    """
    dist = Path("dist")
    if not dist.exists():
        return None

    # Try exact name first
    exact = dist / PROJECT_NAME
    if exact.is_dir():
        return exact

    # Try without hyphens
    alt = dist / PROJECT_NAME.replace("-", "_")
    if alt.is_dir():
        return alt

    # Try the entry point name without extension
    entry_name = Path(ENTRY_POINT).stem
    alt2 = dist / entry_name
    if alt2.is_dir():
        return alt2

    # Last resort: pick the first directory in dist/
    dirs = [d for d in dist.iterdir() if d.is_dir()]
    if dirs:
        # print(f"[build] Expected dist/{PROJECT_NAME}, "
        #       f"found dist/{dirs[0].name}")
        return dirs[0]

    # Maybe --onefile produced a single executable
    files = [f for f in dist.iterdir() if f.is_file()]
    if files:
        pkg_dir = dist / PROJECT_NAME
        pkg_dir.mkdir()
        for f in files:
            shutil.move(str(f), str(pkg_dir / f.name))
        return pkg_dir

    return None


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
            # print(f"[build] Copied {filename}")

    for whl in Path(".").glob("mazegenerator*.whl"):
        shutil.copy2(whl, dist_dir / whl.name)
        # print(f"[build] Copied {whl.name}")


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
        f"  Run the {PROJECT_NAME} executable in this directory.\n"
        "  Or from source: python3 pac-man.py config.json\n"
    )
    with open(dist_dir / "INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    # print("[build] Created INSTRUCTIONS.txt")


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

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[build] Archive created: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def main() -> None:
    """Run the full build pipeline."""
    # print(f"[build] Packaging {PROJECT_NAME}...")
    # print(f"[build] Platform: {sys.platform}")
    # print(f"[build] Python: {sys.executable}")

    if not check_pyinstaller():
        print("[build] PyInstaller not found.")
        print("[build] Install it with: uv add pyinstaller")
        sys.exit(1)

    # Clean previous builds
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"[build] Cleaned {d}/")

    # Build
    if not build_executable():
        sys.exit(1)

    # Find output — auto-detect whatever PyInstaller created
    dist_dir = find_dist_dir()
    if dist_dir is None:
        # print("[build] Error: no output found in dist/")
        # print("[build] Contents of dist/:")
        # dist = Path("dist")
        # if dist.exists():
        #     for item in dist.iterdir():
        #         print(f"  {item}")
        # else:
        #     print("  (dist/ does not exist)")
        sys.exit(1)

    print(f"[build] Found output at: {dist_dir}")

    copy_extras(dist_dir)
    create_launch_instructions(dist_dir)
    zip_path = create_zip(dist_dir)

    print()
    print("  Build complete!")
    print(f"  Upload {zip_path} to Itch.io")


if __name__ == "__main__":
    main()
