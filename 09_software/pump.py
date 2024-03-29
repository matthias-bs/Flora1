"""Control water pump"""
###############################################################################
# pump.py
#
# This module provides the Pump class
#
# - controls the pump driver via GPIO
# - reads the status of the pump driver via GPIO
# - accesses instance property <empty> of Tank class
# - method <power_on> runs the pump for a defined time while preventing
#   dry running and returning the status
# - provides <timestamp> attribute (usage is left to the application)
# - provides <busy> attribute (usage is left to the application)
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
# 20230204 Coding style improvements (with pylint)
#
# To Do:
# -
#
###############################################################################

from time import sleep
from gpio import GPIO

###############################################################################
# Pump class - Pump hardware control/status and software busy flag + timestamp
#
#              Dry running is prevented by using the <empty>-property
#              provided by an instance of the Tank class.
#
###############################################################################
class Pump:
    """Control the pump.

    Attributes:
        p_power (int):          output pin no. for pump driver control
        p_status (int):         input pin no. for pump driver status
        tank (Tank):            Tank object
        _drvstatus (bool):      raw value of pump driver status
        busy (bool):            pump is currently busy (has to be set explicitely)
        timestamp (float):      timestamp (has to be set explicitely)
        status (int):           combined pump/tank status, updated by power_on() method
                                0 after normal operation
                                1 if tank is empty
                                2 if driver-status is not as expected during on-state
        status_str (string):    status as string
        name (string):          instance name (for debugging)
    """
    def __init__(self, pin_pump_power, pin_pump_status, tank, name=""):
        """
        The constructor for Pump class.

        Parameters:
            pin_pump_power (int):  GPIO pin for pump driver control.
            pin_pump_status (int): GPIO pin for pump driver status.
            tank (Tank):           instance of Tank class (to detect empty tank)
            name (string):         instance name (for debugging)
        """
        self.p_power = pin_pump_power
        self.p_status = pin_pump_status
        self.tank = tank
        GPIO.setup(self.p_power, GPIO.OUT)
        GPIO.output(self.p_power, GPIO.LOW)
        GPIO.setup(self.p_status, GPIO.IN)
        self.busy = 0
        self.timestamp = 0
        self.status = 0
        self.name = name

    @property
    def _drvstatus(self):
        """Get raw value (bool) of status pin."""
        return GPIO.input(self.p_status)

    def control(self, power):
        """
        Low-Level pump control.

        Pump is turned on only if tank is not empty.

        Parameters:
            power (bool): power pump on/off

        Returns:
            int: 1 if tank is empty while trying to power pump on,
                 0 otherwise.
        """

        if self.tank.empty and power == 1:
            return 1
        GPIO.output(self.p_power, power)
        return 0

    def power_on(self, on_time):
        """
        Time-based pump control.

        Parameters:
            on_time (int): Power-on time in seconds.

        Returns:
            int: 0 after normal operation
                 1 if tank is empty
                 2 if driver-status is not as expected during on-state
        """
        self.status = 0
        if self.tank.empty:
            self.status = 1
            return self.status
        GPIO.output(self.p_power, GPIO.HIGH)
        sleep(0.5)
        for _ in range(on_time):
            if self._drvstatus != GPIO.HIGH:
                self.status = 2
                break
            if self.tank.empty:
                self.status = 1
                break
            sleep(1)

        GPIO.output(self.p_power, GPIO.LOW)

        return self.status

    @property
    def status_str(self):
        """Get status of last pump activation as string."""
        if self.status == 0:
            return "o.k."
        if self.status == 1:
            return "tank empty"
        return "error"

    def __str__(self):
        return "{}Pin# driver control: {:2}, Pin# driver status: {:2}, \
                Status: {:>10}, Busy: {}, Timestamp: {}"\
                .format((self.name + ' ') if (self.name != '') else '', self.p_power, self.p_status,
                        self.status_str, self.busy, self.timestamp)
