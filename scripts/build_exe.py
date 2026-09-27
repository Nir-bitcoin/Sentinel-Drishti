# build_exe.py

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_pyinstaller():
    try:
        import PyInstaller  # noqa
        return True
    except ImportError:
        return False


def main():
    print("=" * 58)
    print("  SENTINEL DRISHTI - EXE BUILD")
    print("=" * 58)
    print()

    if sys.platform != "win32":
        print("This build script targets Windows only.")
        print("For Linux/macOS, adapt the PyInstaller spec manually.")
        return

    if not check_pyinstaller():
        print("PyInstaller not installed.")
        print("Install: pip install pyinstaller")
        print()
        ans = input("Install now? [y/N]: ").strip().lower()
        if ans == "y":
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        else:
            return

    print("Building standalone executable...")
    print("This may take several minutes.")
    print()

    # One-file build with data files
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name", "sentinel",
        "--onedir",
        "--console",
        "--add-data", "config;config",
        "--add-data", "docs;docs",
        "--add-data", "demo_scenarios;demo_scenarios",
        "--hidden-import", "easyocr",
        "--hidden-import", "PIL",
        "--hidden-import", "numpy",
        "--hidden-import", "psutil",
        "--hidden-import", "yaml",
        str(ROOT / "sentinel.py"),
    ]

    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode == 0:
        print()
        print("=" * 58)
        print("  BUILD COMPLETE")
        print("=" * 58)
        print()
        print("  Output: " + str(ROOT / "dist" / "sentinel" / "sentinel.exe"))
        print()
        print("  To run:")
        print("    .\\dist\\sentinel\\sentinel.exe")
        print()
    else:
        print()
        print("  BUILD FAILED (exit code " + str(result.returncode) + ")")
        print()


if __name__ == "__main__":
    main()