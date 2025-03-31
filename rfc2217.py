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

# Those Global options override default behavior and memory usage
#
DO_debug_library = False

import socket
import select
import threading
import serial
import ssl
try:
 import json
except:
 import simplejson as json
from queue import Queue
from time import sleep
try: # insecure, but for development
 from irciot_shared import *
except:
 from PyIRCIoT.irciot_shared import *

if DO_debug_library:
 from pprint import pprint

import datetime

class PyLayerCOM( irciot_shared_ ):

 class CONST( irciot_shared_.CONST ):
   #
   irciot_protocol_version = '0.3.33'
   #
   irciot_library_version  = '0.0.235'
   #
   com_default_debug = DO_debug_library
   #
   com_default_server = "serial.nsk.ru"
   com_default_tcp_port = 2217
   com_default_ssl = False
   #
   com_default_baud_rate = 9600
   com_default_rtscts  = False
   com_default_xonxoff = False
   com_default_RTS = False
   com_default_DTR = False
   #
   com_parity_NONE = 'N'
   com_parity_EVEN = 'E'
   com_parity_ODD  = 'O'
   com_parity_all  = [
    com_parity_NONE,
    com_parity_EVEN,
    com_parity_ODD ]
   #
   com_default_parity = com_parity_NONE
   #
   com_first_wait = 1
   com_micro_wait = 0.1
   com_default_wait = 1
   #
   com_queue_input  = 0
   com_queue_output = 1
   #
   com_recon_steps  = 8
   #
   com_input_buffer = ""
   #
   com_buffer_size  = 3072
   #
   com_default_mid_pipeline_size = 16
   #
   com_default_MTU = 500
   #
   com_mode_CLIENT = "CLIENT"
   # ^ Connecting to remote virtual COM port using RFC2217 protocol
   com_mode_SERVER = "SERVER"
   # ^ Accepting connections to virtual COM port by RFC2217 protocol
   com_modes = [ com_mode_CLIENT, com_mode_SERVER ]
   com_default_mode = com_mode_CLIENT
   #
   com_default_encoding = irciot_shared_.CONST.enc_UTF8
   #
   # According RFC 2217
   #
   cmd_SET_BAUDRATE = b'\x01'
   cmd_SET_DATASIZE = b'\x02'
   cmd_SET_PARITY   = b'\x03'
   cmd_SET_STOPSIZE = b'\x04'
   cmd_SET_CONTROL  = b'\x05'
   cmd_NOTIFY_LINESTATE  = b'\x06'
   cmd_NOTIFY_MODEMSTATE = b'\x07'
   cmd_FLOWCONTROL_SUSPEND = b'\x08'
   cmd_FLOWCONTROL_RESUME  = b'\x09'
   cmd_SET_LINESTATE_MASK  = b'\x0a'
   cmd_SET_MODEMSTATE_MASK = b'\x0b'
   cmd_PURGE_DATA   = b'\x0c'
   #
   rpl_SET_BAUDRATE = b'\x65'
   rpl_SET_DATASIZE = b'\x66'
   rpl_SET_PARITY   = b'\x67'
   rpl_SET_STOPSIZE = b'\x68'
   rpl_SET_CONTROL  = b'\x69'
   rpl_NOTIFY_LINESTATE  = b'\x6a'
   rpl_NOTIFY_MODEMSTATE = b'\x6b'
   rpl_FLOWCONTROL_SUSPEND = b'\x6c'
   rpl_FLOWCONTROL_RESUME  = b'\x6d'
   rpl_SET_LINESTATE_MASK  = b'\x6e'
   rpl_SET_MODEMSTATE_MASK = b'\x6f'
   rpl_PURGE_DATA   = b'\x70'
   #
   map_RFC2217_cmd_rpl = {
    cmd_SET_BAUDRATE : rpl_SET_BAUDRATE,
    cmd_SET_DATASIZE : rpl_SET_DATASIZE,
    cmd_SET_PARITY   : rpl_SET_PARITY,
    cmd_SET_STOPSIZE : rpl_SET_STOPSIZE,
    cmd_SET_CONTROL  : rpl_SET_CONTROL,
    cmd_NOTIFY_LINESTATE  : rpl_NOTIFY_LINESTATE,
    cmd_NOTIFY_MODEMSTATE : rpl_NOTIFY_MODEMSTATE,
    cmd_FLOWCONTROL_SUSPEND : rpl_FLOWCONTROL_SUSPEND,
    cmd_FLOWCONTROL_RESUME  : rpl_FLOWCONTROL_RESUME,
    cmd_SET_LINESTATE_MASK  : rpl_SET_LINESTATE_MASK,
    cmd_SET_MODEMSTATE_MASK : rpl_SET_MODEMSTATE_MASK,
    cmd_PURGE_DATA   : rpl_PURGE_DATA
   }
   #
   # Telnet codes:
   #
   tel_SE   = b'\xf0' # Subnegotiation End
   tel_NOP  = b'\xf1' # No Operation
   tel_DM   = b'\xf2' # Data Mark
   tel_BRK  = b'\xf3' # Break
   tel_IP   = b'\xf4' # Interrupt Process
   tel_AO   = b'\xf5' # Abort Output
   tel_AYT  = b'\xf6' # Are You There
   tel_EC   = b'\xf7' # Erase Character
   tel_EL   = b'\xf8' # Erase Line
   tel_GA   = b'\xf9' # Go Ahead
   tel_SB   = b'\xfa' # Subnegotiation Begin
   tel_WILL = b'\xfb' #
   tel_WONT = b'\xfc' #
   tel_DO   = b'\xfd' #
   tel_DONT = b'\xfe' #
   tel_IAC  = b'\xff' # Interpret As Command
   tel_2IAC = b'\xff\xff'
   #
   err_SERIALOVERNET  = 3008
   #
   err_DESCRIPTIONS = irciot_shared_.CONST.err_DESCRIPTIONS
   err_DESCRIPTIONS.update({
    err_SERIALOVERNET  : "Serial over Network"
   })
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   self.__com_sock = None
   self.__com_task = None
   #
   super(PyLayerCOM, self).__init__()
   #
   self.com_encoding = self.CONST.com_default_encoding
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
   self.com_baud_rate = self.CONST.com_default_baud_rate
   self.com_rtscts  = self.CONST.com_default_rtscts
   self.com_xonxoff = self.CONST.com_default_xonxoff
   self.com_RTS = self.CONST.com_default_RTS
   self.com_DTR = self.CONST.com_default_DTR
   self.com_parity  = self.CONST.com_default_parity
   #
   self.com_servers = [ ( \
     self.com_server, self.com_tcp_port, self.com_ssl, 0, None ) ]
   #
   self.__com_queue = [0, 0]
   self.__com_queue[self.CONST.com_queue_input]  = Queue(maxsize=0)
   self.__com_queue[self.CONST.com_queue_output] = Queue(maxsize=0)
   #
   self.__com_queue_lock = [0, 0]
   self.__com_queue_lock[self.CONST.com_queue_input]  = False
   self.__com_queue_lock[self.CONST.com_queue_output] = False
   #
   self.__com_mode = self.CONST.com_default_mode
   #
   self.__com_run = False
   self.com_debug = self.CONST.com_default_debug
   #
   self.com_MTU = self.CONST.com_default_MTU
   #
   # Trivial Virtual Users Database (for One User)
   #
   self.__lmid = []   # Last Message ID
   self.__omid = []   # Own last Message ID
   self.__ekey = None # Encryption Public Key
   self.__bkey = None # Blockchain Public Key
   self.__ekto = None # Encryption Public Key Timeout
   self.__bkto = None # Blockchain Public Key Timeout
   #
   self.time_now   = datetime.datetime.now()
   self.__delta_time = 0
   #
   self.lang = self.CONST.hl_default
   #
   self.errors = self.CONST.err_DESCRIPTIONS
   #
   self.irciot_set_locale_(self.lang)
   #
   # End of __init__()

 def set_COM_mode_(self, in_mode):
   if in_mode not in self.com_modes:
     return False
   if self.__com_run:
     return False
   self.__com_mode = in_mode
   return True

 def is_COM_runned_(self):
   return self.__com_run

 def start_COM_(self):
   #
   if self.__com_mode == self.CONST.com_mode_CLIENT:
     my_target = self.com_process_client_
   elif self.__com_mode == self.CONST.com_mode_SERVER:
     my_target = self.com_process_server_
   else:
     return
   self.__com_task = threading.Thread(target = my_target)
   self.__com_run  = True
   self.__com_task.start()
   #
   # End of start_COM_()

 def stop_COM_(self):
   self.__com_run = False
   #sleep(self.CONST.com_micro_wait)
   #self.com_disconnect_()
   if self.__com_task != None:
     sleep(self.CONST.com_micro_wait)
     try:
       self.__com_task.join()
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

 def com_set_parity_(in_parity):
   if in_parity not in self.CONST.com_parity_all:
     return False
   self.com_parity = in_parity
   return True

 def com_handler (self, in_compatibility, in_message_pack):
   # Warning: interface may be changed
   (in_protocol, in_library) = in_compatibility
   if not self.irciot_protocol_version_() == in_protocol \
    or not self.irciot_library_version_() == in_library:
     return False
   try:
     if isinstance(in_message_pack, tuple):
       in_message_pack = [ in_message_pack ]
     if isinstance(in_message_pack, list):
       for my_pack in in_message_pack:
         (my_message, my_vuid) = my_pack
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
     return (True, self.__lmid)
   elif in_action == self.CONST.api_SET_LMID:
     if isinstance(in_params, str):
       self.__lmid.append(in_params)
       if len(self.__lmid) > self.CONST.com_mid_pipeline_size:
         del self.__lmid[0]
       return (True, None)
   elif in_action == self.CONST.api_GET_OMID:
     return (True, self.__omid)
   elif in_action == self.CONST.api_SET_OMID:
     if isinstance(in_params, str):
       self.__omid.append(in_params)
       if len(self.__omid) > self.CONST.com_mid_pipeline_size:
         del self.__omid[0]
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
     return (True, self.__bkto)
   elif in_action == self.CONST.api_SET_BKTO:
     if isinstance(in_params, int):
       self.__bkto = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_EKEY:
     return (True, self.__ekey)
   elif in_action == self.CONST.api_SET_EKEY:
     if isinstance(in_params, str):
       self.__ekey = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_EKTO:
     return (True, self.__ekto)
   elif in_action == self.CONST.api_SET_EKTO:
     if isinstance(jn_params, int):
       self.__ekto = in_params
     return (True, None)
   elif in_action == self.CONST.api_GET_iMTU:
     return (True, self.com_MTU)
   elif in_action == self.CONST.api_GET_iENC:
     return (True, self.com_encoding)
   return (False, None)
   #
   # End of user_handler_()

 def irciot_set_locale_(self, in_lang):
   if not isinstance(in_lang, str):
     return
   self.lang = in_lang
   my_desc = {}
   try:
     from PyIRCIoT.irciot_errors \
     import irciot_get_common_error_descriptions_
     my_desc = irciot_get_common_error_descriptions_(in_lang)
     my_dsec = self.validate_descriptions_(my_desc)
     if my_desc != {}:
       self.errors.update(my_desc)
   except:
     pass
   my_desc = {}
   try:
     from PyIRCIoT.irciot_errors \
     import irciot_get_rfc2217_error_descriptions_
     my_desc = irciot_get_rfc2217_error_descriptions_(in_lang)
     my_desc = self.validate_descriptions_(my_desc)
     if my_desc != {}:
       self.errors.update(my_desc)
   except:
     pass

 # incomplete
 def com_quit_(self):
   pass
   #
   # End of com_quit_()

 # incomplete
 def com_socket_(self):
   return None
   #
   # End of com_socket_()

 # incomplete
 def com_disconnect_(self):
   pass
   #
   # End of com_disconnect_()

 # incomplete
 def com_reconnect_(self):
   if not self.__com_run:
     return
   self.com_disconnect_()
   self.to_log_(self.errors[self.CONST.err_CLOSED] + ", " \
    + self.errors[self.CONST.err_RECONN] \
    + self.errors[self.CONST.err_SERIALOVERNET] \
    + self.errors[self.CONST.err_TRY].format( \
     self.com_recon) + " ...")
   sleep(self.CONST.com_first_wait * self.com_recon)
   self.com_recon += 1
   if self.com_recon > self.CONST.com_recon_steps:
     self.com_recon = 1

 # incomplete
 def com_send_(self, com_out):
   try:
     if com_out == "":
       return -1
     if self.com_debug:
       self.to_log_(self.errors[self.CONST.err_SENDTO] \
        + self.errors[self.CONST.err_SERIALOVERNET] \
        + ": [{}]".format(com_out))
     #self.com_send(bytes(com_out + "\n", self.com_encoding))
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

 # incomplete
 def com_connect_(self, com_server, com_port):
   # self.com_connect((com_server, com_port))
   # self.com_setblocking(False)
   pass

 def com_check_queue_(self, queue_id):
   old_queue_lock = self.__com_queue_lock[queue_id]
   if not old_queue_lock:
     check_queue = self.__com_queue[queue_id]
     self.__com_queue_lock[queue_id] = True
     if not check_queue.empty():
       (com_message, com_wait, com_vuid) = check_queue.get()
       self.__com_queue_lock[queue_id] = old_queue_lock
       return (com_message, com_wait, com_vuid)
     else:
       if old_queue_lock:
         check_queue.task_done()
     self.__com_queue_lock[queue_id] = old_queue_lock
   try:
     sleep(self.CONST.com_micro_wait)
   except:
     pass
   return ("", self.CONST.com_default_wait, self.CONST.api_vuid_all)
   #
   # End of com_check_queue_()

 def com_add_to_queue_(self, in_queue_id, in_message, in_wait, in_vuid):
   old_queue_lock = self.__com_queue_lock[in_queue_id]
   self.__com_queue_lock[in_queue_id] = True
   self.__com_queue[in_queue_id].put((in_message, in_wait, in_vuid))
   self.__com_queue_lock[in_queue_id] = old_queue_lock

 def com_output_all_(self, in_messages_packs, in_wait = None):
   if not isinstance(in_messages_packs, list):
     return
   if not isinstance(in_wait, int) and \
      not isinstance(in_wait, float):
     in_wait = self.CONST.com_default_wait
   for my_pack in in_messages_packs:
     (my_messages, my_vuid) = my_pack
     if isinstance(my_messages, str):
       my_messages = [ my_messages ]
     if isinstance(my_messages, list):
       for my_message in my_messages:
         self.com_add_to_queue_( \
           self.CONST.com_queue_output, \
           my_message, in_wait, my_vuid)
   #
   # End of com_output_all_()

 # incomplete
 def com_socket_(self):
   return None

 # incomplete
 def init_rfc2217_(self):
   #
   C = self.CONST
   #
   # End of init_rfc2217

 # incomplete
 def com_process_server_(self):
   ''' Accepting connections to virtual COM port using RFC2217 protocol '''
   #
   self.init_rfc2217_()
   #
   try:
     com_init = 0
     com_wait = self.CONST.com_first_wait
     com_input_buffer = ""
     com_ret = 0
     com_vuid = "{:s}0".format(self.CONST.api_vuid_cfg)

     while (self.__com_run):

       if not self.__com_sock:
         sleep(self.CONST.com_first_wait)
         self.__com_sock = self.com_socket_()
         com_init = 0

       if com_init < 2:
         com_init += 1

       sleep(self.CONST.com_micro_wait)

   except:
     self.com_disconnect()
   self.__com_run = False
   #
   # End of com_process_server_()

 # incomplete
 def com_process_client_(self):
   ''' Connecting to remote virtual COM port using RFC2217 protocol '''
   #
   self.init_rfc2217_()
   #
   com_init = 0
   com_wait = self.CONST.com_first_wait
   com_input_buffer = ""
   com_ret = 0
   com_vuid = "{:s}0".format(self.CONST.api_vuid_cfg)

   self.__delta_time = 0

   # app.run(host='0.0.0.0', port=50000, debug=True)
   # must be FIXed for Unprivileged user

   while (self.__com_run):

     try:

       if not self.__com_sock:
         sleep(self.CONST.com_first_wait)
         self.__com_sock = self.com_socket_()
         com_init = 0

       if com_init < 2:
         com_init += 1

       if com_init == 1:
         try:
           self.com_connect_(self.com_server, self.tcp_port)
         except:
           self.com_disconnect_()
           # self.__com_sock = self.com_socket_()
           com_init = 0

       sleep(self.CONST.com_micro_wait)

     except socket.error:
       self.com_disconnect()
       self.__com_sock = None

   self.__com_run = False
   #
   # End of com_process_client_()

