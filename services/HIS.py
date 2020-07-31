#!/usr/bin/python3

'''
'' PyIRCIoT (HIS : Hardware Identification Service)
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

def main():
  #
  irciot = PyLayerIRCIoT()
  #

  #
  del irciot
  #
  sys.exit(0)

if __name__ == '__main__':
  main()

