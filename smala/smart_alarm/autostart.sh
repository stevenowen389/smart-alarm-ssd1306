#!/bin/bash

# set environmental variable for the project path
export smart_alarm_path="${SMART_ALARM_PATH:-$HOME/smart_alarm/smart_alarm}"

# stop mpd service in order to run mopidy
sudo service mpd stop

# activate alternative GIPO function ALT5 for gpio18 which
# is pwm1 and enables rpi-zero audio
gpio_alt -p 18 -f 5

# run smart_alarm main script
python $smart_alarm_path/start_smala.py &

# change rights of data.xml to make it editable
sudo chmod o+w $smart_alarm_path/data.xml

# run mopidy for audio control
#mopidy &
