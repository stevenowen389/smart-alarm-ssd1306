import time
from PIL import Image, ImageDraw, ImageFont

# Try CircuitPython driver first, fall back to Adafruit_Python_SSD1306
try:
    import board
    import busio
    from adafruit_ssd1306 import SSD1306_I2C
    has_driver = True
except Exception:
    has_driver = False

# Default display size
WIDTH = 128
HEIGHT = 64

# Initialize display
display = None
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
else:
    try:
        from Adafruit_SSD1306 import SSD1306_128_64
        display = SSD1306_128_64(rst=None)
        display.begin()
        display.clear()
        display.display()
    except Exception as e:
        print('No SSD1306 driver available:', e)
        raise

image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# set decimal point flag - for decimal point blinking
point = False

# introduction message
message = ' DISPLAY TIME '
pos = 0
counter = 0

# loop to scroll through the message
while counter < len(message) * 2:
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0, fill=0)
    draw.text((WIDTH - pos, 20), message, font=font, fill=255)
    # push image
    try:
        if hasattr(display, 'image'):
            display.image(image)
        if hasattr(display, 'show'):
            display.show()
        elif hasattr(display, 'display'):
            display.display()
    except Exception:
        pass
    pos += 2
    if pos > len(message) * 8:
        pos = 0
    time.sleep(0.15)
    counter += 1

# loop displaying the actual time
while True:
    now = time.strftime("%H:%M")
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0, fill=0)
    draw.text((18, 20), now, font=font, fill=255)
    if point:
        draw.ellipse((103, 48, 109, 54), fill=255)
        point = False
    else:
        point = True
    try:
        if hasattr(display, 'image'):
            display.image(image)
        if hasattr(display, 'show'):
            display.show()
        elif hasattr(display, 'display'):
            display.display()
    except Exception:
        pass
    time.sleep(1)




