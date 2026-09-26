# memory_profile.py

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def rss_mb():
    if not HAS_PSUTIL:
        return 0
    p = psutil.Process(os.getpid())
    return round(p.memory_info().rss / (1024 * 1024), 2)


def main():
    if not HAS_PSUTIL:
        print("Install psutil: pip install psutil")
        return

    print("=" * 50)
    print("  SENTINEL DRISHTI - Memory Profile")
    print("=" * 50)
    print()

    startup = rss_mb()
    print("  Startup RAM:        " + str(startup) + " MB")

    from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
    a = EasyOCRScreenAnalyzer(mode="cpu")
    after_ocr = rss_mb()
    print("  After OCR load:     " + str(after_ocr) + " MB")
    print("  OCR model size:     " + str(round(after_ocr - startup, 2)) + " MB")

    img = "docs/screenshots/hr_screenshot.png"
    if Path(img).exists():
        for _ in range(3):
            a.extract_text(img, use_cache=True)
        steady = rss_mb()
        print("  Steady-state RAM:   " + str(steady) + " MB")

        for i in range(20):
            a.extract_text(img, use_cache=True)
        peak = rss_mb()
        print("  Peak RAM:           " + str(peak) + " MB")

    print()


if __name__ == "__main__":
    main()