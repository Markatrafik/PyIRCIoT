#!/usr/bin/python3
import sys
import network
from rfc1459mini import PyLayerIRC
from irciotmini import PyLayerIRCIoT
w=network.WLAN(network.STA_IF);
w.active(True)
w.connect("ESSID", "password")
i=PyLayerIRC()
i.i_server="irc-iot.nsk.ru"
i.i_channel="#NSK"
i.i_port=6667
i.i_start_()
i.i_process_()
sys.exit()
