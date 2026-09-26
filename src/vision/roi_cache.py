# roi_cache.py


import hashlib
from pathlib import Path


class ROICache:
    """Content-hash based cache for OCR results."""

    def __init__(self, max_size=20):
        self.max_size = max_size
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def _hash_file(self, image_path):
        try:
            p = Path(image_path)
            size = p.stat().st_size
            with open(p, "rb") as f:
                head = f.read(4096)
            h = hashlib.sha256(head + str(size).encode()).hexdigest()[:16]
            return h
        except Exception:
            return None

    def get(self, image_path):
        h = self._hash_file(image_path)
        if h is None:
            return None
        if h in self.cache:
            self.hits += 1
            return self.cache[h]
        self.misses += 1
        return None

    def put(self, image_path, result):
        h = self._hash_file(image_path)
        if h is None:
            return
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[h] = result

    def stats(self):
        total = self.hits + self.misses
        rate = round(100 * self.hits / total, 1) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": rate,
        }


if __name__ == "__main__":
    c = ROICache()
    print("Cache initialized")
    print("Stats:", c.stats())