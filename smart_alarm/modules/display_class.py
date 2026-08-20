# from Adafruit_LED_Backpack import AlphaNum4
from Adafruit_SSD1306 import SSD1306_128_64
from PIL import Image, ImageDraw, ImageFont
import time
import logging
import os


# read environmental variable for project path
project_path = os.environ.get('smart_alarm_path', '.')
logger = logging.getLogger(__name__)


class Display(object):
    """Display wrapper around the SSD1306 OLED display.

    The project previously used the Adafruit AlphaNum4 4-digit display. This
    class keeps the public methods expected by smart_alarm, but renders them on
    a 128x64 monochrome OLED instead.
    """

    def __init__(self):
        self.display_lib = SSD1306_128_64(rst=None)
        self.display_lib.begin()
        self.display_lib.clear()
        self.display_lib.display()
        self.width = self.display_lib.width
        self.height = self.display_lib.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        self.display_in_use = False
        logger.info('display-module initialized')

    def _clear_buffer(self):
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_decimal(self, pos, decimal):
        dots = {1: (105, 50), 3: (115, 50)}
        if decimal and pos in dots:
            x, y = dots[pos]
            self.draw.ellipse((x, y, x + 4, y + 4), fill=255)
        elif pos in dots:
            x, y = dots[pos]
            self.draw.rectangle((x, y, x + 4, y + 4), fill=0)

    def _push(self):
        self.display_lib.image(self.image)
        self.display_lib.display()

    def scroll(self, message, number_of_iteration):
        """Scroll a text message across the display."""
        self.display_in_use = True
        text = '   %s   ' % message
        for _ in range(number_of_iteration):
            for offset in range(0, len(text) * 6 + self.width):
                self._clear_buffer()
                self.draw.text((self.width - offset, 20), text, font=self.font, fill=255)
                self._push()
                time.sleep(0.05)
        self.display_in_use = False

    def show_time(self, value):
        """Render a time-like value on the display."""
        if self.display_in_use:
            return
        self._clear_buffer()
        self.draw.text((20, 16), str(value), font=self.font, fill=255)
        self._push()

    def set_brightness(self, value):
        """Change the display brightness via SSD1306 contrast."""
        try:
            contrast = max(0, min(255, int(value * 16)))
            self.display_lib.set_contrast(contrast)
        except AttributeError:
            pass

    def clear_class(self):
        """Clear the display buffer and render the blank state."""
        self._clear_buffer()
        self._push()

    def write(self):
        """Push the current buffer to the OLED."""
        self._push()

    def set_decimal(self, pos, decimal):
        """Render a small decimal marker at the requested position."""
        if self.display_in_use:
            return
        self._draw_decimal(pos, decimal)

    def set_segment(self, led, value):
        """Render a single segment on the OLED using a simple coordinate map."""
        x = led % 16
        y = led // 16
        if value:
            self.draw.rectangle((x * 8, y * 8, x * 8 + 6, y * 8 + 6), fill=255)
        else:
            self.draw.rectangle((x * 8, y * 8, x * 8 + 6, y * 8 + 6), fill=0)

    # The following functions are not mandatory and are kept for backwards
    # compatibility with the previous AlphaNum4 display interface.

    def shutdown(self, number_of_iterations):
        self.display_in_use = True
        for _ in range(number_of_iterations):
            self._clear_buffer()
            for i in range(1, 10):
                self.draw.rectangle((i * 10, 0, i * 10 + 8, 60), fill=255)
                self._push()
                time.sleep(0.08)
        self.display_in_use = False

    def snake(self, number_of_iterations):
        self.display_in_use = True
        for _ in range(number_of_iterations):
            for x in range(0, self.width):
                self._clear_buffer()
                self.draw.rectangle((x, 20, x + 8, 28), fill=255)
                self._push()
                time.sleep(0.02)
        self.display_in_use = False

    def big_stars(self, number_of_iterations):
        self.display_in_use = True
        for _ in range(number_of_iterations):
            self._clear_buffer()
            for star in [(10, 10), (40, 18), (80, 10), (110, 24), (20, 45), (90, 45)]:
                self.draw.ellipse((star[0], star[1], star[0] + 6, star[1] + 6), fill=255)
            self._push()
            time.sleep(0.05)
        self.display_in_use = False


