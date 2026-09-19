#!/usr/bin/env python3
import pigpio
import time
from datetime import datetime

pi = pigpio.pi()

# Free pins (avoiding 12, 13, 18, 19 for audio)
R, G, B = 17, 22, 23

# Software PWM — 100Hz is plenty for slow fades
pi.set_PWM_frequency(100)

SUNRISE_START = (6, 0)
SUNRISE_END   = (6, 30)
SUNSET_START  = (18, 30)
SUNSET_END    = (19, 30)

def set_rgb(r, g, b):
    """r, g, b each 0-255"""
    pi.set_PWM_dutycycle(R, r * 100 / 255)
    pi.set_PWM_dutycycle(G, g * 100 / 255)
    pi.set_PWM_dutycycle(B, b * 100 / 255)

def sunrise():
    """Dark blue → orange → warm white"""
    steps = 60
    for i in range(steps + 1):
        t = i / steps  # 0→1
        # Blue fades out early, green mid, red stays high
        b = int(255 * max(0, 1 - t * 2))
        g = int(255 * max(0, (t - 0.3) * 2))
        r = int(255 * min(1, t * 1.5))
        set_rgb(r, g, b)
        time.sleep(30)  # 30 min total

def sunset():
    """Warm white → yellow → deep orange → off"""
    steps = 60
    for i in range(steps, -1, -1):
        t = i / steps  # 1→0
        # Blue drops first, then green, red lingers
        b = int(255 * max(0, (t - 0.7) * 3.3))
        g = int(255 * max(0, (t - 0.3) * 1.5))
        r = int(255 * min(1, t * 1.2))
        set_rgb(r, g, b)
        time.sleep(30)  # 30 min total

def in_window(start, end):
    now = datetime.now()
    s = now.replace(hour=start[0], minute=start[1], second=0)
    e = now.replace(hour=end[0], minute=end[1], second=0)
    return s <= now <= e

try:
    while True:
        if in_window(SUNRISE_START, SUNRISE_END):
            sunrise()
        elif in_window(SUNSET_START, SUNSET_END):
            sunset()
        else:
            set_rgb(0, 0, 0)
            time.sleep(60)
finally:
    pi.stop()   
