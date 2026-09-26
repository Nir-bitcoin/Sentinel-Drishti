# easyocr_screen.py

import os
import time
import warnings
import sys
import hashlib
from pathlib import Path
from collections import OrderedDict

warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend

try:
    import easyocr
    import numpy as np
    from PIL import Image, ImageEnhance
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


EASYOCR_RECOGNIZER_JOB = "jprl9wnvp"
EASYOCR_RECOGNIZER_LATENCY_MS = 19.3

FAST_WIDTH = 800
MIN_GOOD_CONFIDENCE = 0.85
LOW_CONF_THRESHOLD = 0.60
ROI_PADDING = 30
ROI_UPSCALE = 2.0

_global_reader = None
_global_init_ms = 0
_global_load_error = None

_CACHE_MAX = 100
_ocr_cache = OrderedDict()
_cache_stats = {"hits": 0, "misses": 0, "evictions": 0}


def get_reader():
    global _global_reader, _global_init_ms, _global_load_error
    if _global_reader is not None:
        return _global_reader, _global_init_ms, _global_load_error
    if not HAS_EASYOCR:
        _global_load_error = "easyocr not installed"
        return None, 0, _global_load_error
    print("  [Loading EasyOCR - one time only]")
    t0 = time.time()
    try:
        _global_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        _global_init_ms = round((time.time() - t0) * 1000, 2)
        print("  [Loaded in " + str(_global_init_ms) + " ms]")
    except Exception as e:
        _global_load_error = str(e)
        _global_reader = None
    return _global_reader, _global_init_ms, _global_load_error


def content_hash(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()[:24]
    except Exception:
        return None


def cache_get(key):
    if key is None or key not in _ocr_cache:
        _cache_stats["misses"] += 1
        return None
    _ocr_cache.move_to_end(key)
    _cache_stats["hits"] += 1
    return dict(_ocr_cache[key])


def cache_put(key, value):
    if key is None:
        return
    if key in _ocr_cache:
        _ocr_cache.move_to_end(key)
    _ocr_cache[key] = dict(value)
    while len(_ocr_cache) > _CACHE_MAX:
        _ocr_cache.popitem(last=False)
        _cache_stats["evictions"] += 1


def cache_stats():
    total = _cache_stats["hits"] + _cache_stats["misses"]
    rate = round(100 * _cache_stats["hits"] / total, 1) if total > 0 else 0
    return {
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "evictions": _cache_stats["evictions"],
        "size": len(_ocr_cache),
        "hit_rate_pct": rate,
    }


def cache_clear():
    _ocr_cache.clear()
    _cache_stats["hits"] = 0
    _cache_stats["misses"] = 0
    _cache_stats["evictions"] = 0


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
        return img
    except Exception:
        return None


def two_stage_ocr_roi(reader, pil_img, fast_conf_threshold=MIN_GOOD_CONFIDENCE):
    if reader is None:
        return None, "no reader"

    t0 = time.time()
    img_np = np.array(pil_img)

    try:
        stage1 = reader.readtext(img_np, detail=1, paragraph=False,
                                 canvas_size=1600, mag_ratio=1.0,
                                 decoder="greedy", batch_size=1, workers=0)
    except Exception as e:
        return None, "stage1 error: " + str(e)

    texts = []
    confs = []
    low_conf_boxes = []
    high_conf_count = 0

    for item in stage1:
        if len(item) < 3:
            continue
        bbox, text, conf = item[0], item[1], item[2]
        if conf >= fast_conf_threshold:
            texts.append(text)
            confs.append(conf)
            high_conf_count += 1
        else:
            low_conf_boxes.append(bbox)

    recovered = 0
    for bbox in low_conf_boxes:
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        x_min = max(0, int(min(xs)) - ROI_PADDING)
        x_max = min(img_np.shape[1], int(max(xs)) + ROI_PADDING)
        y_min = max(0, int(min(ys)) - ROI_PADDING)
        y_max = min(img_np.shape[0], int(max(ys)) + ROI_PADDING)

        crop = img_np[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            continue

        try:
            ch, cw = crop.shape[:2]
            if cw > 0 and ch > 0:
                pil_crop = Image.fromarray(crop)
                pil_crop = pil_crop.resize(
                    (int(cw * ROI_UPSCALE), int(ch * ROI_UPSCALE)),
                    Image.LANCZOS
                )
                crop = np.array(pil_crop)
        except Exception:
            pass

        try:
            crop_results = reader.readtext(crop, detail=1, paragraph=False,
                                            decoder="greedy", batch_size=1, workers=0,
                                            canvas_size=1600, mag_ratio=1.0)
        except Exception:
            continue

        best_crop_conf = 0.0
        best_crop_text = ""
        for c in crop_results:
            if len(c) >= 3:
                c_text, c_conf = c[1], c[2]
                if c_conf > best_crop_conf:
                    best_crop_conf = c_conf
                    best_crop_text = c_text

        if best_crop_text and best_crop_conf > 0.5:
            texts.append(best_crop_text)
            confs.append(best_crop_conf)
            recovered += 1

    text = " ".join(texts).strip()
    n = len(texts)
    avg = sum(confs) / len(confs) if confs else 0.0
    mn = min(confs) if confs else 0.0
    ms = round((time.time() - t0) * 1000, 2)

    return {
        "text": text,
        "avg_confidence": round(avg, 3),
        "min_confidence": round(mn, 3),
        "num_detections": n,
        "high_conf_count": high_conf_count,
        "low_conf_count": len(low_conf_boxes),
        "roi_recovered": recovered,
        "inference_ms": ms,
    }, None


class EasyOCRScreenAnalyzer:

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)
        self.mode = mode
        self.reader, self.init_ms, self.load_err = get_reader()

    def extract_text(self, image_path, use_cache=True):
        self.backend.infer("vision", {"image": image_path})

        cache_key = content_hash(image_path)
        if use_cache:
            cached = cache_get(cache_key)
            if cached is not None:
                cached["cache_hit"] = True
                return cached

        pil_img = prep_image(image_path, FAST_WIDTH)
        if pil_img is None:
            return self._bad(image_path, "prep failed")

        result, err = two_stage_ocr_roi(self.reader, pil_img)
        if result is None:
            return self._bad(image_path, err)

        text = result["text"]
        avg = result["avg_confidence"]
        fallback_used = False

        if avg < MIN_GOOD_CONFIDENCE and result["low_conf_count"] > 0:
            try:
                pil_hi = prep_image(image_path, 1000)
                if pil_hi is not None:
                    hi_np = np.array(pil_hi)
                    hi_results = self.reader.readtext(
                        hi_np, detail=1, paragraph=False,
                        canvas_size=2560, mag_ratio=1.0,
                        decoder="greedy", batch_size=1, workers=0
                    )
                    hi_texts = []
                    hi_confs = []
                    for hr in hi_results:
                        if len(hr) >= 3:
                            hi_texts.append(hr[1])
                            hi_confs.append(hr[2])

                    if hi_confs:
                        hi_avg = sum(hi_confs) / len(hi_confs)
                        if hi_avg > avg:
                            text = " ".join(hi_texts).strip()
                            avg = round(hi_avg, 3)
                            result["num_detections"] = len(hi_texts)
                            result["min_confidence"] = round(min(hi_confs), 3)
                            fallback_used = True
            except Exception:
                pass

        if not text:
            st = "EMPTY"
        elif avg >= MIN_GOOD_CONFIDENCE:
            st = "SUCCESS"
        else:
            st = "LOW_CONFIDENCE"

        fast_status = "SUCCESS" if avg >= MIN_GOOD_CONFIDENCE else "LOW_CONFIDENCE"

        final = {
            "text": text,
            "method": "EasyOCR (CPU, two-stage ROI + hybrid)",
            "status": st,
            "num_detections": result["num_detections"],
            "avg_confidence": avg,
            "min_confidence": result["min_confidence"],
            "high_conf_count": result["high_conf_count"],
            "low_conf_count": result["low_conf_count"],
            "roi_recovered": result["roi_recovered"],
            "fallback_used": fallback_used,
            "load_error": self.load_err,
            "init_ms": self.init_ms,
            "inference_ms": result["inference_ms"],
            "cache_hit": False,
            "ai_hub_job": EASYOCR_RECOGNIZER_JOB,
            "ai_hub_latency_ms": EASYOCR_RECOGNIZER_LATENCY_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + EASYOCR_RECOGNIZER_JOB,
            # backward-compat fields
            "image_size": str(FAST_WIDTH) + "x?",
            "used_width": FAST_WIDTH,
            "passes_used": 2 if fallback_used else 1,
            "retry_triggered": result["low_conf_count"] > 0,
            "fast_pass_conf": avg,
            "fast_pass_status": fast_status,
            "quality_pass_conf": avg if fallback_used else 0,
            "quality_pass_status": "SUCCESS" if fallback_used else "SKIPPED",
            "cache_lookup_ms": 0,
        }

        cache_put(cache_key, final)
        return final

    def _bad(self, image_path, err):
        return {
            "text": "", "method": "EasyOCR error", "status": "ERROR",
            "num_detections": 0, "avg_confidence": 0.0, "min_confidence": 0.0,
            "high_conf_count": 0, "low_conf_count": 0, "roi_recovered": 0,
            "fallback_used": False,
            "load_error": err, "init_ms": self.init_ms, "inference_ms": 0,
            "cache_hit": False,
            "ai_hub_job": EASYOCR_RECOGNIZER_JOB,
            "ai_hub_latency_ms": EASYOCR_RECOGNIZER_LATENCY_MS,
            "ai_hub_link": "https://aihub.qualcomm.com/jobs/" + EASYOCR_RECOGNIZER_JOB,
            # backward-compat fields
            "image_size": "n/a",
            "used_width": 0,
            "passes_used": 0,
            "retry_triggered": False,
            "fast_pass_conf": 0,
            "fast_pass_status": "ERROR",
            "quality_pass_conf": 0,
            "quality_pass_status": "SKIPPED",
            "cache_lookup_ms": 0,
        }


if __name__ == "__main__":
    print("Testing two-stage ROI OCR + hybrid fallback...")
    a = EasyOCRScreenAnalyzer(mode="cpu")
    img = "docs/screenshots/hr_screenshot.png"
    if Path(img).exists():
        print()
        print("Run 1 (populate cache):")
        r1 = a.extract_text(img, use_cache=True)
        print("  Status:        " + r1["status"])
        print("  High conf:     " + str(r1["high_conf_count"]))
        print("  Low conf:      " + str(r1["low_conf_count"]))
        print("  ROI recovered: " + str(r1["roi_recovered"]))
        print("  Final conf:    " + str(r1["avg_confidence"]))
        print("  Inference:     " + str(r1["inference_ms"]) + " ms")
        print("  Fallback used: " + str(r1.get("fallback_used", False)))
        print()
        print("Run 2 (cache):")
        r2 = a.extract_text(img, use_cache=True)
        print("  Cache hit:     " + str(r2["cache_hit"]))
        print()
        print("Cache stats:     " + str(cache_stats()))
    else:
        print("Image not found: " + img)