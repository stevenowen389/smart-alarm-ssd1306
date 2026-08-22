# Display wrapper using CircuitPython SSD1306 driver (adafruit-circuitpython-ssd1306)
# Falls back to the older Adafruit_Python_SSD1306 if the CircuitPython driver
# or Blinka/board/busio are unavailable. Keeps the public API used by
# smart_alarm so higher-level code does not need to change.

import time
import logging
import os
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class Display(object):
    """Display wrapper around an SSD1306 OLED using CircuitPython driver.

    On a Raspberry Pi this requires adafruit-blinka and adafruit-circuitpython-ssd1306
    installed in the same Python environment.
    """

    def __init__(self):
        self.display_lib = None
        self.width = 128
        self.height = 64
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        self.display_in_use = False

        # Try CircuitPython driver (preferred)
        try:
            import board
            import busio
            from adafruit_ssd1306 import SSD1306_I2C

            i2c = busio.I2C(board.SCL, board.SDA)
            self.display_lib = SSD1306_I2C(self.width, self.height, i2c)
            # Clear display
            try:
                self.display_lib.fill(0)
                # some drivers use show(), others use display()
                if hasattr(self.display_lib, 'show'):
                    self.display_lib.show()
                elif hasattr(self.display_lib, 'display'):
                    self.display_lib.display()
            except Exception:
                # non-fatal if driver methods differ
                pass

            self.width = getattr(self.display_lib, 'width', self.width)
            self.height = getattr(self.display_lib, 'height', self.height)
            logger.info('SSD1306 (CircuitPython) display initialized')
        except Exception:
            # Fallback to older Adafruit_Python_SSD1306 if available
            try:
                from Adafruit_SSD1306 import SSD1306_128_64

                self.display_lib = SSD1306_128_64(rst=None)
                try:
                    self.display_lib.begin()
                    self.display_lib.clear()
                    self.display_lib.display()
                except Exception:
                    pass

                self.width = getattr(self.display_lib, 'width', self.width)
                self.height = getattr(self.display_lib, 'height', self.height)
                logger.info('SSD1306 (Adafruit_Python) display initialized')
            except Exception:
                # No hardware display available; operate in headless/sim mode
                self.display_lib = None
                logger.warning('No SSD1306 driver available; running in headless mode')

        # recreate image/draw with actual size
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _clear_buffer(self):
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_decimal(self, pos, decimal):
        dots = {
            1: (105, 50),
            3: (115, 50),
        }
        if decimal and pos in dots:
            x, y = dots[pos]
            self.draw.ellipse((x, y, x + 4, y + 4), fill=255)
        elif pos in dots:
            x, y = dots[pos]
            self.draw.rectangle((x, y, x + 4, y + 4), fill=0)

    def _push(self):
        # Try to use a driver-specific method to show a PIL image. Different
        # backends have slightly different APIs; try the common ones.
        if self.display_lib is None:
            # Nothing to push to hardware; keep in-memory image only
            return

        try:
            # CircuitPython driver accepts a framebuffer/FrameBuffer or has
            # a "image" helper in some builds — try in this order.
            if hasattr(self.display_lib, 'image'):
                self.display_lib.image(self.image)
            elif hasattr(self.display_lib, 'blit'):
                # blit may accept an (x,y,image) tuple in some implementations
                try:
                    self.display_lib.blit(0, 0, self.image)
                except Exception:
                    pass
            else:
                # Many CircuitPython drivers expose fill/text/show but not image.
                # Convert PIL image to a raw buffer and write into the display if
                # framebuf is available.
                try:
                    buf = self.image.tobytes()
                    if hasattr(self.display_lib, 'buffer'):
                        # naive copy; may not match exact layout on all drivers
                        self.display_lib.buffer[:] = buf
                except Exception:
                    pass

            if hasattr(self.display_lib, 'show'):
                self.display_lib.show()
            elif hasattr(self.display_lib, 'display'):
                self.display_lib.display()
        except Exception:
            # Non-fatal: keep running but log the error
            logger.exception('Failed to push image to display')

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
            if hasattr(self.display_lib, 'set_contrast'):
                self.display_lib.set_contrast(contrast)
        except Exception:
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
        """Render a single "segment" on the OLED using a simple coordinate map."""
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


