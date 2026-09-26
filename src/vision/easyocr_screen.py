# easyocr_screen.py

import os
import time
import warnings
import sys
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


# AI Hub pe actual EasyOCR jobs
AI_HUB_JOB = "jprl9wnvp"
AI_HUB_MS = 19.3

# widths
FAST_W = 800
BEST_W = 1000

# isse neeche confidence toh retry karo
MIN_CONF = 0.85

# reader ek baar load hota hai, phir reuse
reader_cache = None
reader_load_ms = 0
reader_err = None


def load_reader():
    # sirf pehli baar load hoga
    global reader_cache, reader_load_ms, reader_err

    if reader_cache is not None:
        return reader_cache, reader_load_ms, reader_err

    if not HAS_EASYOCR:
        reader_err = "easyocr not installed"
        return None, 0, reader_err

    print("  [Loading EasyOCR model - one time only]")
    t = time.time()
    try:
        reader_cache = easyocr.Reader(['en'], gpu=False, verbose=False)
        reader_load_ms = round((time.time() - t) * 1000, 2)
        print("  [EasyOCR loaded in " + str(reader_load_ms) + " ms]")
    except Exception as e:
        reader_err = str(e)
        print("  [EasyOCR load failed: " + str(e) + "]")
        reader_cache = None

    return reader_cache, reader_load_ms, reader_err


def prep_image(img_path, max_w):
    # grayscale, thoda crop, resize, contrast
    try:
        img = Image.open(img_path).convert("L")
        w, h = img.size

        # border crop (3%)
        cx = int(w * 0.03)
        cy = int(h * 0.03)
        img = img.crop((cx, cy, w - cx, h - cy))

        # resize if too big
        w2, h2 = img.size
        if w2 > max_w:
            r = max_w / float(w2)
            img = img.resize((max_w, int(h2 * r)), Image.LANCZOS)

        # contrast thoda
        img = ImageEnhance.Contrast(img).enhance(1.3)

        tmp = str(Path(img_path).parent / "_tmp_ocr.png")
        img.save(tmp)
        return tmp, img.size[0], img.size[1], True
    except Exception:
        return img_path, 0, 0, False


def do_ocr(reader, path):
    # ek OCR pass, stats return
    t = time.time()
    txt = ""
    avg = 0.0
    mn = 0.0
    n = 0
    hi = 0

    try:
        res = reader.readtext(path, detail=1)

        parts = []
        confs = []
        for r in res:
            if len(r) >= 3:
                parts.append(r[1])
                confs.append(r[2])

        txt = " ".join(parts).strip()
        n = len(parts)

        if confs:
            avg = sum(confs) / len(confs)
            mn = min(confs)
            for c in confs:
                if c >= 0.7:
                    hi += 1

    except Exception as e:
        return None, "err: " + str(e)

    ms = round((time.time() - t) * 1000, 2)

    return {
        "text": txt,
        "avg": round(avg, 3),
        "min": round(mn, 3),
        "n": n,
        "hi": hi,
        "ms": ms,
    }, None


def cleanup(p):
    if p and Path(p).exists():
        try:
            Path(p).unlink()
        except Exception:
            pass


class EasyOCRScreenAnalyzer:

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)
        self.mode = mode
        self.reader, self.init_ms, self.load_err = load_reader()

    def extract_text(self, image_path):
        inf = self.backend.infer("vision", {"image": image_path})

        # pehle fast try
        p1, w1, h1, ok1 = prep_image(image_path, FAST_W)
        r1, e1 = do_ocr(self.reader, p1) if self.reader else (None, "no reader")
        cleanup(p1) if ok1 else None

        if r1 is None:
            return self._bad(image_path, e1)

        # fast pass kaafi hai?
        fast_good = (r1["avg"] >= MIN_CONF and r1["n"] >= 2)

        if fast_good:
            final = r1
            size = str(w1) + "x" + str(h1)
            used_w = FAST_W
            passes = 1
        else:
            # retry better quality pe
            p2, w2, h2, ok2 = prep_image(image_path, BEST_W)
            r2, e2 = do_ocr(self.reader, p2) if self.reader else (None, "no reader")
            cleanup(p2) if ok2 else None

            if r2 is not None and r2["avg"] > r1["avg"]:
                final = r2
                size = str(w2) + "x" + str(h2)
                used_w = BEST_W
            else:
                final = r1
                size = str(w1) + "x" + str(h1)
                used_w = FAST_W

            passes = 2

        # status
        if not final["text"]:
            st = "EMPTY"
        elif final["avg"] >= MIN_CONF:
            st = "SUCCESS"
        else:
            st = "LOW_CONFIDENCE"

        return {
            "text": final["text"],
            "method": "EasyOCR (CPU)",
            "status": st,
            "num_detections": final["n"],
            "avg_confidence": final["avg"],
            "min_confidence": final["min"],
            "high_conf_count": final["hi"],
            "load_error": self.load_err,
            "init_ms": self.init_ms,
            "inference_ms": final["ms"],
            "image_size": size,
            "used_width": used_w,
            "passes_used": passes,
            "fast_pass_conf": r1["avg"],
            "fast_pass_status": "good" if fast_good else "weak",
            "ai_hub_job": AI_HUB_JOB,
            "ai_hub_latency_ms": AI_HUB_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + AI_HUB_JOB,
        }

    def _bad(self, image_path, err):
        return {
            "text": "",
            "method": "EasyOCR error",
            "status": "ERROR",
            "num_detections": 0,
            "avg_confidence": 0.0,
            "min_confidence": 0.0,
            "high_conf_count": 0,
            "load_error": err,
            "init_ms": self.init_ms,
            "inference_ms": 0,
            "image_size": "n/a",
            "used_width": 0,
            "passes_used": 0,
            "fast_pass_conf": 0,
            "fast_pass_status": "error",
            "ai_hub_job": AI_HUB_JOB,
            "ai_hub_latency_ms": AI_HUB_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + AI_HUB_JOB,
        }


if __name__ == "__main__":
    print("Adaptive OCR test...")
    a = EasyOCRScreenAnalyzer(mode="cpu")

    img = "docs/screenshots/hr_screenshot.png"

    if Path(img).exists():
        print()
        print("running...")
        r = a.extract_text(img)

        print()
        print("--- result ---")
        print("status:      " + r["status"])
        print("passes:      " + str(r["passes_used"]))
        print("image:       " + r["image_size"])
        print("fast conf:   " + str(r["fast_pass_conf"]) + " (" + r["fast_pass_status"] + ")")
        print("final conf:  " + str(r["avg_confidence"]))
        print("min conf:    " + str(r["min_confidence"]))
        print("detections:  " + str(r["num_detections"]))
        print("time:        " + str(r["inference_ms"]) + " ms")
        print()
        print("text:")
        print("  " + r["text"][:150])
    else:
        print("image not found: " + img)