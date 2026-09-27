#arduino

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime


class ArduinoAlert:

    def __init__(self, port=None):
        self.port = port
        self.connected = False
        self.serial = None
        self.last_action = None
        self.last_ts = None
        self.history = []
        if port is not None:
            self._try_connect(port)

    def _try_connect(self, port):
        try:
            import serial
            self.serial = serial.Serial(port, 9600, timeout=1)
            self.connected = True
        except Exception:
            self.connected = False
            self.serial = None

    def green(self):
        self._signal("GREEN", "OFF", "ALLOW")

    def red(self):
        self._signal("RED", "ON", "BLOCK")

    def warn(self):
        self._signal("YELLOW", "PULSE", "WARN")

    def _signal(self, led, buzzer, action):
        ts = datetime.now().strftime("%H:%M:%S")
        self.last_action = action
        self.last_ts = ts

        if self.connected and self.serial:
            try:
                self.serial.write((led + ":" + buzzer + "\n").encode())
            except Exception:
                self.connected = False

        self.history.append({
            "ts": ts, "led": led, "buzzer": buzzer,
            "action": action, "hardware": self.connected,
        })

        print("[" + ts + "] [LED] -> " + led)
        print("[" + ts + "] [BUZZER] -> " + buzzer)
        if not self.connected:
            print("[" + ts + "] [SOFTWARE ALERT] active (Arduino not connected)")

    def status(self):
        return {
            "connected": self.connected,
            "port": self.port if self.connected else None,
            "mode": "HARDWARE" if self.connected else "SOFTWARE",
            "last_action": self.last_action,
            "last_ts": self.last_ts,
            "history_count": len(self.history),
        }

    def render_status(self):
        if self.connected:
            return "Arduino: CONNECTED (" + str(self.port) + ")"
        return "Arduino: NOT CONNECTED  |  Hardware: SKIPPED  |  Software: ACTIVE"


if __name__ == "__main__":
    print("=" * 55)
    print("  ARDUINO ALERT TEST (no hardware)")
    print("=" * 55)
    print()
    a = ArduinoAlert()
    print(a.render_status())
    print()
    print("Allow:")
    a.green()
    print()
    print("Block:")
    a.red()
    print()
    print("Warn:")
    a.warn()
    print()
    print("Status: " + str(a.status()))
    print()