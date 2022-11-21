###############################################################################
# Alert.py
#
# This module provides the Alert class
#
# - detects changes / active range violations attributes of Sensor instances
# - detects changes / active system status errors (e.g. tank empty)
# - implements filter strategy:
#   - mode = 0: no alert
#   - mode = 1: immediate alert upon change to active state
#   - mode = 2: immediate alert upon change to active state, repeated after
#               <repeat_time> if active state still persists
#   - mode = 3: upon change to active state, issue alert only if
#               * it is the first occurence of its kind
#                 or
#               * after <defer_time> after previous alert has expired
#   - mode = 4: same as mode 3, but alert is repeated after <repeat_time>
#               if active state still persists
#
# created: 01/2021 updated: 01/2021
#
# This program is Copyright (C) 01/2021 Matthias Prinke
# <m.prinke@arcor.de> and covered by GNU's GPL.
# In particular, this program is free software and comes WITHOUT
# ANY WARRANTY.
#
# History:
#
# 20210117 Extracted from flora.py
#
# ToDo:
# -
#
###############################################################################

from time import time
from settings import *
from print_line import *

#########################################################################################
# Alert class - Generate alerts depending on plant/sensor data and filter settings
#########################################################################################
class Alert:
    """
    Handle Alerts

    Detect changes in range violations and issue deferred or immediate alerts (depending
    on configuration). If range violation still persists, conditionally repeat alerts
    (again, depending on configuration).

    The update() method can be used to filter alerts of the following kinds:
        - battery
        - temperature
        - conductivity
        - moisture
        - light intensity
    
    Attributes:
        alert_tstamp (float):   timestamp set by an alert of any category (class attribute!!!)
        defer_time (int):       defer time [s]
        repeat_time (int):      repeat time [s]
        name (string):          instance name (for debugging)
        flag (bool):            set by new <cat> trigger
        val_ul (int):           state vector - value underrange low
        val_oh (int):           state vector - value overrange high
        status (bool):          state flag
    """
    alert_tstamp = 0

    def __init__(self, settings, mode, name = ""):
        """
        The constructor for Alert class.

        Parameters:
            config (ConfigParser):  config file parser
            mode (int):             alert mode
            name (string):          instance name (for debugging)
        """
        self.defer_time = settings.alerts_defer_time
        self.repeat_time = settings.alerts_repeat_time
        self.name = name + ' '
        self.mode = mode
        self.tstamp = 0
        self.flag = False
        # Status vectors (previous values)
        self.val_ul = 0
        self.val_oh = 0
        # Status flag
        self.status = False

    def repeat_expired(self):
        """
        Check if time to repeat the alert has expired.

        Returns:    True  if time to repeat has expired
                    False otherwise
        """
        return (time() - self.tstamp) > self.repeat_time

    def defer_expired(self):
        """
        Check if time to defer the alert has expired.

        Returns:    True  if time to defer the alert has expired
                    False otherwise
        """
        return (time() - Alert.alert_tstamp) > self.defer_time

    def check_sensors(self, sensors, attr1, attr2=None):
        """
        Check if an alert has to be issued (or deferred for later) depending on sensor values

        Parameters:
            sensors (Sensors{}):    dictionary of Sensor class
            attr1 (string):         name of 1st Sensor class attribute (comparison flag) to evaluate 
            attr2 (string):         name of 2nd Sencor class attribute (comparison flag) to evaluate

        Returns:    True  alert to be issued
                    False otherwise
        """
        alert = False

        # Save current state and calculate new state
        val_ul_d = self.val_ul
        self.val_ul = 0
        val_oh_d = self.val_oh
        self.val_oh = 0

        # Generate state vector
        for i, s in enumerate(sensors):
            if getattr(sensors[s], attr1):
                self.val_ul |= (1 << i)

            if attr2 != None:
                if getattr(sensors[s], attr2):
                    self.val_oh |= (1 << i)

        # change: level 0->1 change in state vector
        change = (self.val_ul & ~val_ul_d) or (self.val_oh & ~val_oh_d)

        # Active: level 1 in state vector
        active = self.val_ul or self.val_oh

        if change:
            self.tstamp = time()
            self.flag = True

            # Immediate alert, w/ / w/o repeat  
            if (self.mode == 1) or (self.mode == 2):
                if (VERBOSITY > 0):
                    print_line('Alert: {}(M1/2)'.format(self.name), console=True, sd_notify=True)
                alert = True
            elif (self.mode == 3) or (self.mode == 4):
                if self.defer_expired():
                    if VERBOSITY > 0:
                        print_line('Alert: {}(M3/4)'.format(self.name), console=True, sd_notify=True)
                    alert = True

        if (active):
            if (self.mode == 2) and self.tstamp and self.repeat_expired():
                # Condition active and repeat timer expired
                # -> send alert and restart timer
                if VERBOSITY > 0:
                    print_line('Alert: {}(M2, repeat)'.format(self.name), console=True, sd_notify=True)
                alert = true
                self.tstamp = time()
            if ((self.mode == 3) or (self.mode == 4)) and self.flag:
                    if (self.defer_expired()):
                        # Condition active, flag set and deferring timer expired
                        # -> send alert
                        if (VERBOSITY > 0):
                            print_line('Alert: {}(M3/4), deferred)'.format(self.name), console=True, sd_notify=True)
                        self.tstamp = time()
                        alert = True
                        if (self.mode == 3):
                            # Alert will not be repeated
                            self.flag = False

        else:
            # Condition not active
            # -> stop timer / clear flag
            self.tstamp = 0
            self.flag = False

        if alert:
            Alert.alert_tstamp = time()

        return alert

    def check_system(self, status):
        """
        Check if an alert has to be issued (or deferred for later) depending on system status

        Parameters:
            status (bool):  status flag

        Returns:    True  alert to be issued
                    False otherwise
        """
        alert = False

        # Save current status
        status_d = self.status
        self.status = status

        # change: level 0->1 change in state vector
        change = self.status & ~status_d

        # Active: level 1 in state vector
        active = self.status


        if change:
            self.tstamp = time()
            self.flag = True

            # Immediate alert, w/ / w/o repeat
            if (self.mode == 1) or (self.mode == 2):
                if VERBOSITY > 0:
                    print_line('Alert: {}(M1/2)'.format(self.name), console=True, sd_notify=True)
                alert = True
            elif (self.mode == 3) or (self.mode == 4):
                if self.defer_expired():
                    if VERBOSITY > 0:
                        print_line('Alert: {}(M3/4)'.format(self.name), console=True, sd_notify=True)
                    alert = True

        if active:
            if (self.mode == 2) and self.tstamp and self.repeat_expired():
                # Condition active and repeat timer expired
                # -> send alert and restart timer
                if (VERBOSITY > 0):
                    print_line('Alert: {}(M2, repeat)'.format(self.name), console=True, sd_notify=True)
                alert = true
                self.tstamp = time()
            if ((self.mode == 3) or (self.mode == 4)) and self.flag:
                    if (self.defer_expired()):
                        # Condition active, flag set and deferring timer expired
                        # -> send alert
                        if (VERBOSITY > 0):
                            print_line('Alert: {}(M3/4), deferred)'.format(self.name), console=True, sd_notify=True)
                        self.tstamp = time()
                        alert = True
                        if (self.mode == 3):
                            # Alert will not be repeated
                            self.flag = False

        else:
            # Condition not active
            # -> stop timer / clear flag
            self.tstamp = 0
            self.flag = False

        if alert:
            Alert.alert_tstamp = time()

        return alert
