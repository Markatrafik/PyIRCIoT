#!/usr/bin/python3
import sys
import network
from rfc1459mini import PyLayerIRC
from irciotmini import PyLayerIRCIoT
w=network.WLAN(network.STA_IF);
w.active(True)
w.connect("ESSID", "password")
def my_handler(in_datum,in_nick,in_mask):
 print("my_handler($%s$,$%s$,$%s$)"%(in_datum,in_nick,in_mask))
i=PyLayerIRC()
ii=PyLayerIRCIoT()
i.i_server="irc-iot.nsk.ru"
i.i_channel="#NSK"
i.i_port=6667
i.i_handler=ii.ii_pointer
ii.ii_handler=my_handler
i.i_start_()
i.i_process_()
sys.exit()
