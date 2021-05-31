#!/usr/bin/env python3

###############################################################################
# flora.py
# Plant monitoring and irrigation system using Raspberry Pi
#
# - based on data provided by Mi Flora Plant Sensor MQTT Client/Daemon
# - controls water pump for irrigation
# - monitors water tank - two levels, low and empty
# - provides control/status via MQTT
# - sends alerts via SMTP emails
#
# MQTT subscriptions:
#     <base_topic_sensors>/<sensors>{}      (JSON encoded data)
#     <base_topic>/man_report_cmd           (-)
#     <base_topic>/man_irr_cmd              (-)
#     <base_topic>/man_irr_duration_ctrl    (<seconds>)
#     <base_topic>/auto_report_ctrl         (0|1)
#     <base_topic>/auto_irr_ctrl            (0|1)
#
# MQTT publications:
#     <base_topic>/man_irr_stat             (0|1)
#     <base_topic>/man_irr_duration_stat    (<seconds>
#     <base_topic>/auto_report_stat         (0|1)
#     <base_topic>/auto_irr_stat            (0|1)
#
# created: 02/2020 updated: 02/2021
#
# This program is Copyright (C) 02/2020 Matthias Prinke
# <m.prinke@arcor.de> and covered by GNU's GPL.
# In particular, this program is free software and comes WITHOUT
# ANY WARRANTY.
#
# History:
#
# 20200226 Tank level sensor input working
# 20200302 Config file reading implemented
# 20200304 MQTT client for plant sensor data working
# 20200309 E-mail report implemented, pump control via MQTT message working
# 20200325 Sending e-mail report based on sensor/plant data implemented
# 20200421 Specific irrigation time for automatic/manual mode added
#          MQTT feedback messages for manual irrigation time setting added
#          Handling of sensor time-out added
# 20200428 Added switching auto reporting and auto irrigation on/off via MQTT
# 20200502 Rev. 1.0, Initial release
# 20200504 Added night mode
# 20210105 Fixed manual irrigation
#          Messages were queued while irrigation was already in progress,
#          which led to multiple irrigation cycles where only one was desired.
#          Added message 'man_irrigation_status'
# 20210106 Code cleanup
#          Added tank object as parameter to Pump class constructor -
#          the mapping between pump and tank will never change during run time
# 20210116 Major refactoring and switch to object oriented implementation
#          Functional improvement of E-mail reporting
# 20210117 Split source file into multiple modules
#          Replaced set-/get-methods by properties
# 20210118 Renamed MQTT topics
#
# ToDo:
# - compare light value against daily average
# - add humidity/barometric pressure sensor
#
###############################################################################

import locale
import sys
import argparse
import os.path
import json
import paho.mqtt.client as mqtt
from colorama import init as colorama_init
from colorama import Fore, Back, Style
from configparser import ConfigParser
from time import sleep
from ppretty import ppretty #for debugging only

# Flora specific modules
from settings import *
from print_line import *
from gpio import *
from sensor import Sensor
from tank import Tank
from pump import Pump
from irrigation import Irrigation
from alert import *
from report import Report
from email_report import *


# Options expected (mandatory!) in each sensor-/plant-data section of the config-file
OPTIONS = [
    'name',
    'temp_min', 
    'temp_max',
    'cond_min',
    'cond_max',
    'moist_min',
    'moist_lo',
    'moist_hi',
    'moist_max',
    'light_min',
    'light_irr',
    'light_max'
]


#############################################################################################
# MQTT - Eclipse Paho Setup
#############################################################################################
def mqtt_init(config):
    """
    Init MQTT client and connect to MQTT broker

    Parameters:
        config (ConfigParser): config file parser 
    """

    # MQTT Connection
    print_line('Connecting to MQTT broker -->')
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = mqtt_on_connect

    if config['MQTT'].getboolean('tls', False):
    # According to the docs, setting PROTOCOL_SSLv23 "Selects the highest protocol version
    # that both the client and server support. Despite the name, this option can select
    # 'TLS' protocols as well as 'SSL'" - so this seems like a resonable default
        mqtt_client.tls_set(
            ca_certs=config['MQTT'].get('tls_ca_cert', None),
            keyfile=config['MQTT'].get('tls_keyfile', None),
            certfile=config['MQTT'].get('tls_certfile', None),
            tls_version=ssl.PROTOCOL_SSLv23
        )

    if config['MQTT'].get('username'):
        mqtt_client.username_pw_set(config['MQTT'].get('username'),
                                    config['MQTT'].get('password', None))
    try:
        mqtt_client.connect(config['MQTT'].get('hostname', 'localhost'),
                            port=config['MQTT'].getint('port', 1883),
                            keepalive=config['MQTT'].getint('keepalive', 60))
    except:
        print_line('MQTT connection error. Please check your settings in the ' +\
                'configuration file "config.ini"', error=True, sd_notify=True)
        sys.exit(1)

    return mqtt_client



def mqtt_setup_messages(mqtt_client, settings, sensors):
    """
    Subscribe to MQTT topics and set up message callbacks

    Parameters:
        mqtt_client (Client): MQTT Client
    """
    # Subscribe to flora control MQTT topics
    for topic in ['man_report_cmd', 'man_irr_cmd', 'man_irr_duration_ctrl', 'auto_report_ctrl', 'auto_irr_ctrl']:
        print_line('Subscribing to MQTT topic ' + settings.base_topic_flora + '/' + topic,
                   console=True, sd_notify=True)
        mqtt_client.subscribe(settings.base_topic_flora + '/' + topic, qos=2)

    # Subscribe all MQTT sensor topics, e.g. "miflora-mqtt-daemon/appletree/moisture"
    for sensor in sensors:
        print_line('Subscribing to MQTT topic ' + settings.base_topic_sensors + '/' + sensor,
                console=True, sd_notify=True)
        mqtt_client.subscribe(settings.base_topic_sensors + '/' + sensor)

    # Set topic specific message handlers
    mqtt_client.message_callback_add(settings.base_topic_flora + '/man_report_cmd', mqtt_man_report_cmd)
    mqtt_client.message_callback_add(settings.base_topic_flora + '/man_irr_cmd', mqtt_man_irr_cmd)
    mqtt_client.message_callback_add(settings.base_topic_flora + '/man_irr_duration_ctrl', mqtt_man_irr_duration_ctrl)
    mqtt_client.message_callback_add(settings.base_topic_flora + '/auto_report_ctrl', mqtt_auto_report_ctrl)
    mqtt_client.message_callback_add(settings.base_topic_flora + '/auto_irr_ctrl', mqtt_auto_irr_ctrl)

    # Message handler for reception of all other subsribed topics
    mqtt_client.on_message = mqtt_on_message


#############################################################################################
# MQTT - Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
#############################################################################################
def mqtt_on_connect(client, userdata, flags, rc):
    """
    MQTT client connect initialization callback function

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        flags: response flags sent by the broker
        rc: return code - connection result
    """
    if rc == 0:
        print_line('<-- MQTT connection established', console=True, sd_notify=True)
    else:
        print_line('Connection error with result code {} - {}'.format(str(rc),
                   mqtt.connack_string(rc)), error=True)
        #kill main thread
        os._exit(1)

    # Set up MQTT message subscription and handlers
    mqtt_setup_messages(mqtt_client, settings, sensors)


def mqtt_man_report_cmd(client, userdata, msg):
    """
    Send report as mail.

    This is an MQTT message callback function
    Note: The Email timestamp is not updated!


    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain
    """
    print_line('MQTT message "man_report_cmd" received.', console=True, sd_notify=True)

    Email(config).send(Report(settings, sensors, tank, pump).get_content())


def mqtt_man_irr_cmd(client, userdata, msg):
    """
    Run irrigation for <irr_duration> seconds.

    This is an MQTT message callback function

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain
    """
    print_line('MQTT message "man_irr_cmd" received', console=True, sd_notify=True)
    if (pump.busy):
        print_line('Pump already busy ({:s}), ignoring request'
                   .format("manual" if (pump.busy == PUMP_BUSY_MAN) else "auto"),
                   console=True, sd_notify=True)
        return

    mqtt_client.publish(settings.base_topic_flora + '/man_irr_stat', payload=str(1), qos=2)
    pump.busy = PUMP_BUSY_MAN


def mqtt_man_irr_duration_ctrl(client, userdata, msg):
    """
    Set manual irrigation duration (<irr_duration_man>)

    This is an MQTT message callback function

    In this case, MQTT Dash sends the value as string/byte array.
    (b'65' means integer value 65)
    The response message contains the original payload, which
    is used by MQTT Dash to set the visual state.

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain
    """
    settings.irr_duration_man = int(msg.payload)

    print_line('MQTT message "man_irr_duration_ctrl({})" received'.format(settings.irr_duration_man),
               console=True, sd_notify=True)
    client.publish(settings.base_topic_flora + '/man_irr_duration_stat', msg.payload)


def mqtt_auto_report_ctrl(client, userdata, msg):
    """
    Switch auto reporting on/off)

    This is an MQTT message callback function

    In this case, MQTT Dash sends the value as string/byte array.
    (b'0'/b'1' means integer value 0/1)
    The response message contains the original payload, which
    is used by MQTT Dash to set the visual state.

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain
    """
    settings.auto_report = int(msg.payload)

    print_line('MQTT message "auto_report_ctrl({})" received'.format(settings.auto_report),
               console=True, sd_notify=True)
    client.publish(settings.base_topic_flora + '/auto_report_stat', msg.payload)


def mqtt_auto_irr_ctrl(client, userdata, msg):
    """
    Switch auto irrigation on/off

    This is an MQTT message callback function

    In this case, MQTT Dash sends the value as string/byte array.
    (b'0'/b'1' means integer value 0/1)
    The response message contains the original payload, which
    is used by MQTT Dash to set the visual state.

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain
    """
    settings.auto_irrigation = int(msg.payload)

    print_line('MQTT message "auto_irr_ctrl({})" received'.format(settings.auto_irrigation),
               console=True, sd_notify=True)
    client.publish(settings.base_topic_flora + '/auto_irr_stat', msg.payload)


def mqtt_on_message(client, userdata, msg):
    """
    Handle all other MQTT messages, i.e. those with sensor data.

    This is an MQTT message callback function.

    Parameters:
        client: client instance for this callback
        userdata: private user data as set in Client() or user_data_set()
        msg: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain    
    """
    base_topic, sensor = msg.topic.split('/')

    # Convert JSON ecoded data to dictionary
    message = json.loads(msg.payload.decode('utf-8'))

    if (VERBOSITY > 1):
        print_line('MQTT message from {}: {}'.format(sensor, message))

    # Discard data if moisture value suddenly drops to zero
    # FIXME: Is this still useful?
    if ((float(message['moisture']) == 0) and
        (sensors[sensor].moist > 5)):
        return

    sensors[sensor].update_sensor(
        float(message['temperature']),
        int(message['conductivity']),
        int(message['moisture']),
        int(message['light']),
        int(message['battery'])
    )


###############################################################################
# Init
###############################################################################

if __name__ == '__main__':

    locale.setlocale(locale.LC_ALL, 'de_DE.UTF8')

    # Argparse
    # https://pymotw.com/3/configparser/
    # https://stackoverflow.com/questions/22068050/iterate-over-sections-in-a-config-file
    parser = argparse.ArgumentParser(description=PROJECT_NAME)
    parser.add_argument('--config_dir',
                        help='set directory where config.ini is located',
                        default=sys.path[0])
    parse_args = parser.parse_args()

    # Intro
    colorama_init()
    print(Fore.GREEN + Style.BRIGHT)
    print(PROJECT_NAME)
    print(PROJECT_VERSION)
    print('Source:', PROJECT_URL)
    print(Style.RESET_ALL)

    # Load configuration file
    config_dir = parse_args.config_dir
    config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
    config.optionxform = str
    config.read([os.path.join(config_dir, 'config.ini.dist'),
                os.path.join(config_dir, 'config.ini')])

    # Set BCM pin addressing mode
    GPIO.setmode(GPIO.BCM)

    # Generate tank object (fill level sensors)
    tank = Tank(GPIO_TANK_SENS_LOW, GPIO_TANK_SENS_EMPTY)

    # Generate pump object
    pump = Pump(GPIO_PUMP_POWER, GPIO_PUMP_STATUS, tank)
    
    # General email object
    email = Email(config)
 
    # Get configuration data from section [Daemon]
    daemon_enabled = config['Daemon'].getboolean('enabled', 'yes')

    # Get more configuration data from section [General]
    period = config['General'].getint('processing_period', PROCESSING_PERIOD)
    batt_low = config['General'].getint('batt_low', 5)

    # Get list of sensor names from config file
    sensor_list = config['MQTT'].get('sensors')
    sensor_list = sensor_list.split(',')

    if (sensor_list == []):
        print_line('No sensors found in the configuration file "config.ini" in the [MQTT] section.',
                error=True, sd_notify=True)
        sys.exit(1)

    # Get sensor timeout from config file 
    sensor_timeout = config['MQTT'].getint('message_timeout', MESSAGE_TIMEOUT)
    
    # Get sensor battery limit from config file
    sensor_batt_min = config['General'].getint('batt_low', BATT_LOW)
        
    # Create a dictionary of Sensor objects
    sensors = {}
    for sensor in sensor_list:
        sensors[sensor] = Sensor(sensor, sensor_timeout, sensor_batt_min)
        # check if config file contains a section for this sensor
        if (not(config.has_section(sensor))):
            print_line('The configuration file "config.ini" has a sensor named {} in the [MQTT] section,'
                    .format(sensor), error=True, sd_notify=True)
            print_line('but no plant data has provided in a section named accordingly.',
                    error=True, sd_notify=True)
            sys.exit(1)

    # Read all plant data from the section (section name = sensor name)
    for sensor in sensors:
        for option in OPTIONS:
            if (not(config.has_option(sensor, option))):
                print_line('The configuration file "config.ini" has a section "[' + section + ']",',
                        error=True, sd_notify=True)
                print_line('but the mandatory key "' + option + '" is missing.',
                        error=True, sd_notify=True)
                sys.exit(1)
        
        sensors[sensor].init_plant(
            plant     = config[sensor].get('name'),
            temp_min  = config[sensor].getfloat('temp_min'),
            temp_max  = config[sensor].getfloat('temp_max'),
            cond_min  = config[sensor].getint('cond_min'),
            cond_max  = config[sensor].getint('cond_max'),
            moist_min = config[sensor].getint('moist_min'),
            moist_lo  = config[sensor].getint('moist_lo'),            
            moist_hi  = config[sensor].getint('moist_hi'),
            moist_max = config[sensor].getint('moist_max'),
            light_min = config[sensor].getint('light_min'),
            light_irr = config[sensor].getint('light_irr'),
            light_max = config[sensor].getint('light_max')
        )
    
    # Initialize settings
    settings = Settings(config)

    # Initialize irrigation
    irrigation = Irrigation()
    
    # Init MQTT client
    mqtt_client = mqtt_init(config)

    # Start MQTT network handler loop
    mqtt_client.loop_start()

    # Notify syslogd that we are up and running
    sd_notifier.notify('READY=1')

    # Wait until MQTT data is valid (this may take a while...)
    print_line('Waiting for MQTT sensor data -->',
               console=True, sd_notify=True)

    for sensor in sensors:
        while (not(sensors[sensor].valid)):
            sleep(1)
        if (VERBOSITY > 1):
            print_line(sensor + ' ready!', console=True, sd_notify=True)

    print_line('<-- Initial reception of MQTT sensor data succeeded.',
               console=True, sd_notify=True)

    # Init sensor value alerts
    batt_alert  = Alert(settings, config['Alerts'].getint('w_battery', 2), "Battery")
    temp_alert  = Alert(settings, config['Alerts'].getint('w_temperature', 2), "Temperature")
    moist_alert = Alert(settings, config['Alerts'].getint('w_moisture', 2), "Moisture_Warning")
    moist_info  = Alert(settings, config['Alerts'].getint('i_moisture', 2), "Moisture_Info")
    cond_alert  = Alert(settings, config['Alerts'].getint('w_conductivity', 2), "Conductivity")
    light_alert = Alert(settings, config['Alerts'].getint('w_light', 2), "Light")
    
    # Init system alerts
    sensor_err_alert = Alert(settings, config['Alerts'].getint('e_sensor', 2), "Sensor")
    pump_err_alert   = Alert(settings, config['Alerts'].getint('e_pump', 2), "Pump")
    tank_low_alert   = Alert(settings, config['Alerts'].getint('e_tank_low', 2), "Tank Low")
    tank_empty_alert = Alert(settings, config['Alerts'].getint('e_tank_empty', 2), "Tank Empty")
    
    if (DEBUG):
        print_line("---------------------")
        print_line("Settings:")
        print_line("---------------------")
        print_line(ppretty(settings, indent='    ', width=40, seq_length=40,
                           show_protected=True, show_static=True, show_properties=True, show_address=True),
                   console=True, sd_notify=True)

    
    if (DEBUG):
        print_line("---------------------")
        print_line("Sensors: {}".format(sensor_list))
        print_line("---------------------")
        print_line(ppretty(sensors, indent='    ', width=40, seq_length=40,
                           show_protected=True, show_static=True, show_properties=True, show_address=True),
                   console=True, sd_notify=True)
        
    if (VERBOSITY > 0):     
        print_line("-----------------------------------------")
        print_line("Starting Main Execution Loop.")
        print_line("-----------------------------------------")
    

    ###############################################################################
    # Main execution loop
    ###############################################################################
    while (True):
        # Execute manual irrigation (if requested)
        irrigation.man_irrigation(settings, mqtt_client, pump)
        
        # Execute automatic irrigation
        if (settings.auto_irrigation):
            settings.irr_scheduled = irrigation.auto_irrigation(settings, sensors, pump)

        alert  = batt_alert.check_sensors(sensors, 'batt_ul')
        alert |= temp_alert.check_sensors(sensors, 'temp_ul', 'temp_oh')
        alert |= moist_alert.check_sensors(sensors, 'moist_ul', 'moist_oh')
        alert |= moist_info.check_sensors(sensors, 'moist_ll', 'moist_hl')
        alert |= cond_alert.check_sensors(sensors, 'cond_ul', 'cond_oh')
        alert |= light_alert.check_sensors(sensors, 'light_ul', 'light_oh')
        alert |= sensor_err_alert.check_sensors(sensors, 'timeout')
        alert |= pump_err_alert.check_system(pump.status == 2)
        alert |= tank_low_alert.check_system(tank.low)
        alert |= tank_empty_alert.check_system(tank.empty)
       
        # Execute automatic sending of mail reports
        if (settings.auto_report):
            if (alert):
                print_line('Alert triggered.', console=True, sd_notify=True)
                Email(config).send(Report(settings, sensors, tank, pump).get_content())

        # Publish status flags/values
        mqtt_client.publish(settings.base_topic_flora + '/auto_report_stat', str(settings.auto_report), qos=2, retain=True)
        mqtt_client.publish(settings.base_topic_flora + '/auto_irr_stat', payload=str(settings.auto_irrigation), qos=2, retain=True)
        mqtt_client.publish(settings.base_topic_flora + '/man_irr_duration_stat', payload=str(settings.irr_duration_man), qos=2, retain=True)
        mqtt_client.publish(settings.base_topic_flora + '/man_irr_stat', payload=str(0))

        if (VERBOSITY > 1):
            for sensor in sensors:
                print_line("{:16s} Moisture: {:3d} % Temperature: {:2.1f} °C Conductivity: {:4d} uS/cm Light: {:6d} lx Battery: {:3d} %"
                        .format(sensor,
                        sensors[sensor].moist,
                        sensors[sensor].temp,
                        sensors[sensor].cond,
                        sensors[sensor].light,
                        sensors[sensor].batt))

        if (VERBOSITY > 2):
            print_line("Tank:  {}".format(tank), console=True, sd_notify=False)
            print_line("Pumpe: {}".format(pump), console=True, sd_notify=False)     
       
        if (DEBUG):
            print_line("------------------")
            print_line("Battery Alert:")
            print_line("------------------")
            print_line(ppretty(batt_alert, indent='    ', width=40, seq_length=40,
                               show_protected=True, show_static=True, show_properties=True, show_address=True),
                       console=True, sd_notify=True)
        if (DEBUG):
            print_line("------------------")
            print_line("Temperature Alert:")
            print_line("------------------")
            print_line(ppretty(temp_alert, indent='    ', width=40, seq_length=40,
                               show_protected=True, show_static=True, show_properties=True, show_address=True),
                       console=True, sd_notify=True)
        if (DEBUG):
            print_line("------------------")
            print_line("Moisture Alert:")
            print_line("------------------")
            print_line(ppretty(moist_alert, indent='    ', width=40, seq_length=40,
                               show_protected=True, show_static=True, show_properties=True, show_address=True),
                       console=True, sd_notify=True)
        if (DEBUG):
            print_line("------------------")
            print_line("Conductivity Alert:")
            print_line("------------------")
            print_line(ppretty(cond_alert, indent='    ', width=40, seq_length=40,
                               show_protected=True, show_static=True, show_properties=True, show_address=True),
                       console=True, sd_notify=True)
        if (DEBUG):
            print_line("------------------")
            print_line("Light Alert:")
            print_line("------------------")
            print_line(ppretty(light_alert, indent='    ', width=40, seq_length=40,
                               show_protected=True, show_static=True, show_properties=True, show_address=True),
                       console=True, sd_notify=True)

        if (daemon_enabled):
            if (VERBOSITY > 1):
                print_line('Sleeping ({} seconds) ...'.format(period),
                        console=True, sd_notify=False)

            # Sleep for <period> seconds
            for step in range(period):
                # Quit sleeping if flag has been set (asynchronously) in 'mqtt_man_irr_cmd'
                # message callback function
                if (pump.busy):
                    break
                sleep(1)
        else:
            print_line('Execution finished in non-daemon-mode', sd_notify=True)
            mqtt_client.disconnect()
            break