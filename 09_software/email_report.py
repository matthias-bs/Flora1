"""Send a report by email with config and content provided as parameters"""
###############################################################################
# email_report.py
#
#
# - set up communication with SMTP server
# - set up mail header
# - send mail
#
# created: 01/2021 updated: 06/2021
#
# This program is Copyright (C) 01/2021 Matthias Prinke
# <m.prinke@arcor.de> and covered by GNU's GPL.
# In particular, this program is free software and comes WITHOUT
# ANY WARRANTY.
#
# History:
#
# 20210117 Extracted from flora.py
# 20210608 Added base_topic_flora to Email subject
#
# To Do:
# -
#
###############################################################################

import smtplib
import ssl
from email.message import EmailMessage
from settings import DEBUG, VERBOSITY
from print_line import print_line

###############################################################################
# Email class - Setup email object from config file and send message
###############################################################################
class Email:
    """
    Handle e-Mails

    Attributes:
        smtp_server (string):   SMTP server address
        smtp_port (int):        SMTP server port
        smtp_receiver (string): SMTP mail receiver address(es)
        smtp_email (string):    SMTP mail sender address
        smtp_login (string):    SMTP server login
        smtp_passwd (string):   SMTP server password

    """
    def __init__(self, config):
        """
        The constructor for Email class.

        Parameters:
            config (ConfigParser): config file parser
        """
        # Get e-Mail settings from config
        self.base_topic_flora = config['MQTT'].get('base_topic_flora', None)
        self.smtp_server = config['Email'].get('smtp_server', None)
        self.smtp_port = config['Email'].getint('smtp_port', None)
        self.smtp_receiver = config['Email'].get('receiver_email', None)
        self.smtp_email = config['Email'].get('smtp_email', None)
        self.smtp_login = config['Email'].get('smtp_login', None)
        self.smtp_passwd = config['Email'].get('smtp_passwd', None)

        if VERBOSITY > 1:
            print_line(F"E-Mail settings: {self.smtp_server}, {self.smtp_port}, \
                         {self.smtp_email}, {self.smtp_receiver}")

    def send(self, content):
        """
        Send report as mail.

        Parameters:
            content (string): mail content

        Returns:
            bool: success
        """
        msg = EmailMessage()
        msg['Subject'] = "Flora Status (" + self.base_topic_flora + ")"
        msg['From'] = self.smtp_email
        msg['To'] = self.smtp_receiver
        msg.set_content(content, subtype='html')

        context = ssl.create_default_context()
        success = True

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if DEBUG:
                server.set_debuglevel(1)
            server.ehlo()  # Can be omitted
            server.starttls(context = context)
            server.ehlo()  # Can be omitted
            server.login(self.smtp_login, self.smtp_passwd)
            server.send_message(msg)

        except:
            success = False

        finally:
            server.quit()

        return success
