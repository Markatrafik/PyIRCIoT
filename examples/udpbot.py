#!/usr/bin/python3

import sys
import os
import time
import json
import random
#import subprocess
# For keypress handling:
if os.name == "nt":
  import msvcrt
elif os.name == "posix":
  import termios
  import fcntl
  import select

from pprint import pprint
try: # need for development
  from irciot import PyLayerIRCIoT
  from udpbrcst import PyLayerUDPb
except:
  print("\033[1mWarning: using pip installed libraries\033[0m")
  time.sleep(3)
  from PyIRCIoT.irciot import PyLayerIRCIoT
  from PyIRCIoT.udpbrcst import PyLayerUDPb

def main():

  irciot = PyLayerIRCIoT()

  udpbot = PyLayerUDPb()

  # udpbot.bot_background_start_()
  # udpbot.bot_redirect_output_('./udpBot.log')
  
  random.seed()

  # irciot.irc_pointer = udpbot.udpb_handler
  # irciot.user_pointer = udpbot.user_handler

  irciot.ldict_file = "ldict.json"

  # Warning: Be careful with UDP port number
  # don't use port lower 1024 for testing!!!

  udpbot.udpb_port   = 12345
  udpbot.udpb_debug  = True
  udpbot.udpb_talk_with_strangers = True

  udpbot.udpb_init_by_interface_('eth0')

  udpbot.start_udpb_()

  irciot.irciot_enable_blockchain_(irciot.CONST.tag_mid_ED25519)

  irciot.irciot_enable_encryption_(irciot.CONST.tag_ENC_B64Z_RSA)

  print("Starting UDP broadcast transport, press any key to exit", "\r")

  if os.name == "posix":
    stdin_fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(stdin_fd)
    new_attr = old_term[:]
    new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(stdin_fd, termios.TCSANOW, new_attr)
    old_flag = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flag | os.O_NONBLOCK)

  udpb_vuid = udpbot.CONST.api_vuid_all

  try:
   while (udpbot.udpb_run):

    if random.randint(1,100) > 95:
      my_datum = {
        irciot.CONST.tag_OBJECT_TYPE: 'xtest',
        irciot.CONST.tag_SRC_ADDR:    '',
        irciot.CONST.tag_DST_ADDR:    '',
        irciot.CONST.tag_DATE_TIME:
        irciot.irciot_get_current_datetime_()
      }
      my_pack = irciot.irciot_encap_all_(my_datum, None)
      udpbot.udpb_output_all_(my_pack, 1)
      time.sleep(1)

    (udpb_message, udpb_wait, udpb_vuid) \
      = udpbot.udpb_check_queue_(udpbot.CONST.udpb_queue_input)

    if (udpb_message != ""):
       print("udpb_message=[\033[0;44m{}\033[0m]".format(udpb_message))

       if (irciot.is_irciot_(udpb_message)):

          udpb_json = irciot.irciot_deinencap_(udpb_message, udpb_vuid)
          if (udpb_json != ""):
             print("Datumset: [\033[0;41m" + str(udpb_json) + "\033[0m]", "\r")
             sys.stdout.flush()
             try:
               my_datums = json.loads(udpb_json)
             except:
               continue
             if not isinstance(my_datums, list):
               continue
             for my_datum in my_datums:
               my_type = None
               if irciot.CONST.tag_OBJECT_TYPE in my_datum.keys():
                 my_type = my_datum[irciot.CONST.tag_OBJECT_TYPE]
                 if my_type == "xtest":
                   my_datum[irciot.CONST.tag_OBJECT_TYPE] = "xtest-answer"
               if my_type == "xtest":
                 my_datum[irciot.CONST.tag_DATE_TIME] \
                   = irciot.irciot_get_current_datetime_()
                 my_packs = irciot.irciot_encap_all_(my_datum, udpb_vuid)
                 if not my_packs in [ None, [] ]:
                   udpbot.udpb_output_all_(my_packs, 1)

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

  udpbot.udpb_run = False
  print("Stopping UDP broadcast transport, please wait for exit")
  del udpbot
  del irciot
  sys.exit()

if __name__ == '__main__':
  main()

