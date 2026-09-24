# arduino ka simulation. physical board nahi hai to python se kar rahe.
# LED aur buzzer represent karta hai

import time
from datetime import datetime


class SimulatedArduino:

    def __init__(self):
        self.led = "GREEN"
        self.buzzer = "OFF"
        self.log = []

    def _p(self, msg):
        t = datetime.now().strftime("%H:%M:%S")
        line = "[" + t + "] " + msg
        print(line)
        self.log.append(line)

    def set_led(self, color):
        self.led = color
        self._p("[LED] -> " + color)

    def set_buzzer(self, state):
        self.buzzer = state
        self._p("[BUZZER] -> " + state)

    def trigger_alert(self, sev):
        if sev == "HIGH":
            self.set_led("RED")
            self.set_buzzer("ON")
            time.sleep(1)
            self.set_buzzer("OFF")
        elif sev == "MEDIUM":
            self.set_led("YELLOW")
        else:
            self.set_led("GREEN")

    def reset(self):
        self.set_led("GREEN")
        self.set_buzzer("OFF")