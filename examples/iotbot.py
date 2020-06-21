#!/usr/bin/python3

import sys
import os
import time
import json
# For keypress handling:
if os.name == "nt":
  import msvcrt
elif os.name == "posix":
  import termios
  import fcntl
  import select
#import subprocess

try: # need for development
  from irciot import PyLayerIRCIoT
  from rfc1459 import PyLayerIRC
except:
  from PyIRCIoT.irciot import PyLayerIRCIoT
  from PyIRCIoT.rfc1459 import PyLayerIRC

def main():

  irciot = PyLayerIRCIoT()

  ircbot = PyLayerIRC()

  # ircbot.bot_background_start_()
  # ircbot.bot_redirect_output_('./iotBot.log')

  irciot.irc_pointer = ircbot.irc_handler
  irciot.user_pointer = ircbot.user_handler
  irciot.ldict_file = "./ldict.json"

  ircbot.irc_server  = "irc-iot.nsk.ru"
  ircbot.irc_port    = 6667

  #ircbot.irc_server  = "chat.freenode.net"
  #ircbot.irc_port    = 6697
  #ircbot.irc_ssl     = True

  # Warning: Please, run your own IRC server
  # don't use public networks for testing!!!

  ircbot.irc_channel = "#Berdsk"
  ircbot.irc_debug   = True
  ircbot.irc_define_nick_("TestBot")

  # ircbot.irc_talk_with_strangers = True
  # ircbot.irc_ident   = True

  ircbot.start_IRC_()

  # irciot.irciot_enable_blockchain_(irciot.CONST.tag_mid_ED25519)

  # irciot.irciot_enable_encryption_(irciot.CONST.tag_ENC_B64_RSA)

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
   while (ircbot.irc_run):

    (irc_message, irc_wait, irc_vuid) \
      = ircbot.irc_check_queue_(ircbot.CONST.irc_queue_input)

    if (irc_message != ""):
       print("irc_message=[\033[0;44m{}\033[0m]".format(irc_message))

       if (irciot.is_irciot_(irc_message)):
          irc_json = irciot.irciot_deinencap_(irc_message, irc_vuid)
          if not irc_json in [ None, "", "[]" ]:
             print("Datumset: [\033[0;41m" + str(irc_json) + "\033[0m]", "\r")
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

  ircbot.irc_run = False
  ircbot.irc_quit_()
  print("Stopping IRC, please wait for exit")
  ircbot.bot_process_kill_timeout_(5)
  del irciot
  del ircbot
  sys.exit()

if __name__ == '__main__':
  main()

