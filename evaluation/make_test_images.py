# make_test_images.py

import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow required: pip install Pillow")
    sys.exit(1)


OUT_DIR = Path("evaluation/images")
MANIFEST = Path("evaluation/dataset_manifest.csv")

# (id, filename, lines, gt flags)
# gt flags: has_pan, has_phone, has_financial, has_confidential

_PAN_POOL = [
    "ABCDE1234F", "FGHIJ5678K", "ZZZZZ9999Z", "KLMNO2345P",
    "QRSTU6789V", "WXYZA1234B", "BCDEF5678G", "GHIJK9012L",
    "MNOPQ3456R", "STUVW7890X", "YZABC2345D", "DEFGH6789J",
    "IJKLM0123N", "NOPQR4567S", "TUVWX8901Y", "ZABCD3456E",
    "EFGHI7890K", "JKLMN1234O",
]

_PHONE_POOL = [
    "9876543210", "9123456780", "9988776655", "9000111222",
    "9555666777", "9888777666", "9777888999", "9666555444",
    "9333444555", "9222333444", "9111222333", "9000999888",
    "8888777666", "8777666555", "8666555444", "8555444333",
    "8444333222", "8333222111",
]

_FIN_POOL = [
    1500000, 2000000, 2500000, 3000000, 1200000, 1800000,
    2200000, 2800000, 3500000, 900000, 1100000, 1600000,
    2100000, 2700000, 3300000, 800000, 1300000, 1700000,
]

_BASE_TEMPLATES = [
    ("pan_simple",       lambda p, ph, f: ["Employee Record", "PAN: " + p],                      1, 0, 0, 0),
    ("pan_only_line",    lambda p, ph, f: ["PAN " + p],                                          1, 0, 0, 0),
    ("pan_with_name",    lambda p, ph, f: ["Name: Rajesh Kumar", "PAN: " + p],                   1, 0, 0, 0),
    ("pan_uppercase",    lambda p, ph, f: ["TAX DOCUMENT", "PAN: " + p],                         1, 0, 0, 0),
    ("pan_inline",       lambda p, ph, f: ["Ref no: " + p + " valid"],                           1, 0, 0, 0),
    ("phone_simple",     lambda p, ph, f: ["Contact", "Mobile: " + ph],                          0, 1, 0, 0),
    ("phone_only",       lambda p, ph, f: [ph],                                                  0, 1, 0, 0),
    ("phone_with_label", lambda p, ph, f: ["Customer Support", "Call " + ph],                    0, 1, 0, 0),
    ("phone_multiple",   lambda p, ph, f: ["Contact List", "Primary: " + ph],                    0, 1, 0, 0),
    ("phone_inline",     lambda p, ph, f: ["Reach me at " + ph + " anytime"],                    0, 1, 0, 0),
    ("financial_salary", lambda p, ph, f: ["Payroll", "Employee salary: " + str(f)],             0, 0, 1, 0),
    ("financial_ctc",    lambda p, ph, f: ["CTC breakdown", "Annual CTC: " + str(f)],            0, 0, 1, 0),
    ("financial_payroll",lambda p, ph, f: ["Payroll Summary Q4"],                                0, 0, 1, 0),
    ("financial_bonus",  lambda p, ph, f: ["Bonus structure", "Bonus: " + str(f // 5)],          0, 0, 1, 0),
    ("financial_comp",   lambda p, ph, f: ["Compensation review"],                               0, 0, 1, 0),
    ("conf_marking",     lambda p, ph, f: ["CONFIDENTIAL", "Internal only"],                     0, 0, 0, 1),
    ("proprietary",      lambda p, ph, f: ["PROPRIETARY", "Do not distribute"],                  0, 0, 0, 1),
    ("internal_only",    lambda p, ph, f: ["Internal only - Q4 pricing draft"],                  0, 0, 0, 1),
    ("trade_secret",     lambda p, ph, f: ["Trade secret information"],                          0, 0, 0, 1),
    ("benign_meeting",   lambda p, ph, f: ["Team Meeting Notes", "Discuss Q4 roadmap"],          0, 0, 0, 0),
    ("benign_notes",     lambda p, ph, f: ["Project notes", "Due Friday"],                       0, 0, 0, 0),
    ("benign_lunch",     lambda p, ph, f: ["Lunch at 1pm", "Room 4"],                            0, 0, 0, 0),
    ("benign_shopping",  lambda p, ph, f: ["Shopping list", "Milk, eggs, bread"],                0, 0, 0, 0),
    ("benign_greeting",  lambda p, ph, f: ["Good morning team"],                                 0, 0, 0, 0),
    ("mixed_pan_phone",  lambda p, ph, f: ["Employee Record", "PAN: " + p, "Phone: " + ph],       1, 1, 0, 0),
    ("mixed_pan_fin",    lambda p, ph, f: ["PAN: " + p, "Salary: " + str(f)],                    1, 0, 1, 0),
    ("mixed_all_three",  lambda p, ph, f: ["Employee Record", "PAN: " + p, "Phone: " + ph, "Salary: " + str(f)], 1, 1, 1, 0),
    ("mixed_conf_pan",   lambda p, ph, f: ["CONFIDENTIAL", "PAN: " + p],                         1, 0, 0, 1),
    ("mixed_conf_fin",   lambda p, ph, f: ["CONFIDENTIAL - Internal only", "Employee salary record"], 0, 0, 1, 1),
    ("mixed_full",       lambda p, ph, f: ["CONFIDENTIAL - Employee Record", "PAN: " + p, "Phone: " + ph, "Salary: " + str(f)], 1, 1, 1, 1),
]

SAMPLES = []
_counter = 1
for round_idx in range(18):
    pan = _PAN_POOL[round_idx % len(_PAN_POOL)]
    phone = _PHONE_POOL[round_idx % len(_PHONE_POOL)]
    fin = _FIN_POOL[round_idx % len(_FIN_POOL)]

    for base_id, lines_fn, pan_flag, ph_flag, fin_flag, conf_flag in _BASE_TEMPLATES:
        sid = "img" + str(_counter).zfill(3)
        fname = str(_counter).zfill(3) + "_" + base_id + "_r" + str(round_idx) + ".png"
        SAMPLES.append((sid, fname, lines_fn(pan, phone, fin),
                        pan_flag, ph_flag, fin_flag, conf_flag))
        _counter += 1

print("Generated " + str(len(SAMPLES)) + " samples (expected 540)")


def get_font(size=28):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make_image(filename, lines):
    W, H = 900, 120 + 70 * len(lines)
    img = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(36)
    font_body = get_font(28)

    y = 40
    for i, line in enumerate(lines):
        font = font_title if i == 0 else font_body
        color = (20, 20, 120) if i == 0 else (0, 0, 0)
        draw.text((50, y), line, fill=color, font=font)
        y += 60

    draw.rectangle([(5, 5), (W - 5, H - 5)], outline=(200, 200, 200), width=2)

    out_path = OUT_DIR / filename
    img.save(out_path)
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating " + str(len(SAMPLES)) + " test images in " + str(OUT_DIR))
    print()

    manifest_rows = []
    for sid, filename, lines, pan, phone, fin, conf in SAMPLES:
        path = make_image(filename, lines)
        manifest_rows.append({
            "image_id": sid,
            "image_path": str(path).replace("\\", "/"),
            "has_pan": pan,
            "has_phone": phone,
            "has_financial": fin,
            "has_confidential": conf,
        })
        if len(manifest_rows) % 50 == 0:
            print("  created: " + str(len(manifest_rows)) + " images...")

    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["image_id", "image_path", "has_pan",
                        "has_phone", "has_financial", "has_confidential"],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    print()
    print("Done. " + str(len(SAMPLES)) + " images created.")
    print("Manifest: " + str(MANIFEST))
    print()


if __name__ == "__main__":
    main()