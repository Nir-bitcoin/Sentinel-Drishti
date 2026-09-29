# augment_dataset.py
#
# Augments the 30-image controlled regression set into 500+ images
# by applying 17 realistic distortions per original.
#
# Output: evaluation/augmented_dataset/ with 500+ images + manifest CSV

import os
import csv
import random
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Paths
SRC_DIR = Path("evaluation/images")
OUT_DIR = Path("evaluation/augmented_dataset")
MANIFEST_IN = Path("evaluation/dataset_manifest.csv")
MANIFEST_OUT = Path("evaluation/augmented_manifest.csv")

# 30 originals + 17 variants each = 30 + 510 = 540 images
VARIANTS_PER_IMAGE = 17

random.seed(42)
np.random.seed(42)


def augment_image(img, variant_id):
    """Apply a realistic distortion to the image. 17 variant types."""

    v = variant_id % 17

    if v == 0:
        # Slight rotation
        angle = random.choice([-10, -5, 5, 10])
        return img.rotate(angle, expand=True, fillcolor=(255, 255, 255))

    elif v == 1:
        # Gaussian blur (mild)
        return img.filter(ImageFilter.GaussianBlur(radius=1.0))

    elif v == 2:
        # Motion-like blur (stronger)
        return img.filter(ImageFilter.GaussianBlur(radius=1.8))

    elif v == 3:
        # Darker (low light)
        return ImageEnhance.Brightness(img).enhance(0.7)

    elif v == 4:
        # Brighter (overexposed)
        return ImageEnhance.Brightness(img).enhance(1.3)

    elif v == 5:
        # Lower contrast (washed out)
        return ImageEnhance.Contrast(img).enhance(0.6)

    elif v == 6:
        # Higher contrast
        return ImageEnhance.Contrast(img).enhance(1.4)

    elif v == 7:
        # Gaussian noise
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, 15, arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    elif v == 8:
        # JPEG compression artifacts (heavy)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=25)
        buf.seek(0)
        return Image.open(buf).convert(img.mode)

    elif v == 9:
        # Slight zoom + crop
        w, h = img.size
        zoom = random.uniform(0.90, 0.95)
        new_w, new_h = int(w * zoom), int(h * zoom)
        left = random.randint(0, max(0, w - new_w))
        top = random.randint(0, max(0, h - new_h))
        cropped = img.crop((left, top, left + new_w, top + new_h))
        return cropped.resize((w, h), Image.LANCZOS)

    elif v == 10:
        # Sharpen (over-processed look)
        return img.filter(ImageFilter.SHARPEN)

    elif v == 11:
        # Slight color/temperature shift
        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * 1.05)))
        b = b.point(lambda x: min(255, int(x * 0.95)))
        return Image.merge("RGB", (r, g, b))

    elif v == 12:
        # Slight perspective warp (simulates camera angle)
        w, h = img.size
        offset = int(min(w, h) * 0.03)
        coeffs = (
            1, 0, -offset,
            0, 1, 0,
            0, 0, 1,
        )
        return img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

    elif v == 13:
        # Salt and pepper noise
        arr = np.array(img).copy()
        h, w = arr.shape[:2]
        n = int(0.005 * h * w)
        coords = [np.random.randint(0, h - 1, n), np.random.randint(0, w - 1, n)]
        arr[coords[0], coords[1], :] = 255
        coords = [np.random.randint(0, h - 1, n), np.random.randint(0, w - 1, n)]
        arr[coords[0], coords[1], :] = 0
        return Image.fromarray(arr)

    elif v == 14:
        # Resize down + up (resolution loss)
        w, h = img.size
        small = img.resize((w // 2, h // 2), Image.BILINEAR)
        return small.resize((w, h), Image.BILINEAR)

    elif v == 15:
        # Add subtle border / padding (like screenshot frame)
        w, h = img.size
        pad = int(min(w, h) * 0.05)
        new = Image.new("RGB", (w + 2 * pad, h + 2 * pad), (240, 240, 240))
        new.paste(img, (pad, pad))
        return new

    elif v == 16:
        # Combined rotation + blur (compound)
        angle = random.choice([-7, 7])
        rotated = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))
        return rotated.filter(ImageFilter.GaussianBlur(radius=0.8))

    return img


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(MANIFEST_IN, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    print(f"Loaded {len(rows)} original samples from {MANIFEST_IN}")
    print(f"Generating {VARIANTS_PER_IMAGE} variants per image...")
    print(f"Expected total: {len(rows) * (VARIANTS_PER_IMAGE + 1)} images")
    print()

    out_rows = []

    for row in rows:
        src_path = Path(row["image_path"])
        if not src_path.exists():
            print(f"  SKIP (missing): {src_path}")
            continue

        img = Image.open(src_path).convert("RGB")
        image_id = row["image_id"]

        # Keep the clean original in the augmented set
        out_rows.append({
            "image_id": f"{image_id}_orig",
            "image_path": str(src_path).replace("\\", "/"),
            "has_pan": row["has_pan"],
            "has_phone": row["has_phone"],
            "has_financial": row["has_financial"],
            "has_confidential": row["has_confidential"],
            "source": "original",
        })

        for v in range(VARIANTS_PER_IMAGE):
            aug_img = augment_image(img, v)
            filename = f"{image_id}_aug{v:02d}.png"
            out_path = OUT_DIR / filename
            aug_img.save(out_path)

            out_rows.append({
                "image_id": f"{image_id}_aug{v:02d}",
                "image_path": str(out_path).replace("\\", "/"),
                "has_pan": row["has_pan"],
                "has_phone": row["has_phone"],
                "has_financial": row["has_financial"],
                "has_confidential": row["has_confidential"],
                "source": "augmented",
            })

        print(f"  {image_id}: 1 original + {VARIANTS_PER_IMAGE} variants")

    with open(MANIFEST_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_id", "image_path",
                "has_pan", "has_phone", "has_financial", "has_confidential",
                "source",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print()
    print("=" * 60)
    print(f"  Total images generated: {len(out_rows)}")
    print(f"  Manifest: {MANIFEST_OUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()