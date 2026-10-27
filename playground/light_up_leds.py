"""Test APA102 LEDs one at a time, cycling each through red, green, and blue."""
import time

from apa102_pi.driver import apa102


NUM_LEDS = 12
BRIGHTNESS = 8
COLOR_ORDER = "rgb"
PAUSE_SECONDS = 0.75
COLORS = (
    ("red", (255, 0, 0)),
    ("green", (0, 255, 0)),
    ("blue", (0, 0, 255)),
)


def main():
    strip = apa102.APA102(num_led=NUM_LEDS, order=COLOR_ORDER)
    try:
        strip.set_global_brightness(BRIGHTNESS)
        print("Testing each APA102 LED. Press Ctrl+C to stop.")
        for led_index in range(NUM_LEDS):
            for color_name, color in COLORS:
                strip.clear_strip()
                strip.set_pixel(led_index, *color)
                strip.show()
                print("LED {}/{}: {}".format(led_index + 1, NUM_LEDS, color_name))
                time.sleep(PAUSE_SECONDS)
    finally:
        try:
            strip.clear_strip()
        finally:
            strip.cleanup()


if __name__ == "__main__":
    main()
