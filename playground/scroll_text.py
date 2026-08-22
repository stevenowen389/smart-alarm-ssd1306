import time
# from Adafruit_LED_Backpack import AlphaNum4
from PIL import Image, ImageDraw, ImageFont

# Try CircuitPython driver first, fall back to Adafruit_Python_SSD1306
try:
    import board
    import busio
    from adafruit_ssd1306 import SSD1306_I2C
    has_driver = True
except Exception:
    has_driver = False

WIDTH = 128
HEIGHT = 64

# Initialize display
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


def scroll(message, number_of_iteration):
    """Scroll a text message across the OLED display."""
    msg = '   %s   ' % message
    for _ in range(number_of_iteration):
        for offset in range(0, len(msg) * 6 + WIDTH):
            draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0, fill=0)
            draw.text((WIDTH - offset, 20), msg, font=font, fill=255)
            try:
                if hasattr(display, 'image'):
                    display.image(image)
                if hasattr(display, 'show'):
                    display.show()
                elif hasattr(display, 'display'):
                    display.display()
            except Exception:
                pass
            time.sleep(0.05)


while True:
    print('please enter your display message')
    display_message = input('\n-> ')

    scroll(display_message, 2)
    time.sleep(1)