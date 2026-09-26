# easyocr_screen.py
#
# Adaptive two-stage OCR with cache.


import os
import time
import warnings
import sys
import hashlib
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend

try:
    import easyocr
    from PIL import Image, ImageEnhance
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


EASYOCR_RECOGNIZER_JOB = "jprl9wnvp"
EASYOCR_RECOGNIZER_LATENCY_MS = 19.3

FAST_WIDTH = 800
FAST_CANVAS = 1200
QUALITY_WIDTH = 1000
QUALITY_CANVAS = 2560
MIN_GOOD_CONFIDENCE = 0.85

_global_reader = None
_global_init_ms = 0
_global_load_error = None

_ocr_cache = {}


def get_reader():
    global _global_reader, _global_init_ms, _global_load_error

    if _global_reader is not None:
        return _global_reader, _global_init_ms, _global_load_error

    if not HAS_EASYOCR:
        _global_load_error = "easyocr not installed"
        return None, 0, _global_load_error

    print("  [Loading EasyOCR model - one time only]")
    t0 = time.time()
    try:
        _global_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        _global_init_ms = round((time.time() - t0) * 1000, 2)
        print("  [EasyOCR loaded in " + str(_global_init_ms) + " ms]")
    except Exception as e:
        _global_load_error = str(e)
        print("  [EasyOCR load FAILED: " + str(e) + "]")
        _global_reader = None

    return _global_reader, _global_init_ms, _global_load_error


def content_hash(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()[:24]
    except Exception:
        return None


def prep_image(img_path, max_w):
    try:
        img = Image.open(img_path).convert("L")
        w, h = img.size

        cx = int(w * 0.03)
        cy = int(h * 0.03)
        img = img.crop((cx, cy, w - cx, h - cy))

        w2, h2 = img.size
        if w2 > max_w:
            r = max_w / float(w2)
            img = img.resize((max_w, int(h2 * r)), Image.LANCZOS)

        img = ImageEnhance.Contrast(img).enhance(1.3)

        tmp = str(Path(img_path).parent / "_tmp_ocr.png")
        img.save(tmp)
        return tmp, img.size[0], img.size[1]
    except Exception:
        return img_path, 0, 0


def cleanup(p):
    if p and Path(p).exists():
        try:
            Path(p).unlink()
        except Exception:
            pass


def run_ocr_pass(reader, proc, canvas):
    t0 = time.time()
    text = ""
    avg = 0.0
    mn = 0.0
    n = 0

    if reader is None:
        return None

    try:
        results = reader.readtext(
            proc,
            detail=1,
            paragraph=False,
            batch_size=1,
            workers=0,
            canvas_size=canvas,
            mag_ratio=1.0,
            decoder="greedy",
        )

        texts = []
        confs = []
        for r in results:
            if len(r) >= 3:
                texts.append(r[1])
                confs.append(r[2])

        text = " ".join(texts).strip()
        n = len(texts)

        if confs:
            avg = sum(confs) / len(confs)
            mn = min(confs)
    except Exception:
        pass

    ms = round((time.time() - t0) * 1000, 2)

    return {
        "text": text,
        "avg": round(avg, 3),
        "min": round(mn, 3),
        "n": n,
        "ms": ms,
    }


class EasyOCRScreenAnalyzer:

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)
        self.mode = mode
        self.reader, self.init_ms, self.load_err = get_reader()

    def extract_text(self, image_path, use_cache=True):
        inf = self.backend.infer("vision", {"image": image_path})

        cache_key = content_hash(image_path)
        t_cache = time.time()
        if use_cache and cache_key is not None and cache_key in _ocr_cache:
            cached = dict(_ocr_cache[cache_key])
            cache_lookup_ms = round((time.time() - t_cache) * 1000, 3)
            cached["cache_hit"] = True
            cached["cache_lookup_ms"] = cache_lookup_ms
            return cached
        cache_lookup_ms = round((time.time() - t_cache) * 1000, 3)

        proc1, w1, h1 = prep_image(image_path, FAST_WIDTH)
        r1 = run_ocr_pass(self.reader, proc1, FAST_CANVAS)
        cleanup(proc1)

        if r1 is None:
            return self._bad(image_path)

        retry = r1["avg"] < MIN_GOOD_CONFIDENCE or r1["n"] < 2

        if retry:
            proc2, w2, h2 = prep_image(image_path, QUALITY_WIDTH)
            r2 = run_ocr_pass(self.reader, proc2, QUALITY_CANVAS)
            cleanup(proc2)

            if r2 is not None and r2["avg"] > r1["avg"]:
                final = r2
                size = str(w2) + "x" + str(h2)
                used_w = QUALITY_WIDTH
            else:
                final = r1
                size = str(w1) + "x" + str(h1)
                used_w = FAST_WIDTH
            passes = 2
        else:
            final = r1
            size = str(w1) + "x" + str(h1)
            used_w = FAST_WIDTH
            passes = 1

        if not final["text"]:
            st = "EMPTY"
        elif final["avg"] >= MIN_GOOD_CONFIDENCE:
            st = "SUCCESS"
        else:
            st = "LOW_CONFIDENCE"

        result = {
            "text": final["text"],
            "method": "EasyOCR (CPU, adaptive)",
            "status": st,
            "num_detections": final["n"],
            "avg_confidence": final["avg"],
            "min_confidence": final["min"],
            "load_error": self.load_err,
            "init_ms": self.init_ms,
            "inference_ms": final["ms"],
            "image_size": size,
            "used_width": used_w,
            "passes_used": passes,
            "retry_triggered": retry,
            "fast_pass_conf": r1["avg"],
            "cache_hit": False,
            "cache_lookup_ms": cache_lookup_ms,
            "ai_hub_job": EASYOCR_RECOGNIZER_JOB,
            "ai_hub_latency_ms": EASYOCR_RECOGNIZER_LATENCY_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + EASYOCR_RECOGNIZER_JOB,
        }

        if cache_key is not None:
            _ocr_cache[cache_key] = dict(result)

        return result

    def _bad(self, image_path):
        return {
            "text": "",
            "method": "EasyOCR error",
            "status": "ERROR",
            "num_detections": 0,
            "avg_confidence": 0.0,
            "min_confidence": 0.0,
            "load_error": self.load_err,
            "init_ms": self.init_ms,
            "inference_ms": 0,
            "image_size": "n/a",
            "used_width": 0,
            "passes_used": 0,
            "retry_triggered": False,
            "fast_pass_conf": 0,
            "cache_hit": False,
            "cache_lookup_ms": 0,
            "ai_hub_job": EASYOCR_RECOGNIZER_JOB,
            "ai_hub_latency_ms": EASYOCR_RECOGNIZER_LATENCY_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + EASYOCR_RECOGNIZER_JOB,
        }


if __name__ == "__main__":
    print("Testing adaptive OCR...")
    a = EasyOCRScreenAnalyzer(mode="cpu")
    img = "docs/screenshots/hr_screenshot.png"

    if Path(img).exists():
        print()
        print("Run 1 (cold - no cache):")
        r1 = a.extract_text(img, use_cache=False)
        print("  Status:            " + r1["status"])
        print("  Fast pass conf:    " + str(r1["fast_pass_conf"]))
        print("  Retry triggered:   " + str(r1["retry_triggered"]))
        print("  Passes used:       " + str(r1["passes_used"]))
        print("  Final confidence:  " + str(r1["avg_confidence"]))
        print("  Inference:         " + str(r1["inference_ms"]) + " ms")

        print()
        print("Run 2 (populate cache):")
        a.extract_text(img, use_cache=True)

        print()
        print("Run 3 (cache hit test):")
        r3 = a.extract_text(img, use_cache=True)
        print("  Cache hit:         " + str(r3["cache_hit"]))
        print("  Cache lookup:      " + str(r3["cache_lookup_ms"]) + " ms")
        print("  Final confidence:  " + str(r3["avg_confidence"]))
    else:
        print("Image not found: " + img)