#!/usr/bin/python3

'''
'' PyIRCIoT (GRS : Global Resolving Service)
''
'' Copyright (c) 2020 Alexey Y. Woronov
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

def main():
  #
  irciot = PyLayerIRCIoT()
  irc = PyLayerIRC(PyLayerIRC.CONST.irc_mode_SERVICE)
  #

  #
  del irc
  del irciot
  #
  sys.exit(0)

if __name__ == '__main__':
  main()

