# masking.py
import re


def mask_pan(text):
    # ABCDE1234F -> ABCD****F
    return re.sub(r"\b([A-Z]{4})([A-Z]\d{4})([A-Z])\b",
                  r"\1****\3", text)


def mask_phone(text):
    # 9876543210 -> ******3210
    return re.sub(r"\b[6-9](\d{5})(\d{4})\b",
                  r"******\2", text)


def mask_account(text):
    # 123456789012 -> ********9012
    return re.sub(r"\b(\d{8})(\d{4})\b",
                  r"********\2", text)


def mask_aadhaar(text):
    # 1234 5678 9012 -> **** **** 9012
    return re.sub(r"\b(\d{4})\s(\d{4})\s(\d{4})\b",
                  r"**** **** \3", text)


def mask_all(text):
    if not text:
        return ""
    out = text
    out = mask_pan(out)
    out = mask_aadhaar(out)
    out = mask_phone(out)
    out = mask_account(out)
    return out


def summarize_entities(entities, original_text):
    """
    Produce a per-entity masked summary for audit.
    """
    summary = []
    text = original_text or ""

    if "PAN" in entities:
        m = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
        if m:
            v = m.group(0)
            summary.append({
                "entity": "PAN",
                "masked": v[:4] + "****" + v[-1],
                "length": len(v),
            })
        else:
            summary.append({"entity": "PAN", "masked": "ABCD****?", "length": 10})

    if "PHONE" in entities:
        m = re.search(r"\b[6-9]\d{9}\b", text)
        if m:
            v = m.group(0)
            summary.append({
                "entity": "PHONE",
                "masked": "******" + v[-4:],
                "length": len(v),
            })
        else:
            summary.append({"entity": "PHONE", "masked": "******????", "length": 10})

    if "EMPLOYEE_FINANCIAL_DATA" in entities:
        summary.append({"entity": "EMPLOYEE_FINANCIAL_DATA",
                        "masked": "[FINANCIAL]", "length": 0})

    if "CONFIDENTIAL_MARKING" in entities:
        summary.append({"entity": "CONFIDENTIAL_MARKING",
                        "masked": "[CONFIDENTIAL]", "length": 0})

    return summary


if __name__ == "__main__":
    print("=" * 55)
    print("  MASKING TEST")
    print("=" * 55)
    print()

    samples = [
        "PAN ABCDE1234F",
        "Call 9876543210 now",
        "Aadhaar 1234 5678 9012",
        "Account 123456789012",
        "PAN FGHIJ5678K phone 9123456780",
    ]

    for s in samples:
        print("  in:  " + s)
        print("  out: " + mask_all(s))
        print()

    print("Entity summary for audit:")
    print(" ", summarize_entities(
        ["PAN", "PHONE"],
        "PAN ABCDE1234F phone 9123456780"
    ))
    print()