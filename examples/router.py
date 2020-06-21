#!/usr/bin/python3

import sys
import os
import time
import json
# For keypress handling:
if os.name == "nt":
  import msvcrt
elif os.name == "posix"
  import termios
  import fcntl
  import select

from irciot_router import PyIRCIoT_router
from rfc1459 import PyLayerIRC

def main():

  irciot1 = PyIRCIoT_router()
  ircbot1 = PyLayerIRC()

  irciot2 = PyIRCIoT_router()
  ircbot2 = PyLayerIRC()

  # when many instances, you can use methods from any one:
  # ircbot1.bot_background_start_()
  # ircbot1.bot_redirect_output_('./iotBot.log')
  
  irciot1.irc_pointer = ircbot1.irc_handler
  irciot1.user_pointer = ircbot1.user_handler
  
  irciot2.irc_pointer = ircbot2.irc_handler
  irciot2.user_pointer = ircbot2.user_handler

  # Warning: Please, run your own IRC server
  # don't use public networks for testing!!!
  
  irciot1.ldict_file = "./ldict.json"
  ircbot1.irc_server = "irc-iot.nsk.ru"
  ircbot1.irc_port = 6667
  ircbot1.irc_channel = '#nskinput'
  ircbot1.irc_define_nick_('IntBot')
  ircbot1.irc_talk_with_strangers = True
  ircbot1.irc_debug = True

  irciot2.ldict_file = irciot1.ldict_file
  ircbot2.irc_server = "irc-iot.nsk.ru"
  ircbot2.irc_port = 6667
  ircbot2.irc_channel = '#nskoutput'
  ircbot2.irc_define_nick_('ExtBot')
  ircbot2.irc_debug = True
  ircbot2.irc_talk_with_strangers = True

  # Example of IRC-IoT addresses translation:
  #
  # irciot2.router_graphs += [
  # ( irciot2.do_router_translation_, {
  #   irciot2.CONST.tag_IN_SCOPE  : 'controller@kitchen',
  #   irciot2.CONST.tag_OUT_SCOPE : 'server@house'
  # } )

  ircbot1.start_IRC_()
  ircbot2.start_IRC_()

  print("Starting IRC, press any key to exit", "\r")

  if os.name == "posix":
    stdin_fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(stdin_fd)
    new_attr = old_term[:]
    new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(stdin_fd, termios.TCSANOW, new_attr)
    old_flag = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flag | os.O_NONBLOCK)

  irc_vuid = "c0" # Bot itself

  try:
   while (ircbot1.irc_run or ircbot2.irc_run):

    (irc1in_message, irc1_wait, irc1_vuid) \
      = ircbot1.irc_check_queue_(ircbot1.CONST.irc_queue_input)
    if irc1in_message != "":
       print("irc1in_message=[\033[0;44m{}\033[0m]".format(irc1in_message))
       irc1int_message = irciot1.do_router_(irc1in_message, irciot1.CONST.dir_in, irc1_vuid)
       print('irc1int_message=[\033[1m{}\033[0m]'.format(irc1int_message))
       if irc1int_message != "":
          irc2out_message = irciot2.do_router_(irc1int_message, irciot1.CONST.dir_out, irc1_vuid)
          print('irc2out_message=[\033[1m{}\033[0m]'.format(irc2out_message))
          ircbot2.irc_add_to_queue_(ircbot2.CONST.irc_queue_output, \
           irc2out_message, irc1_wait, irc1_vuid)

    (irc2in_message, irc2_wait, irc2_vuid) \
      = ircbot2.irc_check_queue_(ircbot2.CONST.irc_queue_input)
    if irc2in_message != "":
       print("irc2in_message=[\033[0;1;44m{}\033[0m]".format(irc2in_message))
       irc2int_message = irciot1.do_router_(irc2in_message, irciot2.CONST.dir_in, irc2_vuid)
       print('irc2int_message=[\033[1m{}\033[0m]'.format(irc2int_message))
       if irc2int_message != "":
          irc1out_message = irciot2.do_router_(irc2int_message, irciot2.CONST.dir_out, irc2_vuid)
          print('irc2out_message=[\033[1m{}\033[0m]'.format(irc1out_message))
          ircbot1.irc_add_to_queue_(ircbot1.CONST.irc_queue_output, \
           irc1out_message, irc2_wait, irc2_vuid)

    sys.stdout.flush()

    key_a = None
    if os.name == "nt":
      if msvcrt.kbhit():
        key_a = True
    elif os.name == "posix":
      key_a, key_b, key_c = select.select([stdin_fd], [], [], 0.0001)
    if key_a:
       print("[Key pressed]")
       break

  finally:
    if os.name == "posix":
      termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)
      fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flag)

  ircbot1.irc_run = False
  ircbot2.irc_run = False

  ircbot1.irc_quit_()
  ircbot2.irc_quit_()

  print("Stopping IRC, please wait for exit")

  ircbot1.bot_process_kill_timeout_(5)

  del irciot1
  del irciot2

  del ircbot1
  del ircbot2

  sys.exit()

if __name__ == '__main__':
  main()

