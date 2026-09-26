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
SAMPLES = [
    # -------- PAN (5) --------
    ("img01", "01_pan_simple.png",
     ["Employee Record", "PAN: ABCDE1234F"], 1, 0, 0, 0),
    ("img02", "02_pan_only_line.png",
     ["PAN ABCDE1234F"], 1, 0, 0, 0),
    ("img03", "03_pan_with_name.png",
     ["Name: Rajesh Kumar", "PAN: FGHIJ5678K"], 1, 0, 0, 0),
    ("img04", "04_pan_uppercase.png",
     ["TAX DOCUMENT", "PAN: ZZZZZ9999Z"], 1, 0, 0, 0),
    ("img05", "05_pan_inline.png",
     ["Ref no: ABCDE1234F valid"], 1, 0, 0, 0),

    # -------- PHONE (5) --------
    ("img06", "06_phone_simple.png",
     ["Contact", "Mobile: 9876543210"], 0, 1, 0, 0),
    ("img07", "07_phone_only.png",
     ["9876543210"], 0, 1, 0, 0),
    ("img08", "08_phone_with_label.png",
     ["Customer Support", "Call 9123456780"], 0, 1, 0, 0),
    ("img09", "09_phone_multiple.png",
     ["Contact List", "Primary: 9876543210"], 0, 1, 0, 0),
    ("img10", "10_phone_inline.png",
     ["Reach me at 9988776655 anytime"], 0, 1, 0, 0),

    # -------- FINANCIAL (5) --------
    ("img11", "11_financial_salary.png",
     ["Payroll", "Employee salary: 1500000"], 0, 0, 1, 0),
    ("img12", "12_financial_ctc.png",
     ["CTC breakdown", "Annual CTC: 2500000"], 0, 0, 1, 0),
    ("img13", "13_financial_payroll.png",
     ["Payroll Summary Q4"], 0, 0, 1, 0),
    ("img14", "14_financial_bonus.png",
     ["Bonus structure", "Bonus: 300000"], 0, 0, 1, 0),
    ("img15", "15_financial_compensation.png",
     ["Compensation review"], 0, 0, 1, 0),

    # -------- CONFIDENTIAL (4) --------
    ("img16", "16_confidential_marking.png",
     ["CONFIDENTIAL", "Internal only"], 0, 0, 0, 1),
    ("img17", "17_proprietary.png",
     ["PROPRIETARY", "Do not distribute"], 0, 0, 0, 1),
    ("img18", "18_internal_only.png",
     ["Internal only - Q4 pricing draft"], 0, 0, 0, 1),
    ("img19", "19_trade_secret.png",
     ["Trade secret information"], 0, 0, 0, 1),

    # -------- BENIGN (5) --------
    ("img20", "20_benign_meeting.png",
     ["Team Meeting Notes", "Discuss Q4 roadmap"], 0, 0, 0, 0),
    ("img21", "21_benign_notes.png",
     ["Project notes", "Due Friday"], 0, 0, 0, 0),
    ("img22", "22_benign_lunch.png",
     ["Lunch at 1pm", "Room 4"], 0, 0, 0, 0),
    ("img23", "23_benign_shopping.png",
     ["Shopping list", "Milk, eggs, bread"], 0, 0, 0, 0),
    ("img24", "24_benign_greeting.png",
     ["Good morning team"], 0, 0, 0, 0),

    # -------- MIXED (6) --------
    ("img25", "25_mixed_pan_phone.png",
     ["Employee Record", "PAN: ABCDE1234F", "Phone: 9123456780"],
     1, 1, 0, 0),
    ("img26", "26_mixed_pan_financial.png",
     ["PAN: FGHIJ5678K", "Salary: 2000000"],
     1, 0, 1, 0),
    ("img27", "27_mixed_all_three.png",
     ["Employee Record", "PAN: ZZZZZ9999Z",
      "Phone: 9876543210", "Salary: 1500000"],
     1, 1, 1, 0),
    ("img28", "28_mixed_confidential_pan.png",
     ["CONFIDENTIAL", "PAN: ABCDE1234F"],
     1, 0, 0, 1),
    ("img29", "29_mixed_confidential_financial.png",
     ["CONFIDENTIAL - Internal only", "Employee salary record"],
     0, 0, 1, 1),
    ("img30", "30_mixed_full.png",
     ["CONFIDENTIAL - Employee Record",
      "PAN: ABCDE1234F",
      "Phone: 9876543210",
      "Salary: 3000000"],
     1, 1, 1, 1),
]


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
        print("  created: " + str(path))

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