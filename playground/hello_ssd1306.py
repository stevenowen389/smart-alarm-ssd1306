#!/usr/bin/env python3
"""Simple SSD1306 "Hello World" test for the OLED display.

Usage:
  - Activate the project's venv and run:
      source /home/steven/smart_alarm/.venv/bin/activate
      python playground/hello_ssd1306.py

  - Or run with the venv python directly:
      /home/steven/smart_alarm/.venv/bin/python playground/hello_ssd1306.py

Notes:
  - Requires Adafruit_SSD1306 and Pillow installed in the venv.
  - Make sure I2C is enabled on the Pi (raspi-config -> Interfacing Options -> I2C).
"""
import time
import sys

try:
    from Adafruit_SSD1306 import SSD1306_128_64
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    print("Required libraries not found:", e)
    print("Install in venv: python -m pip install Adafruit-SSD1306 pillow")
    sys.exit(1)

# Create display instance (128x64)
disp = SSD1306_128_64(rst=None)

try:
    disp.begin()
    disp.clear()
    disp.display()

    # Create image buffer with mode '1' for 1-bit color
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)

    # Load default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Centered text
    text = "Hello, World!"
    # measure text size
    if font:
        tw, th = draw.textsize(text, font=font)
    else:
        tw, th = draw.textsize(text)

    x = (width - tw) // 2
    y = (height - th) // 2

    # Draw background and text
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, y), text, font=font, fill=255)

    # Send to display
    disp.image(image)
    disp.display()

    print("Displayed text on SSD1306: '{}'. Sleeping 8s before clearing.".format(text))
    time.sleep(8)

    # Clear and exit
    disp.clear()
    disp.display()
    print("Cleared display and exiting.")

except Exception as e:
    print("Error while driving the display:", e)
    print("Check I2C is enabled and the display is connected.")
    sys.exit(2)
