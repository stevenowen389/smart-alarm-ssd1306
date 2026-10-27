# Welcome to "_Smala_" - the IoT Smart Alarm Clock

=======
All credit goes to the creator of the original repo - Fabian Gebhart, this fork is my version that uses a SSD1306 OLED display.
:warning: :warning: **THIS PROJECT IS STILL IN DEVELOPMENT AND MIGHT NOT RUN AS EXPECTED**  :warning: :warning:

Raspberry Pi setup with SSD1306 (quick guide)
=============================================
 *  Attach the smart alarm HAT to the pi zero.
 *  Install the latest RPI OS
 *  Using the latest Raspberry pi Imager, enable SSH, add WIFI ssid and password etc.
 *  When the pi is running, ssh username@piaddress
 *  clone this repo: git clone 
 *  Install the system and Python dependencies from the repository:
    cd ~/smart_alarm-ssd1306
    ./install_dependencies.sh
    
Currently working functions
============================

* text to speech synthesizer
   - user text input
* two ways of wake-up sound:
   - play local mp3 files
   - play internet radio station using url streaming
    
* set alarm via smartphone or any other computer using the raspberry pi url found using ifconfig.
* running apache2 server
* automatic display brightness adjustment due to inbuilt photocell
* audio amplifier volume control
* RGB led sunrise/sunset simulation



