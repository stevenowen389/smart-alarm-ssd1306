# Welcome to "_Smala_" - the IoT Smart Alarm Clock

<<<<<<< HEAD
=======
All credit goes to the original creator of the original repo, this fork is my version that uses a SSD1306 OLED display.
ALL PHOTOS SHOW THE ORIGINAL SMART ALARM CASE, I HAVEN'T MODIFIED THE CAD/STL FILES, I LEAVE THIS UP TO THE USER.
THE WIKI ALSO HAS REFERENCES TO FUNCTIONS THAT I HAVEN'T IMPLEMENTED IE LEDs AND RSS FEEDS.

This smart_alarm project provides an easy to build and program Internet of Things alarm clock. We would love to see you build your own version of it. It is designed, such that you can adapt your needs and improve it easily. Let us know if you want to contribute to this repository or simply want to share your ideas. All kinds of support is appreciated. 


>>>>>>> f188146ca633cd9fbeaba30150c1b335b2235b44
# Instructions - Wiki

:warning: :warning: **THIS PROJECT IS STILL IN DEVELOPMENT AND MIGHT NOT RUN AS EXPECTED**  :warning: :warning:

If you want to build and code your own _smart_alarm_ please visit the **[Smala Wiki](https://github.com/fgebhart/smart_alarm/wiki)**

Or if you just want to dive into the code, simply clone this repository to your computer / Raspberry Pi Zero:

```
cd
git clone https://github.com/fgebhart/smart_alarm.git
```


### Raspberry Pi setup with SSD1306 (quick guide)
Install the latest RPI OS
Using the latest Raspberry pi Imager, enable SSH, add WIFI ssid and password etc.
When the pi is running, ssh username@piaddress
sudo raspi-config, enable I2C in the interface settings.
sudo apt update
sudo apt install -y git openssh-client
sudo nano /boot/firmware/config.txt
Add these lines:
   dtparam=audio=on #this may already exist.
   dtoverlay=audremap,pins_12_13
Ctrl O, enter, Ctrl X, enter
sudo reboot
Verify the audio device: 
   aplay -l
   speaker-test -D default -c 2 -t sine -f 440 -l 1


### Troubleshooting: internet radio / stream playback

Internet radio playback uses `mpd`/`mpc`. If MP3 playback and text-to-speech both work fine, but selecting the "Stream" option fails with an error such as:

```
ERROR: Failed to open "default detected output" (sndio); Requested audio params cannot be satisfied
```

it means `mpd` isn't configured to use the Pi's ALSA audio device (a fresh `mpd` install may default to an incompatible output like `sndio`). Fix it by pointing `mpd` at ALSA explicitly:

```
sudo nano /etc/mpd.conf
```

Add or replace the `audio_output` block with:

```
audio_output {
    type            "alsa"
    name            "smart_alarm_output"
    device          "default"
    mixer_type      "software"
}
```

Then restart `mpd` and test:

```
sudo systemctl restart mpd
mpc clear
mpc add 'https://your-stream-url'
mpc play
mpc status
```

If `device "default"` doesn't work, run `aplay -l` to find the correct ALSA card/device (e.g. `hw:1,0`) and use that instead.


* text to speech synthesizer
* two ways of wake-up sound:
    - play local mp3 files
<<<<<<< HEAD
   - play internet radio station
=======
    - play internet radio station and
    
>>>>>>> f188146ca633cd9fbeaba30150c1b335b2235b44
* set alarm via smartphone or any other computer
* running apache2 server
* automatic display brightness adjustment due to inbuilt photocell
* audio amplifier volume control



### Thanks 

