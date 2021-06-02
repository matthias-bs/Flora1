# Set up *IoT MQTT Panel* from configuration file

You can either edit the provided [JSON configuration file](https://github.com/matthias-bs/Flora1/blob/main/10_mqtt_dashboard/IoTMQTTPanel_Example.json) before importing it or import it as-is and make the required changes in *IoT MQTT Panel*. Don't forget to add the broker's certificate if using Secure MQTT! (in the App: *Connections -> Edit Connections: Certificate path*.)

The dashboard will look like this:
![IoTMQTTPanel - Flora-Control](https://raw.githubusercontent.com/matthias-bs/Flora1/main/10_mqtt_dashboard/IoTMQTTPanel_Flora-Control.png)

----
**Install _IoT MQTT Panel_ on your Android device**
  
  see [IoT MQTT Panel](https://snrlab.in/iot/iot-mqtt-panel-user-guide)

----
**Editing [IoTMQTTPanel_Example.json](https://github.com/matthias-bs/Flora1/blob/main/10_mqtt_dashboard/IoTMQTTPanel_Example.json)**

At the beginning, replace the dummy IP address *123.345.678* and port *8883* by your MQTT broker's IP address/hostname and port, change *Your_Client_ID* and *Your_MQTT_Connection* as needed:
```
[...]
"connections":[{"autoConnect":true,"host":"123.345.678","port":8883,"clientId":"Your_Client_ID","connectionName":"Your_MQTT_Connection"
[...]
```

At the end, change *Your_Username* and *Your_Password* as needed:
```
[...]
"username":"Your_Username","password":"Your_Password"
[...]
```

----
**Changing example configuration in _IoT MQTT Panel_**

**Edit _Connection Name_, _Client ID_ and _Broker_:**
![Edit Connection Name, Client ID and Broker](https://github.com/matthias-bs/Flora1/blob/main/10_mqtt_dashboard/IoTMQTTPanel-Edit_Connection-1.png)

**Edit _Username_ and _Password_:**
![Edit Username and Password](https://github.com/matthias-bs/Flora1/blob/main/10_mqtt_dashboard/IoTMQTTPanel-Edit_Connection-2.png)
