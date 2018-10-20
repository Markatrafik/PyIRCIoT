'''
'' PyIRCIoT (PyLayerIRC class)
''
'' Copyright (c) 2018 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

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
   irciot_protocol_version_compatible = '0.3.10'
   #
   irciot_library_version_compatible  = '0.0.28'
   #
   # Bot specific constants
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
   # Temporal:
   irc_default_uplink_nick = "iotBot"
   irc_default_uplink_nick2 = "FaceBot"
   #
   irc_queue_input  = 0
   irc_queue_output = 1
   #
   irc_input_buffer = ""
   #
   irc_buffer_size = 2048
   #
   irc_modes = { "CLIENT", "SERVICE", "SERVER" }
   #
   # According RFC 1459
   #
   irc_ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
   irc_ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
   irc_ascii_letters = irc_ascii_lowercase + irc_ascii_uppercase
   irc_ascii_digits = "0123456789"
   irc_special_chars = "-[]\\`^{}"
   irc_nick_chars = irc_ascii_letters \
     + irc_ascii_digits + irc_special_chars
   irc_translation = "".maketrans( \
     irc_ascii_uppercase + "[]\\^",
     irc_ascii_lowercase + "{}|~")
   #
   code_WELCOME           = "001"
   code_YOURHOST          = "002"
   code_CREATED           = "003"
   code_MYINFO            = "004"
   code_FEATURELIST       = "005"
   code_TRACELINK         = "200"
   code_TRACECONNECTING   = "201"
   code_TRACEHANDSHAKE    = "202"
   code_TRACEUNKNOWN      = "203"
   code_TRACEOPERATOR     = "204"
   code_TRACEUSER         = "205"
   code_TRACESERVER       = "206"
   code_TRACESERVICE      = "207"
   code_TRACENEWTYPE      = "208"
   code_TRACECLASS        = "209"
   code_TRACERECONNECT    = "210"
   code_STATSLINKINFO     = "211"
   code_STATSCOMMANDS     = "212"
   code_STATSCLINE        = "213"
   code_STATSNLINE        = "214"
   code_STATSILINE        = "215"
   code_STATSKLINE        = "216"
   code_STATSQLINE        = "217"
   code_STATSYLINE        = "218"
   code_ENDOFSTATS        = "219"
   code_UMODEIS           = "221"
   code_SERVICEINFO       = "231"
   code_ENDOFSERVICES     = "232"
   code_SERVICE           = "233"
   code_SERVLIST          = "234"
   code_SERVLISTEND       = "235"
   code_STATSLLINE        = "241"
   code_STATSUPTIME       = "242"
   code_STATSOLINE        = "243"
   code_STATSHLINE        = "244"
   code_LUSERCONNS        = "250"
   code_LUSERCLIENT       = "251"
   code_LUSEROP           = "252"
   code_LUSERUNKNOWN      = "253"
   code_LUSERCHANNELS     = "254"
   code_LUSERME           = "255"
   code_ADMINME           = "256"
   code_ADMINLOC1         = "257"
   code_ADMINLOC2         = "258"
   code_ADMINEMAIL        = "259"
   code_TRACELOG          = "261"
   code_ENDOFTRACE        = "262"
   code_TRYAGAIN          = "263"
   code_N_LOCAL           = "265"
   code_N_GLOBAL          = "266"
   code_NONE              = "300"
   code_AWAY              = "301"
   code_USERHOST          = "302"
   code_ISON              = "303"
   code_UNAWAY            = "305"
   code_NOAWAY            = "306"
   code_WHOISUSER         = "311"
   code_WHOISSERVER       = "312"
   code_WHOISOPERATOR     = "313"
   code_WHOWASUSER        = "314"
   code_ENDOFWHO          = "315"
   code_WHOISCHANOP       = "316"
   code_WHOISIDLE         = "317"
   code_ENDOFWHOIS        = "318"
   code_WHOISCHANNELS     = "319"
   code_LISTSTART         = "321"
   code_LIST              = "322"
   code_LISTEND           = "323"
   code_CHANNELMODEIS     = "324"
   code_CHANNELCREATE     = "329"
   code_NOTOPIC           = "331"
   code_CURRENTTOPIC      = "332"
   code_TOPICINFO         = "333"
   code_INVITING          = "341"
   code_SUMMONING         = "342"
   code_INVITELIST        = "346"
   code_ENDOFINVITELIST   = "347"
   code_EXCEPTLIST        = "348"
   code_ENDOFEXCEPTLIST   = "349"
   code_VERSION           = "351"
   code_WHOREPLY          = "352"
   code_NAMREPLY          = "353"
   code_KILLDONE          = "361"
   code_CLOSING           = "362"
   code_CLOSEEND          = "363"
   code_LINKS             = "364"
   code_ENDOFLINKS        = "365"
   code_ENDOFNAMES        = "366"
   code_BANLIST           = "367"
   code_ENDOFBANLIST      = "368"
   code_ENDOFWHOWAS       = "369"
   code_INFO              = "371"
   code_MOTD              = "372"
   code_INFOSTART         = "373"
   code_ENDOFINFO         = "374"
   code_MOTDSTART         = "375"
   code_ENDOFMOTD         = "376"
   code_YOUREOPER         = "381"
   code_REHASHING         = "382"
   code_MYPORTIS          = "384"
   code_TIME              = "391"
   code_USERSSTART        = "392"
   code_USERS             = "393"
   code_ENDOFUSERS        = "394"
   code_NOUSER            = "395"
   code_NOSUCHNICK        = "401"
   code_NOSUCHSERVER      = "402"
   code_NOSUCHCHANNEL     = "403"
   code_CANNOTSENDTOCHAN  = "404"
   code_TOOMANYCHANNELS   = "405"
   code_WASNOSUCHNICK     = "406"
   code_TOOMANYTARGETS    = "407"
   code_NOORIGIN          = "409"
   code_NORECIPIENT       = "411"
   code_NOTEXTTOSEND      = "412"
   code_NOOPLEVEL         = "413"
   code_WILDTOPLEVEL      = "414"
   code_UNKNOWNCOMMAND    = "421"
   code_NOMOTD            = "422"
   code_NOADMININFO       = "423"
   code_FILEERROR         = "424"
   code_NONICKNAMEGIVEN   = "431"
   code_ERRONEUSNICKNAME  = "432"
   code_NICKNAMEINUSE     = "433"
   code_NICKCOLLISION     = "436"
   code_UNAVAILRESOURCE   = "437"
   code_USERNOTINCHANNEL  = "441"
   code_NOTONCHANNEL      = "442"
   code_NOLOGIN           = "444"
   code_SUMMONDISABLED    = "445"
   code_USERSDISABLED     = "446"
   code_NOTREGISTERED     = "451"
   code_NEEDMOREPARAMS    = "461"
   code_ALREADYREGISTERED = "462"
   code_PASSWDMISMATCH    = "464"
   code_YOUREBANNEDCREEP  = "465"
   code_YOUWILLBEBANNED   = "466"
   code_KEYSET            = "467"
   code_CHANNELISFULL     = "471"
   code_UNKNOWNMODE       = "472"
   code_INVITEONLYCHAN    = "473"
   code_BANNEDFROMCHAN    = "474"
   cade_BADCHANNELKEY     = "475"
   code_BADCHANNELMASK    = "476"
   code_NOCHANMODES       = "477"
   code_BANLISTFULL       = "478"
   code_NOPRIVILEGES      = "481"
   code_CANTKILLSERVER    = "483"
   code_RESTRICTED        = "484"
   code_UNIQOPPRIVSNEEDED = "485"
   code_NOOPERHOST        = "491"
   code_NOSERVICEHOST     = "492"
   code_UMODEUNKNOWNFLAG  = "501"
   code_USERSDONTMATCH    = "502"
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
   # Temporal:
   self.irc_uplink_nick = self.CONST.irc_default_uplink_nick
   self.irc_uplink_nick2 = self.CONST.irc_default_uplink_nick2
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
   self.time_now   = datetime.datetime.now()
   self.delta_time = 0
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
   if not self.irc_debug:
     return
   print(msg)
   
 def irc_tolower_(self, irc_input):
   return irc_input.translate(self.CONST.irc_translation)
   
 def is_irc_channel_(self, irc_channel):
   str_mask  = "^#[" + self.CONST.irc_ascii_letters + "_]{1,24}$"
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(irc_channel)
   
 def irc_check_mask_(self, irc_from, irc_mask):
   str_from = self.irc_tolower_(irc_from)
   str_mask = self.irc_tolower_(irc_mask).replace("\\", "\\\\")
   for char in ".$|[](){}+":
     str_mask = str_mask.replace(char, "\\" + char)
   str_mask = str_mask.replace("?", ".")
   str_mask = str_mask.replace("*", ".*")
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(str_from)
 
 def irc_trace_add_nick_(self, irc_nick, irc_mask, irc_user, irc_info):
   pass
   
 def irc_trace_add_user_(self, irc_mask, irc_chan, irciot_parameters):
   pass
   
 def irc_trace_clear_nicks_(self):
   pass
   
 def irc_trace_clear_users_(self):
   pass

 def irc_trace_delete_nick_(self, irc_nick):
   pass

 def irc_trace_get_nick_struct_(self, position):
   return {}

 def irc_trace_get_nick_struct_by_nick_(self, irc_nick):
   return {}
   
 def irc_trace_get_user_mask_(self, position):
   return "test!test@test.test"

 def irc_trace_get_user_struct_(self, position):
   return {}
  
 def irc_trace_check_all_users_masks_(self, irc_from, irciot_parameters):
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
   try:
     self.irc.close()
   except:
     pass
  
 def irc_reconnect_(self):
   if not self.irc_run:
     return
   self.irc_disconnect_()
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
     self.to_log_("socket.error in irc_send_() ...")
     return -1
   except ValueError:
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
   ret = self.irc_send_("NICK " + irc_nick + "%s" \
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

 def irc_add_to_queue_(self, queue_id, irc_message, irc_wait):
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
     self.delta_time = 0

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
           try:
             self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           except:
             to_log_("Cannot re-create socket for IRC")
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
         (irc_ret, irc_input_buffer, self.delta_time) \
          = self.irc_recv_(irc_wait)
       irc_wait = self.CONST.irc_default_wait
       if (self.delta_time > 0):
         irc_wait = self.delta_time
    
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

         if (irc_input_command[:4] \
              == self.CONST.code_NICKNAMEINUSE + " "):
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

         if (irc_input_command[:4] \
              == self.CONST.code_NOTREGISTERED + " "):
           irc_init = 1
           irc_wait = self.CONST.irc_default_wait

         if irc_input_split.find(" KICK ") != -1:
           irc_init = 3
           irc_wait = self.CONST.irc_default_wait
         
         if (irc_input_split[:4] \
              == self.CONST.code_BANNEDFROMCHAN + " "):
           irc_init = 3
           irc_wait = self.CONST.irc_default_wait
 
         if (irc_input_split.find(" PRIVMSG ") != -1) \
          or (irc_input_split == ""):

           irc_name = ""
           irc_message = None
        
           if (irc_input_split != ""):
             irc_name = irc_input_split.split('!',1)[0][1:]
             self.time_now = datetime.datetime.now()
             irc_message = irc_input_split.split('PRIVMSG',1)[1].split(':',1)[1]
             irc_message = irc_message.strip()
       
           if ((irc_message == None) and (irc_input_buffer == "")):
             self.time_now = datetime.datetime.now()
             irc_message = ""

           if (((irc_name == self.irc_uplink_nick) \
             or (irc_name == self.irc_uplink_nick2)) \
            and (irc_init > 3) and (self.is_json_(irc_message))):
         
             self.irc_add_to_queue_(self.CONST.irc_queue_input, irc_message, \
              self.CONST.irc_default_wait)
           
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

