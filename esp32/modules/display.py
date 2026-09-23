"""SSD1306 OLED rendering: the live clock and an alarm-set indicator."""
from machine import I2C, Pin
import ssd1306

import pins


class Display(object):
    WIDTH = 128
    HEIGHT = 64

    def __init__(self):
        i2c = I2C(0, scl=Pin(pins.I2C_SCL), sda=Pin(pins.I2C_SDA))
        self._oled = ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c)

    def render_clock(self, now, alarm_enabled=False):
        hour, minute, _ = now
        self._oled.fill(0)
        self._oled.text("{:02d}:{:02d}".format(hour, minute), 40, 24, 1)
        if alarm_enabled:
            self._oled.text("ALARM SET", 24, 48, 1)
        self._oled.show()

    def show_message(self, text):
        self._oled.fill(0)
        self._oled.text(text[:16], 0, 24, 1)
        self._oled.show()
