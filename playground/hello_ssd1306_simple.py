"""Simple SSD1306 test using CircuitPython driver (works with adafruit-blinka)

Installs required on the Pi (inside your venv or system python):
  python -m pip install --upgrade pip
  python -m pip install adafruit-blinka adafruit-circuitpython-ssd1306 pillow

Run:
  cd /home/steven/smart_alarm
  source .venv/bin/activate
  python playground/hello_ssd1306_simple.py

If the driver isn't available this script will write /tmp/hello_ssd1306_simple.png instead.
"""

import time
from PIL import Image, ImageDraw, ImageFont

try:
    import board
    import busio
    from adafruit_ssd1306 import SSD1306_I2C
    has_driver = True
except Exception:
    has_driver = False

WIDTH = 128
HEIGHT = 64

# Create blank image for drawing.
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

if has_driver:
    i2c = busio.I2C(board.SCL, board.SDA)
    display = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    try:
        display.fill(0)
        display.show()
    except Exception:
        try:
            display.display()
        except Exception:
            pass

# Draw "Hello World" in the buffer and push to display (or save as fallback)
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
draw.text((10, 26), "Hello World", font=font, fill=255)

pushed = False
if has_driver:
    try:
        # Preferred: many builds provide image(image) helper
        if hasattr(display, 'image'):
            display.image(image)
            display.show()
            pushed = True
    except Exception:
        pushed = False

    if not pushed:
        try:
            # Try blit style API
            if hasattr(display, 'blit'):
                display.blit(0, 0, image)
                display.show()
                pushed = True
        except Exception:
            pushed = False

if not has_driver or not pushed:
    image.save('/tmp/hello_ssd1306_simple.png')
    print('Could not push to hardware display; saved /tmp/hello_ssd1306_simple.png')
else:
    print('Displayed "Hello World" on SSD1306')

# Pause so you can see the message on the display
time.sleep(2)

# Clear display before exit
if has_driver:
    try:
        display.fill(0)
        display.show()
    except Exception:
        try:
            display.display()
        except Exception:
            pass
