import time
import os
import sys
apa102_path = os.environ.get('APA102_PI_PATH', os.path.expanduser('~/APA102_Pi'))
sys.path.append(os.path.abspath(apa102_path))
import colorschemes
import apa102
import logging


# read environmental variable for project path
project_path = os.environ['smart_alarm_path']
logger = logging.getLogger(__name__)

# colour keyframes (R, G, B) approximating a dawn's progression from a dark
# ember, through orange/amber, to a bright daylight white. sunset simply
# plays these keyframes in reverse.
SUNRISE_COLOUR_STOPS = [
    (20, 0, 0),
    (255, 40, 0),
    (255, 120, 0),
    (255, 180, 60),
    (255, 220, 150),
    (255, 255, 255),
]


class LEDs(object):
    """
    LEDs class: manages the implementation of the 'wake-up'-leds.
    Makes us of tinues APA102_Pi library: https://github.com/tinue/APA102_Pi
    """

    def __init__(self):
        """init functions: set variables and start adafruit dotstar class"""
        # write to error.log file
        logger.info('led-module initialized')
        self.number_of_leds = 9
        self.stop_led = False
        self.leds_active = False

    def stopping_leds(self):
        """stops leds when button is pressed"""
        logger.debug('leds are being stopped')
        logger.debug('now stopping leds')
        self.stop_led = True

    def rainbow(self, brightness, duration_time):
        """colorful rainbow cycling through all leds"""
        if self.stop_led:
            logger.debug('skipping led rainbow, since button was pressed')
            return
        logger.debug('running led rainbow with brightness {}/10 for {}sec'.format(brightness, duration_time))
        self.leds_active = True
        clock = 0
        start = time.time()
        while clock < duration_time and self.stop_led is False:
            rainbow = colorschemes.Rainbow(numLEDs=self.number_of_leds, pauseValue=0.02, numStepsPerCycle=255,
                                           numCycles=1, globalBrightness=brightness)
            rainbow.start()
            clock = time.time() - start
        self.leds_active = False

    def white_blinking(self, duration_time):
        """most bright white blinking, finally you should wake up"""
        if self.stop_led:
            logger.debug('skipping led white blinking, since button was pressed')
            return
        logger.debug('running led white blinking')
        self.leds_active = True
        clock = 0
        start = time.time()
        while clock < duration_time and self.stop_led is False:
            blinking = colorschemes.Solid(numLEDs=self.number_of_leds, pauseValue=0.05, numStepsPerCycle=1,
                                          numCycles=1)
            blinking.start()
            time.sleep(0.05)
            clock = time.time() - start
        self.leds_active = False

    def wake_up_light_show(self, duration_time):
        """combination of earlier functions, adjust when needed"""
        self.rainbow(1, duration_time / 4)
        self.rainbow(3, duration_time / 4)
        self.rainbow(10, duration_time / 4)
        self.white_blinking(duration_time / 4)

    @staticmethod
    def _interpolate_colour(colour_stops, fraction):
        """returns an (r, g, b) tuple interpolated between colour_stops at
        the given fraction (0.0 - 1.0) of the whole sequence"""
        fraction = min(max(fraction, 0.0), 1.0)
        segment_count = len(colour_stops) - 1
        segment_length = 1.0 / segment_count
        segment_index = min(int(fraction / segment_length), segment_count - 1)
        segment_fraction = (fraction - segment_index * segment_length) / segment_length
        start_colour = colour_stops[segment_index]
        end_colour = colour_stops[segment_index + 1]
        return tuple(
            int(round(start_colour[i] + (end_colour[i] - start_colour[i]) * segment_fraction))
            for i in range(3)
        )

    def _run_gradient(self, colour_stops, duration_time, start_brightness, end_brightness, update_interval=1.0):
        """gradually fades the whole strip through colour_stops while ramping
        the global brightness from start_brightness to end_brightness (both
        on the APA102's native 0-31 scale). Used by sunrise()/sunset()."""
        self.leds_active = True
        strip = apa102.APA102(num_led=self.number_of_leds)
        try:
            start_time = time.time()
            elapsed = 0
            while elapsed < duration_time and self.stop_led is False:
                fraction = elapsed / duration_time
                colour = self._interpolate_colour(colour_stops, fraction)
                brightness = int(round(start_brightness + (end_brightness - start_brightness) * fraction))
                strip.set_global_brightness(brightness)
                for led_index in range(self.number_of_leds):
                    strip.set_pixel(led_index, colour[0], colour[1], colour[2])
                strip.show()
                time.sleep(update_interval)
                elapsed = time.time() - start_time
            if self.stop_led is False:
                # make sure the sequence reaches its exact final colour/brightness
                final_colour = colour_stops[-1]
                strip.set_global_brightness(end_brightness)
                for led_index in range(self.number_of_leds):
                    strip.set_pixel(led_index, final_colour[0], final_colour[1], final_colour[2])
                strip.show()
        finally:
            strip.cleanup()
            self.leds_active = False

    def sunrise(self, duration_time, max_brightness=10):
        """simulated sunrise: gradually brightens and shifts colour from a
        dark ember through orange and warm white up to a bright white,
        imitating a natural dawn as a gentle wake-up cue"""
        if self.stop_led:
            logger.debug('skipping led sunrise, since button was pressed')
            return
        logger.debug('running led sunrise for {}sec, up to brightness {}/31'.format(duration_time, max_brightness))
        self._run_gradient(SUNRISE_COLOUR_STOPS, duration_time, start_brightness=0, end_brightness=max_brightness)

    def sunset(self, duration_time, start_brightness=10):
        """simulated sunset: gradually dims and shifts colour from a bright
        white down through warm white, orange and a dark ember to fully off,
        imitating a natural dusk as a gentle wind-down cue"""
        if self.stop_led:
            logger.debug('skipping led sunset, since button was pressed')
            return
        logger.debug('running led sunset for {}sec, from brightness {}/31'.format(duration_time, start_brightness))
        self._run_gradient(list(reversed(SUNRISE_COLOUR_STOPS)), duration_time, start_brightness=start_brightness, end_brightness=0)
