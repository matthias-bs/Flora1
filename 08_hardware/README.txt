README
=======

Selecting a Raspberry Pi version
---------------------------------
My initial plan was to re-use an old Raspberry Pi Model B (which is more than adequate regarding speed and memory), but the WiFi connection via USB WiFi dongle proved to be unreliable. Restarting the driver via script called from a cron-job did not help either.
Moving to a Rasbberry Pi 3 Model A+ solved this issue. This version was selected as a good compromise between power consumption, size, price and processing power.

Connector J4
-------------
Due to the initial plan using a Raspberry Pi Model B, a 26-pin header was used. For changing to a Raspberry Pi 3, a ribbon cable with a 26-pin-connector on one side and a 40-pin-connector on the other side was used. *It is highly recommended to use a 40-pin header in new designs!*

High Side Driver Infineon BTS621L1
-----------------------------------
The driver works fine, but the device package seems to be outdated (and is not very practical for breadboard designs).

Breadboard vs. printed circuit board
-------------------------------------
It's a matter of taste, but I would rather design a printed circuit board and have them made by a PCB service.

Barometric Pressure Sensor connector (J1)
------------------------------------------
For new designs, I prefer a Bosch BME280 instead of the NXP MPL115. The BME280 provides temperature, humidity and barometric pressure with (in my opinion) excellent specifications.
