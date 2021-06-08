# flora1 MQTT Messages

```
MQTT subscriptions:
     <base_topic_sensors>/<sensors>{}      (JSON encoded data)
     <base_topic>/man_report_cmd           (-)
     <base_topic>/man_irr_cmd              (1|2)                         1: pump #1 / 2: pump #2
     <base_topic>/man_irr_duration_ctrl    (<seconds>)
     <base_topic>/auto_report_ctrl         (0|1)
     <base_topic>/auto_irr_ctrl            (0|1)

MQTT publications:
     <base_topic>/status                   (online|offline|idle|dead$)
     <base_topic>/man_irr_stat             (0|1)
     <base_topic>/man_irr_duration_stat    (<seconds>
     <base_topic>/auto_report_stat         (0|1)
     <base_topic>/auto_irr_stat            (0|1)
     <base_topic>/tank                     (0|1|2)                        0: empty / 1: low / 2: o.k.

$ via LWT
```
