# Display wrapper using CircuitPython SSD1306 driver (adafruit-circuitpython-ssd1306)
# Falls back to the older Adafruit_Python_SSD1306 if the CircuitPython driver
# or Blinka/board/busio are unavailable. Keeps the public API used by
# smart_alarm so higher-level code does not need to change.

import time
import logging
import os
import threading
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
        self.font = self._load_font()
        self.decimal_positions = {}
        self.alarm_status = False
        self._buffer_lock = threading.RLock()
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

    def _load_font(self, size=32):
        for font_path in (
                '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf'):
            try:
                return ImageFont.truetype(font_path, size)
            except OSError:
                pass
        return ImageFont.load_default()

    def _draw_decimal(self, pos, decimal):
        if pos in self.decimal_positions:
            x, y = self.decimal_positions[pos]
            if decimal:
                self.draw.ellipse((x, y, x + 4, y + 4), fill=255)
            else:
                self.draw.rectangle((x, y, x + 4, y + 4), fill=0)

    def _draw_alarm_status(self):
        x, y = self.width - 8, 2
        fill = 255 if self.alarm_status else 0
        self.draw.ellipse((x, y, x + 4, y + 4), fill=fill)

    def _time_layout(self, value):
        text = str(value)
        character_width = self.draw.textlength('0', font=self.font)
        character_spacing = 8
        text_width = character_width * len(text) + character_spacing * max(0, len(text) - 1)
        text_bbox = self.draw.textbbox((0, 0), text, font=self.font)
        text_height = text_bbox[3] - text_bbox[1]
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2 - text_bbox[1]
        self.decimal_positions = {}
        if len(text) >= 4:
            # Center the indicator dots in the gap between digit 2 and digit 3.
            decimal_x = int(x + 2 * character_width + (3 * character_spacing) / 2 - 2)
            decimal_y = int(y + text_height // 2 - 6)
            self.decimal_positions = {
                1: (decimal_x, decimal_y),
                3: (decimal_x, decimal_y + 16),
            }
        return text, x, y

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
            elif hasattr(self.display_lib, 'framebuf'):
                # Try to use framebuf attribute directly with PIL image
                try:
                    import framebuf
                    # Convert PIL 1-bit image to framebuf format
                    buf = framebuf.FrameBuffer(bytearray(self.image.tobytes()), self.width, self.height, framebuf.MONO_HLSB)
                    self.display_lib.framebuf.blit(buf, 0, 0)
                except Exception:
                    pass
            elif hasattr(self.display_lib, 'blit'):
                # blit may accept an (x,y,image) tuple in some implementations
                try:
                    self.display_lib.blit(0, 0, self.image)
                except Exception:
                    pass
            else:
                # Fallback: try direct buffer copy (may not work on all drivers)
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
        with self._buffer_lock:
            self.display_in_use = True
            try:
                text = '   %s   ' % message
                scroll_font = self._load_font(32)
                text_width = int(self.draw.textlength(text, font=scroll_font))
                text_bbox = self.draw.textbbox((0, 0), text, font=scroll_font)
                text_y = (self.height - (text_bbox[3] - text_bbox[1])) // 2 - text_bbox[1]
                for _ in range(number_of_iteration):
                    for offset in range(0, text_width + self.width, 4):
                        self._clear_buffer()
                        self.draw.text((self.width - offset, text_y), text, font=scroll_font, fill=255)
                        self._push()
                        time.sleep(0.03)
            finally:
                self.display_in_use = False

    def show_time(self, value):
        """Render a time-like value on the display."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            self._clear_buffer()
            text, x, y = self._time_layout(value)
            character_width = self.draw.textlength('0', font=self.font)
            for index, character in enumerate(text):
                self.draw.text((x + index * (character_width + 8), y), character, font=self.font, fill=255)
            self._draw_alarm_status()
            self._push()

    def show_message(self, message):
        """Render a centered static message on the display."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            self._clear_buffer()
            message_font = self._load_font(24)
            text_bbox = self.draw.textbbox((0, 0), message, font=message_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (self.width - text_width) // 2 - text_bbox[0]
            y = (self.height - text_height) // 2 - text_bbox[1]
            self.draw.text((x, y), message, font=message_font, fill=255)
            self._push()

    def set_brightness(self, value):
        """Change the display brightness via SSD1306 contrast."""
        try:
            brightness = max(0.0, min(15.0, float(value)))
            contrast = round(brightness * 255 / 15)
            logger.debug('setting display brightness %.2f/15 to contrast %d', brightness, contrast)
            if hasattr(self.display_lib, 'contrast'):
                self.display_lib.contrast(contrast)
            elif hasattr(self.display_lib, 'set_contrast'):
                self.display_lib.set_contrast(contrast)
            else:
                logger.warning('Display driver does not support brightness control')
        except Exception:
            logger.exception('Failed to set display brightness')

    def clear_class(self):
        """Clear the display buffer and render the blank state."""
        with self._buffer_lock:
            self._clear_buffer()
            self._push()

    def write(self):
        """Push the current buffer to the OLED."""
        with self._buffer_lock:
            self._push()

    def set_decimal(self, pos, decimal):
        """Render a small decimal marker at the requested position."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            self._draw_decimal(pos, decimal)

    def update_decimal(self, pos, decimal):
        """Update one indicator and send the current framebuffer."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            self._draw_decimal(pos, decimal)
            self._push()

    def update_decimals(self, decimals):
        """Update multiple indicators and send one framebuffer."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            for pos, decimal in decimals.items():
                self._draw_decimal(pos, decimal)
            self._push()

    def set_alarm_status(self, active):
        """Set the separate alarm status indicator."""
        with self._buffer_lock:
            if self.display_in_use:
                return
            self.alarm_status = bool(active)
            self._draw_alarm_status()
            self._push()

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
        with self._buffer_lock:
            self.display_in_use = True
            try:
                for _ in range(number_of_iterations):
                    self._clear_buffer()
                    for i in range(1, 10):
                        self.draw.rectangle((i * 10, 0, i * 10 + 8, 60), fill=255)
                        self._push()
                        time.sleep(0.08)
            finally:
                self.display_in_use = False

    def snake(self, number_of_iterations):
        with self._buffer_lock:
            self.display_in_use = True
            try:
                for _ in range(number_of_iterations):
                    for x in range(self.width):
                        self._clear_buffer()
                        self.draw.rectangle((x, 20, x + 8, 28), fill=255)
                        self._push()
                        time.sleep(0.02)
            finally:
                self.display_in_use = False
