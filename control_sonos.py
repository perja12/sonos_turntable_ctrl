import glob
import sys
import soco

from pypowermate import Powermate

SONOS_PLAYBAR_NAME = "Stue/TV"
SONOS_CONNECT_AMP_NAME = "Platespiller"

POWERMATE_MAX = 800
DEFAULT_TV_VOLUME = 10

def mapFromTo(x, a, b, c, d):
    y = (x - a) / (b - a)* (d - c) + c
    return int(y)


def findDeviceByName(name):
    for zone in soco.discover():
        if zone.player_name == name:
            return zone
    return None


def mapVolumeToSpeed(volume):
    return mapFromTo(volume, 0, 100, 0, POWERMATE_MAX)


def set_volume(volume, current_volume, zone):
    if current_volume != volume:
        #print("Setting volume to %d" % volume)
        zone.volume = volume
        current_volume = volume
    return current_volume


def detect_powermate():
    paths = glob.glob('/dev/input/by-id/usb-Griffin_*_PowerMate*')
    if not paths:
        return None
    print('Detected Powermate at %s' % paths[0])
    return Powermate(paths[0])

if __name__ == '__main__':
    p = detect_powermate()

    if not p:
        sys.stderr.write('error: no powermate found\n')
        sys.exit(1)

    sonos_tv = findDeviceByName(SONOS_PLAYBAR_NAME)
    sonos_turntable = findDeviceByName(SONOS_CONNECT_AMP_NAME)

    if not sonos_tv or not sonos_turntable:
        sys.stderr.write('error: no sonos devices found\n')
        sys.exit(1)

    speed = mapVolumeToSpeed(sonos_tv.volume)
    cur_vol = sonos_tv.volume
    current_track = sonos_tv.get_current_track_info()
    play_turntable = sonos_tv.is_playing_line_in

    while True:
        (ts, evt, val) = p.read_event()
        if evt == Powermate.EVENT_BUTTON:
            if val == Powermate.BUTTON_UP:
                play_turntable = not play_turntable
                if play_turntable:
                    current_track = sonos_tv.get_current_track_info()
                    sonos_tv.switch_to_line_in(source=sonos_turntable)
                    sonos_tv.play()
                else:
                    cur_vol = set_volume(DEFAULT_TV_VOLUME, cur_vol, sonos_tv)
                    speed = mapVolumeToSpeed(DEFAULT_TV_VOLUME)

                    sonos_tv.play_uri(uri=current_track['uri'])
                    if sonos_tv.is_playing_line_in:
                        sonos_tv.switch_to_tv()

        elif evt == p.EVENT_ROTATE:
            speed += val
            speed = min(max(speed, 0), POWERMATE_MAX)
            vol = mapFromTo(speed, 0, POWERMATE_MAX, 0, 100)
            cur_vol = set_volume(vol, cur_vol, sonos_tv)
