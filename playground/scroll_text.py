import time
# from Adafruit_LED_Backpack import AlphaNum4
from Adafruit_SSD1306 import SSD1306_128_64
from PIL import Image, ImageDraw, ImageFont

# Create display instance on the 128x64 OLED display.
display = SSD1306_128_64(rst=None)
display.begin()
display.clear()
display.display()

image = Image.new('1', (display.width, display.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()


def scroll(message, number_of_iteration):
    """Scroll a text message across the OLED display."""
    msg = '   %s   ' % message
    for _ in range(number_of_iteration):
        for offset in range(0, len(msg) * 6 + display.width):
            draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=0, fill=0)
            draw.text((display.width - offset, 20), msg, font=font, fill=255)
            display.image(image)
            display.display()
            time.sleep(0.05)


while True:
    print('please enter your display message')
    display_message = input('\n-> ')

    scroll(display_message, 2)
    time.sleep(1)