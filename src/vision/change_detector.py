# change_detector.py
#
# Detects whether the screen changed significantly since last frame.


import hashlib
from pathlib import Path


class ChangeDetector:
    """Detects significant screen changes using content hashing."""

    def __init__(self):
        self.last_hash = None
        self.last_size = None
        self.frames_checked = 0
        self.frames_unchanged = 0

    def _hash_file(self, image_path):
        # fast hash: first 8KB + file size
        try:
            p = Path(image_path)
            size = p.stat().st_size
            with open(p, "rb") as f:
                head = f.read(8192)
            h = hashlib.sha256(head + str(size).encode()).hexdigest()[:16]
            return h, size
        except Exception:
            return None, None

    def has_changed(self, image_path):
        """Returns True if screen changed since last call."""
        self.frames_checked += 1

        h, size = self._hash_file(image_path)
        if h is None:
            return True  # if can't read, assume changed

        # first frame
        if self.last_hash is None:
            self.last_hash = h
            self.last_size = size
            return True

        # compare
        if h == self.last_hash and size == self.last_size:
            self.frames_unchanged += 1
            return False

        self.last_hash = h
        self.last_size = size
        return True

    def stats(self):
        total = self.frames_checked
        unchanged = self.frames_unchanged
        saved = round(100 * unchanged / total, 1) if total > 0 else 0
        return {
            "frames_checked": total,
            "frames_unchanged": unchanged,
            "ocr_skipped_pct": saved,
        }


if __name__ == "__main__":
    d = ChangeDetector()
    img = "docs/screenshots/hr_screenshot.png"

    if Path(img).exists():
        print("Frame 1:", d.has_changed(img))
        print("Frame 2:", d.has_changed(img))
        print("Frame 3:", d.has_changed(img))
        print("Stats:", d.stats())
    else:
        print("Image not found")