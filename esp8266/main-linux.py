#!/usr/bin/python3
import sys
from rfc1459mini import PyLayerIRC
from irciotmini import PyLayerIRCIoT
i=PyLayerIRC()
ii=PyLayerIRCIoT()
i.i_server="irc-iot.nsk.ru"
i.i_channel="#NSK"
i.i_port=6667
i.i_handler=ii.ii_pointer
i.i_start_()
i.i_process_()
sys.exit()
