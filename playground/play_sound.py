import time
import pygame
import RPi.GPIO as GPIO

# set pin for amplifier switch
amp_switch_pin = 5

GPIO.setwarnings(False)
# configure RPI GPIO
GPIO.setmode(GPIO.BCM)
# set pin to output
GPIO.setup(amp_switch_pin, GPIO.OUT)


def play_mp3_file(mp3_file):
    """Play an mp3 file using pygame and control amplifier via GPIO."""
    try:
        # set output high to turn on amplifier
        GPIO.output(amp_switch_pin, 1)

        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)
        print("now playing file:", mp3_file)
        pygame.mixer.music.play()

        # wait for playback to finish, sleeping to avoid busy-waiting
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    finally:
        # ensure amplifier is turned off even on errors
        GPIO.output(amp_switch_pin, 0)


if __name__ == "__main__":
    play_mp3_file("example.mp3")
    # cleanup GPIO state when finished
    GPIO.cleanup()
