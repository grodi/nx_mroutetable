# nx_mroutetable
## Description
The script prints mroute information in a better readable table format on NX-OS platforms.<br>
Optional the incoming/outgoing interface description are shown.<br>
To reduce the table width a filter can be configured which shortens the interface descriptions as well as cdp/lldp hostnames.<br>
```event manager environment RMLIST "connected-to-, .mydom.dom, yyy-, zzz"```

Note: The script is not vrf aware, it uses the default vrf.

## To use
1. Copy script to N9K switch bootflash:scripts/
2. Execute using:
   ```
   source nx_mroutetable.py
   ```
   or
   ```
   source nx_mroutetable.py -d
   ```
4. Configure an alias, e.g.
   ```
   cli alias name mroute source nx_mroutetable.py
   ```
5. Configure a list removing unnessacary characters form interfaces description or the cdp/lldp neighbor hostname
   ```
   event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
   ```
The script was tested on N9K using 10.6.1 release. But it should run under every NX release > 10.

## Sample Output
```
nx-leaf# mroute -d

*** Displaying the multicast routing table ***

Running "show ip mroute detail"
and "show interface description"

IIf: Traffic Ingress Interface   IIfDescr: Ingress Interface Description
OIF: Traffic Outgoing Interface  OIFDesc:  Outgoing Interface Description
--------------------------------------------------------------------------------------------------------------------------------------------------------
Source           Group             Uptime    IIf    IIfDesc         RPF Neigh     Packets  Bytes      Rate/bps   OIF    Uptime    Owner   OIfDesc
--------------------------------------------------------------------------------------------------------------------------------------------------------
10.10.1.190/32   239.0.0.2/32      3w0d      e1/11  rleaf-1-e1/53   10.15.128.1   126290   6440790    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.190/32   239.0.0.3/32      3w0d      e1/12  rleaf-1-e1/54   10.15.128.5   126290   6440790    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.10.194/32  239.8.0.4/32      3w0d      e1/22  rleaf-2-e1/54   10.15.128.13  126396   6446196    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.10.194/32  239.8.0.5/32      3w0d      e1/22  rleaf-2-e1/54   10.15.128.13  126397   6446247    27.200    -v
                                                                                                                 e1/12  01:30:11  pim     rleaf-1-e1/54
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.186/32   239.8.0.6/32      2d21h     e1/11  rleaf-3-e1/53   10.15.128.1   16564    844764     27.200    -v
                                                                                                                 Null0  2d21h     nbmreg  ---
10.10.1.190/32   239.8.0.12/32     1d01h     e1/11  rleaf-3-e1/53   10.15.128.1   6062     309162     27.200    -v
                                                                                                                 Null0  1d01h     nbmreg  ---
10.11.1.2/32     239.8.2.0/32      1w2d      e1/36  Interlink       10.15.241.2   0        0          0.000     -v
                                                                                                                 e1/22  1w2d      pim     rleaf-2-e1/54
10.10.10.194/32  239.16.0.0/32     3w0d      e1/21  rleaf-4-e1/53   10.15.128.9   126397   6446247    27.200    -v
                                                                                                                 e1/11  02:41:58  pim     rleaf-1-e1/53
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.10.194/32  239.16.0.1/32     3w0d      e1/21  rleaf-4-e1/53   10.15.128.9   126396   6446196    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.10.194/32  239.16.0.2/32     3w0d      e1/22  rleaf-4-e1/54   10.15.128.13  126396   6446196    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.10.194/32  239.16.0.3/32     3w0d      e1/22  rleaf-4-e1/54   10.15.128.13  126396   6446196    27.200    -v
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.190/32   239.16.0.4/32     3w0d      e1/11  rleaf-1-e1/53   10.15.128.1   126293   6440943    27.200    -v
                                                                                                                 e1/22  1d01h     pim     rleaf-2-e1/54
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.190/32   239.16.0.5/32     3w0d      e1/12  rleaf-1-e1/54   10.15.128.5   126293   6440943    27.200    -v
                                                                                                                 e1/21  1d01h     pim     rleaf-2-e1/53
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.190/32   239.16.0.6/32     3w0d      e1/11  rleaf-3-e1/53   10.15.128.1   126293   6440943    27.200    -v
                                                                                                                 e1/21  1d01h     pim     rleaf-2-e1/53
                                                                                                                 Null0  3w0d      nbmreg  ---
10.10.1.186/32   239.16.0.7/32     2d21h     e1/12  rleaf-1-e1/54   10.15.128.5   16564    844764     27.200    -v
                                                                                                                 Null0  2d21h     nbmreg  ---
```
