"""Logging to console/systemd with formatting and classification"""
###############################################################################
# print_line.py
#
# This module provides the print_line() function.
#
# - console output with timestamp and coloured text to stdout/stderr
# - output with timestamp as Systemd Service Notifications
# - send mail
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
# To Do:
# -
#
###############################################################################

import sys
from time import localtime, strftime
import sdnotify
from unidecode import unidecode
from colorama import Fore, Style

###################################################################################
# Logging function
###################################################################################

# Systemd Service Notifications
# https://github.com/bb4242/sdnotify
# sd_notifier: instance of SystemdNotifier class
sd_notifier = sdnotify.SystemdNotifier()

def print_line(text, error = False, warning=False, sd_notify=False, console=True):
    """
    Logging function

    Parameters:
        text (string):    logging text
        error (bool):     format console output as error
        warning (bool):   format console output as warning
        sd_notify (bool): generate systemd sd_notify protocol output
        console (bool):   generate console output (with formatting depending on flags error/warning)
    """
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif warning:
            print(Fore.YELLOW + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
    timestamp_sd = strftime('%b %d %H:%M:%S', localtime())
    if sd_notify:
        sd_notifier.notify('STATUS={} - {}.'.format(timestamp_sd, unidecode(text)))
