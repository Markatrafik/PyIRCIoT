#!/usr/bin/python3

'''
'' PyIRCIoT (GTS : Global Time Service)
''
'' Copyright (c) 2020-2021 Alexey Y. Woronov
''
'' By using this file, you agree to the terms and conditions set
'' forth in the LICENSE file which can be found at the top level
'' of this package
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

import sys

from PyIRCIoT.irciot import PyLayerIRCIoT
from PyIRCIoT.rfc1459 import PyLayerIRC

default_config_file = "/etc/irciot/GTS.conf"
default_config_values = {
  'irc_server': 'localhost',
  'irc_port':   '6667',
  'irc_mode':   'bot',
  'irc_nick':   'GTS'
}

def main():
  #
  irciot = PyLayerIRCIoT()
  irc = PyLayerIRC(PyLayerIRC.CONST.irc_mode_SERVICE)
  #
  irc.load_config_file_(default_config_file, default_config_values)
  #

  #
  del irc
  del irciot
  #
  sys.exit(0)

if __name__ == '__main__':
  main()

