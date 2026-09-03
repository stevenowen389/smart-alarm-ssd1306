#!/usr/bin/env python3
"""Play one MP3 without the alarm daemon or amplifier GPIO."""

import argparse
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default='smart_alarm/sounds/blop.mp3')
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print('file not found:', os.path.abspath(args.file))
        return 2

    pygame_module = None
    try:
        import pygame
        pygame_module = pygame

        print('SDL version:', pygame.get_sdl_version())
        print('SDL audio driver:', os.environ.get('SDL_AUDIODRIVER', '(default)'))
        pygame.mixer.init()
        print('mixer:', pygame.mixer.get_init())
        pygame.mixer.music.load(args.file)
        print('loaded:', os.path.abspath(args.file))
        pygame.mixer.music.play()

        started = time.monotonic()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print('playback seconds:', round(time.monotonic() - started, 2))
        return 0
    except Exception as error:
        print(type(error).__name__ + ':', error, file=sys.stderr)
        return 1
    finally:
        if pygame_module is not None:
            pygame_module.mixer.quit()


if __name__ == '__main__':
    raise SystemExit(main())