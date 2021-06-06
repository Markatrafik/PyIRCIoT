#!/usr/bin/python3

'''
'' PyIRCIoT (HIS : Hardware Identification Service)
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

from time import sleep

default_latency_wait = 0.1
default_config_file = "/etc/irciot/HIS.conf"
default_config_values = {
  'irc_server': 'localhost',
  'irc_port':   '6667',
  'irc_mode':   'bot',
  'irc_nick':   'HIS',
  'irc_info':   'IRC-IoT HIS Service'
}

def main():
  #
  def my_usage_handler_():
    print("Usage: {} [start]".format(sys.argv[0]))
    sys.exit(0)
  #
  irc = PyLayerIRC(PyLayerIRC.CONST.irc_mode_CLIENT)
  #
  irc.load_config_file_(default_config_file, default_config_values)
  #
  irc_serv = irc.get_config_value_('irc_server')
  irc_port = irc.get_config_value_('irc_port')
  irc_nick = irc.get_config_value_('irc_nick')
  irc_info = irc.get_config_value_('irc_info')
  #
  irc.irc_server = irc_serv
  irc.irc_port = int(irc_port)
  irc.irc_info = irc_info
  irc.irc_define_nick_(irc_nick)
  irc.irc_channel = None
  #
  irc.bot_name = irc_nick
  irc.bot_usage_handler = my_usage_handler_
  irc.bot_background_start_()
  #
  irciot = PyLayerIRCIoT()
  #
  irc.start_IRC_()
  #
  while (irc.irc_run):
    (irc_msg, irc_wait, irc_vuid) \
      = irc.irc_check_queue_(irc.CONST.irc_queue_input)
    if (irciot.is_irciot_(irc_msg)):
      pass

    if irc_wait <= 0:
      irc_wait = default_latency_wait
    sleep(irc_wait)
  #
  del irc
  del irciot
  #
  sys.exit(0)

if __name__ == '__main__':
  main()

