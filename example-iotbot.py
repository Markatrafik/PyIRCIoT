#!/usr/bin/python3

import sys
import os
import time
import json
# For keypress handling:
import termios
import fcntl
import select
#import subprocess

try: # need for development
 from irciot import PyIRCIoT
 from rfc1459 import PyLayerIRC
except:
 import PyIRCIoT

def main():

  # if (len(sys.argv) == 1): 
  #  print("Starting iotBot...")
  #  independent_process = subprocess.Popen(
  #   ['python3.5', os.path.expanduser(sys.argv[0]), 'background']
  #  )
  #  return
   
  # sys.stdout = open('./iotBot.log', 'w+')
  
  # if (len(sys.argv) > 1):
  #  if (sys.argv[1] != 'background'):
  #   return  
 
  irciot = PyIRCIoT()
  
  ircbot = PyLayerIRC()
  
  ircbot.irc_server  = "irc.undernet.org"

  # Warning: Please, run your own IRC server
  # don't use public networks for testing!!!
  
  ircbot.irc_port    = 6667
  ircbot.irc_channel = "#Berdsk"
  ircbot.irc_debug   = True

  ircbot.start_IRC_()
  
  print("Starting IRC, press any key to exit", "\r")
  
  stdin_fd = sys.stdin.fileno()
  old_term = termios.tcgetattr(stdin_fd)
  new_attr = old_term[:]
  new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(stdin_fd, termios.TCSANOW, new_attr)
  old_flag = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
  fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flag | os.O_NONBLOCK)
 
  try: 
   while (ircbot.irc_run):
  
    (irc_message, irc_wait) \
      = ircbot.irc_check_queue_(ircbot.CONST.irc_queue_input)
      
    if (irc_message != ""):
      
       if (irciot.is_irciot_(irc_message)):
          irc_json = irciot.irciot_deinencap_(irc_message)
          if (irc_json != ""):
             print("Datumset: [" + str(irc_json) + "]", "\r")
             sys.stdout.flush()

    key_a, key_b, key_c = select.select([stdin_fd], [], [], 0.0001)
    if key_a:
       print("[Key pressed]")
       break

  finally:
    termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flag)

  ircbot.irc_run = False
  ircbot.irc_quit_()
  print("Stopping IRC, please wait for exit")
  del ircbot
  sys.exit()
    
main()

