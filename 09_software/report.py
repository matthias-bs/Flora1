"""Create HTML-formatted report"""
###############################################################################
# report.py
#
# This module provides the Report class
#
# - generates HTML report with various sensor/plant and system data
#
# created: 01/2021
#
# This program is Copyright (C) 01/2021 Matthias Prinke
# <m.prinke@arcor.de> and covered by GNU's GPL.
# In particular, this program is free software and comes WITHOUT
# ANY WARRANTY.
#
# History:
#
# 20210118 Extracted from flora.py
# 20210608 Added support of 2nd pump
# 20230204 Coding style improvements (with pylint)
# 20250401 Removed email support, added JSON output for MQTT
#
# To Do:
# -
#
###############################################################################

import json
from datetime import datetime
from time import time


###############################################################################
# Report class - Generate status report  
###############################################################################
class Report:
    """
    Generate status report
    
    Attributes:
        settings      (Settings):   instance of Settings class
        sensors       (list):       list of Sensor instances
        pumps         (list):       list of Pump instances
        tank          (Tank):       instance of Tank class
        min_light_irr (int):        smallest max. light intensity which still allows irrigation
    """
    def __init__(self, settings, sensors, pumps, tank):
        """
        The constructor for Report class.

        Args:
            settings (Settings): instance of Settings class
            sensors (list): list of Sensor instances
            pumps (list): list of Pump instances
            tank (Tank): instance of Tank class
        """
        self.settings = settings
        self.sensors = sensors
        self.pumps = pumps
        self.tank = tank
        self.data = {}
        self.min_light_irr = 1000000
        
    def gen_report(self):
        """
        Generate report

        Returns:
            str: JSON formatted report
        """
        self.data['timestamp'] = datetime.now().strftime("%x %X")
        
        # Find minimum light_irr value of all sensors
        for s in self.sensors:
            self.min_light_irr = min(self.min_light_irr, s.light_irr)

        self.sensor_settings()
        self.system_status()
        self.system_settings()
        return json.dumps(self.data)

    def sensor_settings(self):
        """
        Add sensor (and plant) settings / status to report.
        """
        for s in self.sensors:
            self.data[s.name] = {}
            self.data[s.name]['settings'] = {}
            self.data[s.name]['settings']['plant'] = s.plant
            self.data[s.name]['settings']['moist_min'] = s.moist_min
            self.data[s.name]['settings']['moist_lo'] = s.moist_lo
            self.data[s.name]['settings']['moist_hi'] = s.moist_hi
            self.data[s.name]['settings']['moist_max'] = s.moist_max
            self.data[s.name]['settings']['temp_min'] = s.temp_min
            self.data[s.name]['settings']['temp_max'] = s.temp_max
            self.data[s.name]['settings']['cond_min'] = s.cond_min
            self.data[s.name]['settings']['cond_max'] = s.cond_max
            self.data[s.name]['settings']['light_min'] = s.light_min
            self.data[s.name]['settings']['light_max'] = s.light_max
            self.data[s.name]['settings']['batt_min'] = s.batt_min

            if s.valid:
                self.data[s.name]['status'] = {}
                self.data[s.name]['status']['batt_ul'] = s.batt_ul
                self.data[s.name]['status']['temp_ul'] = s.temp_ul
                self.data[s.name]['status']['temp_oh'] = s.temp_oh
                self.data[s.name]['status']['moist_ul'] = s.moist_ul
                self.data[s.name]['status']['moist_ll'] = s.moist_ll
                self.data[s.name]['status']['moist_ul'] = s.moist_ul
                self.data[s.name]['status']['moist_oh'] = s.moist_oh
                self.data[s.name]['status']['cond_ul'] = s.cond_ul
                self.data[s.name]['status']['cond_oh'] = s.cond_oh
                self.data[s.name]['status']['light_ul'] = s.cond_ul
                self.data[s.name]['status']['light_oh'] = s.cond_oh

    def system_status(self):
        """
        Add system status to report.
        """
        self.data['irrigation'] = []
        self.data['pump'] = []
        for pump in self.pumps:
            if (pump.timestamp != 0):
                last_irrigation = datetime.fromtimestamp(pump.timestamp).strftime("%x %X")
                next_irrigation = datetime.fromtimestamp(pump.timestamp + \
                                                         self.settings.irr_rest).strftime("%x %X")
                scheduled = self.settings.irr_scheduled[i]
                self.data['irrigation'].append({'last': last_irrigation, 'next': next_irrigation, 'scheduled': scheduled})

        for pump in self.pumps:
            if (pump.status == 2):
                status = "on: error"
            elif (pump.status == 4):
                status = "off: error"
            else:
                status = "ok"
            self.data['pump'].append(status)

        tank_status = ['empty', 'low', 'ok']
        self.data['tank'] = tank_status[self.tank.status]

    def system_settings(self):
        """
        Add system settings to report.
        """
        self.data['irrigation'] = {}
        self.data['irrigation']['auto_enabled'] = self.settings.auto_irrigation
        self.data['irrigation']['auto_duration'] = []
        self.data['irrigation']['auto_duration'].append(self.settings.irr_duration_auto1)
        self.data['irrigation']['auto_duration'].append(self.settings.irr_duration_auto2)
        self.data['irrigation']['man_duration'] = self.settings.irr_duration_man
        self.data['irrigation']['auto_rest'] = self.settings.irr_rest
        self.data['irrigation']['auto_max_light'] = self.min_light_irr
