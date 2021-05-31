###############################################################################
# tank.py
#
# This module provides the Tank class
#
# - provides the tank fill level status values <low> and <empty>
#   by reading the according sensor outputs via GPIO pins
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

from gpio import *

###############################################################################
# Tank class - Fill level sensor status
###############################################################################
class Tank:
    """
    Get the tank level sensor values of the low- and empty-mark.

    Attributes:
        name (string):  instance name (for debugging)
        low (bool):     fill-level low
        empty (bool):   fill-level empty
        p_low (int):    input pin no. for fill-level empty sensor
        p_empty (int):  input pin no. for fill-level low sensor 
    """
    def __init__(self, pin_sensor_low, pin_sensor_empty, name=""):
        """
        The constructor for Tank class.

        Parameters:
            pin_sensor_low (int):   GPIO pin no. of low level sensor.
            pin_sensor_empty (int): GPIO pin no. of empty level sensor.
            name (string):          instance name
        """
        self.name = name
        self.p_low = pin_sensor_low
        self.p_empty = pin_sensor_empty
        GPIO.setup(self.p_low, GPIO.IN)
        GPIO.setup(self.p_empty, GPIO.IN)

    @property
    def empty(self):
        """
        Get current status of tank empty level sensor.

        Returns:
            bool: True if tank is empty, false otherwise.
        """
        return (GPIO.input(self.p_empty) == True)

    @property
    def low(self):
        """
        Get current status of tank low level sensor.

        Returns:
            bool: True if tank is low, false otherwise.
        """
        return (GPIO.input(self.p_low) == True)
    
    def __str__(self):
        if (self.name != ""):
            name_str = "Name: {} ".format(self.name)
        else:
            name_str = ""
        return ("{}Pin# low: {:2}, Pin# empty: {:2}, Low: {}, Empty: {}"
                .format(name_str, self.p_low, self.p_empty, self.low, self.empty))
