"""Central GPIO/bus pin assignments for the ESP32 smart alarm.

Adjust these to match your actual wiring, then every module imports from
here instead of hardcoding pin numbers.
"""

# I2C bus shared by the OLED display and the DS3231 RTC
I2C_SCL = 22
I2C_SDA = 21

# I2S bus to the MAX98357A amp
I2S_ID = 0
I2S_SCK = 26   # BCLK
I2S_WS = 25    # LRC
I2S_SD = 27    # DIN

# SD card (SPI mode)
SD_SLOT = 2
SD_SCK = 18
SD_MOSI = 23
SD_MISO = 19
SD_CS = 5

# Silence/snooze button (wired to GND, uses internal pull-up)
BUTTON_PIN = 4
