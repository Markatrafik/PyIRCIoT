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
import ssl
from queue import Queue
from time import sleep

#from pprint import pprint

import datetime

class PyLayerIRC(object):

 class CONST(object):
   #
   irciot_protocol_version_compatible = '0.3.21'
   #
   irciot_library_version_compatible  = '0.0.63'
   #
   # Bot specific constants
   #
   irc_first_wait = 30
   irc_micro_wait = 0.15
   irc_default_wait = 30
   #
   irc_default_debug = False
   #
   irc_default_nick = "MyBot"
   irc_default_info = "IRC-IoT Bot"
   irc_default_quit = "Bye!"
   #
   irc_default_server = "irc-iot.nsk.ru"
   irc_default_port = 6667
   irc_default_password = None
   irc_default_ssl = False
   #
   irc_default_proxy = None
   irc_default_proxy_server = None
   irc_default_proxy_port = None
   irc_default_proxy_password = None
   #
   # Will be replaced to channel-list:
   irc_default_channel = "#myhome"
   irc_default_chankey = None
   #
   # 0. Unique User ID
   # 1. IRC User Mask
   # 2. IRC Channel Name
   # 3. Blockchain Key
   # 4. User Options
   # 5. Last Message ID
   #
   irc_default_users = [ \
    ( 1, "iotBot!*irc@irc-iot.nsk.ru",    "#myhome", None, None, None ), \
    ( 2, "FaceBot!*irc@faceserv*.nsk.ru", "#myhome", None, None, None ) ]
   #
   irc_queue_input  = 0
   irc_queue_output = 1
   #
   irc_input_buffer = ""
   #
   irc_buffer_size = 2048
   #
   irc_modes = [ "CLIENT", "SERVICE", "SERVER" ]
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
   irc_max_nick_length    = 15
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
   code_NICKCHANGETOOFAST = "438"
   code_USERNOTINCHANNEL  = "441"
   code_NOTONCHANNEL      = "442"
   code_USERONCHANNEL     = "443"
   code_NOLOGIN           = "444"
   code_SUMMONDISABLED    = "445"
   code_USERSDISABLED     = "446"
   code_NOTREGISTERED     = "451"
   code_NEEDMOREPARAMS    = "461"
   code_ALREADYREGISTERED = "462"
   code_NOPERMFORHOST     = "463"
   code_PASSWDMISMATCH    = "464"
   code_YOUREBANNEDCREEP  = "465"
   code_YOUWILLBEBANNED   = "466"
   code_KEYSET            = "467"
   code_CHANNELISFULL     = "471"
   code_UNKNOWNMODE       = "472"
   code_INVITEONLYCHAN    = "473"
   code_BANNEDFROMCHAN    = "474"
   code_BADCHANNELKEY     = "475"
   code_BADCHANNELMASK    = "476"
   code_NOCHANMODES       = "477"
   code_BANLISTFULL       = "478"
   code_NOPRIVILEGES      = "481"
   code_CHANOPRIVSNEEDED  = "482"
   code_CANTKILLSERVER    = "483"
   code_RESTRICTED        = "484"
   code_UNIQOPPRIVSNEEDED = "485"
   code_NOOPERHOST        = "491"
   code_NOSERVICEHOST     = "492"
   code_UMODEUNKNOWNFLAG  = "501"
   code_USERSDONTMATCH    = "502"
   #
   cmd_ADMIN      = "ADMIN"
   cmd_AWAY       = "AWAY"
   cmd_CTCP       = "CTCP"
   cmd_CTCPREPLY  = "CTCPREPLY"
   cmd_DCC_CON    = "DCC_CONNECT"
   cmd_DCC_DISCON = "DCC_DISCONNECT"
   cmd_DCC_MSG    = "DCCMSG"
   cmd_DISCONNECT = "DISCONNECT"
   cmd_ERROR      = "ERROR"
   cmd_INFO       = "INFO"
   cmd_INVITE     = "INVITE"
   cmd_ISON       = "ISON"
   cmd_JOIN       = "JOIN"
   cmd_KICK       = "KICK"
   cmd_KILL       = "KILL"
   cmd_LINKS      = "LINKS"
   cmd_LIST       = "LIST"
   cmd_MODE       = "MODE"
   cmd_NAMES      = "NAMES"
   cmd_NICK       = "NICK"
   cmd_NOTICE     = "NOTICE"
   cmd_NJOIN      = "NJOIN"
   cmd_OPER       = "OPER"
   cmd_PART       = "PART"
   cmd_PASS       = "PASS"
   cmd_PING       = "PING"
   cmd_PONG       = "PONG"
   cmd_PRIVMSG    = "PRIVMSG"
   cmd_PRIVNOTICE = "PRIVNOTICE"
   cmd_PUBMSG     = "PUBMSG"
   cmd_PUBNOTICE  = "PUBNOTICE"
   cmd_REHASH     = "REHASH"
   cmd_RESTART    = "RESTART"
   cmd_QUIT       = "QUIT"
   cmd_SERVER     = "SERVER"
   cmd_SQUIT      = "SQUIT"
   cmd_STATS      = "STATS"
   cmd_SUMMON     = "SUMMON"
   cmd_TIME       = "TIME"
   cmd_TOPIC      = "TOPIC"
   cmd_TRACE      = "TRACE"
   cmd_USER       = "USER"
   cmd_USERS      = "USERS"
   cmd_USERHOST   = "USERHOST"
   cmd_VERSION    = "VERSION"
   cmd_WALLOPS    = "WALLOPS"
   cmd_WHOIS      = "WHOIS"
   cmd_WHOWAS     = "WHOWAS"
   cmd_WHO        = "WHO"
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   self.irc_host = socket.gethostname()
   #
   self.irc_nick = self.CONST.irc_default_nick
   self.irc_info = self.CONST.irc_default_info
   self.irc_quit = self.CONST.irc_default_quit
   #
   self.irc_nick_length = self.CONST.irc_max_nick_length
   #
   self.irc_server = self.CONST.irc_default_server
   self.irc_port = self.CONST.irc_default_port
   self.irc_password = self.CONST.irc_default_password
   self.irc_ssl = self.CONST.irc_default_ssl
   #
   self.irc_proxy = None
   if self.CONST.irc_default_proxy != None:
     self.irc_proxy_server = self.CONST.irc_default_proxy_server
     self.irc_proxy_port = self.CONST.irc_default_proxy_port
     self.irc_proxy_password = self.CONST.irc_default_proxy_password
   #
   self.irc_status = 0
   self.irc_last = None
   #
   self.irc_servers = [ ( \
     self.irc_server, self.irc_port, \
     self.irc_password, self.irc_ssl, 0, None ) ]
   #
   self.irc_proxies = []
   if self.irc_proxy != None:
     self.irc_proxies = [ ( \
     self.irc_proxy_server, self.irc_proxy_port, \
     self.irc_proxy_password, 0, None ) ]
   #
   self.irc_channel = self.CONST.irc_default_channel
   self.irc_chankey = self.CONST.irc_default_chankey
   self.join_retry  = 0
   #
   # ( irc channel, irc channel key, join retry count )
   self.irc_channels = [ ( \
     self.irc_channel, self.irc_chankey, 0 ) ]
   #
   self.irc_users = self.CONST.irc_default_users
   self.irc_nicks = []
   #
   self.irc_queue = [0, 0]
   self.irc_queue[self.CONST.irc_queue_input]  = Queue(maxsize=0)
   self.irc_queue[self.CONST.irc_queue_output] = Queue(maxsize=0)
   #
   self.irc_queue_lock = [0, 0]
   self.irc_queue_lock[self.CONST.irc_queue_input]  = False
   self.irc_queue_lock[self.CONST.irc_queue_output] = False
   #
   self.irc_commands = []
   self.irc_codes    = []
   #
   self.irc_task  = None
   self.irc_run   = False
   self.irc_mode  = self.CONST.irc_modes[0]
   self.irc_debug = self.CONST.irc_default_debug
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

 def irc_tolower_(self, in_input):
   return in_input.translate(self.CONST.irc_translation)

 def is_irc_nick_(self, in_nick):
   if not isinstance(in_nick, str):
     return False
   str_mask = "^[" + self.CONST.irc_ascii_letters \
    + "_\^\[\]\{\}][" + self.CONST.irc_ascii_letters \
    + self.CONST.irc_ascii_digits + "-_\^\[\]\{\}]{1,12}$"
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(in_nick)

 def is_irc_channel_(self, in_channel):
   if not isinstance(in_channel, str):
     return False
   str_mask = "^#[" + self.CONST.irc_ascii_letters \
    + self.CONST.irc_ascii_digits + "-_\^\[\]\{\}]{1,24}$"
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(in_channel)

 def irc_compare_channels_(self, ref_channel, cmp_channel):
   if not self.is_irc_channel_(ref_channel):
     return False
   if not self.is_irc_channel_(cmp_channel):
     return False
   return (self.irc_tolower_(ref_channel) \
        == self.irc_tolower_(cmp_channel))

 def irc_compare_nicks_(self, ref_nick, cmp_nick):
   if not self.is_irc_nick_(ref_nick):
     return False
   if not self.is_irc_nick_(cmp_nick):
     return False
   return (self.irc_tolower_(ref_nick) \
        == self.irc_tolower_(cmp_nick))

 def irc_check_mask_(self, in_from, in_mask):
   str_from = self.irc_tolower_(in_from)
   str_mask = self.irc_tolower_(in_mask).replace("\\", "\\\\")
   for char in ".$|[](){}+":
     str_mask = str_mask.replace(char, "\\" + char)
   str_mask = str_mask.replace("?", ".")
   str_mask = str_mask.replace("*", ".*")
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(str_from)

 def irc_track_add_nick_(self, in_nick, in_mask, in_user, in_info):
   if not self.is_irc_nick_(in_nick):
     return
   my_struct = self.irc_track_get_nick_struct_by_nick_(in_nick)
   if (my_struct == None):
     self.irc_nicks.append((in_nick, in_mask, in_user, in_info))
   else:
     self.irc_track_update_nick_(in_nick, in_mask, in_user, in_info)
   #
   # End of irc_track_add_nick_()

 def irc_track_add_user_(self, in_mask, in_chan, irciot_parameters):
   if not self.is_irc_channel_(in_chan):
     return
   in_key = None
   in_opt = None
   in_mid = None
   if irciot_parameters != None:
     (in_key, in_opt, in_mid) = irciot_parameters
   pass
   #
   # End of irc_track_add_user_()

 def irc_track_update_nick_(self, in_nick, in_mask, in_user, in_info):
   if not self.is_irc_nick_(in_nick):
     return
   for my_index, my_struct in enumerate(self.irc_nicks):
     (my_nick, my_mask, my_user, my_info) = my_struct
     # comparing of the masks will be here ...
     if (self.irc_compare_nicks_(my_nick, in_nick)):
       if in_mask != None:
         my_mask = in_mask
       if in_user != None:
         my_user = irc_in
       if in_info != None:
         my_info = in_info
       self.irc_nicks[my_index] = (in_nick, my_mask, my_user, my_info)
       break
   #
   # End of irc_track_update_nick_()

 def irc_track_clear_nicks_(self):
   self.irc_nicks = []

 def irc_track_clear_users_(self):
   self.irc_users = []

 def irc_track_delete_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_user, my_info) = my_struct
     if (self.irc_compare_nicks_(my_nick, in_nick)):
       self.irc_nicks.remove(my_struct)
       break

 def irc_track_get_nick_struct_(self, in_position):
   try:
     my_struct = self.irc_nicks[in_position]
   except:
     my_struct = None
   return my_struct

 def irc_track_get_nick_struct_by_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return None
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_user, my_info) = my_struct
     if self.irc_compare_nicks_(my_nick, in_nick):
       return my_struct
   return None

 def irc_track_clarify_nicks_(self):
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_user, my_info) = my_struct
     if ((my_mask == None) or (my_info == None)):
       self.irc_whois_nick_(my_nick)
       if my_mask == None:
         my_mask = ""
       if my_info == None:
         my_info = ""
       self.irc_track_update_nick_(my_nick, my_mask, my_user, my_info)
       break
   #
   # End of irc_track_clarify_nicks_()

 def irc_track_get_user_mask_(self, in_position):
   return "test!test@test.test"

 def irc_track_get_user_struct_(self, in_position):
   user_struct = {}
   return user_struct

 def irc_track_check_all_users_masks_(self, in_from, in_channel, \
   irciot_parameters = None):
   in_key = None
   in_opt = None
   in_mid = None
   if irciot_parameters != None:
     (in_key, in_opt, in_mid) = irciot_parameters
   return True

 def irc_cfg_check_user_(self, in_from, in_channel, \
   irciot_parameters = None):
   in_key = None
   in_opt = None
   in_mid = None
   if irciot_parameters != None:
     (in_key, in_opt, in_mid) = irciot_parameters   
   for my_user in self.irc_users:
     ( my_uid, my_mask, my_chan, my_crypt, my_opt, my_mid ) = my_user
     if ((in_channel == "*") or \
      (self.irc_compare_channels_(in_channel, my_chan))):
       if self.irc_check_mask_(in_from, my_mask):
         return True
   return False
  #
  # End of irc_cfg_check_user_()

 def is_json_(self, in_message):
   try:
     json_object = json.loads(in_message)
   except ValueError:
     return False
   return True

 def irc_disconnect_(self):
   try:
     self.irc.shutdown()
   except:
     pass
   self.irc_track_clear_nicks_()
   try:
     self.irc.close()
   except:
     pass
   #
   # End of irc_disconnect_()

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
       return -1
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
   ret = self.irc_send_("QUIT :%s\r\n" % self.irc_quit)
   return ret

 def irc_extract_nick_mask_(self, in_string):
   try:
     irc_mask = in_string.split(' ', 1)[0][1:]
     irc_nick = irc_mask.split('!', 1)[0]
   except:
     irc_mask = "!@"
     irc_nick = ""
   return (irc_nick, irc_mask)

 def irc_extract_message_(self, in_string):
   try:
     irc_msg = in_string.split( \
      self.CONST.cmd_PRIVMSG, 1)[1].split(':', 1)[1]
     return irc_msg.strip()
   except:
     return None

 def irc_whois_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return -1
   ret = self.irc_send_(self.CONST.cmd_WHOIS + " " + in_nick)
   return ret
   
 def irc_who_channel_(self, in_channel):
   if not self.is_irc_channel_(in_channel):
     return -1
   ret = self.irc_send_(self.CONST.cmd_WHO + " " + in_channel)
   return ret

 def irc_random_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return -1
   random.seed()
   irc_nick = in_nick + "%d" % random.randint(0, 999)
   if (self.join_retry > 2):
       nick_length = random.randint(1, self.irc_nick_length)
       irc_nick = ''.join( \
        random.choice(self.CONST.irc_nick_chars) \
        for i in range(nick_length))
   ret = self.irc_send_(self.CONST.cmd_NICK + " " + irc_nick)
   return ret
   #
   # End of irc_random_nick_()

 def irc_socket_(self):
   try:
     irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     if self.irc_ssl:
       irc_socket = ssl.wrap_socket(irc_socket)
   except socket.error:
     to_log_("Cannot create socket for IRC")
     return None
   return irc_socket

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
   #
   # End of irc_check_queue_()

 def irc_add_to_queue_(self, in_queue_id, in_message, in_wait):
   old_queue_lock = self.irc_queue_lock[in_queue_id]
   self.irc_queue_lock[in_queue_id] = True
   self.irc_queue[in_queue_id].put((in_message, in_wait))
   self.irc_queue_lock[in_queue_id] = old_queue_lock

 # CLIENT Hooks:

 def func_nick_in_use_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if (self.irc_random_nick_(self.irc_nick) == 1):
     return (-1, 0, in_wait)
   return (in_ret, in_init, in_wait)

 def func_not_reg_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   return (in_ret, 1, self.CONST.irc_default_wait)

 def func_banned_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if (self.join_retry > 1):
     if (self.irc_random_nick_(self.irc_nick) == 1):
        return (-1, 0, in_wait)
   return (in_ret, 3, self.CONST.irc_default_wait)

 def func_on_kick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   return (in_ret, 3, self.CONST.irc_default_wait)
   
 def func_on_kill_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_quit_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   self.irc_track_delete_nick_(irc_nick)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_fast_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   # ... will be calculated from warning, not RFC 1459 ...
   in_wait = 3
   return (in_ret, in_init, in_wait)

 def func_chan_nicks_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(":")
     if (my_array[0] == ""):
       my_array = my_array[2].split(" ")
       for my_nick in my_array:
         if (my_nick[0] == '@'):
           my_nick = my_nick[1:]
         self.irc_track_add_nick_(my_nick, None, None, None)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait)
   #
   # End of func_chan_nicks_()
   
 def func_end_nicks_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(" ")
     in_ret = self.irc_who_channel_(my_array[3])
   except:
     return (in_ret, in_init, in_wait)     
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_who_user_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(":")
     if (my_array[0] == ""):
       my_info = my_array[2][2:]
       my_array = my_array[1].split(" ")
       my_nick = my_array[7]
       my_user = my_array[4]
       my_host = my_array[5]
       my_mask = my_nick + "!" + my_user + "@" + my_host
       self.irc_track_update_nick_(my_nick, my_mask, None, my_info)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait)
   #
   # End of func_who_user_()

 def func_whois_user_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(":")
     if (my_array[0] == ""):
       my_info = my_array[2]
       my_array = my_array[1].split(" ")
       my_nick = my_array[3]
       my_user = my_array[4]
       my_host = my_array[5]
       my_mask = my_nick + "!" + my_user + "@" + my_host
       self.irc_track_update_nick_(my_nick, my_mask, None, my_info)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait - 1)
   #
   # End of func_whois_user_()

 def func_on_join_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   self.irc_track_add_nick_(irc_nick, irc_mask, None, None)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_part_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   self.irc_track_delete_nick_(irc_nick)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_error_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if (in_string.find("Closing ") or in_string.find(" timeout")):
      return (-1, 0, in_wait)
   return (in_ret, 1, self.CONST.irc_default_wait)

 # SERVICE Hooks:

 def func_on_srv_info_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args 
   return (in_ret, in_init, in_wait)

 def init_rfc1459_(self):
   #
   C = self.CONST
   #
   self.irc_codes = [ \
    (C.code_NICKNAMEINUSE,    "NICKNAMEINUSE",    self.func_nick_in_use_), \
    (C.code_NOTREGISTERED,    "NOTREGISTERED",    self.func_not_reg_), \
    (C.code_BANNEDFROMCHAN,   "BANNEDFROMCHAN",   self.func_banned_), \
    (C.code_NICKCHANGETOOFAST,"NICKCHANGETOOFAST",self.func_fast_nick_), \
    (C.code_NAMREPLY,         "NAMREPLY",         self.func_chan_nicks_), \
    (C.code_WHOISUSER,        "WHOISUSER",        self.func_whois_user_), \
    (C.code_ENDOFNAMES,       "ENDOFNAMES",       self.func_end_nicks_), \
    (C.code_WHOREPLY,         "WHOREPLY",         self.func_who_user_), \
    (C.code_NOSUCHNICK,       "NOSUCHNICK",       None), \
    (C.code_NOSUCHSERVER,     "NOSUCHSERVER",     None), \
    (C.code_NOSUCHCHANNEL,    "NOSUCHCHANNEL",    None), \
    (C.code_CANNOTSENDTOCHAN, "CANNOTSENDTOCHAN", None), \
    (C.code_TOOMANYCHANNELS,  "TOOMANYCHANNELS",  None), \
    (C.code_WASNOSUCHNICK,    "WASNOSUCHNICK",    None), \
    (C.code_TOOMANYTARGETS,   "TOOMANYTARGETS",   None), \
    (C.code_NOORIGIN,         "NOORIGIN",         None), \
    (C.code_NORECIPIENT,      "NORECIPIENT",      None), \
    (C.code_NOTEXTTOSEND,     "NOTEXTTOSEND",     None), \
    (C.code_NOOPLEVEL,        "NOOPLEVEL",        None), \
    (C.code_WILDTOPLEVEL,     "WILDTOPLEVEL",     None), \
    (C.code_UNKNOWNCOMMAND,   "UNKNOWNCOMMAND",   None), \
    (C.code_NOMOTD,           "NOMOTD",           None), \
    (C.code_NOADMININFO,      "NOADMININFO",      None), \
    (C.code_FILEERROR,        "FILEERROR",        None), \
    (C.code_NONICKNAMEGIVEN,  "NONICKNAMEGIVEN",  None), \
    (C.code_ERRONEUSNICKNAME, "ERRONEUSNICKNAME", None), \
    (C.code_NICKNAMEINUSE,    "NICKNAMEINUSE",    None), \
    (C.code_NICKCOLLISION,    "NICKCOLLISION",    None), \
    (C.code_UNAVAILRESOURCE,  "UNAVAILRESOURCE",  None), \
    (C.code_USERNOTINCHANNEL, "USERNOTINCHANNEL", None), \
    (C.code_NOTONCHANNEL,     "NOTONCHANNEL",     None), \
    (C.code_NOLOGIN,          "NOLOGIN",          None), \
    (C.code_SUMMONDISABLED,   "SUMMONDISABLED",   None), \
    (C.code_USERSDISABLED,    "USERSDISABLED",    None), \
    (C.code_NEEDMOREPARAMS,   "NEEDMOREPARAMS",   None), \
    (C.code_USERSDONTMATCH,   "USERSDONTMATCH",   None), \
    (C.code_ALREADYREGISTERED,"ALREADYREGISTERED",None), \
    (C.code_PASSWDMISMATCH,   "PASSWDMISMATCH",   None), \
    (C.code_YOUREBANNEDCREEP, "YOUREBANNEDCREEP", None), \
    (C.code_YOUWILLBEBANNED,  "YOUWILLBEBANNED",  None), \
    (C.code_KEYSET,           "KEYSET",           None), \
    (C.code_CHANNELISFULL,    "CHANNELISFULL",    None), \
    (C.code_UNKNOWNMODE,      "UNKNOWNMODE",      None), \
    (C.code_INVITEONLYCHAN,   "INVITEONLYCHAN",   None), \
    (C.code_BANNEDFROMCHAN,   "BANNEDFROMCHAN",   None), \
    (C.code_BADCHANNELKEY,    "BADCHANNELKEY",    None), \
    (C.code_BADCHANNELMASK,   "BADCHANNELMASK",   None), \
    (C.code_NOCHANMODES,      "NOCHANMODES",      None), \
    (C.code_BANLISTFULL,      "BANLISTFULL",      None), \
    (C.code_NOPRIVILEGES,     "NOPRIVILEGES",     None), \
    (C.code_CANTKILLSERVER,   "CANTKILLSERVER",   None), \
    (C.code_RESTRICTED,       "RESTRICTED",       None), \
    (C.code_UNIQOPPRIVSNEEDED,"UNIQOPPRIVSNEEDED",None), \
    (C.code_NOOPERHOST,       "NOOPERHOST",       None), \
    (C.code_NOSERVICEHOST,    "NOSERVICEHOST",    None), \
    (C.code_UMODEUNKNOWNFLAG, "UMODEUNKNOWNFLAG", None) ]
   #
   if self.irc_mode == self.CONST.irc_modes[0]:
     self.irc_commands = [ \
      (C.cmd_INVITE,  None), \
      (C.cmd_JOIN,    self.func_on_join_), \
      (C.cmd_KICK,    self.func_on_kick_), \
      (C.cmd_KILL,    self.func_on_kill_), \
      (C.cmd_MODE,    None), \
      (C.cmd_NICK,    self.func_on_nick_), \
      (C.cmd_NOTICE,  None), \
      (C.cmd_PART,    self.func_on_part_), \
      (C.cmd_PONG,    None), \
      (C.cmd_PRIVMSG, None), \
      (C.cmd_QUIT,    self.func_on_quit_), \
      (C.cmd_ERROR,   self.func_on_error_) ]

   else: # RFC 2813
     self.irc_cmmands = [ \
      (C.cmd_PASS,    None), (C.cmd_SERVER,     None), \
      (C.cmd_NICK,    None), (C.cmd_QUIT,       None), \
      (C.cmd_SQUIT,   None), (C.cmd_JOIN,       None), \
      (C.cmd_NJOIN,   None), (C.cmd_MODE,       None), \
      (C.cmd_LINKS,   None), (C.cmd_KILL,       None), \
      (C.cmd_NAMES,   None), (C.cmd_INVITE,     None), \
      (C.cmd_STATS,   None), (C.cmd_CONNECT,    None), \
      (C.cmd_TRACE,   None), (C.cmd_ADMIN,      None), \
      (C.cmd_WHO,     None), (C.cmd_INFO,       self.func_on_srv_info_), \
      (C.cmd_WHOIS,   None), (C.cmd_WHOWAS,     None), \
      (C.cmd_AWAY,    None), (C.cmd_RESTART,    None), \
      (C.cmd_SUMMON,  None), (C.cmd_USERS,      None), \
      (C.cmd_WALLOPS, None), (C.cmd_USERHOST,   None), \
      (C.cmd_TOPIC,   None), (C.cmd_KICK,       None), \
      (C.cmd_PONG,    None), (C.cmd_PART,       None), \
      (C.cmd_ERROR,   None), (C.cmd_PRIVMSG,    None), \
      (C.cmd_PUBMSG,  None), (C.cmd_PUBNOTICE,  None), \
      (C.cmd_NOTICE,  None), (C.cmd_PRIVNOTICE, None), \
      (C.cmd_ISON,    None) ]

 def irc_process_(self):

   self.init_rfc1459_()

   try:
     irc_init = 0
     irc_wait = self.CONST.irc_first_wait
     irc_input_buffer = ""
     irc_ret = 0

     self.delta_time = 0

     # app.run(host='0.0.0.0', port=50000, debug=True)
     # must be FIXed for Unprivileged user

     self.irc = self.irc_socket_()

     while (self.irc_run):
     
       if not self.irc:
         sleep(self.CONST.irc_first_wait)
         self.irc = self.irc_socket_()
         irc_init = 0

       if (irc_init < 6):
         irc_init += 1

       if (irc_init == 1):
         try:
           self.irc_connect_(self.irc_server, self.irc_port)
         except socket.error:
           self.irc_disconnect_()
           self.irc = self.irc_socket_()
           irc_init = 0

       elif (irc_init == 2):
         if self.irc_password:
           self.irc_send_(self.CONST.cmd_PASS \
            + " " + self.irc_password)
         if (self.irc_send_(self.CONST.cmd_USER \
          + " " + self.irc_nick + " " + self.irc_host \
          + " 1 :" + self.irc_info) == -1):
           irc_init = 0

       elif (irc_init == 3):
         self.join_retry = 0
         if (self.irc_send_(self.CONST.cmd_NICK \
          + " " + self.irc_nick) == -1):
           irc_init = 0

       elif (irc_init == 4):
         irc_wait = self.CONST.irc_default_wait
         self.join_retry += 1
         if (self.irc_send_(self.CONST.cmd_JOIN \
          + " " + self.irc_channel + str(" " \
          + self.irc_chankey if self.irc_chankey else "")) == -1):
           irc_init = 0

       elif (irc_init == 5):
         irc_wait = self.CONST.irc_default_wait
         self.join_retry += 1
         if (self.irc_send_(self.CONST.cmd_JOIN \
          + " " + self.irc_channel + "%s\r\n" % str(" " \
          + self.irc_chankey if self.irc_chankey else "")) == -1):
           irc_init = 0

       if (irc_init > 0):
         (irc_ret, irc_input_buffer, self.delta_time) \
          = self.irc_recv_(irc_wait)

       irc_wait = self.CONST.irc_default_wait

       if (self.delta_time > 0):
         irc_wait = self.delta_time
       else:
         if (irc_init == 6):
            self.irc_track_clarify_nicks_()

       if (irc_ret == -1):
         self.irc_reconnect_()
         irc_input_buffer = ""
         irc_init = 0
         self.irc = self.irc_socket_()

       irc_prefix = ":" + self.irc_server + " "
       irc_prefix_len = len(irc_prefix)

       for irc_input_split in re.split(r'[\r\n]', irc_input_buffer):

         if irc_input_split[:5] == self.CONST.cmd_PING + " ":
           if (self.irc_pong_(irc_input_split) == -1):
             irc_ret = -1
             irc_init = 0
           else:
             self.irc_track_clarify_nicks_()

         try:
           irc_input_cmd = irc_input_split.split(' ')[1]
         except:
           irc_input_cmd = ""

         if (irc_input_split[:irc_prefix_len] == irc_prefix):
           # Parse codes only from valid server
           for irc_cod_pack in self.irc_codes:
             (irc_code, code_name, irc_function)  = irc_cod_pack
             if (irc_function != None):
                if (irc_input_cmd == irc_code):
                  irc_args = (irc_input_split, \
                   irc_ret, irc_init, irc_wait)
                  (irc_ret, irc_init, irc_wait) = irc_function(irc_args)

         for irc_cmd_pack in self.irc_commands:
           (irc_cmd, irc_function) = irc_cmd_pack
           if (irc_function != None):
              if (irc_input_cmd == irc_cmd):
                irc_args = (irc_input_split, \
                 irc_ret, irc_init, irc_wait)
                (irc_ret, irc_init, irc_wait) = irc_function(irc_args)

         if (irc_input_cmd == self.CONST.cmd_PRIVMSG \
          or irc_input_split == ""):

           irc_nick = ""
           irc_mask = "!@"
           irc_message = None

           if (irc_input_split != ""):
             (irc_nick, irc_mask) \
              = self.irc_extract_nick_mask_(irc_input_split)
             self.time_now = datetime.datetime.now()
             irc_message = self.irc_extract_message_(irc_input_split)

           if ((irc_message == None) and (irc_input_buffer == "")):
             self.time_now = datetime.datetime.now()
             irc_message = ""

           if ((self.irc_cfg_check_user_(irc_mask, self.irc_channel)) \
             and (irc_init > 3) and (self.is_json_(irc_message))):

             self.irc_add_to_queue_(self.CONST.irc_queue_input, \
              irc_message, self.CONST.irc_default_wait)
           
           irc_input_split = ""

         irc_input_buff = ""

       if (irc_init > 5):
          (irc_message, irc_wait) \
           = self.irc_check_queue_(self.CONST.irc_queue_output)
          if (irc_message != ""):
             self.irc_send_(self.CONST.cmd_PRIVMSG + " " \
               + self.irc_channel + " :" + irc_message)
          irc_message = ""    

   except socket.error:
     self.irc_disconnect()
     irc_init = 0
   #
   # End of irc_process_()

