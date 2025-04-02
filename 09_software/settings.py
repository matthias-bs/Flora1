"""Provide default settings and user defined settings from the configuration file"""
###############################################################################
# settings.py
#
# This module provides constants as default application settings
# and the class Settings which mostly provides attributes set
# from the configuration file.
#
# It is higly recommended to leave the constants as-is and to
# modify config.ini instead!!!
#
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
# 20210117 Extracted from flora.py
# 20210602 Added PROJECT_BUILD
# 20210608 Added support of 2nd pump
# 20221010 Fixed initialization of irr_rest
# 20230204 Coding style improvements (with pylint)
# 20250401 Removed auto_report and alerts settings
#
# To Do:
# -
#
###############################################################################


###############################################################################
# Constants
###############################################################################
DEBUG               = False
VERBOSITY           = 1

PROJECT_NAME        = 'flora'
PROJECT_VERSION     = 'V3.0.0'
PROJECT_BUILD       = '20250401'
PROJECT_URL         = 'https://github.com/matthias-bs/Flora1'

GPIO_TANK_SENS_LOW  = 23
GPIO_TANK_SENS_EMPTY = 24
GPIO_PUMP_POWER     = [17, 27]
GPIO_PUMP_STATUS    = [22, 22]

PUMP_BUSY_MAN       = 1
PUMP_BUSY_AUTO      = 2

# Config defaults
PROCESSING_PERIOD   = 300
MESSAGE_TIMEOUT     = 900
NIGHT_BEGIN         = "24:00"
NIGHT_END           = "00:00"
AUTO_IRRIGATION     = 1
IRR_DURATION_AUTO   = 120
IRR_DURATION_MAN    = 60
IRR_REST            = 7200
BATT_LOW            = 5

###############################################################################
# Settings class - Global settings from config file, MQTT messages and others
###############################################################################
class Settings:
    """Global settings from config file"""
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        self.irr_scheduled = [False, False]
        self.auto_irrigation = config['General'].getint('auto_irrigation', AUTO_IRRIGATION)
        self.irr_duration_auto1 = config['General'].getint('irrigation_duration_auto1',
                                                           IRR_DURATION_AUTO)
        self.irr_duration_auto2 = config['General'].getint('irrigation_duration_auto2',
                                                           IRR_DURATION_AUTO)
        self.irr_duration_man = config['General'].getint('irrigation_duration_man',
                                                         IRR_DURATION_MAN)
        self.irr_rest = config['General'].getint('irrigation_rest', IRR_REST)
        self.base_topic_sensors = config['MQTT'].get('base_topic_sensors',
                                                     'miflora-mqtt-daemon').lower()
        self.base_topic_flora = config['MQTT'].get('base_topic_flora',
                                                   'flora').lower()
        night_begin = config['General'].get('night_begin', NIGHT_BEGIN)
        night_end = config['General'].get('night_end', NIGHT_END)
        night_begin_hr, night_begin_min = night_begin.split(':')
        night_end_hr, night_end_min = night_end.split(':')
        self.night_begin_hr = int(night_begin_hr)
        self.night_begin_min = int(night_begin_min)
        self.night_end_hr = int(night_end_hr)
        self.night_end_min = int(night_end_min)
