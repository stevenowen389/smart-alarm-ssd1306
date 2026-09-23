"""Runs automatically on every reset. Connects Wi-Fi and mounts the SD card
before main.py starts, so both are ready when the app modules import.
"""
import os
import time
import network
import machine

import pins


def connect_wifi(timeout_ms=15000):
    try:
        import wifi_secrets
    except ImportError:
        print("wifi_secrets.py missing - copy wifi_secrets.py.example and fill it in")
        return False

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(wifi_secrets.SSID, wifi_secrets.PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while not sta.isconnected() and time.ticks_diff(deadline, time.ticks_ms()) > 0:
            time.sleep_ms(200)
    print("wifi connected:", sta.ifconfig()) if sta.isconnected() else print("wifi connect timed out")
    return sta.isconnected()


def mount_sd():
    try:
        sd = machine.SDCard(
            slot=pins.SD_SLOT,
            sck=pins.SD_SCK,
            mosi=pins.SD_MOSI,
            miso=pins.SD_MISO,
            cs=pins.SD_CS,
        )
        os.mount(sd, "/sd")
        print("sd card mounted at /sd")
        return True
    except OSError as error:
        print("sd card mount failed:", error)
        return False


connect_wifi()
mount_sd()
