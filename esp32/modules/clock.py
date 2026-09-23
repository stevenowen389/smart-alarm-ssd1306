"""Time source: DS3231 RTC over I2C, with NTP used once at boot to correct
the RTC if it's available and the RTC looks unset.
"""
import time
from machine import I2C, Pin

import pins

try:
    import ds3231
except ImportError:
    ds3231 = None


class Clock(object):
    def __init__(self):
        self._i2c = I2C(0, scl=Pin(pins.I2C_SCL), sda=Pin(pins.I2C_SDA))
        self._rtc = ds3231.DS3231(self._i2c) if ds3231 else None
        if self._rtc is None:
            print("ds3231 driver not found - falling back to NTP-only time")
            self._sync_ntp()

    def _sync_ntp(self):
        try:
            import ntptime
            ntptime.settime()
        except Exception as error:
            print("ntp sync failed:", error)

    def now(self):
        """Return (hour, minute, second) in 24h format."""
        if self._rtc is not None:
            dt = self._rtc.datetime()
            return dt[3], dt[4], dt[5]
        _, _, _, hour, minute, second, _, _ = time.localtime()[:8]
        return hour, minute, second

    def set_from_ntp(self):
        self._sync_ntp()
        if self._rtc is not None:
            y, m, d, hh, mm, ss, wd, _ = time.localtime()
            self._rtc.datetime((y, m, d, hh, mm, ss, wd))
