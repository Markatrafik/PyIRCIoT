'''
'' PyIRCIoT
''
'' Copyright (c) 2018 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>

import socket
import select
import json
import random
import re
import threading
from queue import Queue
from time import sleep

#from pprint import pprint

import datetime

class PyLayerIRC(object):

 class CONST(object):
   #
   irc_first_wait = 30
   irc_micro_wait = 0.15
   irc_default_wait = 30
   #
   irc_default_port = 6667
   irc_default_server = "irc-iot.nsk.ru"
   irc_default_nick = "MyBot"
   irc_default_info = "IRC-IoT Bot"
   irc_default_channel = "#myhome"
   irc_default_uplink_nick = "iotBot"
   #
   irc_queue_input  = 0
   irc_queue_output = 1
   #
   irc_input_buffer = ""
   #
   irc_buffer_size = 2048
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   self.irc_host = socket.gethostname()
   self.irc_nick = self.CONST.irc_default_nick
   self.irc_info = self.CONST.irc_default_info
   self.irc_port = self.CONST.irc_default_port
   self.irc_server = self.CONST.irc_default_server
   self.irc_channel = self.CONST.irc_default_channel
   self.irc_uplink_nick = self.CONST.irc_default_uplink_nick
   #
   self.irc_queue = [0, 0]
   self.irc_queue[self.CONST.irc_queue_input]  = Queue(maxsize=0)
   self.irc_queue[self.CONST.irc_queue_output] = Queue(maxsize=0)
   #
   self.irc_queue_lock = [0, 0]
   self.irc_queue_lock[self.CONST.irc_queue_input]  = False
   self.irc_queue_lock[self.CONST.irc_queue_output] = False
   #
   self.irc_task  = None
   self.irc_run   = False
   self.irc_debug = False
   #
   # End of __init__()

 def start_IRC_(self):
   #
   self.irc_task = threading.Thread(target = self.irc_process_)
   self.irc_run  = True
   self.irc_task.start()
   #
   # End of start_IRC_()
   
 def stop_IRC_(self):
   #
   self.irc_run = False
   sleep(self.CONST.irc_micro_wait)
   self.irc_disconnect_()
   #
   try:
     self.irc_task.join()
   except:
     pass
   #
   # End of stop_IRC_()
   
 def __del__(self):
   self.stop_IRC_()
   
 def to_log_(self, msg):
   print(msg)

 def check_irc_mask_(self, irc_from, irc_mask):
   return True
  
 def check_all_masks_(self, irc_from):
   return True
   
 def is_json_(self, test_message):
   try:
     json_object = json.loads(test_message)
   except ValueError:
     return False
   return True

 def irc_disconnect_(self):
   try:
     self.irc.shutdown()
   except:
     pass
   self.irc.close()
  
 def irc_reconnect_(self):
   self.irc_disconnect_()
   if (self.irc_debug):
     self.to_log_("Connection closed, reconnecting to IRC ... ")
   sleep(self.CONST.irc_first_wait)
   
 def irc_td2ms_(self, td):
   return td.days * 86400 + td.seconds + td.microseconds / 1000000

 def irc_send_(self, irc_out):
   try:
     if (irc_out == ""):
       return
     if (self.irc_debug):
       self.to_log_("Sending to IRC: [" + irc_out + "]")
     self.irc.send(bytes(irc_out + "\n", "UTF-8"))
     sleep(self.CONST.irc_micro_wait)
     irc_out = ""
     return 0
   except socket.error:
     if (self.irc_debug):
       self.to_log_("socket.error in irc_send_() ...")
     return -1
   except ValueError:
     if (self.irc_debug):
       self.to_log_("ValueError in irc_send_() ...")
     return -1
   #
   # End of irc_send_()
   
 def irc_recv_(self, recv_timeout):
   try:
     time_in_recv = datetime.datetime.now()
     ready = select.select([self.irc], [], [], recv_timeout)
     time_out_recv = datetime.datetime.now()
     delta_time_in = self.irc_td2ms_(time_out_recv - time_in_recv)
     delta_time = self.CONST.irc_default_wait
     if (recv_timeout < self.CONST.irc_default_wait):
       delta_time = 0
     if (delta_time_in < recv_timeout):
       delta_time = recv_timeout - delta_time_in
     if (delta_time_in < 0):
       delta_time = 0
     if ready[0]:
       irc_input \
        = self.irc.recv(self.CONST.irc_buffer_size).decode("UTF-8")
       irc_input = irc_input.strip("\n")
       irc_input = irc_input.strip("\r")
       if (irc_input != ""):
         if (self.irc_debug):
           self.to_log_("Received from IRC: [" + irc_input + "]")
         return (0, irc_input, delta_time)
       return (-1, "", delta_time)
     return (0, "", delta_time)
   except socket.error:
     return (-1, "", 0)
   except ValueError:
     return (-1, "", 0)
   #
   # End of irc_recv_()

 def irc_pong_(self, irc_input):
   irc_string = irc_input.split(":")
   ret = self.irc_send_("PONG %s\r\n" % irc_string[1])
   return ret
   
 def irc_quit_(self):
   ret = self.irc_send_("QUIT :Bye!\r\n")
   return ret
  
 def irc_random_nick_(self, irc_nick):
   random.seed()
   ret = self.irc_send_(irc, "NICK " + irc_nick + "%s" \
    % random.randint(100, 999))
   return ret
  
 def irc_connect_(self, irc_server, irc_port):
   self.irc.connect((irc_server, irc_port))
   # self.irc.setblocking(False)
   
 def irc_check_queue_(self, queue_id):
   old_queue_lock = self.irc_queue_lock[queue_id]
   if not old_queue_lock:
     check_queue = self.irc_queue[queue_id]
     self.irc_queue_lock[queue_id] = True
     if not check_queue.empty():
       (irc_message, irc_wait) = check_queue.get()
       self.irc_queue_lock[queue_id] = old_queue_lock
       return (irc_message, irc_wait)
     else:
       if old_queue_lock:
          check_queue.task_done()
     self.irc_queue_lock[queue_id] = old_queue_lock
   try:
     sleep(self.CONST.irc_micro_wait)
   except:
     pass
   return ("", self.CONST.irc_default_wait)

 def irc_add_to_queue_(self, queue_id, irc_message, irc_wait = 0):
   old_queue_lock = self.irc_queue_lock[queue_id]
   self.irc_queue_lock[queue_id] = True
   self.irc_queue[queue_id].put((irc_message, irc_wait))
   self.irc_queue_lock[queue_id] = old_queue_lock
   
 def irc_process_(self):

   try:
     irc_init = 0
     irc_wait = self.CONST.irc_first_wait
     irc_input_buffer = ""
     irc_ret = 0
     delta_time = 0

     # app.run(host='0.0.0.0', port=50000, debug=True)
     # must be FIXed for Unprivileged user

     try:     
       self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     except:
       to_log_("Cannot create socket for IRC")

     while (self.irc_run):

       if (irc_init < 6):
         irc_init += 1
     
       if (irc_init == 1):
         try:
           self.irc_connect_(self.irc_server, self.irc_port)
         except socket.error:
           self.irc_disconnect_()
           self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           irc_init = 0

       elif (irc_init == 2):
         if (self.irc_send_("USER " + self.irc_nick + " " \
          + self.irc_host + " 1 :" + self.irc_info) == -1):
           irc_init = 0

       elif (irc_init == 3):
         if (self.irc_send_("NICK " + self.irc_nick) == -1):
           irc_init = 0

       elif (irc_init == 4):
         irc_wait = self.CONST.irc_default_wait
         if (self.irc_send_("JOIN " + self.irc_channel) == -1):
           irc_init = 0
           
       elif (irc_init == 5):
         irc_wait = self.CONST.irc_default_wait
         if (self.irc_send_("JOIN " + self.irc_channel + "\r\n") == -1):
           irc_init = 0
   
       if (irc_init > 0):
         (irc_ret, irc_input_buffer, delta_time) \
          = self.irc_recv_(irc_wait)
       irc_wait = self.CONST.irc_default_wait
       if (delta_time > 0):
         irc_wait = delta_time
    
       if (irc_ret == -1):
         self.irc_reconnect_()
         irc_input_buffer = ""
         irc_init = 0
         self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
       irc_prefix = ":" + self.irc_server + " "
       irc_prefix_len = len(irc_prefix)
   
       for irc_input_split in re.split(r'[\r\n]', irc_input_buffer):
     
         irc_input_command \
          = irc_input_split[irc_prefix_len:irc_prefix_len + 10]
     
         if irc_input_split[:5] == "PING ":
           if (self.irc_pong_(irc_input_split) == -1):
             irc_ret = -1
             irc_init = 0

         if irc_input_command[:4] == "433 ":
           if (self.irc_random_nick_(self.irc_nick) == 1):
             irc_ret = -1
             irc_init = 0
       
         if irc_input_split[:6] == "ERROR ":
           irc_init = 1
           irc_wait = self.CONST.irc_default_wait
           if (irc_input_split.find("Closing ") \
            or irc_input_split.find(" timeout")):
             irc_ret = -1
             irc_init = 0

         if irc_input_command[:4] == "451 ":
           irc_init = 1
           irc_wait = self.CONST.irc_default_wait

         if irc_input_split.find(" KICK ") != -1:
           irc_init = 3
           irc_wait = self.CONST.irc_default_wait
         
         if irc_input_split[:4] == "474 ":
           irc_init = 3
           irc_wait = self.CONST.irc_default_wait
 
         if (irc_input_split.find(" PRIVMSG ") != -1) \
          or (irc_input_split == ""):

           irc_name = ""
           irc_message = None
        
           if (irc_input_split != ""):
             irc_name = irc_input_split.split('!',1)[0][1:]
             time_now = datetime.datetime.now()
             irc_message = irc_input_split.split('PRIVMSG',1)[1].split(':',1)[1]
             irc_message = irc_message.strip()
       
           if ((irc_message == None) and (irc_input_buffer == "")):
             time_now = datetime.datetime.now()
             irc_message = ""

           if ((irc_name == self.irc_uplink_nick) and (irc_init > 3) \
            and (self.is_json_(irc_message))):
         
             self.irc_add_to_queue_(self.CONST.irc_queue_input, irc_message, 0)
           
           irc_input_split = ""

         irc_input_buff = ""
       
       if (irc_init > 5):
          (irc_message, irc_wait) \
           = self.irc_check_queue_(self.CONST.irc_queue_output)
          if (irc_message != ""):
             self.irc_send_("PRIVMSG " + self.irc_channel + " :" + irc_message)
          irc_message = ""    
      
   except socket.error:
     self.irc_disconnect()
     irc_init = 0
   #
   # End of irc_process_()

