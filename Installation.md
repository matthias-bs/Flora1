# Flora1 Software Installation

----
**Overview**

1. Raspberry Pi OS Installation
2. Mosquitto MQTT-Broker Installation and Configuration
3. miflora-mqtt-daemon Installation
4. Optional: Configure Raspberry Pi with static IP address
5. Optional: Set up port forwarding in your router to access your MQTT broker from internet
6. flora1 Installation and Configuration

----
**1. Raspberry Pi OS Installation / Update**

Please refer to https://www.raspberrypi.org/software/.

If you want to use an existing installation, an update might be a good idea:
```
$ sudo apt-get update
$ sudo apt-get upgrade
```
----
**2. Mosquitto MQTT-Broker Installation and Configuration**

Please refer to https://github.com/eclipse/mosquitto for details.

Installation:
```
$ sudo apt-get install -y mosquitto mosquitto-clients
```

Excellent resources on MQTT and Mosquitto:
* http://www.steves-internet-guide.com
* https://www.hivemq.com/mqtt-essentials/

How to set up security mechanisms:
* http://www.steves-internet-guide.com/mqtt-security-mechanisms/
* http://www.steves-internet-guide.com/mqtt-username-password-example/
* http://www.steves-internet-guide.com/mosquitto-tls/

The [MQTT-Explorer](https://github.com/thomasnordquist/MQTT-Explorer) is very useful for testing.

----
**3. miflora-mqtt-daemon Installation**

Please refer to https://github.com/ThomDietrich/miflora-mqtt-daemon.

For compatibility with Flora1, set `reporting_method = mqtt-json` in the **miflora-mqtt-daemon** `config.ini`.

----
**4. Optional: Configure Raspberry Pi with static IP address**

Example `/etc/dhcpcd.conf`:
```
[...]
interface wlan0
static ip_address=192.168.0.10/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```
In this example, the Raspberry gets the private IP Address `192.168.0.10` and the router/DNS has the private IP address ```192.168.0.1```.

----
**5. Optional: Set up port forwarding in your router to access your MQTT broker from the Internet**

***Please refer to your router's documentation and make sure to maintain security!***
***It is highly recommended to allow only Secure MQTT (MQTT over TLS, port 8883) forwarding.***

----
**6. flora1 Installation and Configuration**

Install Python 3 (should already been done in step 3):
```
$ sudo apt install git python3 python3-pip
```

Copy all source files from https://github.com/matthias-bs/Flora1/tree/main/09_software to `/opt/flora`.
```
$ cd /opt/flora
$ sudo cp config.ini.dist config.ini
```
Edit `config.ini` as required. (e.g. ```sudo nano config.ini```) 

Flora1 needs access to GPIO ports to monitor the tank level and and to control the pump.

```$ sudo adduser daemon gpio```

Test your setup / ```config.ini```:

```python3 flora.py```

If everything works as desired: Congratulations!

Now set up flora to run in daemon mode:
```
$ sudo cp /opt/flora/template.service /etc/systemd/system/flora.service
$ sudo systemctl daemon-reload
$ sudo systemctl start flora.service
$ sudo systemctl status flora.service
$ sudo systemctl enable flora.service
```

If needed, check status/error messages in ```/var/log/syslog```.
