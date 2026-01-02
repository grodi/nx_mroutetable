# nx_mroutetable
## Description
The script prints mroute information in a better readable table format on NX-OS platforms.
Optional the incoming/outgoing interface description are shown.<br>
To reduce the table width a filter can be configured which shortens the interface descriptions as well as cdp/lldp hostnames.<br>
```event manager environment RMLIST "connected-to-, .mydom.dom, yyy-, zzz"```

Note: The script is not vrf aware, it uses the default vrf.

## To use
1. Copy script to N9K switch bootflash:scripts/
2. Execute using:
   ```
   source n9k_mroutetable.py
   ```
   or
   ```
   source n9k_mroutetable.py -d
   ```
4. Configure an alias, e.g.
   ```
   cli alias name mroute source n9k_mroutetable.py
   ```
5. Configure a list removing unnessacary characters form interfaces description or the cdp/lldp neighbor hostname
   ```
   event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
   ```
The script was tested on N9K using 10.6.1 release.
