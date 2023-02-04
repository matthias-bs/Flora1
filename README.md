# flora1

[![linting: pylint](https://github.com/matthias-bs/flora1/actions/workflows/pylint.yml/badge.svg)](https://github.com/matthias-bs/flora1/actions/workflows/pylint.yml)
[![GitHub release](https://img.shields.io/github/release/matthias-bs/flora1?maxAge=3600)](https://github.com/matthias-bs/flora1/releases)

**Raspberry Pi Irrigation System**

![flora-1_188x300](https://user-images.githubusercontent.com/83612361/120393655-9590ad80-c332-11eb-8bba-2d2cbcf6389f.jpg)


**Features**
* Plant status monitorig via [Xiaomi Mi Flora Plant Sensor MQTT Client/Daemon](https://github.com/ThomDietrich/miflora-mqtt-daemon)
* Tank low / tank empty status monitoring with XKC-Y25-T12V (Non-Contact Liquid Level Sensor)
* Pump control (12 Volts) with [Infineon BTS621L1](https://www.infineon.com/cms/en/product/power/smart-low-side-high-side-switches/high-side-switches/classic-profet-12v-automotive-smart-high-side-switch/bts621l1-e3128a/) (Smart Two-Channel High-Side Power Switch)
* Automatic and manual irrigation control with one or two pumps
* Status reports via Email (HTML) with complex trigger filtering

* Controlling and monitoring via MQTT 


**Dashboard with [IoT MQTT Panel](https://snrlab.in/iot/iot-mqtt-panel-user-guide) (Example)**

![IoTMQTTPanel_Flora-Control_400x580](https://user-images.githubusercontent.com/83612361/120223811-7adf0b80-c242-11eb-98a7-2d18f1335ca9.png)

**Flora Status Report (Example)**

![flora_email](https://user-images.githubusercontent.com/83612361/120225128-f5108f80-c244-11eb-9133-0f7b753c0b68.png)

**Why is it called _flora1_?**

Because _flora2_ is already in the works!

----

## Disclaimer and Legal

> *Xiaomi* and *Mi Flora* are registered trademarks of *BEIJING XIAOMI TECHNOLOGY CO., LTD.*
>
> This project is a community project not for commercial use.
> The authors will not be held responsible in the event of device failure or withered plants.
>
> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Xiaomi* or any of its affiliates or subsidiaries.
