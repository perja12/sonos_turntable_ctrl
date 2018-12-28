import glob
import sys
import soco

from pypowermate import Powermate

SONOS_PLAYBAR_NAME = "Stue/TV"
SONOS_CONNECT_AMP_NAME = "Platespiller"

POWERMATE_MAX = 800
DEFAULT_TV_VOLUME = 10

def map_from_to(x, a, b, c, d):
    y = (x - a) / (b - a)* (d - c) + c
    return int(y)


def find_device_by_name(name):
    for zone in soco.discover():
        if zone.player_name == name:
            return zone
    return None


def map_volume_to_speed(volume):
    return map_from_to(volume, 0, 100, 0, POWERMATE_MAX)


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


def set_led(powermate, enable):
    if enable:
        powermate.set_steady_led(0)
    else:
        powermate.set_steady_led(200)

if __name__ == '__main__':
    p = detect_powermate()

    if not p:
        sys.stderr.write('error: no powermate found\n')
        sys.exit(1)

    sonos_tv = find_device_by_name(SONOS_PLAYBAR_NAME)
    sonos_turntable = find_device_by_name(SONOS_CONNECT_AMP_NAME)

    if not sonos_tv or not sonos_turntable:
        sys.stderr.write('error: no sonos devices found\n')
        sys.exit(1)

    speed = map_volume_to_speed(sonos_tv.volume)
    cur_vol = sonos_tv.volume
    current_track = sonos_tv.get_current_track_info()
    play_turntable = sonos_tv.is_playing_line_in

    set_led(p, play_turntable)

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
                    speed = map_volume_to_speed(DEFAULT_TV_VOLUME)

                    sonos_tv.play_uri(uri=current_track['uri'])
                    if sonos_tv.is_playing_line_in:
                        sonos_tv.switch_to_tv()

                set_led(p, play_turntable)

        elif evt == p.EVENT_ROTATE:
            speed += val
            speed = min(max(speed, 0), POWERMATE_MAX)
            vol = map_from_to(speed, 0, POWERMATE_MAX, 0, 100)
            cur_vol = set_volume(vol, cur_vol, sonos_tv)
