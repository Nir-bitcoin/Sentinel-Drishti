# screen_capture.py
from datetime import datetime
from pathlib import Path

HAS_OCR = False
try:
    import pytesseract
    from PIL import Image
    pytesseract.get_tesseract_version()
    HAS_OCR = True
except Exception:
    HAS_OCR = False


class ScreenCapture:

    def __init__(self):
        self.last_capture = None
        self.ocr_enabled = HAS_OCR

    def capture_from_image(self, image_path, app_name="Unknown"):
        # Try OCR, if it fails read the .txt file
        text = ""
        method = ""

        if self.ocr_enabled:
            try:
                img = Image.open(image_path)
                text = pytesseract.image_to_string(img).strip()
                method = "OCR"
            except Exception:
                text = ""
                method = ""

        # fallback
        if text == "":
            txt_file = Path(image_path).with_suffix(".txt")
            if txt_file.exists():
                text = txt_file.read_text(encoding="utf-8").strip()
                method = "fallback-txt"
            else:
                text = "[no text available]"
                method = "none"

        self.last_capture = {
            "timestamp": datetime.now().isoformat(),
            "app": app_name,
            "source": str(image_path),
            "content": text,
            "method": method,
        }
        return self.last_capture

    def capture_text(self, content, app_name="Unknown"):
        # Direct text input. Used for demo scenarios.
        self.last_capture = {
            "timestamp": datetime.now().isoformat(),
            "app": app_name,
            "source": "direct",
            "content": content,
            "method": "direct",
        }
        return self.last_capture