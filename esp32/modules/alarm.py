"""Alarm loop: compares the clock to config.json each tick and triggers
playback; watches the button so playback can be silenced mid-alarm.
"""
import json
import uasyncio as asyncio
from machine import Pin

import pins

CONFIG_PATH = "config.json"


class Alarm(object):
    def __init__(self, clock, display, audio):
        self._clock = clock
        self._display = display
        self._audio = audio
        self._button = Pin(pins.BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self._stop_requested = False
        self._already_fired_minute = None
        self.config = self._load_config()

    def _load_config(self):
        with open(CONFIG_PATH) as f:
            return json.load(f)

    def save_config(self, new_config):
        self.config.update(new_config)
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f)

    def _button_pressed(self):
        return self._button.value() == 0

    async def run(self):
        while True:
            hour, minute, second = self._clock.now()

            if (
                self.config.get("alarm_enabled")
                and hour == self.config.get("alarm_hour")
                and minute == self.config.get("alarm_minute")
                and self._already_fired_minute != minute
            ):
                self._already_fired_minute = minute
                self._audio.set_volume(self.config.get("volume", 70))
                self._display.show_message("WAKE UP")
                self._audio.play_wav(
                    self.config.get("sound_file"),
                    stop_flag=self._button_pressed,
                )

            if minute != self.config.get("alarm_minute"):
                self._already_fired_minute = None

            await asyncio.sleep(1)
