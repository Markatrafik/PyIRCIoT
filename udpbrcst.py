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

#from pprint import pprint

import datetime

class PyLayerUDPb(object):

 class CONST(object):
   #
   irciot_protocol_version = '0.3.29'
   #
   irciot_library_version  = '0.0.168'
   #
   default_udpb_port = 12345
   default_udpb_ip   = ""
   # where "" - all IP addresses
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   self.udpb_port = default_udpb_port
   self.udpb_ip   = default_udpb_ip
   #
   self.udpb_sock = None
   #
   # End of PyLayerUDPb.__init__()

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

 def udpb_receive_(self):
  # data, addr = sock.recvfrom(1024)
  pass
 
 def udpb_send_(self, in_data):
  # sock.sendto(in_data, ('<broadcast>', self.udpb_port))
  # sleep(small_sleep)
  pass

 def is_ipv4_address_(self, in_ipv4_address):
   if not isinstance(in_ipv4_address, str):
     return False
   try:
     socket.inet_pton(socket.AF_INET, in_ipv4_address)
   except socket.error:
     return False
   return True

 def is_ipv6_address_(self, in_ipv6_address):
   if not isinstance(in_ipv6_address, str):
     return False
   try:
     socket.inet_pton(socket.AF_INET6, in_ipv6_address)
   except socket.error:
     return False
   return True

 def is_ip_address_(self, in_ip_address):
   if self.is_ipv4_address_(in_ip_address):
     return True
   if self.is_ipv6_address_(in_ip_address):
     return True
   return False

