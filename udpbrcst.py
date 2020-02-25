'''
'' PyIRCIoT (PyLayerUDPb class)
''
'' Copyright (c) 2019 Alexey Y. Woronov
''
'' By using this file, you agree to the terms and conditions set
'' forth in the LICENSE file which can be found at the top level
'' of this package
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

import socket
import select
import json
import threading
import ssl
from queue import Queue
from time import sleep
from irciot_shared import *

#from pprint import pprint

import datetime

class PyLayerUDPb( irciot_shared_ ):

 class CONST( irciot_shared_.CONST ):
   #
   irciot_protocol_version = '0.3.31'
   #
   irciot_library_version  = '0.0.180'
   #
   udpb_default_debug = False
   #
   udpb_default_port = 12345
   udpb_default_ip   = ""
   # where "" - all IP addresses
   #
   udpb_default_size = 1024 # in bytes
   #
   udpb_first_wait = 1
   udpb_micro_wait = 0.1
   udpb_default_wait = 1
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   super(PyLayerUDPb, self).__init__()
   #
   self.udpb_task = None
   self.udpb_run = False
   self.udpb_debug = self.CONST.udpb_default_debug
   #
   self.udpb_port = self.CONST.udpb_default_port
   self.udpb_ip   = self.CONST.udpb_default_ip
   #
   self.udpb_size = self.CONST.udpb_default_size
   #
   self.udpb_sock = None
   #
   # End of PyLayerUDPb.__init__()

 def __del__(self):
   self.stop_udpb_()

 def to_log_(self, msg):
   if not self.udpb_debug:
     return
   print(msg)

 def irciot_protocol_version_(self):
   return self.CONST.irciot_protocol_version

 def irciot_library_version_(self):
   return self.CONST.irciot_library_version

 def udpb_setup_(self):
  if self.is_ipv4_address_(self.udpb_ip):
    my_af_inet = socket.AF_INET
  if self.is_ipv6_address_(self.udpb_ip):
    my_af_inet = socket.AF_INET6
  else:
    return
  try:
    self.udpb_sock = socket.socket(my_af_inet, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    self.udpb_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.udpb_sock.bind((self.udpb_ip, self.udpb_port))
  except:
    return
  #
  # End of udpb_setup_()

 def start_udpb_(self):
  self.udpb_task = threading.Thread(target = self.udpb_process_)
  self.udpb_run  = True
  self.udpb_task.start()
  #
  # End of start_udpb_()

 def stop_udpb_(self):
  self.udpb_run  = False
  sleep(self.CONST.udpb_micro_wait)
  #self.udpb_disconnect_()
  try:
    self.udpb_task.join()
  except:
    pass
  #
  # End of stop_udpb_()

 # incomplete
 def udpb_get_ip_by_vuid_(in_vuid):
  return None

 # incomplete
 def udpb_receive_(self):
  try:
    my_data, my_addr = self.udpb_sock.recvfrom(self.udp_size)
    ( my_ip, my_port ) = my_addr
    if my_port != self.udpb_port \
    or not self.is_ip_address_(my_ip):
      return None
    return ( my_data, my_ip )
  except:
    return None
  #
  # End of udpb_receive_()

 # incomplete
 def udpb_send_(self, in_data, in_vuid = self.CONST.in_vuid_all):
  if self.udpb_sock == None:
    return
  if not self.is_ip_port_(self.udpb_port):
    return
  if not isinstance(in_vuid, str):
    return
  if in_vuid[0] not in self.CONST.api_vuid_any:
    return
  if in_vuid == '*':
    my_addr = '<broadcast>'
  else:
    my_addr = self.udpb_get_ip_by_vuid_(in_vuid)
  if my_addr == None:
    return
  self.udpb_sock.sendto(in_data, (my_addr, self.udpb_port))
  sleep(self.CONST.udpb_micro_wait)
  #
  # End of udpb_send_()

 # incomplete
 def udpb_process_(self):
   #
   try:
      udpb_init = 0
      udpb_wait = self.CONST.udpb_first_wait
      udpb_input_buffer = ""
      udpb_ret = 0

      while (sefl.udpb_run):
         sleep(self.CONST.udpb_micro_wait)

   except:
      udpb_init = 0
   #
   # End of udpb_process_()

