import json
import os
import re
import http.client
import rivalcfg
import time


class GameSenseManager:

    mouse = rivalcfg.get_first_mouse()
    app_name = 'Prime_Wireless_Battery'
    app_name = app_name.upper()
    core_props_filename = '%PROGRAMDATA%/SteelSeries/SteelSeries Engine 3/coreProps.json'
    absolute_core_props_filename = re.sub(r'%([^%]+)%', lambda match: os.environ.get(match.group(1)), core_props_filename)

    with open(absolute_core_props_filename, 'r', encoding='utf-8') as file:
        core_props_json = json.load(file)

    if core_props_json:
        endpoint = core_props_json['address'].split(':')
        sseAddress = endpoint[0]
        ssePort = endpoint[1]
    else:
        raise ValueError('Error finding SSE address.')

    app_reg_data = {
        'game': app_name,
        'game_display_name': 'Mouse Battery Idicator for OLED',
        'developer': 'Tobiasz Latocha'
    }

    percent_event_name = 'DISPLAY_MOUSE_PERCENT'

    percent_event = {
        'game': app_name,
        'event': percent_event_name,
        'value_optional': True,
        'handlers': [{
            'device-type': 'screened',
            'mode': 'screen',
            'datas': [{
                'lines': [{
                    'has-text': True,
                    'context-frame-key': 'headline',
                    'bold': True,
                },
                    {
                        'has-text': True,
                        'context-frame-key': 'subline'
                    },
                    {
                        'has-progress-bar': True,
                        'context-frame-key': 'progress'
                    }]
            }]
        }]
    }

    def postToEngine(self, request_type, data):
        jsonData = json.dumps(data)

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(jsonData)
        }

        conn = http.client.HTTPConnection(self.sseAddress, port=self.ssePort)
        conn.request('POST', request_type, body=jsonData, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            print(response.read().decode('utf-8'))
        else:
            print("Błąd: " + response.status)

        conn.close()

    def updateBatteryPercentage(self, percent, isCharging):
        if isCharging is False:
            headline = "Remaning"
        elif isCharging is True and percent != 630 and percent != -5:
            headline = "Charging"
        text_to_display = 'Battery level: ' + str(percent) + '%'
        event_data = {
            'game': self.app_name,
            'event': self.percent_event_name,
            'data': {
                'frame': {
                    'headline': headline,
                    'subline': text_to_display,
                    'progress': percent
                }
            }
        }
        self.postToEngine('/game_event', event_data)

    def deviceIsOff(self):
        headline = "Mouse is offline"
        text_to_display = "Connect device"

        event_data = {
            'game': self.app_name,
            'event': self.percent_event_name,
            'data': {
                'frame': {
                    'headline': headline,
                    'subline': text_to_display,
                    'progress': 0
                }
            }
        }

        self.postToEngine('/game_event', event_data)


    def startApp(self):
        while True:
            mouse = rivalcfg.get_first_mouse()
            if mouse is None:
                self.deviceIsOff()
            elif mouse.battery['is_charging'] == "None":
                self.deviceIsOff()
            else:
                try:
                    while True:
                        time.sleep(1)
                        battery = rivalcfg.get_first_mouse().battery
                        if battery['level'] >= 0 and battery['level'] <= 100:
                            self.updateBatteryPercentage(battery['level'], battery['is_charging'])
                except:
                    continue
            time.sleep(1)


    def addAppToSSE(self):
        self.postToEngine('/game_metadata', self.app_reg_data)
        self.postToEngine('/bind_game_event', self.percent_event);

    def exitApp(self):
        exit_event = {
            'game': self.app_name
        }

        self.postToEngine('/stop_game', exit_event)

    def removeApp(self):
        remove_event = {
            'game': self.app_name
        }
        self.postToEngine('/remove_game', remove_event)