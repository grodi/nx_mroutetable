#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Athor:       grodi, chgrodde@googlemail.com
# Version:     1.0
# Description:
# The script prints mroute information in a better readable table format on NX-OS platforms.
# Optional the incoming/outgoing interface description are shown.
# To reduce the table width a filter can be configured which shortens the interface descriptions as well as cdp/lldp hostnames. 
# event manager environment RMLIST "connected-to-, .mydom.dom, yyy-, zzz"
#
# Note: The script is not vrf aware, it uses the default vrf.
#
# To use:
#   1. Copy script to N9K switch bootflash:scripts/
#   2. Execute using:
# source nx_mroutetable.py
#   or
# source nx_mroutetable.py -d
#
#   3. Configure an alias, e.g.
# cli alias name mroute source nx_mroutetable.py
#
#   4. Configure a list removing unnessacary characters form interfaces description or the cdp/lldp neighbor hostname
# event manager environment RMLIST "connected-to-, xxx-, yyy-, zzz"
#
# The script was tested on N9K using 10.6.1 release.
#

from __future__ import division

import sys
import xml.etree.cElementTree as ET
import re
from optparse import OptionParser   # deprecated, better use argparse

try:
    from cli import cli
except:
    ignore = None

# max column width
max_descr_width = 21      # interface description

# a list of character strings removed from interface description to shorten the table width
#ifdescr_rm_list = ["connected-to-", "n93108-", "n93k-"]

# IPv4 multicast regex
mcip_regex = re.compile(
    r'^(22[4-9]|23[0-9])(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$'
)


def args_parser():
    usage = (
        "\n  source nx_mroutetable.py [option(s)]\n"
        "      valid options are -d or -a [ADDRESS]\n"
        "      or a combination of both options in the form of -da")
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--description",
                      action="store_true",
                      dest="d_flag",
                      default=False,
                      help="shows description for ingress and egress interfaces")
    parser.add_option("-a", "--address",
                      dest="address",
                      default=False,
                      help="Limits the output to specified multicast address")
    
    options, args = parser.parse_args()

    if len(args) > 0:
        parser.error("No valid option!")
    return options

def rmlist_parser():
    ## Get character remove list from environment command
    # Run CLI command to fetch the line(s)
    try:
        env_cmd = cli('show running-config | include "event manager environment"')
    except Exception as e:
        print(f"Error running command: {e}")
        env_cmd = None

    # init character remove list with none
    rm_list = None

    if env_cmd:
        # Regex pattern for: event manager environment <VAR> "<VALUE>"
        pattern = r"event manager environment\s+(\S+)\s+\"([^\"]+)\""

        matches = re.findall(pattern, env_cmd)
        #print ("Raw matches: ", matches)

        params = {key: value for key, value in matches}

        # convert to dict RMLIST to a list
        if "RMLIST" in params:
            raw_value = params["RMLIST"]
            # Split into list if you want
            rm_list = [item.strip() for item in raw_value.split(",") if item.strip()]
            #print(f"List form: {rm_list}")
        #else:
         #   print("RMLIST not found.")
            
    return rm_list


def getifdescr(l_interface, l_if_descr_root, l_rm_list):
    if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
    ifdescr = ('---')
    for d in l_if_descr_root.iter(if_manager + 'ROW_interface'):
        try:
            interface = d.find(if_manager + 'interface').text
            #print (interface)
            if interface == l_interface:
                if "loopback" in interface:
                    ifdescr = "removed"
                    break
                ifdescr = d.find(if_manager + 'desc').text
                # optimize description width
                for r in (l_rm_list or []):
                     ifdescr = ifdescr.replace(r, "")
                ifdescr = ifdescr.replace("Ethernet", "e")
                ifdescr = ifdescr[:max_descr_width-1]
                break
        except:
            pass
    return ifdescr


### Main Program ###

## Get script options
# d_flag: adds a description column to table output
option = args_parser()

print ()
print ("*** Displaying the multicast routing table ***")

## if d_flag is set, get remove list from NX-configuration
if option.d_flag:
    rm_list = rmlist_parser()

## when -a option is specified, run an ip address validation check
if option.address:
    if not mcip_regex.match(option.address):
        print(f"Invalid Multicast IP address: {option.address}")
        sys.exit()

print ()
print (f'Running "show ip mroute{" " + option.address if option.address else ""} detail"')
       
## get the mroute table in detail xml format
try:
    mroute_tree = ET.ElementTree(ET.fromstring(cli(f'show ip mroute{" " + option.address if option.address else ""} detail | xml | exclude "]]>]]>"')))
    mroute_root = mroute_tree.getroot()
except Exception as e:
    print(f"Error running command: {e}")
    sys.exit()
mroute_ns = '{http://www.cisco.com/nxos:1.0:mrib}'

print ('and "show interface description"' if option.d_flag else "")

## when -d option is specified, obtain the interface description as XML
if option.d_flag:
    try:
        if_descr_tree = ET.ElementTree(ET.fromstring(cli('show interface description | xml | exclude "]]>]]>"')))
        if_descr_root = if_descr_tree.getroot()
    except Exception as e:
        print(f"Error running command: {e}")
        sys.exit()
print ()


#OIF Owners: S - IGMP Static
#            I - IGMP Dynamic
#            P - PIM
#            N - NBM Static
#            m - MRIB Static
#            M - MRIB Dynamic

# Incoming Interface (IIF) = Null
# - it typically means the router knows about the multicast group or source but does not yet have (or no longer has) a valid Reverse Path Forwarding (RPF) interface toward the source or Rendezvous Point (RP)
# - In PIM-SM, when the router learns about a group from an IGMP join but hasn’t yet learned which RP is responsible, it may install a (*,G) entry with IIF = Null temporarily.
# - If the multicast source is directly connected, sometimes you’ll see an (S,G) with IIF = Null until the first data packet arrives. Once packets come in on the local interface, the router updates the IIF dynamically.


print ('IIf: Traffic Ingress Interface   IIfDescr: Ingress Interface Description')
print ('OIF: Traffic Outgoing Interface  OIFDesc:  Outgoing Interface Description')

## prepare table header
sum_header = (
     f"{'Source':{17}}"
     f"{'Group':19}"
     f"{'Uptime':{11}}"
     f"{'IIf':{7}}"
     + (f"{'IIfDesc':{max_descr_width}}" if option.d_flag else '')
     + f"{'RPF Neigh':{14}}"
     f"{'Packets':{9}}"
     f"{'Bytes':{10}}"
     f"{'Rate/bps':{10}}"
)

oif_header = (
     f"{'OIF':{7}}"
     f"{'Uptime':{10}}"
     f"{'Owner':{8}}"
     + (f"{'OIfDesc':{max_descr_width}}" if option.d_flag else '')
)

# print table header
print ("-" * len(sum_header + oif_header))
print (sum_header + oif_header)
print ("-" * len(sum_header + oif_header))

## start iterating through the mroute table
for i in mroute_root.iter(mroute_ns + 'ROW_one_route'):
    group_addrs = i.find(mroute_ns + 'group_addrs').text
    source_addrs = i.find(mroute_ns + 'source_addrs').text
    uptime = i.find(mroute_ns + 'uptime').text
    route_iif = i.find(mroute_ns + 'route-iif').text

    # search for a inteface description when -d option is set    
    if option.d_flag:
           iifdescr = getifdescr(route_iif, if_descr_root, rm_list)

    route_iif = route_iif.replace("Ethernet", "e")      # shorten output
    route_iif = route_iif.replace("loopback", "loo")    # shorten output

    rpf_nbr = i.find(mroute_ns + 'rpf-nbr').text
    stats_pkts = i.find(mroute_ns + 'stats-pkts').text
    stats_bytes = i.find(mroute_ns + 'stats-bytes').text
    stats_rate_buf = i.find(mroute_ns + 'stats-rate-buf').text
    stats_rate_buf = stats_rate_buf.replace(' bps', '')


    print(
        f"{source_addrs:{17}}{group_addrs:{19}}{uptime:{11}}"
        f"{route_iif:{7}}"
        + (f"{iifdescr:{max_descr_width}}" if option.d_flag else '')
        + f"{rpf_nbr:{14}}"
        f"{stats_pkts:{9}}{stats_bytes:{10}}{stats_rate_buf:{10}}"
        f"{'-v':7}{'':11}{'':7}"   # placeholder for OIF output
    )

    for oif_row in i.iter(mroute_ns + 'ROW_oif'):
        oif_name = oif_row.find(mroute_ns + 'oif-name').text

        # search for interface description when the -d option is set    
        if option.d_flag:
                oifdescr = getifdescr(oif_name, if_descr_root, rm_list)

        oif_name = oif_name.replace("Ethernet", "e")      # shorten output
        oif_uptime = oif_row.find(mroute_ns +'oif-uptime').text
        

        for oif_mpib in oif_row.iter(mroute_ns + 'ROW_oif_mpib'):
            oif_mpib_name = oif_mpib.find(mroute_ns + 'oif-mpib-name').text

        print(
            " " * len(sum_header)
             + f" {oif_name:7}{oif_uptime:10}{oif_mpib_name:8}"
             + (f"{oifdescr:{max_descr_width}}" if option.d_flag else '')
        )

    #print()

sys.exit()
