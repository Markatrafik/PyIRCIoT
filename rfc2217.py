'''
'' PyIRCIoT (PyLayerCOM class)
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

import socket
import select
import json
import threading
import pyserial
import ssl
from queue import Queue
from time import sleep
from irciot_shared import *

#from pprint import pprint

import datetime

class PyLayerCOM(irciot_shared_):

 class CONST(object):
   #
   irciot_protocol_version = '0.3.31'
   #
   irciot_library_version  = '0.0.181'
   #
   com_default_debug = False
   #
   com_default_server = "serial.nsk.ru"
   com_default_tcp_port = 2217
   com_default_ssl = False
   #
   com_first_wait = 1
   com_micro_wait = 0.1
   com_default_wait = 1
   #
   api_GET_LMID = 101 # Get Last Message ID
   api_SET_LMID = 102 # Set Last Message ID
   api_GET_OMID = 111 # Get Own last Message ID
   api_SET_OMID = 112 # Set Own last Message ID
   api_GET_EKEY = 301 # Get Encryption Key
   api_SET_EKEY = 302 # Set Encryption Key
   api_GET_EKTO = 351 # Get Encryption Key Timeout
   api_SET_EKTO = 352 # Set Encryption Key Timeout
   api_GET_BKEY = 501 # Get Blockchain key
   api_SET_BKEY = 502 # Set Blockchain Key
   api_GET_BKTO = 551 # Get Blockchain Key Timeout
   api_SET_BKTO = 552 # Set Blockchain Key Timeout
   api_GET_VUID = 700 # Get list of Virtual User IDs
   #
   api_vuid_cfg = 'c' # VUID prefix for users from config
   api_vuid_tmp = 't' # VUID prefix for temporal users
   api_vuid_srv = 's' # VUID prefix for IRC-IoT Services
   api_vuid_all = '*' # Means All users VUIDs when sending messages
   #
   api_vuid_self = 'c0' # Default preconfigured VUID
   #
   # Basic IRC-IoT Services
   #
   api_vuid_CRS = 'sC' # Cryptographic Repository Service
   api_vuid_GDS = 'sD' # Global Dictionary Service
   api_vuid_GRS = 'sR' # Global Resolving Service
   api_vuid_GTS = 'sT' # Global Time Service
   #
   api_vuid_PRS = 'sr' # Primary Routing Service
   #
   com_queue_input  = 0
   com_queue_output = 1
   #
   com_recon_steps  = 8
   #
   com_input_buffer = ""
   #
   com_buffer_size  = 2048
   #
   com_modes = [ "CLIENT", "SERVER" ]
   #
   com_default_mid_pipeline_size = 16
   #
   # According RFC 2217
   #
   # Constants defined by RFC will be here
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   self.com_host = socket.gethostname()
   #
   self.com_server = self.CONST.com_default_server
   self.com_tcp_port = self.CONST.com_default_tcp_port
   self.com_ssl = self.CONST.com_default_ssl
   #
   self.com_status = 0
   self.com_recon = 1
   self.com_last = None
   #
   self.com_servers = [ ( \
     self.com_server, self.com_tcp_port, self.com_ssl, 0, None ) ]
   #
   self.com_queue = [0, 0]
   self.com_queue[self.CONST.com_queue_input]  = Queue(maxsize=0)
   self.com_queue[self.CONST.com_queue_output] = Queue(maxsize=0)
   #
   self.com_queue_lock = [0, 0]
   self.com_queue_lock[self.CONST.com_queue_input]  = False
   self.com_queue_lock[self.CONST.com_queue_output] = False
   #
   self.com_task  = None
   self.com_run   = False
   self.com_debug = self.CONST.com_default_debug
   #
   # Trivial Virtual Users Database (for One User)
   #
   self.lmid = []    # Last Message ID
   self.omid = []    # Own last Message ID
   self.ekey = None  # Encryption Public Key
   self.bkey = None  # Blockchain Public Key
   self.ekto = None  # Encryption Public Key Timeout
   self.bkto = None  # Blockchain Public Key Timeout
   #
   self.time_now   = datetime.datetime.now()
   self.delta_time = 0
   #
   # End of __init__()

 def start_COM_(self):
   #
   self.com_task = threading.Thread(target = self.com_process_)
   self.com_run  = True
   self.com_task.start()
   #
   # End of start_COM_()

 def stop_COM_(self):
   self.com_run = False
   sleep(self.CONST.com_micro_wait)
   #self.com_disconnect_()
   try:
     self.com_task.join()
   except:
     pass
   #
   # End of stop_COM_()

 def __del__(self):
   self.stop_COM_()

 def to_log_(self, msg):
   if not self.com_debug:
     return
   print(msg)

 def irciot_protocol_version_(self):
   return self.CONST.irciot_protocol_version

 def irciot_library_version_(self):
   return self.CONST.irciot_library_version

 def com_handler (self, in_compatibility, in_message_pack):
   # Warning: interface may be changed
   (in_protocol, in_library) = in_compatibility
   if not self.irciot_protocol_version_() == in_protocol \
    or not self.irciot_library_version_() == in_library:
     return False
   try:
     if isinstance(in_message_pack, list):
       for my_pack in in_message_pack:
         (my_message, my_vuid) = my_pack
         self.com_add_to_queue_( \
           self.CONST.com_queue_output, my_message, \
           self.CONST.com_micro_wait, my_vuid)
     else:
       (my_message, my_vuid) = in_message_pack
       self.com_add_to_queue_( \
         self.CONST.com_queue_output, my_message, \
         self.CONST.com_micro_wait, my_vuid)
   except:
     return False
   return True

 def user_handler (self, in_compatibility, in_action, in_vuid, in_params):
   # Warning: interface may be changed
   (in_protocol, in_library) = in_compatibility
   if not self.irciot_protocol_version_() == in_protocol \
    or not self.irciot_library_version_() == in_library \
    or not isinstance(in_action, int) \
    or not isinstance(in_vuid, str) \
    or not (isinstance(in_params, str) \
         or isinstance(in_params, int) \
         or in_params == None):
     return (False, None)
   if in_vuid != self.CONST.api_vuid_cfg:
     return (False, None)
   if   in_action == self.CONST.api_GET_LMID:
     return (True, self.lmid)
   elif in_action == self.CONST.api_SET_LMID:
     if isinstance(in_params, str):
       self.lmid.append(in_params)
       if len(self.lmid) > self.CONST.com_mid_pipeline_size:
         del self.lmid[0]
       return (True, None)
   elif in_action == self.CONST.api_GET_OMID:
     return (True, self.omid)
   elif in_action == self.CONST.api_SET_OMID:
     if isinstance(in_params, str):
       self.omid.append(in_params)
       if len(self.omid) > self.CONST.com_mid_pipeline_size:
         del self.omid[0]
       return (True, None)
   elif in_action == self.CONST.api_GET_VUID:
     return (True, self.CONST.api_vuid_self)
   elif in_action == self.CONST.api_GET_BKEY:
     return (True, self.bkey)
   elif in_action == self.CONST.api_SET_BKEY:
     if isinstance(in_params, str):
       self.bkey = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_BKTO:
     return (True, self.bkto)
   elif in_action == self.CONST.api_SET_BKTO:
     if isinstance(in_params, int):
       self.bkto = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_EKEY:
     return (True, self.ekey)
   elif in_action == self.CONST.api_SET_EKEY:
     if isinstance(in_params, str):
       self.ekey = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_EKTO:
     return (True, self.ekto)
   elif in_action == self.CONST.api_SET_EKTO:
     if isinstance(jn_params, int):
       self.ekto = in_params
     return (True, None)
   return (False, None)
   #
   # End of user_handler_()

 def com_quit_(self):
   pass
   #
   # End of com_quit_()

 def com_disconnect_(self):
   pass
   #
   # End of com_disconnect_()

 def com_reconnect_(self):
   if not self.com_run:
     return
   self.com_disconnect_()
   self.to_log_("Connection closed, " \
    + "reconnecting to Serial over Network (try: %d) ... " \
     % self.com_recon)
   # sleep(self.CONST.com_first_wait * self.com_recon)
   self.com_recon += 1
   if self.com_recon > self.CONST.com_recon_steps:
     self.com_recon = 1

 def com_send_(self, com_out):
   try:
     if com_out == "":
       return -1
     if self.com_debug:
       self.to_log_("Sending to Serial over Network: [" + com_out + "]")
     #self.com_send(bytes(com_out + "\n", 'utf-8'))
     sleep(self.CONST.com_micro_wait)
     com_out = ""
     return 0
   except socket.error:
     self.to_log_("socket.error in com_send_() ...")
     return -1
   except ValueError:
     self.to_log_("ValueError in com_send_() ...")
     return -1
   #
   # End of com_send_()

 def com_connect_(self, com_server, com_port):
   # self.com_connect((com_server, com_port))
   # self.com_setblocking(False)
   pass

 def com_check_queue_(self, queue_id):
   old_queue_lock = self.com_queue_lock[queue_id]
   if not old_queue_lock:
     check_queue = self.com_queue[queue_id]
     self.com_queue_lock[queue_id] = True
     if not check_queue.empty():
       (com_message, com_wait, com_vuid) = check_queue.get()
       self.com_queue_lock[queue_id] = old_queue_lock
       return (com_message, com_wait, com_vuid)
     else:
       if old_queue_lock:
          check_queue.task_done()
     self.com_queue_lock[queue_id] = old_queue_lock
   try:
     sleep(self.CONST.com_micro_wait)
   except:
     pass
   return ("", self.CONST.com_default_wait, self.CONST.api_vuid_all)
   #
   # End of com_check_queue_()

 def com_add_to_queue_(self, in_queue_id, in_message, in_wait, in_vuid):
   old_queue_lock = self.com_queue_lock[in_queue_id]
   self.com_queue_lock[in_queue_id] = True
   self.com_queue[in_queue_id].put((in_message, in_wait, in_vuid))
   self.com_queue_lock[in_queue_id] = old_queue_lock

 def com_output_all_(self, in_messages_packs, in_wait = None):
   if not isinstance(in_messages_packs, list):
     return
   if not isinstance(in_wait, int) and \
      not isinstance(in_wait, float):
     in_wait = self.CONST.com_default_wait
   for my_pack in in_messages_packs:
     (my_messages, my_vuid) = my_pack
     if isinstance(my_messages, str):
       self.com_add_to_queue_( \
         self.CONST.com_queue_output, \
         my_messages, in_wait, my_vuid)
     elif isinstance(my_messages, list):
       for my_message in my_messages:
         self.com_add_to_queue_( \
           self.CONST.com_queue_output, \
           my_message, in_wait, my_vuid)
   #
   # End of com_output_all_()

 # SERVICE Hooks:

 def init_rfc2217_(self):
   #
   C = self.CONST
   #
   # End of init_rfc2217

 def com_process_(self):
   #
   self.init_rfc2217_()
   #
   try:
     com_init = 0
     com_wait = self.CONST.com_first_wait
     com_input_buffer = ""
     com_ret = 0
     com_vuid = "%s0" % self.CONST.api_vuid_cfg

     self.delta_time = 0

     # app.run(host='0.0.0.0', port=50000, debug=True)
     # must be FIXed for Unprivileged user

     while (self.com_run):

       if not self.com:
         sleep(self.CONST.com_first_wait)
         # self.com = self.irc_socket_()
         com_init = 0

       if com_init < 2:
         com_init += 1

       if irc_init == 1:
         try:
           self.com_connect_(self.com_server, self.tcp_port)
         except:
           self.com_disconnect_()
           # self.com = self.com_socket_()
           irc_init = 0

       sleep(self.CONST.com_micro_wait)

   except socket.error:
     self.com_disconnect()
     com_init = 0
   #
   # End of com_process_()

