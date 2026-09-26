# audit_chain.py

import hashlib
import json
from pathlib import Path
from datetime import datetime


class AuditChain:
    """Append-only hash chain for audit records."""

    def __init__(self, log_dir="audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

    def _load_last_hash(self, log_file):
        if not log_file.exists():
            return "0" * 64
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                return last.get("hash", "0" * 64)
        except Exception:
            pass
        return "0" * 64

    def append(self, event):
        today = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"chain_{today}.jsonl"

        prev_hash = self._load_last_hash(log_file)

        entry = {
            "event_id": "SD-" + datetime.now().strftime("%Y%m%d%H%M%S%f")[:18],
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "previous_hash": prev_hash,
        }

        payload = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        entry["hash"] = current_hash

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def verify_chain(self, log_file=None):
        if log_file is None:
            files = sorted(self.log_dir.glob("chain_*.jsonl"))
            if not files:
                return False, "no log files found"
            log_file = files[-1]

        log_file = Path(log_file)
        if not log_file.exists():
            return False, "log file not found"

        prev = "0" * 64
        count = 0

        with open(log_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                except Exception:
                    return False, "line " + str(line_num) + ": invalid JSON"

                if entry.get("previous_hash") != prev:
                    return False, "line " + str(line_num) + ": chain broken"

                stored_hash = entry.pop("hash")
                payload = json.dumps(entry, sort_keys=True)
                computed = hashlib.sha256(payload.encode()).hexdigest()

                if computed != stored_hash:
                    return False, "line " + str(line_num) + ": hash mismatch"

                prev = stored_hash
                count += 1

        return True, str(count) + " events verified"


if __name__ == "__main__":
    c = AuditChain()
    c.append({"action": "TEST_1", "user": "test"})
    c.append({"action": "TEST_2", "user": "test"})
    c.append({"action": "TEST_3", "user": "test"})

    valid, msg = c.verify_chain()
    print("Chain valid: " + str(valid))
    print("Details: " + msg)