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

