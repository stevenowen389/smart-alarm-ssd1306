from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from PIL import ImageFont
import time
import logging
import os

# read environmental variable for project path
project_path = os.environ['smart_alarm_path']
logger = logging.getLogger(__name__)

class Display(object):
    """
    Display class: manages all methods concerning the OLED display.
    """

    def __init__(self):
        """init function: imports luma oled class and initializes the device"""
        # Set up I2C communication (Default port=1, address=0x3C for most SSD1306 OLEDs)
        try:
            self.serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(self.serial)
        except Exception as e:
            logger.error(f"Failed to initialize OLED hardware: {e}")
            raise
            
        self.display_in_use = False
        
        # Internal text buffer to mirror old alphanumeric print behavior
        self._current_text = ""
        
        # Load a default font (or use a specific TrueType font if preferred)
        self.font = ImageFont.load_default()
        
        logger.info('OLED display-module initialized')

    def scroll(self, message, number_of_iteration):
        """scrolls the given message from right to left through the display."""
        self.display_in_use = True
        pos = 0
        counter = 0
        message = "   " + message + "   "
        
        # The OLED can show more text, but keeping the 4-char constraint to match original behavior
        while counter < (len(message) - 3) * number_of_iteration:
            self._current_text = message[pos:pos + 4]
            self.write()
            
            pos += 1
            if pos > len(message) - 4:
                pos = 0
            time.sleep(0.12)
            counter += 1
        self.display_in_use = False

    def show_time(self, time_str):
        """displays the given time using the canvas layout"""
        if self.display_in_use:
            return
        # Expecting a string format like "12:34" or "1234"
        self._current_text = str(time_str)
        self.write()

    def set_brightness(self, value):
        """change the displays brightness. Value mapped from 0-15 to 0-255"""
        # luma.oled accepts a value from 0 to 255
        contrast_value = int((value / 15.0) * 255)
        self.device.contrast(contrast_value)

    def clear_class(self):
        """clears the internal text buffer"""
        self._current_text = ""

    def write(self):
        """draws the current buffer text directly onto the OLED frame"""
        with canvas(self.device) as draw:
            # draw.text((X_pixel, Y_pixel), text, font, fill)
            # Adjust (0, 0) coordinates if you want to center the text on screen
            draw.text((0, 0), self._current_text, font=self.font, fill="white")

    def set_decimal(self, pos, decimal):
        """Appends a dot to the text buffer if True (simulating segment decimal)"""
        if self.display_in_use:
            return
        if decimal and "." not in self._current_text:
            self._current_text += "."
        self.write()

    def set_segment(self, led, value):
        """Legacy segment support: Stubbed out since OLED uses pixels"""
        pass

    # Simplified animation stubs replacing the old segment games

    def shutdown(self, number_of_iterations):
        """Flashes screen off to simulate shutdown"""
        self.display_in_use = True
        for _ in range(number_of_iterations):
            self.device.hide()
            time.sleep(0.2)
            self.device.show()
            time.sleep(0.2)
        self.display_in_use = False

    def snake(self, number_of_iterations):
        """Legacy animation: Stubbed out"""
        pass

    def big_stars(self, number_of_iterations):
        """Legacy animation: Stubbed out"""
        pass

