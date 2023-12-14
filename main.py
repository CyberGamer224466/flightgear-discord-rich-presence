import time
import requests
import json
from pypresence import Presence

properties = {
    'altitude': 'position/gear-agl-m',
    'altitude-ft': 'position/altitude-agl-ft',
    'aircraft-desc': 'sim/description',
    'airspeed-kt': 'velocities/airspeed-kt',
    'airport': 'sim/tower/airport-id'
}

APPLICATION_ID = 834452760530518027
fg_started = False
run = True

# Read or prompt user for the HTTP port
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        http_port = config.get("http_port", "8080")
except FileNotFoundError:
    http_port = input("Enter the HTTP port for FlightGear (default is 8080): ") or '8080'

    # Save the user's choice to the configuration file
    with open("config.json", "w") as config_file:
        json.dump({"http_port": http_port}, config_file)

def get_prop(prop):
    global fg_started
    try:
        r = requests.get(f'http://127.0.0.1:{http_port}/json/{prop}')
        if not fg_started:
            timestart = time.time()
            fg_started = True
        return r.json()['value']
    except requests.exceptions.ConnectionError:
        if fg_started:
            run = False
        return

def get_all_props():
    altitude = get_prop(properties['altitude-ft'])
    altitude = int(altitude * 10) / 10
    if altitude < -0.1:
        altitude = 'CRASHED'
    else:
        altitude = str(altitude)
        if len(altitude) > 5:
            altitude = altitude[:-5] + ' ' + altitude[-5:]
        altitude += 'ft'

    acd = get_prop(properties['aircraft-desc'])
    ac_desc = ' '.join(list(acd[:16].split(' ')[:-1]))
    ac_desc = acd

    airport = get_prop(properties['airport'])
    return ac_desc, altitude, airport

def set_status():
    if fg_started:
        ac_desc, altitude, airport = get_all_props()
        details = f'Flying at {altitude} near {airport} airport'
        state = f"{ac_desc}"
        large_image = 'logo'
    else:
        large_image = 'logo'
        details = 'In FG launcher'
        state = 'Preparation for the flight'
        get_prop('sim/description')
    RPC.update(
        start=timestart,
        large_image=large_image,
        large_text='FlightGear',
        small_image=large_image,
        small_text='FlightGear',
        details=details,
        state=state,
        buttons=[
            {"label": "GitHub", "url": "https://github.com/CyberGamer224466/flightgear-discord-rich-presence"}
        ],
        instance=False
    )

RPC = Presence(APPLICATION_ID, pipe=0)  # Initialize the client class
RPC.connect()
timestart = time.time()
while run:
    set_status()
    time.sleep(1)