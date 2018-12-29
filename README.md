# Control Sonos with the Griffin Powermate

This is a special purpose script to make it easier to get the audio from my turntable out on the Sonos Playbar.

Setup:
* Turntable connected to line-in on Sonos Connect:Amp
* Sonos Playbar connected to TV.

Features:
* Powermate can control volume of the Sonos Playbar
* Pushing the knob of the Powermate will make the turntable play on the Sonos Playbar. Pressing it again will reset it to whatever it was playing before and also set volume to 10.


## Setup

First you want to adjust the names of your sonos devices (see top of control_sonos.py). Use the same names as in the Android or iOS app.

You need this udev rule in order for the script to get permission to the Powermate:
`sudo cp 98-powermate.rules /etc/udev/rules.d/`

Make sure you have python3 and pipenv installed:  `pip3 install --user pipenv`

Run it directly with `pipenv run python control_sonos.py`

## Systemd service

You may want to enable systemd service for this script as it automatically restarts the scripts when rebooting.

* Install with `sudo cp sonos_turntable_ctrl.service /etc/systemd/system/`
* Enable service to run at boot: `sudo systemctl enable sonos_turntable_ctrl`
* Start the service: `sudo systemctl start sonos_turntable_ctrl`
* Check the logs: `sudo journalctl -u sonos_turntable_ctrl`
