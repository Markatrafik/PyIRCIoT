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
import datetime
import threading
import ssl
from queue import Queue
from time import sleep
from irciot_shared import *

import datetime

class PyLayerUDPb( irciot_shared_ ):

 class CONST( irciot_shared_.CONST ):
   #
   irciot_protocol_version = '0.3.31'
   #
   irciot_library_version  = '0.0.181'
   #
   udpb_default_debug = False
   #
   udpb_default_port = 12345
   udpb_default_ip   = ''
   # ^ this is must be a Brodacast IP address of Network interface
   #
   udpb_queue_input  = 0
   udpb_queue_output = 1
   #
   udpb_default_size = 1024 # in bytes
   #
   udpb_first_wait = 1
   udpb_micro_wait = 0.1
   udpb_latency_wait = 1
   udpb_default_wait = 1
   #
   udpb_default_talk_with_strangers = True
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
   self.udpb_queue = [0, 0]
   self.udpb_queue[self.CONST.udpb_queue_input  ] = Queue(maxsize=0)
   self.udpb_queue[self.CONST.udpb_queue_output ] = Queue(maxsize=0)
   #
   self.udpb_queue_lock = [0, 0]
   self.udpb_queue_lock[self.CONST.udpb_queue_input  ] = False
   self.udpb_queue_lock[self.CONST.udpb_queue_output ] = False
   #
   self.udpb_talk_with_strangers \
     = self.CONST.udpb_default_talk_with_strangers
   #
   self.udpb_client_sock = None
   self.udpb_server_sock = None
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
  def my_init_socket_(in_af_inet):
    my_sock = socket.socket(in_af_inet, \
      socket.SOCK_DGRAM, socket.IPPROTO_UDP)
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
  self.udpb_client_sock = my_init_socket_(my_af_inet)
  #try:
  self.udpb_client_sock.bind((self.udpb_ip, self.udpb_port))
  self.udpb_server_sock = my_init_socket_(my_af_inet)
  self.udpb_server_sock.settimeout(self.CONST.udpb_default_wait)
  #except:
  #  return
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
 def udpb_track_get_ip_by_vuid_(self, in_vuid):
  return ""

 # incomplete
 def udpb_track_get_vuid_by_ip_(self, in_ip):
  return self.CONST.api_vuid_all

 def udpb_check_queue_(self, in_queue_id):
  old_queue_lock = self.udpb_queue_lock[in_queue_id]
  if not old_queue_lock:
    check_queue = self.udpb_queue[in_queue_id]
    self.udpb_queue_lock[in_queue_id] = True
    if not check_queue.empty():
      (udpb_message, udpb_wait, udpb_vuid) = check_queue.get()
      self.udpb_queue_lock[in_queue_id] = old_queue_lock
      return (udpb_message, udpb_wait, udpb_vuid)
    else:
      if old_queue_lock:
         check_queue.task_done()
    self.udpb_queue_lock[in_queue_id] = old_queue_lock
  try:
    sleep(self.CONST.udpb_micro_wait)
  except:
    pass
  return ("", self.CONST.udpb_default_wait, self.CONST.api_vuid_all)
  #
  # End of udpb_check_queue_()

 def udpb_add_to_queue_(self, in_queue_id, in_message, in_wait, in_vuid):
  old_queue_lock = self.udpb_queue_lock[in_queue_id]
  self.udpb_queue_lock[in_queue_id] = True
  self.udpb_queue[in_queue_id].put((in_message, in_wait, in_vuid))
  self.udpb_queue_lock[in_queue_id] = old_queue_lock
  #
  # End of udpb_add_to_queue_()

 # incomplete
 def udpb_receive_(self, recv_timeout):
  if self.udpb_client_sock == None:
    return ( -1, "", 0, "" )
  try:
    time_in_recv = datetime.datetime.now()
    ready = select.select([self.udpb_client_sock], [], [], 0)
    my_timerest = recv_timeout
    while ready[0] == [] and my_timerest > 0:
      my_timeout = my_timerest % self.CONST.udpb_latency_wait
      if my_timeout == 0:
        my_timeout = self.CONST.udpb_latency_wait
      ready = select.select([self.udpb_client_sock], [], [], my_timeout)
      if not self.udpb_queue[self.CONST.udpb_queue_output].empty():
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
    if ready[0]:
      my_data, my_addr = self.udpb_client_sock.recvfrom(self.udpb_size)
      ( my_ip, my_port ) = my_addr
      if not self.is_ip_address_(my_ip) or not self.is_ip_port_(my_port):
        return ( -1, "", 0, "" )
      udpb_input = my_data.decode('utf-8')
      udpb_input = udpb_input.strip('\n').strip('\r')
      if udpb_input != "":
        if self.udpb_debug:
          self.to_log_("Received from UDP(%s): <" \
            % my_ip + udpb_input + ">")
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
  if self.udpb_server_sock == None:
    return False
  if in_vuid == None:
    in_vuid = self.CONST.api_vuid_all
  if not self.is_ip_port_(self.udpb_port):
    return False
  if not isinstance(in_string, str) or not isinstance(in_vuid, str):
    return False
  if in_vuid == '*':
    my_addr = '<broadcast>'
  elif in_vuid[0] not in self.CONST.api_vuid_any:
    return False
  else:
    my_addr = self.udpb_track_get_ip_by_vuid_(in_vuid)
    if not self.is_ip_address_(my_ip):
      return False
  if self.udpb_debug:
    self.to_log_("Sending to UDP(%s:%s): <" \
      % (my_addr, self.udpb_port) + in_string + ">")
  my_data = bytes(in_string, 'utf-8')
  self.udpb_server_sock.sendto(my_data, (my_addr, self.udpb_port))
  sleep(self.CONST.udpb_micro_wait)
  return True
  #
  # End of udpb_send_()

 # incomplete
 def udpb_process_(self):
   #
   self.udpb_setup_()
   #
   try:
     udpb_init = 0
     udpb_wait = self.CONST.udpb_first_wait
     udpb_message = ""
     udpb_ret = 0
     udpb_ip = ""
     udpb_vuid = "%s0" % self.CONST.api_vuid_cfg

     while (self.udpb_run):

       if not self.udpb_client_sock or not self.udpb_server_sock:
         self.udpb_setup_()
         sleep(self.CONST.udpb_default_wait)

       if udpb_init < 2:
         udpb_init += 1

       if udpb_init == 1:
         if self.udpb_debug:
           # This is test stuff, must be removed later:
           self.udpb_send_('{"hello":"world!"}')

       if udpb_init > 0:
         ( udpb_ret, udpb_message, self.delta_time, udpb_ip ) \
           = self.udpb_receive_(udpb_wait)
         if self.is_json_(udpb_message):
           udpb_vuid = self.udpb_track_get_vuid_by_ip_( udpb_ip )
           if (self.udpb_talk_with_strangers \
            and udpb_vuid[0] == self.CONST.api_vuid_tmp) \
            or (udpb_vuid[0] in self.CONST.api_vuid_any \
            and udpb_vuid[0] != self.CONST.api_vuid_tmp):
             self.udpb_add_to_queue_(self.CONST.udpb_queue_input, \
               udpb_message, self.CONST.udpb_default_wait, udpb_vuid)

       udpb_wait = self.CONST.udpb_default_wait

       if self.delta_time > 0:
         udpb_wait = self.delta_time

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
   #
   # End of udpb_process_()

