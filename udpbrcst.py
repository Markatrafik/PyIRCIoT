'''
'' PyIRCIoT (PyLayerUDPb class)
''
'' Copyright (c) 2019-2020 Alexey Y. Woronov
''
'' By using this file, you agree to the terms and conditions set
'' forth in the LICENSE file which can be found at the top level
'' of this package
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

# Those Global options override default behavior and memory usage
#
DO_debug_library = False

import socket
import select
import datetime
import threading
import ipaddress
import ifaddr
import ssl
try:
 import json
except:
 import simplejson as json
from queue import Queue
from time import time
from time import sleep
try: # insecure, but for development
 from irciot_shared import *
except:
 from PyIRCIoT.irciot_shared import *

import datetime

if DO_debug_library:
 from pprint import pprint

class PyLayerUDPb( irciot_shared_ ):

 class CONST( irciot_shared_.CONST ):
  #
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.233'
  #
  udpb_default_debug = DO_debug_library
  #
  udpb_default_port = 12345
  udpb_default_ip = ""
  udpb_default_ip_broadcast = '<broadcast>'
  # ^ this is must be a Brodacast IP address of Network interface
  #
  udpb_queue_input  = 0
  udpb_queue_output = 1
  #
  udpb_default_size = 2048 # in bytes
  #
  udpb_first_wait = 1
  udpb_micro_wait = 0.1
  udpb_latency_wait = 1
  udpb_default_wait = 1
  #
  udpb_default_MTU = 1000 # in bytes
  #
  udpb_default_encoding = irciot_shared_.CONST.enc_UTF8
  #
  # 0. Unique User ID
  # 1. User IP address (IPv4 or IPv6)
  # 3. Additional User options
  #
  udpb_default_users = [
   (  1, '10.10.10.1',     None ),
   (  2, '192.168.1.128',  None ),
   (  3, 'fc00::1',        None )  ]
  #
  udpb_default_talk_with_strangers = True
  #
  def __setattr__(self, *_):
    pass

 def __init__(self):
  #
  import os
  #
  self.CONST = self.CONST()
  #
  super(PyLayerUDPb, self).__init__()
  #
  self.__udpb_task = None
  self.udpb_run = False
  self.udpb_debug = self.CONST.udpb_default_debug
  #
  self.udpb_encoding = self.CONST.udpb_default_encoding
  self.udpb_MTU = self.CONST.udpb_default_MTU
  #
  self.udpb_port = self.CONST.udpb_default_port
  self.udpb_ip   = self.CONST.udpb_default_ip
  self.udpb_ip_broadcast = self.CONST.udpb_default_ip_broadcast
  #
  self.udpb_size = self.CONST.udpb_default_size
  #
  self.__udpb_queue = [0, 0]
  self.__udpb_queue[self.CONST.udpb_queue_input  ] = Queue(maxsize=0)
  self.__udpb_queue[self.CONST.udpb_queue_output ] = Queue(maxsize=0)
  #
  self.__udpb_queue_lock = [0, 0]
  self.__udpb_queue_lock[self.CONST.udpb_queue_input  ] = False
  self.__udpb_queue_lock[self.CONST.udpb_queue_output ] = False
  #
  self.udpb_users = self.CONST.udpb_default_users
  self.udpb_anons = []
  #
  self.udpb_local_ip_addresses  = []
  self.udpb_local_ip_broadcasts = []
  #
  self.udpb_talk_with_strangers \
    = self.CONST.udpb_default_talk_with_strangers
  #
  self.__udpb_client_sock = None
  self.__udpb_server_sock = None
  #
  self.__os_name = self.get_os_name_()
  #
  self.udpb_update_local_ip_addresses_()
  #
  self.__delta_time = 0
  #
  # End of PyLayerUDPb.__init__()

 def __del__(self):
  self.stop_udpb_()
  try:
    import signal
    signal.alarm(0)
  except:
    pass

 def to_log_(self, msg):
  if not self.udpb_debug:
    return
  print(msg)

 def irciot_protocol_version_(self):
  return self.CONST.irciot_protocol_version

 def irciot_library_version_(self):
  return self.CONST.irciot_library_version

 def udpb_handler (self, in_compatibility, in_message_pack):
  # Warning: interface may be changed
  (in_protocol, in_library) = in_compatibility
  if not self.irciot_protocol_version_() == in_protocol \
   or not self.irciot_library_version_() == in_library:
    return False
  my_message_pack = in_message_pack
  if isinstance(in_message_pack, tuple):
    my_message_pack = [ in_message_pack ]
  if isinstance(my_message_pack, list):
    for my_pack in my_message_pack:
      (my_message, my_vuid) = my_pack
      self.udpb_add_to_queue_( \
      self.CONST.udpb_queue_output, my_message, \
      self.CONST.udpb_micro_wait, my_vuid)
  return True

 # incomplete
 def user_handler (self, in_compatibility, in_action, in_vuid, in_params):
  # Warning: interface may be changed
  (in_protocol, in_library) = in_compatibility
  if not self.irciot_protocol_version_() == in_protocol \
   or not self.irciot_library_version_() == in_library \
   or not isinstance(in_action, int) \
   or not isinstance(in_vuid, str) \
   or not (isinstance(in_params, str) or in_params == None):
    return (False, None)
  my_vt = None # VUID Type
  my_user = None
  my_anon = None
  my_opt  = None
  if in_vuid in self.CONST.api_vuid_not_srv:
    my_vt = in_vuid
  else:
    my_re = re.search("{}(\d+)".format( \
     self.CONST.api_vuid_cfg), in_vuid)
    if my_re:
      my_vt = self.CONST.api_vuid_cfg
      my_user = self.udpb_cfg_get_user_struct_by_vuid_(in_vuid)
      if my_user != None:
        my_time = self.CONST.api_epoch_maximal
        ( my_uid, my_ip, my_opt ) = my_user
    else:
      my_re = re.search("{}(\d+)".format( \
       self.CONST.api_vuid_tmp), in_vuid)
      if my_re:
        my_vt = self.CONST.api_vuid_tmp
        my_anon = self.udpb_track_get_anons_by_vuid_(in_vuid)
        if my_anon != None:
          ( my_uid, my_ip, my_time ) = my_anon
      else:
        return (False, None)
  if in_action == self.CONST.api_GET_iMTU:
    return (True, self.CONST.udpb_MTU)
  if in_action == self.CONST.api_GET_iENC:
    return (True, self.CONST.udpb_encoding)
  return (False, None)
  #
  # End of user_handler_()

 def udpb_update_local_ip_addresses_(self):
  new_ip_addresses = []
  new_ip_broadcasts = []
  try:
    my_adapters = ifaddr.get_adapters()
    for my_adapter in my_adapters:
      for my_ip in my_adapter.ips:
        if self.is_ipv4_address_(my_ip.ip):
          new_ip_addresses += [ my_ip.ip ]
          my_net = ipaddress.IPv4Network(my_ip.ip \
            + '/{:d}'.format(my_ip.network_prefix), strict = False)
          my_broadcast = '{}'.format(my_net.broadcast_address)
          new_ip_broadcasts += [ my_broadcast ]
          del my_broadcast
          del my_net
        elif isinstance(my_ip.ip, tuple):
          ( my_ipv6, my_ipv6_flowinfo, my_ipv6_scope_id ) = my_ip.ip
          if self.is_ipv6_address_(my_ipv6):
            new_ip_addresses += [ my_ipv6 ]
      if new_ip_addresses != []:
        self.udpb_local_ip_addresses = new_ip_addresses
      if new_ip_broadcasts != []:
        self.udpb_local_ip_broadcasts = new_ip_broadcasts
  except:
    pass
  #
  # End of udpb_update_local_ip_addresses_():

 def udpb_init_by_interface_(self, in_interface, in_ipv6 = False):
  if not isinstance(in_interface, str) \
  or not isinstance(in_ipv6, bool):
    return False
  try:
    my_adapters = ifaddr.get_adapters()
    for my_adapter in my_adapters:
      my_adapter_name = my_adapter.name
      if isinstance(my_adapter_name, bytes):
        my_adapter_name = str(my_adapter_name, self.udpb_encoding)
      if my_adapter_name == in_interface:
        for my_ip in my_adapter.ips:
          if not in_ipv6 and self.is_ipv4_address_(my_ip.ip):
            self.udpb_ip = my_ip.ip
            my_net = ipaddress.IPv4Network(my_ip.ip \
              + '/{:d}'.format(my_ip.network_prefix), strict = False)
            self.udpb_ip_broadcast \
              = '{}'.format(my_net.broadcast_address)
            break
          elif in_ipv6 and isinstance(my_ip.ip, tuple):
            ( my_ipv6, my_ipv6p1, my_ipv6p2 ) = my_ip.ip
            if self.is_ipv6_address_(my_ipv6):
              self.udpb_ip = my_ipv6
              break
  except:
    return False
  return False
  #
  # End of udpb_init_by_interface_()

 def udpb_setup_(self):
  def my_init_socket_(in_af_inet, in_os_name):
    my_sock = socket.socket(in_af_inet, \
      socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if in_os_name == self.CONST.os_windows:
      my_sock.setsockopt(socket.SOL_SOCKET, \
        socket.SO_REUSEADDR, 1)
    else:
      my_sock.setsockopt(socket.SOL_SOCKET, \
        socket.SO_REUSEPORT, 1)
    my_sock.setsockopt(socket.SOL_SOCKET, \
      socket.SO_BROADCAST, 1)
    return my_sock
  if not self.is_ip_address_(self.udpb_ip):
    self.udpb_ip = self.CONST.udpb_default_ip
  if not self.is_ip_port_(self.udpb_port):
    self.udpb_port = self.CONST.udpb_default_port
  if self.is_ipv4_address_(self.udpb_ip):
    my_af_inet = socket.AF_INET
  elif self.is_ipv6_address_(self.udpb_ip):
    my_af_inet = socket.AF_INET6
  elif self.udpb_ip == "":
    my_af_inet = socket.AF_INET
  else:
    return
  self.udpb_update_local_ip_addresses_()
  self.__udpb_client_sock = my_init_socket_(my_af_inet, \
    self.__os_name)
  if self.__os_name == self.CONST.os_windows:
    my_bind_ip = self.udpb_ip
  else:
    my_bind_ip = self.udpb_ip_broadcast
  try:
    self.__udpb_client_sock.bind((my_bind_ip, self.udpb_port))
    self.__udpb_server_sock = my_init_socket_(my_af_inet, self.__os_name)
    self.__udpb_server_sock.settimeout(self.CONST.udpb_default_wait)
  except:
    return
  #
  # End of udpb_setup_()

 def start_udpb_(self):
  self.__udpb_task = threading.Thread(target = self.udpb_process_)
  self.udpb_run  = True
  self.__udpb_task.start()
  #
  # End of start_udpb_()

 def stop_udpb_(self):
  self.udpb_run  = False
  #sleep(self.CONST.udpb_micro_wait)
  #self.udpb_disconnect_()
  if self.__udpb_task != None:
    sleep(self.CONST.udpb_micro_wait)
    try:
      self.__udpb_task.join()
    except:
      pass
  #
  # End of stop_udpb_()

 def udpb_cfg_get_user_struct_by_vuid_(in_vuid):
  for my_user in self.udpb_users:
    ( my_id, my_ip, my_opt ) = my_user
    if in_vuid == "{:s}{:d}".format(self.CONST.api_vuid_cfg, my_id):
      return my_user
  return None

 def udpb_track_get_ip_by_vuid_(self, in_vuid):
  for my_user in self.udpb_users:
    ( my_id, my_ip, my_opt ) = my_user
    if in_vuid == "{:s}{:d}".format(self.CONST.api_vuid_cfg, my_id):
      return my_ip
  for my_anon in self.udpb_anons:
    ( my_id, my_ip, my_time ) = my_anon
    if in_vuid == "{:s}{:d}".format(self.CONST.api_vuid_tmp, my_id):
      return my_ip
  return ""

 def udpb_track_get_vuid_by_ip_(self, in_ip):
  if not self.is_ip_address_(in_ip):
    return None
  for my_user in self.udpb_users:
    ( my_id, my_ip, my_opt ) = my_user
    if in_ip == my_ip:
      return "{:s}{:d}".format(self.CONST.api_vuid_cfg, my_id)
  for my_anon in self.udpb_anons:
    ( my_id, my_ip, my_time ) = my_anon
    if in_ip == my_ip:
      return "{:s}{:d}".format(self.CONST.api_vuid_tmp, my_id)
  return None

 def udpb_track_add_vuid_by_ip_(self, in_ip):
  if not self.is_ip_address_(in_ip):
    return None
  new_id = self.CONST.api_first_temporal_vuid
  for my_anon in self.udpb_anons:
    ( my_id, my_ip, my_time ) = my_anon
    if new_id < my_id:
      new_id = my_id
  my_time = int(time())
  self.udpb_anons.append(( new_id, in_ip, my_time ))
  return "{:s}{:d}".format(self.CONST.api_vuid_tmp, new_id)

 def udpb_track_clear_anons_(self):
  self.udpb_anons = []

 def udpb_check_queue_(self, in_queue_id):
  old_queue_lock = self.__udpb_queue_lock[in_queue_id]
  if not old_queue_lock:
    check_queue = self.__udpb_queue[in_queue_id]
    self.__udpb_queue_lock[in_queue_id] = True
    if not check_queue.empty():
      (udpb_message, udpb_wait, udpb_vuid) = check_queue.get()
      self.__udpb_queue_lock[in_queue_id] = old_queue_lock
      return (udpb_message, udpb_wait, udpb_vuid)
    else:
      if old_queue_lock:
         check_queue.task_done()
    self.__udpb_queue_lock[in_queue_id] = old_queue_lock
  try:
    sleep(self.CONST.udpb_micro_wait)
  except:
    pass
  return ("", self.CONST.udpb_default_wait, self.CONST.api_vuid_all)
  #
  # End of udpb_check_queue_()

 def udpb_add_to_queue_(self, in_queue_id, in_message, in_wait, in_vuid):
  old_queue_lock = self.__udpb_queue_lock[in_queue_id]
  self.__udpb_queue_lock[in_queue_id] = True
  self.__udpb_queue[in_queue_id].put((in_message, in_wait, in_vuid))
  self.__udpb_queue_lock[in_queue_id] = old_queue_lock
  #
  # End of udpb_add_to_queue_()

 # incomplete
 def udpb_receive_(self, recv_timeout):
  if self.__udpb_client_sock == None:
    return ( -1, "", 0, "" )
  try:
    time_in_recv = datetime.datetime.now()
    ready = select.select([self.__udpb_client_sock], [], [], 0)
    my_timerest = recv_timeout
    while ready[0] == [] and my_timerest > 0 and self.udpb_run:
      my_timeout = my_timerest % self.CONST.udpb_latency_wait
      if my_timeout == 0:
        my_timeout = self.CONST.udpb_latency_wait
      ready = select.select([self.__udpb_client_sock], [], [], my_timeout)
      if not self.__udpb_queue[self.CONST.udpb_queue_output].empty():
        break
      my_timerest -= my_timeout
    time_out_recv = datetime.datetime.now()
    delta_time_in = self.td2ms_(time_out_recv - time_in_recv)
    delta_time = self.CONST.udpb_default_wait
    if recv_timeout < self.CONST.udpb_default_wait:
      delta_time = 0
    if delta_time_in < recv_timeout:
      delta_time = recv_timeout - delta_time_in
    if delta_time_in < 0:
      delta_time = 0
    if ready[0] and self.udpb_run:
      my_data, my_addr = self.__udpb_client_sock.recvfrom(self.udpb_size)
      ( my_ip, my_port ) = my_addr
      if not self.is_ip_address_(my_ip) or not self.is_ip_port_(my_port):
        return ( -1, "", 0, "" )
      if my_ip in self.udpb_local_ip_addresses + [ self.udpb_ip ]:
        return ( -1, "", delta_time, "" )
      udpb_input = my_data.decode(self.udpb_encoding)
      udpb_input = udpb_input.strip('\n').strip('\r')
      if udpb_input != "":
        if self.udpb_debug:
          self.to_log_("Received from " \
           + "UDP({}): <{}>".format(my_ip, udpb_input))
        return ( 0, udpb_input, delta_time, my_ip )
      return ( -1, "", delta_time, my_ip )
  except socket.error:
    return ( -1, "", 0, "" )
  except ValueError:
    return ( -1, "", 0, "" )
  return ( 0, "", 0, "" )
  #
  # End of udpb_receive_()

 # incomplete
 def udpb_send_(self, in_string, in_vuid = None):
  if self.__udpb_server_sock == None:
    return False
  if in_vuid == None:
    in_vuid = self.CONST.api_vuid_all
  if not self.is_ip_port_(self.udpb_port):
    return False
  if not isinstance(in_string, str) or not isinstance(in_vuid, str):
    return False
  if in_vuid == self.CONST.api_vuid_all:
    my_addr = self.udpb_ip_broadcast
  elif in_vuid[0] not in self.CONST.api_vuid_any:
    return False
  else:
    my_addr = self.udpb_track_get_ip_by_vuid_(in_vuid)
    if not self.is_ip_address_(my_addr):
      return False
  if self.udpb_debug:
    self.to_log_(self.errors[self.CONST.err_SENDTO] \
     + "UDP({}:{}): <{}>".format(my_addr, self.udpb_port, in_string))
  my_data = bytes(in_string, self.udpb_encoding)
  self.__udpb_server_sock.sendto(my_data, (my_addr, self.udpb_port))
  sleep(self.CONST.udpb_micro_wait)
  return True
  #
  # End of udpb_send_()

 def udpb_output_all_(self, in_messages_packs, in_wait = None):
   if not isinstance(in_messages_packs, list):
     return
   if not isinstance(in_wait, int) and \
      not isinstance(in_wait, float):
     in_wait = self.CONST.udpb_default_wait
   for my_pack in in_messages_packs:
     (my_messages, my_vuid) = my_pack
     if isinstance(my_messages, str):
       my_messages = [ my_messages ]
     if isinstance(my_messages, list):
       for my_message in my_messages:
         self.udpb_add_to_queue_( \
           self.CONST.udpb_queue_output, \
           my_message, in_wait, my_vuid)
   #
   # End of udpb_output_all_()

 # incomplete
 def udpb_process_(self):
   #
   self.udpb_setup_()
   #
   udpb_init = 0
   udpb_wait = self.CONST.udpb_first_wait
   udpb_message = ""
   udpb_ret = 0
   udpb_ip = ""
   udpb_vuid = "{:s}0".format(self.CONST.api_vuid_cfg)
   #
   while (self.udpb_run):
     try:
       if not self.__udpb_client_sock or not self.__udpb_server_sock:
         self.udpb_setup_()
         sleep(self.CONST.udpb_default_wait)

       if udpb_init < 2:
         udpb_init += 1

       if udpb_init > 0:
         ( udpb_ret, udpb_message, self.__delta_time, udpb_ip ) \
           = self.udpb_receive_(udpb_wait)
         if self.is_json_(udpb_message):
           udpb_vuid = self.udpb_track_get_vuid_by_ip_( udpb_ip )
           if udpb_vuid == None:
             udpb_vuid = self.udpb_track_add_vuid_by_ip_( udpb_ip )
           if isinstance(udpb_vuid, str):
             if (self.udpb_talk_with_strangers \
              and udpb_vuid[0] == self.CONST.api_vuid_tmp) \
              or (udpb_vuid[0] in self.CONST.api_vuid_any \
              and udpb_vuid[0] != self.CONST.api_vuid_tmp):
               self.udpb_add_to_queue_(self.CONST.udpb_queue_input, \
                 udpb_message, self.CONST.udpb_default_wait, udpb_vuid)

       udpb_wait = self.CONST.udpb_default_wait

       if self.__delta_time > 0:
         udpb_wait = self.__delta_time

       if udpb_ret == -1:
         udpb_message = ""

       if udpb_init > 1:
         ( udpb_message, udpb_wait, udpb_vuid ) \
           = self.udpb_check_queue_(self.CONST.udpb_queue_output)
         udpb_message = str(udpb_message)
         if udpb_message != "":
           self.udpb_send_(udpb_message, udpb_vuid)
         udpb_message = ""

       sleep(self.CONST.udpb_micro_wait)

     except socket.error:
       udpb_init = 0
       sleep(self.CONST.udpb_default_wait)

   self.udpb_run = False
   #
   # End of udpb_process_()

