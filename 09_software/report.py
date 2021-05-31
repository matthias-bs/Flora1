###############################################################################
# report.py
#
# This module provides the Report class
# 
# - generates HTML report with various sensor/plant and system data
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
# 20210118 Extracted from flora.py
#
# ToDo:
# - 
#
###############################################################################

from unidecode import unidecode
from datetime import datetime
from time import time, strftime

###############################################################################
# Report class - Generate status report  
###############################################################################
class Report:
    """
    Generate status report
    
    Accesses the following object instances:
    - <settings>
    - <sensors>
    - <pump>
    - <tank>
    - <alert>
    
    Attributes:
        sensors (Sensor{}):     dictionary of Sensor class
        rep (string):           report contents
    """
    def __init__(self, settings, sensors, tank, pump):
        """
        The constructor for Report class.
        
        Parameters:
            sensors (Sensor{}):     dictionary of Sensor class
        """
        self.settings = settings
        self.sensors = sensors
        self.tank = tank
        self.pump = pump
        
        # Find minimum light_irr value of all sensors
        self.min_light_irr = 1000000
        for s in sensors:
            self.min_light_irr = min(self.min_light_irr, sensors[s].light_irr)

        self.rep = ""
        self.header()
        self.sensor_status()
        self.system_status()
        self.footer()
        self.rep = unidecode(self.rep)
        

    def header(self):
        """
        Generate HTML header for email report.

        The result is stored in the attribute <rep>.
        """
        self.rep += '<!DOCTYPE html>\n'
        self.rep += '<html>\n'
        self.rep += '<head>\n'
        self.rep += '<title>Flora Status Report</title>\n'
        self.rep += '</head>\n'
        self.rep += '<body>\n'
        self.rep += '<h1>Flora Status Report</h1>\n'
        date = datetime.now()
        self.rep += 'erstellt: {:s}<br><br>\n'.format(date.strftime("%x %X"))    


    def sensor_status(self):
        """
        Add sensor (and plant) status (HTML table) to report.

        Needs access to the object instance <sensors>.

        The background color of table cells is set to orange for notifications
        and to red for alerts.

        The content is appended to the attribute <rep>.
        """
        self.rep += '<table border="1">\n'
        self.rep += '<tr><th>Sensor<th>Soll/Ist<th>Feuchte [%]<th>Temperatur [&deg;C]\
                    <th>Leitf. [µS/cm]<th>Licht [lux]</tr>\n'

        for sensor in self.sensors:
            s = self.sensors[sensor]
            self.rep += '<tr>\n'
            self.rep += '<td>{:s} ({:s})'.format(s.name, s.plant)
            self.rep += '<td>Soll'
            self.rep += '<td align="center">{:3.0f} ... [{:3.0f} ...{:3.0f}] ...{:3.0f}'\
                        .format(s.moist_min, s.moist_lo, s.moist_hi, s.moist_max)
            self.rep += '<td align="center">{:3.0f} ... {:3.0f}'.format(s.temp_min, s.temp_max)
            self.rep += '<td align="center">{:4.0f} ... {:4.0f}'.format(s.cond_min, s.cond_max)
            self.rep += '<td align="center">{:6.0f} ... {:6.0f}'.format(s.light_min, s.light_max)
            self.rep += '</tr>\n'
            self.rep += '<tr>\n'

            if (s.valid == False):
                self.rep += '<td bgcolor="grey">-<td>Ist'
                self.rep += '<td align="center" bgcolor="grey">-'
                self.rep += '<td align="center" bgcolor="grey">-'
                self.rep += '<td align="center" bgcolor="grey">-'
                self.rep += '<td align="center" bgcolor="grey">-'
            else:
                if (s.batt_ul):
                    col = "red"
                else:
                    col = "white"
                self.rep += '<td bgcolor="{:s}">Batt:{:3.0f} %\n'\
                    .format(col, s.batt)
                self.rep += '<td>Ist\n'
                if (s.moist_ll or s.moist_hl):
                    col = "orange"
                elif (s.moist_ul or s.moist_oh):
                    col = "red"
                else:
                    col = "white"
                self.rep += '<td align="center" bgcolor="{:s}">{:3.0f}\n'\
                    .format(col, s.moist)

                if (s.temp_ul or s.temp_oh):
                    col = "red"
                else:
                    col = "white"
                self.rep += '<td align="center" bgcolor="{:s}">{:3.0f}\n'\
                    .format(col, s.temp)

                if (s.cond_ul or s.cond_oh):
                    col = "red"
                else:
                    col = "white"
                self.rep += '<td align="center" bgcolor="{:s}">{:3.0f}\n'\
                    .format(col, s.cond)

                if (s.light_ul or s.light_oh):
                    col = "red"
                else:
                    col = "white"
                self.rep += '<td align="center" bgcolor="{:s}">{:3.0f}\n'\
                    .format(col, s.light)
            
            self.rep += '</tr>\n'
        # END: for s in sensor_list:
        self.rep += '</table>\n'


    def system_status(self):
        """
        Add system status (HTML table) to report.
        
        Needs access to the object instances <settings>, <pump>, <tank>, <alert>
        
        The content is appended to the attribute <rep>.
        """
        self.rep += '<h2>Systemstatus</h2>\n'
        self.rep += '<table border="1">\n'
        self.rep += '<tr><td>Automatische Benachrichtigung<td align="right">{:}</tr>\n'\
            .format("Ein" if(self.settings.auto_report) else "Aus")
        self.rep += '<tr><td>Automatische Bew&auml;sserung<td align="right">{:}</tr>\n'\
            .format("Ein" if (self.settings.auto_irrigation) else "Aus")
        self.rep += '<tr><td>Bew&auml;sserungsdauer (autom.) [s]<td align="right">{:d}</tr>\n'\
            .format(self.settings.irr_duration_auto)
        self.rep += '<tr><td>Bew&auml;sserungsdauer (manuell) [s]<td align="right">{:d}</tr>\n'\
            .format(self.settings.irr_duration_man)
        self.rep += '<tr><td>Pause nach Bew&auml;sserung [s]<td align="right">{:d}</tr>\n'\
            .format(self.settings.irr_rest)        
        self.rep += '<tr><td>max. Beleuchtungsst&auml;rke [lx]<td align="right">{:d}</tr>\n'\
            .format(self.min_light_irr)
        last_irrigation = "-" if (self.pump.timestamp == 0) \
                              else datetime.fromtimestamp(self.pump.timestamp).strftime("%x %X")
        self.rep += '<tr><td>letzte automatische Bew&auml;sserung<td align="right">{:s}</tr>\n'\
            .format(last_irrigation)

        if (self.pump.timestamp != 0):
            next_irrigation = datetime.fromtimestamp(pump.timestamp + self.settings.irr_rest).strftime("%x %X")
        else:
            next_irrigation = "-"
        self.rep += '<tr><td>n&auml;chste Bew&auml;sserung fr&uuml;hestens<td align="right">{:s}</tr>\n'\
            .format(next_irrigation)

        self.rep += '<tr><td>Bew&auml;sserung geplant<td align="right">{:s}</tr>\n'\
            .format("Ja" if self.settings.irr_scheduled else "Nein")

        if (self.tank.empty):
            tank_status = "leer"
            col = "red"
        elif (self.tank.low):
            col = "orange"
            tank_status = "niedrig"
        else:
            col = "white"
            tank_status = "i.O."

        self.rep += '<tr><td>Status Tank<td align="right" bgcolor="{:s}">{:s}</tr>\n'\
            .format(col, tank_status)

        if (self.pump.status == 2):
            col = "red"
            pump_status_str = "on: error"
        elif (self.pump.status == 4):
            col = "red"
            pump_status_str = "off: error"
        else:
            col = "white"
            pump_status_str = "i.O."

        self.rep += '<tr><td>Status Pumpe<td align="right" bgcolor="{:s}">{:s}</tr>\n'\
            .format(col, pump_status_str)

        next_alert =  time() + min(self.settings.alerts_defer_time, self.settings.alerts_repeat_time)
        next_alert = datetime.fromtimestamp(next_alert).strftime("%x %X")
        self.rep += '<tr><td>n&auml;chste Mitteilung (falls aktiv)<td  align="right">{:s}</tr>'.format(next_alert)
        self.rep += '</table>\n'

    def footer(self):
        """
        Add HTML footer to report.
        
        The content is appended to the attribute <rep>.
        """
        self.rep += '</body>\n'
        self.rep += '</html>\n'
    
    def get_content(self):
        """Return report content from attribute <rep>."""
        return (self.rep)
