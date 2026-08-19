import time
# from Adafruit_LED_Backpack import AlphaNum4
from Adafruit_SSD1306 import SSD1306_128_64
from PIL import Image, ImageDraw, ImageFont

# Create display instance on default I2C address (0x3C)
display = SSD1306_128_64(rst=None)
display.begin()
display.clear()
display.display()

image = Image.new('1', (display.width, display.height))
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
    draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=0, fill=0)
    draw.text((display.width - pos, 20), message, font=font, fill=255)
    display.image(image)
    display.display()
    pos += 2
    if pos > len(message) * 8:
        pos = 0
    time.sleep(0.15)
    counter += 1

# loop displaying the actual time
while True:
    now = time.strftime("%H:%M")
    draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=0, fill=0)
    draw.text((18, 20), now, font=font, fill=255)
    if point:
        draw.ellipse((103, 48, 109, 54), fill=255)
        point = False
    else:
        point = True
    display.image(image)
    display.display()
    time.sleep(1)




