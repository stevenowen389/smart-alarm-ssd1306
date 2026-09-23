# ESP32 Smart Alarm (MicroPython) — minimal scaffold

A from-scratch, ESP32-native reimplementation of the smart_alarm concept.
Does not reuse any code from the Raspberry Pi version (see repo root) —
only the idea: OLED clock, web page to set an alarm, wake with a sound,
silence with a button.

## Hardware (v1)
- ESP32 dev board
- SSD1306 128x64 OLED, I2C
- DS3231 RTC module, I2C (same bus as OLED)
- MAX98357A I2S DAC/amp + small speaker
- Push button (silence/snooze)
- MicroSD card breakout, SPI (stores .wav sound files)

Wiring is defined in one place: [pins.py](pins.py). Adjust to match your
actual board before flashing.

## Firmware setup
1. Flash the official MicroPython firmware for ESP32 (esp32-idfX-*.bin from
   micropython.org) using `esptool.py`.
2. Install third-party libraries onto the device's `/lib` folder using
   `mpremote mip install`, over a serial connection to the board:
   ```
   mpremote mip install github:stlehmann/micropython-ssd1306
   mpremote mip install github:mcauser/micropython-ds3231
   mpremote mip install github:miguelgrinberg/microdot
   ```
   (Or copy the driver `.py` files manually into `/lib` if you don't have
   internet access on the dev machine.)
3. Copy `wifi_secrets.py.example` to `wifi_secrets.py` and fill in your SSID
   and password. `wifi_secrets.py` is gitignored — never commit real
   credentials.
4. Copy this entire `esp32/` folder's contents onto the device with
   `mpremote cp -r . :` (run from inside the `esp32/` folder), or use the
   Thonny/`ampy` file transfer of your choice.
5. Put pre-rendered 16-bit PCM `.wav` files (e.g. generated once from any
   TTS tool on your PC) onto the SD card under `/sd/sounds/`.
6. Reset the board. `boot.py` connects Wi-Fi and mounts the SD card;
   `main.py` starts the display/alarm loop and the web server.

## Build order / status
- [ ] OLED shows live time (reads DS3231, falls back to NTP if RTC absent)
- [ ] Button press plays a test `.wav` over I2S
- [ ] Web page at `http://<device-ip>/` sets alarm hour/minute + volume
- [ ] Alarm loop triggers playback automatically at the set time
- [ ] Stretch: internet radio streaming, on-device TTS, LEDs, brightness sensor

## Layout
```
boot.py              Wi-Fi connect, SD mount, then imports main
main.py              wires modules together, runs the async event loop
pins.py              all GPIO/I2C/SPI/I2S pin assignments in one place
config.json          alarm hour/minute/volume/sound file (replaces data.xml)
wifi_secrets.py.example
modules/
  display.py         SSD1306 clock rendering
  clock.py           DS3231 read/set, NTP fallback
  audio.py           I2S init + play_wav()
  alarm.py           compares clock to config, triggers audio, watches button
  web.py             microdot routes: GET / , POST /set_alarm
web/
  index.html         alarm time + volume form
sounds/
  README.md          notes on generating .wav clips (files themselves live on SD)
```
