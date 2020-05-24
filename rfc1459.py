'''
'' PyIRCIoT (PyLayerIRC class)
''
'' Copyright (c) 2018-2020 Alexey Y. Woronov
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
DO_default_draft = "ircu"   # Integrator must define IRC software

import socket
import select
import random
import re
import threading
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

class PyLayerIRC( irciot_shared_ ):

 class CONST( irciot_shared_.CONST ):
   #
   irciot_protocol_version = '0.3.33'
   #
   irciot_library_version  = '0.0.203'
   #
   # Bot specific constants
   #
   irc_first_wait = 28
   irc_micro_wait = 0.12
   irc_ident_wait = 8
   irc_default_wait = 28
   irc_latency_wait = 1
   #
   irc_default_debug = DO_debug_library
   #
   irc_default_nick = "MyBot"
   irc_default_info = "IRC-IoT Bot"
   irc_default_quit = "Bye!"
   #
   irc_default_server = "irc-iot.nsk.ru"
   irc_default_port = 6667
   irc_default_password = None
   irc_default_ssl = False
   irc_default_ident = False
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
   # User options:
   irc_aop   = 101 # give (+o) him channel operator status
   irc_aban  = 102 # ban (+b) him on these channels
   irc_avo   = 103 # give (+v) him a voice on channels
   irc_akick = 130 # kick it from these channels
   irc_adeop = 131 # take away (-o) his channel operator status
   irc_unban = 132 # unban (-b) mask on channels when banned
   irc_adevo = 133 # take away (-v) his voice on channels
   #
   # 0. Unique User ID
   # 1. IRC User Mask
   # 2. IRC Channel Name
   # 3. User Options
   # 4. Encryption Private or Secret Key
   # 5. Blockchain Private Key
   # 6. Last Message ID
   # 7. Encryption Key Timeout
   # 8. Blockchain Key Timeout
   # 9. My last Message ID
   #
   # Deault Message ID pipeline size:
   irc_default_mid_pipeline_size = 16
   #
   irc_default_users = [ \
    ( 1, "iotBot!*irc@irc-iot.nsk.ru",    irc_default_channel, \
      None, None, None, None, None, None, None ), \
    ( 2, "FaceBot!*irc@faceserv*.nsk.ru", irc_default_channel, \
      irc_aop, None, None, None, None, None, None ), \
    ( 3, "noobot!*bot@irc-iot.nsk.ru",    irc_default_channel, \
      [ irc_aop, irc_unban ], None, None, None, None, None, None ) ]
   #
   irc_default_talk_with_strangers = False
   #
   irc_queue_input  = 0
   irc_queue_output = 1
   #
   irc_recon_steps  = 8
   #
   irc_input_buffer = ""
   #
   irc_buffer_size  = 2560
   #
   irc_layer_modes  = [ "CLIENT", "SERVICE", "SERVER" ]
   #
   irc_default_nick_retry = 3600 # in seconds
   #
   irc_default_network_tag = "IRC-IoT"
   #
   # According RFC 1459
   #
   irc_ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
   irc_ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
   irc_ascii_letters = irc_ascii_lowercase + irc_ascii_uppercase
   irc_ascii_digits = "0123456789"
   irc_special_chars = "-[]\\`^{}"
   irc_nick_first_char = irc_ascii_letters + "[]\\`^{}"
   irc_nick_chars = irc_ascii_letters \
     + irc_ascii_digits + irc_special_chars
   irc_translation = "".maketrans( \
     irc_ascii_uppercase + "[]\\^",
     irc_ascii_lowercase + "{}|~")
   irc_transmocker = "".maketrans( \
     "aAoOBEGgIlSsT-_05891",
     "4400836911557_-OSBgl" )
   irc_mode_add = "+"
   irc_mode_del = "-"
   irc_change_modes \
     = irc_mode_add \
     + irc_mode_del
   irc_umode_op = "o"
   irc_umode_voice = "v"
   irc_umode_ban = "b"
   irc_user_modes \
     = irc_umode_op \
     + irc_umode_voice\
     + irc_umode_ban
   irc_channel_modes = "psitnm"
   irc_extra_modes = "lk"
   irc_all_modes \
     = irc_user_modes \
     + irc_channel_modes \
     + irc_extra_modes
   irc_all_modes_chars \
     = irc_change_modes \
     + irc_all_modes
   #
   irc_nick_regexp = "^[" + irc_ascii_letters \
     + "_`\^\\\[\]\{\}][" + irc_ascii_letters \
     + irc_ascii_digits + "\-_`\^\\\[\]\{\}]{1,12}$"
   irc_channel_regexp = "^#[" + irc_ascii_letters \
     + irc_ascii_digits + "\-_\^\[\]\{\}]{1,24}$"
   #
   irc_default_draft = DO_default_draft
   #
   #  1. "RFC1459" Internet Relay Chat Protocol '1993
   #  2. "RFC2812" IRC Draft: Client Protocol '2000
   #  3. "asp"        -- AspIRCd (Charybdis fork) '2019
   #  4. "Bahamut"    -- Bahamut, ver. 2.0.7
   #  5. "beware"     -- beware ircd, Delphi based, ver. 2.2.0
   #  6. "Charybdis"  -- charybdis-ircd, ver. 3.5.0 '2020
   #  7. "ConfRoom"   -- Conference Room
   #  8. "discord"    -- discordIRCd, js based, ver. 0.5.0
   #  9. "Elemental"  -- Elemental-IRCd, ver. 6.6.2
   # 10. "hybrid"     -- ircd-hybrid, @ EFNet, ver. 8.2.29
   # 11. "Insp"       -- Inspircd, ver. 2.0
   # 12. "IRCNet"     -- IRCNet ircd, @ IRCNet, ver. 2.12.2
   # 13. "IRCPlus"    -- IRCPlus, ver. 5.0
   # 14. "ircu"       -- ircd-ircu aka Undernet IRCd, ver. 2.10.12.10
   # 15. "miniircd"   -- miniircd, Python based, ver. 1.3 '2003
   # 16. "Nefarious"  -- Nefarious ircd
   # 17. "Nefarious2" -- Nefarious IRCu (ircu fork) '2020
   # 18. "ng"         -- ngIRCd aka Next Generation IRCd, ver. 25 '2019
   # 19. "Oragono"    -- Oragono, Golang based, ver. 2.0.0 '2016
   # 20. "plexus"     -- PleXusIRCd '2005
   # 21. "pircd"      -- Perl IRCd, Perl based '2002
   # 22. "pure"       -- pureIRCd, CSharp based '2008
   # 23. "ratbox"     -- ircd-ratbox, @ EFNet, ver. 3.0.8 '2006
   # 24. "Rock"       -- rock-ircd aka RockIRCd (UnrealIRCd fork), '2009
   # 25. "Rubi"       -- RubiIRCd, Ruby based '2009
   # 26. "RusNet"     -- ircd RusNet, @ RusNet, ver. 1.4.19
   # 27. "seven"      -- ircd-seven, ver. 1.1.3
   # 28. "Shadow"     -- ShadowIRCd, ver. 6.3.3 '2003
   # 29. "snircd"     -- snircd (ircu fork), @ QuakeNet, ver. 1.3.4
   # 30. "solid"      -- solid-ircd (Bahamut fork), ver. 3.4.8 '2004
   # 31. "Synchronet" -- Synchronet IRCd, js based
   # 32. "Unreal"     -- UnrealIRCd, ver. 5.0.4 '2020
   # 33. "We"         -- WeIRCd
   # 34. "PyIRCIoT" (when it works in IRC server mode)
   #
   irc_max_nick_length = 15
   if irc_default_draft == "ircu":
     irc_max_nick_length = 12
   irc_max_topic_length = 160
   irc_max_network_name_length = 80
   #
   default_mtu = 480
   if irc_default_draft == "ircu":
     default_mtu = 440
   #
   ircd_Ch_se = [ "Charybdis", "seven" ]
   ircd_Ch_se_ra = [ "Charybdis", "seven", "ratbox" ]
   ircd_Ch_se_ra_pl = [ "Charybdis", "seven", "ratbox", "plexus" ]
   ircd_Un_Ch_se = [ "Unreal", "Charybdis", "seven" ]
   ircd_Un_Ba = [ "Unreal", "Bahamut" ]
   ircd_iu_sn = [ "ircu", "snircd" ]
   ircd_iu_Un_sn = [ "ircu", "Unreal", "snircd" ]
   #
   code_RPL_WELCOME        = "001"
   code_RPL_YOURHOST       = "002"
   code_RPL_CREATED        = "003"
   code_RPL_MYINFO         = "004"
   code_RPL_ISUPPORT       = "005"
   if irc_default_draft in [ "ircu", "Unreal" ]:
     code_MAP              = "005"
     code_MAPMORE          = "006"
   if irc_default_draft == "ircu":
     code_MAPEND           = "007"
     code_SNOMASK          = "008"
     code_STATMEMTOT       = "009"
     code_STATMEM          = "010"
   if irc_default_draft in [ "Unreal", "Charybdis", "hybrid", \
    "seven", "IRCNet", "plexus", "ratbox" ]:
     code_RPL_REDIR        = "010"
   if irc_default_draft == "IRCNet":
     code_MAPSTART         = "018"
     code_RPL_HELLO        = "020"
   if irc_default_draft in ircd_iu_sn:
     code_APASSWARN_SET    = "030"
     code_APASSWARN_SECRET = "031"
     code_APASSWARN_CLEAR  = "032"
   if irc_default_draft == "Unreal":
     code_REMOTEISUPPORT   = "105"
   code_RPL_TRACELINK      = "200"
   code_RPL_TRACECONNECTING = "201"
   code_RPL_TRACEHANDSHAKE = "202"
   code_RPL_TRACEUNKNOWN   = "203"
   code_RPL_TRACEOPERATOR  = "204"
   code_RPL_TRACEUSER      = "205"
   code_RPL_TRACESERVER    = "206"
   if irc_default_draft == "plexus":
     code_RPL_TRACECAPTURED = "207"
   else:
     code_RPL_TRACESERVICE = "207"
   code_RPL_TRACENEWTYPE   = "208"
   code_RPL_TRACECLASS     = "209"
   if irc_default_draft == "Unreal":
     code_RPL_STATSHELP    = "210"
   else:
     code_RPL_TRACERECONNECT = "210"
   code_RPL_STATSLINKINFO  = "211"
   code_RPL_STATSCOMMANDS  = "212"
   code_RPL_STATSCLINE     = "213"
   code_RPL_STATSNLINE     = "214"
   code_RPL_STATSILINE     = "215"
   code_RPL_STATSKLINE     = "216"
   if irc_default_draft in ircd_iu_sn:
     code_STATSPLINE       = "217"
   else:
     code_STATSQLINE       = "217"
   code_STATSYLINE         = "218"
   code_ENDOFSTATS         = "219"
   if irc_default_draft == "Unreal":
     code_STATSBLINE       = "220"
   code_UMODEIS            = "221"
   if irc_default_draft in ircd_iu_sn:
     code_RPL_STATSJLINE   = "222"
   if irc_default_draft == "Unreal":
     code_SQLINE_NICK      = "222"
   if irc_default_draft == "Bahamut":
     code_STATSELINE       = "223"
   if irc_default_draft == "Unreal":
     code_STATSGLINE       = "223"
     code_STATSTLINE       = "224"
   if irc_default_draft == "Bahamut":
     code_RPL_STATSCLONE   = "225"
     code_RPL_STATSCOUNT   = "226"
   if irc_default_draft in [ "ircu", "hybrid", "plexus", "snircd" ]:
     code_RPL_STATALINE    = "226"
   if irc_default_draft == "Unreal":
     code_RPL_STATSELINE   = "225"
     code_RPL_STATSNLINE   = "226"
     code_RPL_STATSVLINE   = "227"
     code_RPL_STATSBANVER  = "228"
   code_RPL_SERVICEINFO    = "231"
   code_RPL_ENDOFSERVICES  = "232"
   code_RPL_SERVICE        = "233"
   code_RPL_SERVLIST       = "234"
   code_RPL_SERVLISTEND    = "235"
   code_STATSLLINE         = "241"
   code_STATSUPTIME        = "242"
   code_STATSOLINE         = "243"
   if irc_default_draft == "RFC2812":
     code_RPL_STATSSLINE   = "244"
   else:
     code_STATSHLINE       = "244"
   if irc_default_draft in [ "Unreal", "Bahamut", "Charybdis", \
    "IRCNet", "plexus", "seven", "ratbox" ]:
     code_RPL_STATSSLINE   = "245"
   if irc_default_draft == "ircu":
     code_STATSTLINE       = "246"
     code_STATSGLINE       = "247"
   if irc_default_draft == "Unreal":
     code_STATSXLINE       = "247"
   if irc_default_draft == "ircu":
     code_STATSULINE       = "248"
   code_RPL_STATSDEBUG     = "249" # Unknown
   code_LUSERCONNS         = "250"
   code_RPL_LUSERCLIENT    = "251"
   code_RPL_LUSEROP        = "252"
   code_RPL_LUSERUNKNOWN   = "253"
   code_RPL_LUSERCHANNELS  = "254"
   code_RPL_LUSERME        = "255"
   code_RPL_ADMINME        = "256"
   code_RPL_ADMINLOC1      = "257"
   code_RPL_ADMINLOC2      = "258"
   code_RPL_ADMINEMAIL     = "259"
   code_RPL_TRACELOG       = "261"
   code_RPL_ENDOFTRACE     = "262"
   if irc_default_draft in [ "RFC2812", "IRCNet" ]:
     code_RPL_TRYAGAIN     = "263"
   else:
     code_RPL_LOAD2HI      = "263"
   code_N_LOCAL            = "265"
   code_N_GLOBAL           = "266"
   if irc_default_draft in [ "ircu", "Unreal", "Bahamut", "snircd" ]:
     code_RPL_SILELIST     = "271"
     code_RPL_ENDOFSILELIST = "272"
   if irc_default_draft in ircd_iu_Un_sn:
     code_RPL_STATUSDLINE  = "275"
   if irc_default_draft == "Bahamut":
     code_RPL_USIGNSSL     = "275"
   if irc_default_draft in [ "Charybdis", "seven", "hybrid", "plexus" ]:
     code_RPL_WHOISCERTFP  = "276"
   if irc_default_draft in ircd_iu_sn:
     code_RPL_STATSRLINE   = "276"
     code_RPL_GLIST        = "280"
     code_RPL_ENDOFGLIST   = "281"
   if irc_default_draft == "Unreal":
     code_RPL_HELPHDR      = "290"
     code_RPL_HELPOP       = "291"
     code_RPL_HELPTLR      = "292"
     code_RPL_HELPHLP      = "293"
     code_RPL_HELPFWD      = "294"
     code_RPL_HELPIGN      = "295"
   if irc_default_draft == "snircd":
     code_RPL_DATASTR      = "290"
     code_RPL_ENDOFCHECK   = "291"
   code_RPL_NONE           = "300" # Unused?
   code_RPL_AWAY           = "301"
   code_RPL_USERHOST       = "302"
   code_RPL_ISON           = "303"
   code_RPL_TEXT           = "304"
   code_RPL_UNAWAY         = "305"
   code_RPL_NOAWAY         = "306"
   if irc_default_draft == "ircu":
     code_RPL_USERIP       = "307"
   if irc_default_draft in [ "Bahamut", "hybrid" ]:
     code_RPL_WHOISADMIN   = "308"
   if irc_default_draft == "Unreal":
     code_RPL_RULESSTART   = "308"
     code_RPL_ENDOFRULES   = "309"
   if irc_default_draft == "Bahamut":
     code_WHOISSADMIN      = "309"
   if irc_default_draft == "Unreal":
     code_RPL_WHOISHELPOP  = "310"
   elif irc_default_draft == "Bahamut":
     code_RPL_WHOISSVCMSG  = "310"
   elif irc_default_draft in [ "hybrid", "plexus" ]:
     code_RPL_WHOISMODES   = "310"
   else:
     code_RPL_WHOISHELP    = "310" # Unknown
   code_RPL_WHOISUSER      = "311"
   code_RPL_WHOISSERVER    = "312"
   code_RPL_WHOISOPERATOR  = "313"
   code_RPL_WHOWASUSER     = "314"
   code_RPL_ENDOFWHO       = "315"
   code_RPL_WHOISCHANOP    = "316"
   code_RPL_WHOISIDLE      = "317"
   code_RPL_ENDOFWHOIS     = "318"
   code_RPL_WHOISCHANNELS  = "319"
   code_RPL_WHOISWORLD     = "320" # Unknown
   code_RPL_LISTSTART      = "321"
   code_RPL_LIST           = "322"
   code_RPL_LISTEND        = "323"
   code_RPL_CHANNELMODEIS  = "324"
   if irc_default_draft in ircd_Ch_se:
     code_RPL_CHANNELMLOCK = "325"
     code_RPL_CHANNELURL   = "328"
   if irc_default_draft == "Insp":
     code_RPL_CHANNELCREATED = "329"
   code_RPL_NOTOPIC        = "331"
   if irc_default_draft == "Insp":
     code_RPL_NOTOPICSET   = "331"
   code_RPL_CURRENTTOPIC   = "332"
   code_RPL_TOPICINFO      = "333"
   if irc_default_draft in ircd_iu_sn:
     code_RPL_LISTUSAGE    = "334"
   if irc_default_draft in ircd_Un_Ba:
     code_RPL_COMMANDSYNTAX = "334"
   if irc_default_draft == "Unreal":
     code_RPL_LISTSYNTAX   = "334"
     code_RPL_WHOISBOT     = "335"
   if irc_default_draft in [  "Bahamut", "Charybdis", \
    "hybrid", "seven" ]:
     code_RPL_WHOISTEXT    = "337"
   code_RPL_WHOISACTUALLY  = "338"
   if irc_default_draft in ircd_iu_Un_sn:
     code_RPL_USERIP       = "340"
   code_RPL_INVITING       = "341"
   code_RPL_SUMMONING      = "342"
   if irc_default_draft in [ "Unreal", "ratbox", "seven", \
    "Bahamut", "Charybdis", "hybrid", "plexus" ]:
     code_RPL_INVITELIST   = "346"
     code_RPL_ENDOFINVITELIST = "347"
     code_RPL_EXCEPTLIST   = "348"
     code_RPL_ENDOFEXCEPTLIST = "349"
   code_RPL_VERSION        = "351"
   code_RPL_WHOREPLY       = "352"
   code_RPL_NAMREPLY       = "353"
   if irc_default_draft == "ircu":
     code_WHOSPCRP1        = "354"
   code_RPL_KILLDONE       = "361"
   code_RPL_CLOSING        = "362"
   code_RPL_CLOSEEND       = "363"
   code_RPL_LINKS          = "364"
   code_RPL_ENDOFLINKS     = "365"
   code_RPL_ENDOFNAMES     = "366"
   code_RPL_BANLIST        = "367"
   code_RPL_ENDOFBANLIST   = "368"
   code_RPL_ENDOFWHOWAS    = "369"
   code_RPL_INFO           = "371"
   code_RPL_MOTD           = "372"
   code_RPL_INFOSTART      = "373"
   code_RPL_ENDOFINFO      = "374"
   code_RPL_MOTDSTART      = "375"
   code_RPL_ENDOFMOTD      = "376"
   code_RPL_MOTD2          = "377" # Unknown
   code_RPL_AUSTMOTD       = "378" # Austnet?
   if irc_default_draft == "Unreal":
     code_RPL_WHOISMODES   = "379"
   code_RPL_YOUREOPER      = "381"
   code_RPL_REHASHING      = "382"
   if irc_default_draft in [ "Unreal", "IRCNet", "RFC2812" ]:
     code_RPL_YOURESERVICE = "383"
   code_RPL_MYPORTIS       = "384"
   if irc_default_draft in [ "Unreal", "Bahamut", "IRCNet", \
    "Charybdis", "seven", "ratbox" ]:
     code_RPL_NOTOPERANYMORE = "385"
   if irc_default_draft == "Unreal":
     code_RPL_QLIST        = "386"
     code_RPL_ENDOFQLIST   = "387"
     code_RPL_ALIST        = "388"
     code_RPL_ENDOFALIST   = "389"
   code_RPL_TIME           = "391"
   code_RPL_USERSSTART     = "392"
   code_RPL_USERS          = "393"
   code_RPL_ENDOFUSERS     = "394"
   code_RPL_NOUSERS        = "395"
   code_ERR_NOSUCHNICK     = "401"
   code_ERR_NOSUCHSERVER   = "402"
   code_ERR_NOSUCHCHANNEL  = "403"
   code_ERR_CANNOTSENDTOCHAN = "404"
   code_ERR_TOOMANYCHANNELS = "405"
   code_ERR_WASNOSUCHNICK  = "406"
   code_ERR_TOOMANYTARGETS = "407"
   if irc_default_draft == "Unreal":
     code_ERR_NOSUCHSERVICE = "408"
   code_ERR_NOORIGIN       = "409"
   if irc_default_draft == "ircu":
     code_ERR_QUERYTOOLONG = "410"
   code_ERR_NORECIPIENT    = "411"
   code_ERR_NOTEXTTOSEND   = "412"
   code_NOOPLEVEL          = "413"
   code_ERR_WILDTOPLEVEL   = "414"
   if irc_default_draft == "ircu":
     code_QUERYTOOLONG     = "416"
   code_ERR_UNKNOWNCOMMAND = "421"
   code_ERR_NOMOTD         = "422"
   code_ERR_NOADMININFO    = "423"
   code_ERR_FILEERROR      = "424"
   if irc_default_draft == "Unreal":
     code_NOOPERMOTD       = "425"
   code_NONICKNAMEGIVEN    = "431"
   code_ERR_ERRONEUSNICKNAME = "432"
   code_ERR_NICKNAMEINUSE  = "433"
   if irc_default_draft == "Unreal":
     code_ERR_NORULES      = "434"
     code_SERVICECONFUSED  = "435"
   code_ERR_NICKCOLLISION  = "436"
   code_UNAVAILRESOURCE    = "437" # Unknown
   if irc_default_draft == "ircu":
     code_ERR_BANNICKCHANGE = "437"
     code_NICKCHANGETOOFAST = "438"
   if irc_default_draft in [ "ircu", "Bahamut", "Unreal", \
    "plexus", "snircd" ]:
     code_ERR_TARGETTOOFAST = "439"
   if irc_default_draft == "Bahamut":
     code_SERVICESDOWN     = "440"
   code_USERNOTINCHANNEL   = "441"
   code_ERR_NOTONCHANNEL   = "442"
   code_ERR_USERONCHANNEL  = "443"
   code_ERR_NOLOGIN        = "444"
   code_ERR_SUMMONDISABLED = "445"
   code_ERR_USERSDISABLED  = "446"
   if irc_default_draft in [ "Unreal", "Insp" ]:
     code_ERR_NONICKCHANGE = "447"
   code_ERR_NOTREGISTERED  = "451"
   if irc_default_draft == "Unreal":
     code_HOSTILENAME      = "455"
     code_NOHIDING         = "459"
     code_NOTFORHALFOPS    = "460"
   code_NEEDMOREPARAMS     = "461"
   code_ALREADYREGISTERED  = "462"
   code_NOPERMFORHOST      = "463"
   code_PASSWDMISMATCH     = "464"
   code_YOUREBANNEDCREEP   = "465"
   code_ERR_YOUWILLBEBANNED = "466"
   code_ERR_KEYSET         = "467"
   if irc_default_draft in ircd_iu_sn:
     code_ERR_INVALIDUSERNAME = "468"
   if irc_default_draft == "Unreal":
     code_LINKSET          = "469"
     code_LINKCHANNEL      = "470"
   code_ERR_CHANNELISFULL  = "471"
   code_ERR_UNKNOWNMODE    = "472"
   code_ERR_INVITEONLYCHAN = "473"
   code_ERR_BANNEDFROMCHAN = "474"
   code_ERR_BADCHANNELKEY  = "475"
   code_BADCHANNELMASK     = "476"
   if irc_default_draft == "Bahamut":
     code_NEEDREGGEDNICK   = "477"
   else:
     code_NOCHANMODES      = "477" # Unknown
   code_ERR_BANLISTFULL    = "478"
   if irc_default_draft == "pircd":
     code_SECUREONLYCHANNEL = "479"
   if irc_default_draft == "Unreal":
     code_LINKFULL         = "479"
     code_CANNOTKNOCK      = "480"
   code_ERR_NOPRIVILEGES   = "481"
   code_CHANOPRIVSNEEDED   = "482"
   code_ERR_CANTKILLSERVER = "483"
   if irc_default_draft == "ircu":
     code_ISCHANSERVICE    = "484"
   else:
     code_RESTRICTED       = "484" # Unknown
   if irc_default_draft == "Unreal":
     code_ERR_KILLDENY     = "485"
     code_HTMDISABLED      = "486"
     code_SECUREONLYCHAN   = "489"
   else:
    code_UNIQOPPRIVSNEEDED = "485" # Unknown
   if irc_default_draft == "Unreal":
     code_ERR_NOSWEAR      = "490"
   code_ERR_NOOPERHOST     = "491"
   code_ERR_NOSERVICEHOST  = "492"
   code_ERR_UMODEUNKNOWNFLAG = "501"
   code_ERR_USERSDONTMATCH = "502"
   if irc_default_draft == "ircu":
     code_SILELISTFULL     = "511"
   if irc_default_draft in ircd_iu_sn:
     code_ERR_NOSUCHGLINE  = "512"
   else:
     code_ERR_TOOMANYWATCH = "512" # Unknown
   if irc_default_draft in ircd_iu_sn:
     code_ERR_BADPING      = "513"
   else:
     code_ERR_NOSUCHGLINE  = "513"
   if irc_default_draft == "Unreal":
     code_ERR_NEEDPONG     = "513"
     code_ERR_NOINVITE     = "518"
     code_ERR_ADMONLY      = "519"
     code_ERR_OPERONLY     = "520"
     code_ERR_LISTSYNTAX   = "521"
     code_ERR_WHOSYNTAX    = "522"
     code_ERR_WHOLIMEXCEED = "523"
     code_ERR_OPERSPVERIFY = "524"
   if irc_default_draft in ircd_Un_Ba:
     code_RPL_LOGON        = "600"
     code_RPL_LOGOFF       = "601"
   if irc_default_draft == "Unreal":
     code_RPL_WATCHOFF     = "602"
     code_RPL_WATCHSTAT    = "603"
   if irc_default_draft == "Bahamut":
     code_RPL_NOWON        = "604"
     code_RPL_NOWOFF       = "605"
   if irc_default_draft == "Unreal":
     code_RPL_WATCHLIST    = "606"
     code_RPL_ENDOFWATCHLIST = "607"
     code_MAPMORE          = "610"
   if irc_default_draft in ircd_Un_Ba:
     code_RPL_DCCSTATUS    = "617"
   if irc_default_draft == "Unreal":
     code_RPL_DUMPING      = "640"
     code_RPL_DUMPRPL      = "641"
     code_RPL_EODUMP       = "642"
     code_RPL_SPAMCMDFWD   = "659"
   if irc_default_draft in ircd_Un_Ch_se:
     code_RPL_STARTTLS     = "670"
   if irc_default_draft in ircd_Ch_se_ra_pl:
     code_TESTMASK         = "724"
     code_TESTLINE         = "725"
     code_NOTESTLINE       = "726"
   if irc_default_draft == "plexus":
     code_RPL_ISCAPTURED   = "727"
   if irc_default_draft in ircd_Ch_se_ra:
     code_TESTMASKGECOS    = "727"
   if irc_default_draft == "plexus":
     code_ISUNCAPTURED     = "728"
   if irc_default_draft in ircd_Ch_se:
     code_QUIETLIST        = "728"
     code_ENDOFQUIETLIST   = "729"
   if irc_default_draft in ircd_Ch_se_ra:
     code_MONONLINE        = "730"
     code_MONOFFLINE       = "731"
     code_MONLIST          = "732"
     code_ENDOFMONLIST     = "733"
     code_MONLISTFULL      = "734"
     code_RSACHALLENGE2    = "740"
     code_ENDOFRSACHALLNGE2 = "741"
   if irc_default_draft in ircd_Un_Ch_se:
     code_MLOCKRESTRICTED  = "742"
   if irc_default_draft in ircd_Ch_se:
     code_ERR_INVALIDBAN   = "743"
     code_ERR_TOPICLOCK    = "744"
     code_RPL_SCANMATCHED  = "750"
     code_RPL_SCANUMODES   = "751"
   if irc_default_draft == "IRCNet":
     code_RPL_ETRACEEND    = "759"
   if irc_default_draft == "PyIRCIoT":
     code_RPL_JSON         = "851"
   if irc_default_draft in ircd_Un_Ch_se:
     code_RPL_LOGGEDIN     = "900"
     code_RPL_LOGGEDOUT    = "901"
     code_ERR_NICKLOCKED   = "902"
     code_RPL_SASLSUCCESS  = "903"
     code_ERR_SASLFAIL     = "904"
     code_ERR_SASLTOOLONG  = "905"
     code_ERR_SASLABORTED  = "906"
     code_ERR_SASLALREADY  = "907"
   if irc_default_draft in ircd_Ch_se:
     code_RPL_SASLMECHS    = "908"
   if irc_default_draft == "Insp":
     code_RPL_AUTOOPLIST      = "910"
     code_RPL_ENDOFAUTOOPLIST = "911"
     code_ERR_WORDFILTERED    = "936"
     code_RPL_SPAMFILTERLIST      = "940"
     code_ERR_ENDOFSPAMFILTERLIST = "941"
     code_RPL_EXEMPTCHANOPSLIST   = "953"
     code_ERR_ENDOFEXEMPTCHANOPSLIST = "954"
   if irc_default_draft in [ "Unreal", "plexus" ]:
     code_ERR_CANNOTDOCOMMAND  = "972"
   if irc_default_draft == "Insp":
     code_ERR_CANTUNLOADMODULE = "972"
     code_RPL_UNLOADEDMODULE   = "973"
     code_ERR_CANTLOADMODULE   = "974"
     code_RPL_LOADEDMODULE = "975"
   if irc_default_draft == "Bahamut":
     code_ERR_NUMERICERROR = "999"
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
   cmd_MOTD       = "MOTD"
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
   if irc_default_draft == "ircu":
     cmd_ACCOUNT   = "ACCOUNT"
     cmd_CLARMODE  = "CLEARMODE"
     cmd_CLOSE     = "CLOSE"
     cmd_CNOTICE   = "CNOTICE"
     cmd_CONNECT   = "CONNECT"
     cmd_CPRIVMSG  = "CPRIVMSG"
     cmd_CREATE    = "CREATE"
     cmd_DESTRUCT  = "DESCTRUCT"
     cmd_DESYNCH   = "DESYNCH"
     cmd_DIE       = "DIE"
     cmd_GLINE     = "GLINE"
     cmd_HASH      = "HASH"
     cmd_HELP      = "HELP"
     cmd_JUPE      = "JUPE"
     cmd_LUSERS    = "LUSERS"
     cmd_MAP       = "MAP"
     cmd_OPMODE    = "OPMODE"
     cmd_PRIVS     = "PRIVS"
     cmd_PROTO     = "PROTO"
     cmd_RESET     = "RESET"
     cmd_RPING     = "RPING"
     cmd_RPONG     = "RPONG"
     cmd_SET       = "SET"
     cmd_SETTIME   = "SETTIME"
     cmd_SILENCE   = "SILENCE"
     cmd_UPING     = "UPING"
     cmd_USERIP    = "USERIP"
     cmd_WALLCHOPS = "WALLCHOPS"
     cmd_WALLUSERS = "WALLUSERS"
     cmd_WALLVOICE = "WALLVOICE"
   #
   if irc_default_draft == "ircu":
     feature_AWAYLEN    = "AWAYLEN"
   feature_CASEMAPPING  = "CAEMAPPING"
   if irc_default_draft == "ircu":
     feature_CHANNELLEN = "CHANNELLEN"
   feature_CHANMODES    = "CHANMODES"
   feature_CHANTYPES    = "CHANTYPES"
   if irc_default_draft == "ircu":
     feature_CNOTICE    = "CNOTICE"
     feature_CPRIVMSG   = "CPRIVMSG"
     feature_MAXCHANLEN = "MAXCHANNELLEN"
     feature_KICKLEN    = "KICKLEN"
     feature_MODES      = "MODES"
     feature_MAXCHANS   = "MAXCHANNELS"
     feature_MAXBNANS   = "MAXBANS"
     feature_MAXNICKLEN = "MAXNICKLEN"
     feature_NETWORK    = "NETWORK"
   feature_NICKLEN      = "NICKLEN"
   feature_PREFIX       = "PREFIX"
   if irc_default_draft == "ircu":
     feature_SILENCE    = "SILENCE"
     feature_STATUSMSG  = "STATUSMSG"
     feature_TOPICLEN   = "TOPICLEN"
     feature_USERIP     = "USERIP"
     feature_WALLCHOPS  = "WALLCHOPS"
     feature_WALLVOICES = "WALLVOICES"
     feature_WHOX       = "WHOX"
   #
   featt_EMPTY  = 0
   featt_FLAGS  = 1
   featt_STRING = 2
   featt_NUMBER = 3
   #
   ident_default_ip   = '0.0.0.0'
   ident_default_port = 113
   #
   def __setattr__(self, *_):
      pass

 def __init__(self):
   #
   self.CONST = self.CONST()
   #
   super(PyLayerIRC, self).__init__()
   #
   self.__irc_nick_matcher \
    = re.compile(self.CONST.irc_nick_regexp, re.IGNORECASE)
   self.__irc_channel_matcher \
    = re.compile(self.CONST.irc_channel_regexp, re.IGNORECASE)
   #
   self.__irc_nick = self.CONST.irc_default_nick
   self.irc_user = self.irc_tolower_(self.CONST.irc_default_nick)
   self.irc_info = self.CONST.irc_default_info
   self.irc_quit = self.CONST.irc_default_quit
   self.irc_nick_old = self.__irc_nick
   self.irc_nick_base = self.__irc_nick
   self.irc_nick_try = ""
   #
   self.irc_nick_length = self.CONST.irc_max_nick_length
   self.irc_topic_length = self.CONST.irc_max_topic_length
   #
   self.irc_server = self.CONST.irc_default_server
   self.irc_port = self.CONST.irc_default_port
   self.irc_password = self.CONST.irc_default_password
   self.irc_ssl = self.CONST.irc_default_ssl
   self.irc_ident = self.CONST.irc_default_ident
   #
   # This variable is not used to connect, if you don't have a server name
   # and you want to use the IP, put its text value into self.irc_server
   self.irc_server_ip = None
   self.irc_local_port = 0
   self.irc_network_name = None
   #
   self.irc_proxy = None
   if self.CONST.irc_default_proxy != None:
     self.irc_proxy_server = self.CONST.irc_default_proxy_server
     self.irc_proxy_port = self.CONST.irc_default_proxy_port
     self.irc_proxy_password = self.CONST.irc_default_proxy_password
   #
   self.irc_status = 0
   self.irc_recon = 1
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
   self.irc_anons = []
   self.irc_nicks = []
   #
   self.irc_talk_with_strangers = \
     self.CONST.irc_default_talk_with_strangers
   self.irc_last_temporal_vuid = \
     self.CONST.api_first_temporal_vuid
   #
   self.irc_queue = [0, 0]
   self.irc_queue[self.CONST.irc_queue_input  ] = Queue(maxsize=0)
   self.irc_queue[self.CONST.irc_queue_output ] = Queue(maxsize=0)
   #
   self.irc_queue_lock = [0, 0]
   self.irc_queue_lock[self.CONST.irc_queue_input  ] = False
   self.irc_queue_lock[self.CONST.irc_queue_output ] = False
   #
   self.irc_commands = []
   self.irc_codes    = []
   self.irc_features = []
   #
   self.irc_layer_mode \
     = self.CONST.irc_layer_modes[0]
   #
   self.irc_task  = None
   self.irc_run   = False
   self.irc_debug = self.CONST.irc_default_debug
   #
   self.ident_task = None
   self.ident_run  = False
   self.ident_ip   = self.CONST.ident_default_ip
   self.ident_port = self.CONST.ident_default_port
   #
   self.irc_mid_pipeline_size \
     = self.CONST.irc_default_mid_pipeline_size
   #
   self.time_now   = datetime.datetime.now()
   self.time_ping  = self.time_now
   self.delta_time = 0
   self.delta_ping = 0
   #
   self.update_irc_host_()
   #
   # End of __init__()

 def update_irc_host_(self):
   try:
     my_ip = self.get_src_ip_by_dst_ip_(self.irc_server_ip)
     my_host = self.dns_reverse_resolver_(my_ip)
     if socket.gethostbyname(my_host) != my_ip:
       my_host = None
   except:
     my_host = None
   if my_host == None:
     try:
       my_host = socket.gethostname()
     except:
       my_host = "localhost";
   self.irc_host = my_host

 def ident_server_(self):
   def ident_ok_():
     if not self.irc_run:
       self.ident_run = False
     if not self.ident_run:
       return False
     return True
   if not self.is_ip_address_(self.ident_ip):
     return
   if not self.is_ip_port_(self.ident_port):
     return
   while (self.ident_run):
     try:
       if self.is_ipv4_address_(self.ident_ip):
         my_af_inet = socket.AF_INET
       else:
         my_af_inet = socket.AF_INET6
       my_socket = socket.socket(my_af_inet, socket.SOCK_STREAM)
       my_socket.settimeout(self.CONST.irc_ident_wait)
       my_socket.bind((self.ident_ip, self.ident_port))
       my_socket.listen(1)
     except:
       my_socket.close()
       sleep(self.CONST.irc_default_wait)
       if not ident_ok_():
         break
       continue
     while (ident_ok_()):
       try:
         try:
           my_conn, my_addr = my_socket.accept()
         except:
           break
         if not ident_ok_():
           break
         if not my_addr[0] in [ self.irc_server_ip, '127.0.0.1', '::1' ]:
           my_conn.close()
           break
         while (ident_ok_()):
           my_ready = select.select([my_socket], [], [], 0)
           if my_ready[0] == [] and ident_ok_():
             my_data = my_conn.recv(self.CONST.irc_buffer_size).decode('utf-8')
             if my_data:
               for my_char in [ '\n', '\r', ' ' ]:
                 my_data = my_data.replace(my_char, '')
               my_split = my_data.split(',')
               my_ok = True
               my_port = "%s" % self.irc_port
               if my_split[0] == "" or my_split[1] != my_port:
                 break
               if self.is_ip_port_(self.irc_local_port):
                 my_port = "%d" % self.irc_local_port
                 if my_split[0] != my_port:
                   my_ok = False
               my_out = "%s , %s : " % (my_split[0], my_split[1])
               if my_ok:
                 my_out += "USERID : UNIX : %s\n" % self.irc_user
               else:
                 my_out += "ERROR : NO-USER\n"
               my_conn.send(bytes(my_out, 'utf-8'))
               self.ident_run = False
               break
             else:
               break
           else:
             sleep(self.CONST.irc_micro_wait)
         my_conn.close()
         sleep(self.CONST.irc_micro_wait)
       except:
         my_conn.close()
       sleep(self.CONST.irc_micro_wait)
     try:
       my_socket.close()
     except:
       pass
     sleep(self.CONST.irc_micro_wait)
   #
   # End of ident_server_()

 def start_IRC_(self):
   #
   self.irc_run  = True
   self.irc_task = threading.Thread(target = self.irc_process_)
   self.irc_task.start()
   #
   # End of start_IRC_()

 def stop_IRC_(self):
   #
   self.irc_run = False
   self.ident_run = False
   self.irc_debug = False
   sleep(self.CONST.irc_micro_wait)
   self.irc_disconnect_()
   self.stop_ident_()
   if self.irc_task != None:
     sleep(self.CONST.irc_micro_wait)
     try:
       self.irc_task.join()
     except:
       pass
   #
   # End of stop_IRC_()

 def start_ident_(self):
   #
   self.ident_run = True
   self.ident_task = threading.Thread(target = self.ident_server_)
   self.ident_task.start()
   #
   # End of start_ident_()

 def stop_ident_(self):
   #
   self.ident_run = False
   if self.ident_task != None:
     sleep(self.CONST.irc_micro_wait)
     try:
       self.ident_task.join()
     except:
       pass

 def __del__(self):
   self.stop_IRC_()
   try:
     import signal
     signal.alarm(0)
   except:
     pass

 def to_log_(self, msg):
   if not self.irc_debug:
     return
   print(msg)

 def irciot_protocol_version_(self):
   return self.CONST.irciot_protocol_version

 def irciot_library_version_(self):
   return self.CONST.irciot_library_version

 def irc_handler (self, in_compatibility, in_message_pack):
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
       self.irc_add_to_queue_( \
         self.CONST.irc_queue_output, my_message, \
         self.CONST.irc_micro_wait, my_vuid)
   return True

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
   if in_vuid in self.CONST.api_vuid_not_srv:
     my_vt = in_vuid
   else:
     my_re = re.search("%s(\d+)" \
       % self.CONST.api_vuid_cfg, in_vuid)
     if my_re:
       my_vt = self.CONST.api_vuid_cfg
       my_user = self.irc_cfg_get_user_struct_by_vuid_(in_vuid)
       if my_user != None:
         ( my_uid,  my_mask, my_chan, my_opt, \
           my_ekey, my_bkey, my_lmid, \
           my_ekto, my_bkto, my_omid ) = my_user
     else:
       my_re = re.search("%s(\d+)" \
         % self.CONST.api_vuid_tmp, in_vuid)
       if my_re:
         my_vt = self.CONST.api_vuid_tmp
         my_anon = self.irc_track_get_anons_by_vuid_(in_vuid)
         if my_anon != None:
           ( an_id, an_mask, an_chan, an_opt, \
             an_ekey, an_bkey, an_lmid, \
             an_ekto, an_bkto, an_omid ) = my_anon
       else:
         return (False, None)
   if in_action == self.CONST.api_GET_LMID:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_lmid)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_lmid)
   elif in_action == self.CONST.api_SET_LMID:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         None, None, in_params, None, None, None)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, None, None, in_params, \
         None, None, None)
   elif in_action == self.CONST.api_GET_OMID:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_omid)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_omid)
   elif in_action == self.CONST.api_SET_OMID:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         None, None, None, None, None, in_params)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, None, None, None, \
         None, None, in_params)
   elif in_action == self.CONST.api_GET_VUID:
     if in_vuid in self.CONST.api_vuid_not_srv:
       my_vuid_list = []
       for my_nick in self.irc_nicks:
         (in_nick, my_mask, my_vuid, my_info) = my_nick
         if not self.irc_talk_with_strangers:
           if my_vuid[0] != self.CONST.api_vuid_cfg:
             continue
         if my_vt in [ \
           self.CONST.api_vuid_cfg, \
           self.CONST.api_vuid_tmp ]:
           if my_vuid[0] != my_vt:
             continue
         my_vuid_list.append(my_vuid)
       return (True, my_vuid_list)
   elif in_action == self.CONST.api_GET_BKEY:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_bkey)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_bkey)
   elif in_action == self.CONST.api_SET_BKEY:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         None, in_params, None, None, None, None)
       return (True, None)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, None, in_params, \
         None, None, None, None)
       return (True, None)
   elif in_action == self.CONST.api_GET_EKEY:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_ekey)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_ekey)
   elif in_action == self.CONST.api_SET_EKEY:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         in_params, None, None, None, None, None)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, in_params, None, \
         None, None, None, None)
   elif in_action == self.CONST.api_GET_EKTO:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_ekto)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_ekto)
   elif in_action == self.CONST.api_SET_EKTO:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         None, None, None, in_params, None, None)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, None, None, \
         None, in_params,  None, None)
   elif in_action == self.CONST.api_GET_BKTO:
     if my_vt == self.CONST.api_vuid_cfg:
       if my_user != None:
         return (True, my_bkto)
     elif my_vt == self.CONST.api_vuid_tmp:
       if my_anon != None:
         return (True, an_bkto)
   elif in_action == self.CONST.api_SET_BKTO:
     if my_vt == self.CONST.api_vuid_cfg:
       self.irc_track_update_ucfgs_by_vuid_(in_vuid, \
         None, None, None, None, in_params, None)
     elif my_vt == self.CONST.api_vuid_tmp:
       self.irc_track_update_anons_by_vuid_(in_vuid, \
         None, None, None, None, None, \
         None, None, in_params,  None)
   elif in_action == self.CONST.api_GET_iMTU:
     return (True, self.CONST.default_mtu)
   return (False, None)
   #
   # End of user_handler_()

 def irc_tolower_(self, in_input):
   return in_input.translate(self.CONST.irc_translation)

 def irc_tomock_(self, in_input):
   return in_input.translate(self.CONST.irc_transmocker)

 def irc_get_list_(self, in_input):
   if in_input == None:
     return []
   if isinstance(in_input, list):
     return in_input
   else:
     return [ in_input ]

 def is_irc_nick_(self, in_nick):
   if not isinstance(in_nick, str):
     return False
   if len(in_nick) > self.CONST.irc_max_nick_length:
     return False
   return self.__irc_nick_matcher.match(in_nick)

 def is_irc_channel_(self, in_channel):
   if not isinstance(in_channel, str):
     return False
   return self.__irc_channel_matcher.match(in_channel)

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

 def irc_define_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return
   self.__irc_nick = in_nick
   self.irc_nick_old = in_nick
   self.irc_nick_base = in_nick
   if self.irc_run:
     self.irc_send_(self.CONST.cmd_NICK + " " + in_nick)

 def irc_get_nick_(self):
   return self.__irc_nick

 def irc_check_mask_(self, in_from, in_mask):
   str_from = self.irc_tolower_(in_from)
   str_mask = self.irc_tolower_(in_mask).replace("\\", "\\\\")
   for char in ".$|[](){}+":
     str_mask = str_mask.replace(char, "\\" + char)
   str_mask = str_mask.replace("?", ".")
   str_mask = str_mask.replace("*", ".*")
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   my_result = irc_regexp.match(str_from)
   if my_result != None:
     if my_result:
       return True
   return False

 def irc_track_cleanup_anons_(self):
   for my_anon in self.irc_anons:
     ( an_id, an_mask, an_chan, an_opt, \
       an_ekey, an_bkey, an_lmid, \
       an_ekto, an_bkto, an_omid ) = my_anon
     an_vuid = "%s%s" % (self.CONST.api_vuid_tmp, str(an_id))
     an_ok = False
     for my_nick in self.irc_nicks:
       (in_nick, my_mask, my_vuid, my_info) = my_nick
       if my_vuid == an_vuid:
         an_ok = True
     if not an_ok:
       self.irc_anons.remove(my_anon)
   #
   # End of irc_track_cleanup_anons_()

 def irc_track_update_ucfgs_by_vuid_(self, in_vuid, \
  in_ekey, in_bkey, in_lmid, in_ekto, in_bkto, in_omid):
   if not isinstance(in_vuid, str):
     return
   # Configured users must be setup from the local config,
   # but some of the fields may be missing, in this case,
   # the needed values will be taken from the network
   for my_index, my_ucfg in enumerate(self.irc_users):
     ( my_id, my_mask, my_channel, my_opt, \
       my_ekey, my_bkey, my_lmid, \
       my_ekto, my_bkto, my_omid ) = my_ucfg
     my_vuid  = self.CONST.api_vuid_cfg
     my_vuid += "%d" % my_id
     if in_vuid == my_vuid:
       # Updating crypto keys only if they are not defined
       if my_ekey == None and isinstance(in_ekey, str):
         my_ekey = in_ekey
       if my_bkey == None and isinstance(in_bkey, str):
         my_bkey = in_bkey
       if my_ekto == None and isinstance(in_ekto, int):
         my_ekto = in_ekto
       if my_bkto == None and isinstance(in_bkto, int):
         my_bkto = in_bkto
       # Only the last message ID can be updated in pipeline
       if isinstance(in_lmid, str):
         if isinstance(my_lmid, list):
           if not in_lmid in my_lmid:
             my_lmid.append(in_lmid)
             if len(my_lmid) > self.irc_mid_pipeline_size:
               del my_lmid[0]
         else:
           my_lmid = [ in_lmid ]
       if isinstance(in_omid, str):
         if isinstance(my_omid, list):
           if not in_omid in my_omid:
             my_omid.append(in_omid)
             if len(my_omid) > self.irc_mid_pipeline_size:
               del my_omid[0]
         else:
           my_omid = [ in_omid ]
       my_cfgs = ( my_id,  my_mask, my_channel, \
         my_opt,  my_ekey, my_bkey, my_lmid, \
         my_ekto, my_bkto, my_omid )
       self.irc_users[my_index] = my_cfgs
       break
   #
   # End of irc_track_update_ucfgs_by_vuid_()

 def irc_track_update_anons_by_vuid_(self, in_vuid, \
  in_mask, in_chan, in_opt,  in_ekey, in_bkey, \
  in_lmid, in_ekto, in_bkto, in_omid ):
   if not isinstance(in_vuid, str):
     return
   my_re = re.search("%s(\d+)" \
     % self.CONST.api_vuid_tmp, in_vuid)
   if my_re:
     my_id = my_re.group(1)
   else:
     return
   my_ok = False
   for my_index, my_anon in enumerate(self.irc_anons):
     ( an_id,   my_mask, my_chan, my_opt,  \
       my_ekey, my_bkey, my_lmid, my_ekto, \
       my_bkto, my_omid ) = my_anon
     if my_id == an_id:
       my_ok = True
       if isinstance(in_mask, str):
         my_mask = in_mask
       if self.is_irc_channel_(in_chan):
         my_chan = in_chan
       if in_opt != None:
         my_opt = in_opt
       if isinstance(in_ekey, str):
         my_ekey = in_ekey
       if isinstance(in_bkey, str):
         my_bkey = in_bkey
       if isinstance(in_lmid, str):
         if isinstance(my_lmid, list):
           if not in_lmid in my_lmid:
             my_lmid.append(in_lmid)
             if len(my_lmid) > self.irc_mid_pipeline_size:
               del my_lmid[0]
         else:
           my_lmid = [ in_lmid ]
       if isinstance(in_ekto, int):
         my_ekto = in_ekto
       if isinstance(in_bkto, int):
         my_bkto = in_bkto
       if isinstance(in_omid, str):
         if isinstance(my_omid, list):
           if not in_omid in my_omid:
             my_omid.append(in_omid)
             if len(my_omid) > self.irc_mid_pipeline_size:
               del my_omid[0]
         else:
           my_omid = [ in_omid ]
       my_anon = ( an_id, my_mask, my_chan, my_opt, my_ekey, \
        my_bkey, my_lmid, my_ekto, my_bkto, my_omid )
       self.irc_anons[my_index] = my_anon
       break
   if not my_ok:
     for my_anon in self.irc_anons:
       if my_anon[1] == in_mask:
         my_ok = True
   if not my_ok:
     my_lmid = None
     my_omid = None
     if isinstance(my_lmid, str):
       my_lmid = [ in_lmid ]
     if isinstance(my_omid, str):
       my_omid = [ in_omid ]
     self.irc_anons.append( ( my_id, in_mask, \
      in_chan, in_opt,  in_ekey, in_bkey, my_lmid,
      in_ekto, in_bkto, my_omid ) )
   #
   # End of irc_track_update_anons_by_vuid_()

 def irc_track_get_anons_by_vuid_(self, in_vuid):
   if not isinstance(in_vuid, str):
     return None
   my_re = re.search("%s(\d+)" \
     % self.CONST.api_vuid_tmp, in_vuid)
   if my_re:
     my_id = my_re.group(1)
   else:
     return None
   for my_anon in self.irc_anons:
     ( an_id, an_mask, an_chan, an_opt, \
       an_ekey, an_bkey, an_lmid, \
       an_ekto, an_bkto, an_omid ) = my_anon
     if my_id == an_id:
       return my_anon
   return None
   #
   # End of irc_track_get_anons_by_vuid_()

 def irc_track_fast_nick_(self, in_nick, in_mask):
   my_ok = True
   for my_struct in self.irc_nicks:
     if my_struct[0] == in_nick:
       my_ok = False
   if my_ok:
     self.irc_track_add_nick_(in_nick, in_mask, None, None)
   #
   # End of irc_track_fast_nick_()

 def irc_track_add_nick_(self, in_nick, in_mask, in_vuid, in_info):
   if not self.is_irc_nick_(in_nick):
     return
   if in_nick == self.__irc_nick:
     return
   my_struct = self.irc_track_get_nick_struct_by_nick_(in_nick)
   if my_struct == None:
     self.irc_nicks.append((in_nick, in_mask, in_vuid, in_info))
   else:
     self.irc_track_update_nick_(in_nick, in_mask, in_vuid, in_info)
   #
   # End of irc_track_add_nick_()

 def irc_track_update_nick_(self, in_nick, in_mask, in_vuid, in_info):
   if not self.is_irc_nick_(in_nick):
     return
   if in_nick == self.__irc_nick:
     return
   for my_index, my_struct in enumerate(self.irc_nicks):
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     # comparing of the masks will be here ...
     # self.irc_check_mask_(in_from, in_mask)
     if self.irc_compare_nicks_(my_nick, in_nick):
       if isinstance(in_mask, str):
         my_mask = in_mask
         if in_vuid == None:
           my_vuid = self.irc_get_vuid_by_mask_(my_mask, self.irc_channel)
       if isinstance(in_vuid, str):
         my_vuid = in_vuid
       if isinstance(in_info, str):
         my_info = in_info
       self.irc_nicks[my_index] = (in_nick, my_mask, my_vuid, my_info)
       if self.irc_talk_with_strangers:
         self.irc_track_update_anons_by_vuid_(my_vuid, \
          my_mask, self.irc_channel, \
          None, None, None, None, None, None, None)
       break
   #
   # End of irc_track_update_nick_()

 def irc_track_clear_anons_(self):
   self.irc_anons = []

 def irc_track_clear_nicks_(self):
   self.irc_nicks = []

 def irc_track_delete_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     if self.irc_compare_nicks_(my_nick, in_nick):
       self.irc_nicks.remove(my_struct)
       if self.irc_talk_with_strangers:
         self.irc_track_cleanup_anons_()
       break
   #
   # End of irc_track_delete_nick_()

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
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     if self.irc_compare_nicks_(my_nick, in_nick):
       return my_struct
   return None

 def irc_track_get_nick_struct_by_vuid_(self, in_vuid):
   if not isinstance(in_vuid, str):
     return None
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     if my_vuid == in_vuid:
       return my_struct
   return None

 def irc_track_get_nick_by_vuid_(self, in_vuid):
   if not isinstance(in_vuid, str):
     return None
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     if my_vuid == in_vuid:
       return my_nick
   return None

 def irc_track_clarify_nicks_(self):
   for my_struct in self.irc_nicks:
     (my_nick, my_mask, my_vuid, my_info) = my_struct
     if my_mask == None or my_info == None:
       self.irc_whois_nick_(my_nick)
       if my_mask == None:
         my_mask = ""
       if my_info == None:
         my_info = ""
       self.irc_track_update_nick_(my_nick, my_mask, my_vuid, my_info)
       break
   #
   # End of irc_track_clarify_nicks_()

 def irc_cfg_get_user_mask_(self, in_position):
   if not isinstance(in_position, int):
     return None
   try:
     my_user = self.irc_users[ in_position ]
     ( my_id,   my_mask, my_chan, my_opt,  \
       my_ekey, my_bkey, my_lmid, my_ekto, \
       my_bkto, my_omid ) = my_user
     return my_mask
   except:
     return None
   #
   # End of irc_cfg_get_user_mask_()

 def irc_cfg_get_user_struct_(self, in_position):
   if not isinstance(in_position, int):
     return None
   try:
     my_struct = self.irc_users[ in_position ]
     return my_struct
   except:
     return None
   #
   # End of irc_cfg_get_user_struct_()

 def irc_cfg_get_vuid_(self, in_position):
   if not isinstance(in_position, int):
     return None
   try:
     my_user = self.irc_users[ in_position ]
     ( my_id,   my_mask, my_chan, my_opt,  \
       my_ekey, my_bkey, my_lmid, my_ekto, \
       my_bkto, my_omid ) = my_user
     return "%s%d" % (self.CONST.api_vuid_cfg, my_id)
   except:
     return None
   #
   # End of irc_cfg_get_vuid_()

 def irc_cfg_get_user_struct_by_vuid_(self, in_vuid):
   if not isinstance(in_vuid, str):
     return None
   for my_user in self.irc_users:
     my_vuid = self.CONST.api_vuid_cfg
     my_vuid += "%d" % my_user[0]
     if my_vuid == in_vuid:
       return my_user
   return None
   #
   # End of irc_cfg_get_user_strcut_by_vuid_()

 def irc_cfg_check_user_(self, in_from, in_channel, \
   irciot_parameters = None):
   if not self.is_irc_channel_(in_channel):
     return None
   in_opt  = None
   in_ekey = None
   in_bkey = None
   in_lmid = None
   in_ekto = None
   in_bkto = None
   in_omid = None
   if irciot_parameters != None:
     ( in_opt, in_ekey, in_bkey, in_lmid, \
      in_ekto, in_bkto, in_omid ) = irciot_parameters
   for my_user in self.irc_users:
     ( my_uid,  my_mask, my_chan, my_opt,  \
       my_ekey, my_bkey, my_lmid, my_ekto, \
       my_bkto, my_omid ) = my_user
     if ((in_channel == "*") or \
      (self.irc_compare_channels_(in_channel, my_chan))):
       if self.irc_check_mask_(in_from, my_mask):
         return "%s%d" % (self.CONST.api_vuid_cfg, my_uid)
   return None
   #
   # End of irc_cfg_check_user_()

 def irc_get_unique_temporal_vuid_(self, in_mask):
   max_id = self.irc_last_temporal_vuid
   tmp_id = random.randint(max_id + 1, max_id + 100)
   my_id = max_id
   for my_nick_struct in self.irc_nicks:
     (my_nick, my_mask, my_vuid, my_info) = my_nick_struct
     if not isinstance(my_vuid, str):
       continue
     my_re = re.search("%s(\d+)" \
       % self.CONST.api_vuid_tmp, my_vuid)
     if my_re:
       if my_mask == in_mask:
         return my_vuid
       my_id = my_re.group(1)
     my_id = int(my_id)
     if my_id > max_id:
       max_id = my_id
   self.irc_last_temporal_vuid = tmp_id
   return "%s%d" % (self.CONST.api_vuid_tmp, tmp_id)

 def irc_get_vuid_by_mask_(self, in_mask, in_channel):
   if not self.is_irc_channel_(in_channel):
     return None
   my_vuid = self.irc_cfg_check_user_(in_mask, in_channel)
   if my_vuid == None and self.irc_talk_with_strangers:
     my_vuid = self.irc_get_unique_temporal_vuid_(in_mask)
   return my_vuid

 def irc_get_vuid_type_(self, in_vuid):
   if isinstance(in_vuid, str):
     if len(in_vuid) > 0:
       return in_vuid[0]
   return None

 def irc_get_useropts_from_user_struct_(self, in_user_struct):
   if not isinstance(in_user_struct, tuple):
     return []
   if len(in_user_struct) < 4:
     return []
   my_opts = in_user_struct[3]
   if not isinstance(my_opts, list):
     my_opts = [ my_opts ]
   return my_opts

 def irc_disconnect_(self):
   try:
     self.irc.shutdown(2)
   except:
     pass
   self.stop_ident_()
   self.irc_track_clear_nicks_()
   self.irc_track_clear_anons_()
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
   self.to_log_("Connection closed, " \
    + "reconnecting to IRC (try: %d) ... " % self.irc_recon)
   sleep(self.CONST.irc_first_wait * self.irc_recon)
   self.irc_recon += 1
   if self.irc_recon > self.CONST.irc_recon_steps:
     self.irc_recon = 1

 def irc_send_(self, irc_out):
   try:
     if irc_out == "":
       return -1
     if self.irc_debug:
       self.to_log_("Sending to IRC: [" \
         + irc_out.replace('\r','\\r').replace('\n','\\n') + "\\n]")
     self.irc.send(bytes(irc_out + "\n", 'utf-8'))
     sleep(self.CONST.irc_micro_wait)
     irc_out = ""
     return 0
   except socket.error:
     self.to_log_("socket.error in irc_send_() ...")
     return -1
   except ValueError:
     self.to_log_("ValueError in irc_send_() ...")
     return -1
   except:
     return -1
   #
   # End of irc_send_()

 def irc_recv_(self, recv_timeout):
   try:
     time_in_recv = datetime.datetime.now()
     ready = select.select([self.irc], [], [], 0)
     my_timerest = recv_timeout
     while ready[0] == [] and my_timerest > 0 and self.irc_run:
       my_timeout = my_timerest % self.CONST.irc_latency_wait
       if my_timeout == 0:
         my_timeout = self.CONST.irc_latency_wait
       ready = select.select([self.irc], [], [], my_timeout)
       if not self.irc_run:
         return (-1, "", 0)
       if not self.irc_queue[self.CONST.irc_queue_output].empty():
         break
       my_timerest -= my_timeout
     time_out_recv = datetime.datetime.now()
     delta_time_in = self.td2ms_(time_out_recv - time_in_recv)
     delta_time = self.CONST.irc_default_wait
     if recv_timeout < self.CONST.irc_default_wait:
       delta_time = 0
     if delta_time_in < recv_timeout:
       delta_time = recv_timeout - delta_time_in
     if delta_time_in < 0:
       delta_time = 0
     if ready[0] and self.irc_run:
       irc_input = self.irc.recv(self.CONST.irc_buffer_size \
         ).decode('utf-8', 'ignore')
       if irc_input != "":
         if self.irc_debug:
           self.to_log_("Received from IRC: [" \
             + irc_input.replace('\r',"\\r").replace('\n',"\\n\n").rstrip() + "]")
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
   ret = self.irc_send_("%s %s\r" \
     % (self.CONST.cmd_PONG, irc_string[1]))
   return ret

 def irc_quit_(self):
   ret = self.irc_send_("%s :%s\r" \
     % (self.CONST.cmd_QUIT, self.irc_quit))
   sleep(self.CONST.irc_latency_wait)
   return ret

 def irc_umode_(self, in_channel, in_nicks, in_change, in_umode):
   if not self.is_irc_channel_(in_channel):
     return None
   if isinstance(in_nicks, str):
     my_nicks = [ in_nicks ]
   elif isinstance(in_nicks, list):
     my_nicks = in_nicks
   else:
     return None
   my_str = ''
   for my_nick in my_nicks:
     if not self.is_irc_nick_(my_nick):
       return None
     my_str += in_umode
   for my_nick in my_nicks:
     my_str += ' ' + my_nick
   ret = self.irc_send_("%s %s %s%s\r\n" \
     % (self.CONST.cmd_MODE, in_channel, in_change, my_str))
   return ret
   #
   # End of irc_umode_()

 def irc_op_(self, in_channel, in_nicks):
   return self.irc_umode_(in_channel, in_nicks, \
      self.CONST.irc_mode_add, self.CONST.irc_umode_op)

 def irc_deop_(self, in_channel, in_nicks):
   return self.irc_umode_(in_channel, in_nicks, \
      self.CONST.irc_mode_del, self.CONST.irc_umode_op)

 def irc_voice_(self, in_channel, in_nicks):
   return self.irc_umode_(in_channel, in_nicks, \
      self.CONST.irc_mode_add, self.CONST.irc_umode_voice)

 def irc_devoice_(self, in_channel, in_nicks):
   return self.irc_umode_(in_channel, in_nicks, \
      self.CONST.irc_mode_del, self.CONST.irc_umode_voice)

 def irc_extract_single_(self, in_string):
   try:
     irc_single = in_string.split()[3]
   except:
     return None
   return irc_single

 def irc_extract_nick_mask_(self, in_string):
   try:
     my_mask = in_string.split(' ', 1)[0][1:]
     my_nick = my_mask.split('!', 1)[0]
   except:
     my_mask = "!@"
     my_nick = ""
   return (my_nick, my_mask)

 def irc_extract_message_(self, in_string):
   try:
     irc_msg = in_string.split( \
      self.CONST.cmd_PRIVMSG, 1)[1].split(':', 1)[1]
     return irc_msg.strip()
   except:
     return None

 def irc_extract_code_params_(self, in_string):
   try:
     my_out = ""
     my_idx = 0
     for my_item in in_string.split(' '):
      if my_idx == 1 and len(my_item) != 3:
        return None
      if my_idx > 2:
        if my_out != "":
          my_out += " "
        my_out += my_item
      my_idx += 1
     return my_out
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

 def irc_random_nick_(self, in_nick, in_force = False):
   if not self.is_irc_nick_(in_nick):
     return -1
   random.seed()
   irc_nick = self.irc_tomock_(in_nick)
   if irc_nick == in_nick:
     irc_nick = in_nick + "%d" % random.randint(0, 999)
   if (self.join_retry > 2) or in_force:
     nick_length = random.randint(2, self.irc_nick_length)
     irc_nick = random.choice(self.CONST.irc_nick_first_char)
     irc_nick += ''.join( \
      random.choice(self.CONST.irc_nick_chars) \
      for i in range(nick_length - 1))
   ret = self.irc_send_(self.CONST.cmd_NICK + " " + irc_nick)
   self.irc_nick_try = irc_nick
   if ret == 0:
     self.irc_nick_old = self.__irc_nick
     self.__irc_nick = irc_nick
   return ret
   #
   # End of irc_random_nick_()

 def irc_socket_(self, in_server_name):
   try:
     my_server_ip = socket.gethostbyname(in_server_name)
     if self.is_ipv6_address_(my_server_ip):
       my_af_inet = socket.AF_INET6
     else:
       my_af_inet = socket.AF_INET
     irc_socket = socket.socket(my_af_inet, socket.SOCK_STREAM)
     if self.irc_ssl:
       irc_socket = ssl.wrap_socket(irc_socket)
   except socket.error:
     self.to_log_("Cannot create socket for IRC")
     return None
   self.irc_server_ip = my_server_ip
   self.update_irc_host_()
   return irc_socket

 def irc_connect_(self, in_server_ip, in_port):
   if self.irc_ident:
     self.start_ident_()
   try:
     self.irc.connect((in_server_ip, in_port))
   except:
     return
   self.irc_local_port = self.irc.getsockname()[1]
   # self.irc.setblocking(False)

 def irc_check_queue_(self, in_queue_id):
   old_queue_lock = self.irc_queue_lock[in_queue_id]
   if not old_queue_lock:
     check_queue = self.irc_queue[in_queue_id]
     self.irc_queue_lock[in_queue_id] = True
     if not check_queue.empty():
       (irc_message, irc_wait, irc_vuid) = check_queue.get()
       self.irc_queue_lock[in_queue_id] = old_queue_lock
       return (irc_message, irc_wait, irc_vuid)
     else:
       if old_queue_lock:
          check_queue.task_done()
     self.irc_queue_lock[in_queue_id] = old_queue_lock
   try:
     sleep(self.CONST.irc_micro_wait)
   except:
     pass
   return ("", self.CONST.irc_default_wait, self.CONST.api_vuid_all)
   #
   # End of irc_check_queue_()

 def irc_add_to_queue_(self, in_queue_id, in_message, in_wait, in_vuid):
   old_queue_lock = self.irc_queue_lock[in_queue_id]
   self.irc_queue_lock[in_queue_id] = True
   self.irc_queue[in_queue_id].put((in_message, in_wait, in_vuid))
   self.irc_queue_lock[in_queue_id] = old_queue_lock

 def irc_check_and_restore_nick_(self):
   if self.__irc_nick != self.irc_nick_base:
     if self.irc_send_(self.CONST.cmd_NICK \
      + " " + self.irc_nick_base) != -1:
      self.irc_nick_old = self.__irc_nick
      self.__irc_nick = self.irc_nick_base

 def irc_umode_by_nick_mask_(self, in_nick, in_mask, in_vuid):
   if self.irc_get_vuid_type_(in_vuid) == self.CONST.api_vuid_cfg:
     my_user = self.irc_cfg_get_user_struct_by_vuid_(in_vuid)
     if my_user == None:
       return
     my_opts = self.irc_get_useropts_from_user_struct_(my_user)
     if self.CONST.irc_aop in my_opts:
       self.irc_op_(self.irc_channel, in_nick)
     if self.CONST.irc_avo in my_opts:
       self.irc_voice_(self.irc_channel, in_nick)

 # CLIENT Hooks:

 def func_feature_network_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if in_string not in [ "", None ]:
     my_string = in_string
     my_max = self.CONST.irc_max_network_name_length
     if len(in_string) > my_max:
       my_string = in_string[:my_max]
     if not self.CONST.irc_default_network_tag in my_string:
       self.to_log_("Warning! not an IRC-IoT network, " \
        + "name: '%s'" % my_string)
     self.irc_network_name = my_string
   return (in_ret, in_init, in_wait)

 def func_feature_topiclen_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_len = int(in_string)
     if my_len > 0 and my_len < self.CONST.irc_max_topic_length:
       self.irc_topic_length = my_len
   except:
     pass
   return (in_ret, in_init, in_wait)

 def func_feature_nicklen_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_len = int(in_string)
     if my_len > 0 and my_len < self.CONST.irc_max_nick_length:
       self.irc_nick_length = my_len
   except:
     pass
   return (in_ret, in_init, in_wait)

 # incomplete
 def func_featurelist_(self, in_args):
   ''' RPL_ISUPPORT handler '''
   (in_string, in_ret, in_init, in_wait) = in_args
   my_string = self.irc_extract_code_params_(in_string)
   if my_string == None:
     return (in_ret, in_init, in_wait)
   my_string = my_string.split(':')[0]
   for my_item in my_string.split(' '):
     if my_item != "":
       my_split = my_item.split('=')
       my_param = ""
       my_feature = my_split[0]
       if len(my_split) == 2:
         my_param = my_split[1]
       for irc_pack in self.irc_features:
         (irc_feature, featt_type, irc_function)  = irc_pack
         if irc_function != None:
           if my_feature == irc_feature:
             if featt_type == self.CONST.featt_EMPTY \
              and my_param != "":
               continue
             if featt_type == self.CONST.featt_NUMBER \
              and not my_param.isdigit():
               continue
             if featt_type in [ self.CONST.featt_STRING, \
              self.CONST.featt_FLAGS ] and my_param == "":
               continue
             irc_args = (my_param, in_ret, in_init, in_wait)
             (in_ret, in_init, in_wait) = irc_function(irc_args)
   return (in_ret, in_init, in_wait)

 def func_nick_in_use_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if self.irc_random_nick_(self.irc_nick_base) == 1:
     return (-1, 0, in_wait)
   return (in_ret, in_init, in_wait)

 def func_restore_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   self.__irc_nick = self.irc_nick_old
   return (in_ret, 3, in_wait)

 def func_not_reg_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   #if self.irc_random_nick_(self.__irc_nick) == 1:
   #  return (-1, 0, in_wait)
   return (in_ret, 1, self.CONST.irc_default_wait)

 def func_banned_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if self.join_retry > 1:
     if self.irc_random_nick_(self.__irc_nick) == 1:
       self.join_retry += 1
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

 def func_no_such_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   irc_nick = self.irc_extract_single_(in_string)
   self.irc_track_delete_nick_(irc_nick)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   if irc_nick == self.irc_nick_base:
     self.irc_check_and_restore_nick_()
   my_split = in_string.split(':', 3)
   if len(my_split) > 2:
     new_nick = my_split[2]
     if self.is_irc_nick_(new_nick):
       new_mask = new_nick + irc_mask[len(irc_nick):]
       # checking the new mask with new nick for belong to the
       # registered user, and, if necessary, give him rights
       my_vuid = self.irc_get_vuid_by_mask_(new_mask, self.irc_channel)
       self.irc_umode_by_nick_mask_(new_nick, new_mask, my_vuid)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_fast_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   # ... will be calculated from warning, not by RFC 1459 ...
   in_wait = 3
   return (in_ret, in_init, in_wait)

 def func_chan_nicks_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(":")
     if my_array[0] == "":
       my_array = my_array[2].split(" ")
       for my_nick in my_array:
         if my_nick[0] == '@':
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
     if my_array[0] == "":
       my_info = my_array[2][2:]
       my_array = my_array[1].split(" ")
       my_nick = my_array[7]
       my_user = my_array[4]
       my_host = my_array[5]
       my_mask = my_nick + "!" + my_user + "@" + my_host
       my_vuid = self.irc_get_vuid_by_mask_(my_mask, self.irc_channel)
       self.irc_track_update_nick_(my_nick, my_mask, my_vuid, my_info)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait)
   #
   # End of func_who_user_()

 def func_whois_user_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   try:
     my_array = in_string.split(":")
     if my_array[0] == "":
       my_info = my_array[2]
       my_array = my_array[1].split(" ")
       my_nick = my_array[3]
       my_user = my_array[4]
       my_host = my_array[5]
       my_mask = my_nick + "!" + my_user + "@" + my_host
       my_vuid = self.irc_get_vuid_by_mask_(my_mask, self.irc_channel)
       self.irc_track_update_nick_(my_nick, my_mask, my_vuid, my_info)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait - 1)
   #
   # End of func_whois_user_()

 def func_on_join_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   my_vuid = self.irc_get_vuid_by_mask_(irc_mask, self.irc_channel)
   self.irc_umode_by_nick_mask_(irc_nick, irc_mask, my_vuid)
   self.irc_track_add_nick_(irc_nick, irc_mask, my_vuid, None)
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_part_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   self.irc_track_delete_nick_(irc_nick)
   if irc_nick == self.irc_nick_base:
     self.irc_check_and_restore_nick_()
   return (in_ret, in_init, self.CONST.irc_default_wait)

 def func_on_mode_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   (irc_nick, irc_mask) = self.irc_extract_nick_mask_(in_string)
   try:
     my_array = in_string.split(" ")
     if len(my_array) < 5:
       return (in_ret, in_init, in_wait)
     if my_array[1] != 'MODE':
       return (in_ret, in_init, in_wait)
     my_channel = my_array[2]
     if not self.is_irc_channel_(my_channel):
       return (in_ret, in_init, in_wait)
     my_mode_string = my_array[3]
     if len(my_mode_string) < 2:
       return (in_ret, in_init, in_wait)
     for my_char in my_mode_string:
       if not my_char in self.CONST.irc_all_modes_chars:
         return (in_ret, in_init, in_wait)
     my_change = self.CONST.irc_mode_add
     my_index = 0
     my_nick = False
     my_unban = None
     for my_char in my_mode_string:
       if my_char in self.CONST.irc_change_modes:
         my_change = my_char
       elif my_char in self.CONST.irc_user_modes:
         my_mask = my_array[my_index + 4]
         self.to_log_( \
           "mode change '%s','%s' for '%s' on '%s'" \
           % (my_change, my_char, my_mask, my_channel))
         if ((my_change == self.CONST.irc_mode_del) \
           and (my_char == self.CONST.irc_umode_op)):
           my_vuid = self.irc_get_vuid_by_mask_(irc_mask, \
             self.irc_channel)
           self.irc_umode_by_nick_mask_(my_mask, irc_mask, \
             my_vuid)
         if ((my_change == self.CONST.irc_mode_add) \
           and (my_char == self.CONST.irc_umode_ban)):
           my_mask_array = my_mask.split("!")
           my_pseudo  = self.__irc_nick + '!'
           my_pseudo += my_mask_array[1]
           if self.irc_check_mask_(my_pseudo, my_mask):
             my_nick = True
           for my_item in self.irc_nicks:
             (n_nick, n_mask, n_vuid, n_info) = my_item
             if n_vuid[0] == self.CONST.api_vuid_cfg:
               if self.irc_check_mask_(n_mask, my_mask):
                 my_unban = n_vuid
                 break
           if not my_unban:
             for my_num in range(len(self.irc_users)):
               u_mask = self.irc_cfg_get_user_mask_(my_num)
               if isinstance(u_mask, str):
                 u_mask = u_mask.replace('*', '_')
                 if self.irc_check_mask_(u_mask, my_mask):
                   u_vuid = self.irc_cfg_get_vuid_(my_num)
                   if u_vuid != None:
                     my_unban = u_vuid
                     break
         my_index += 1
       elif my_char in self.CONST.irc_channel_modes:
         self.to_log_( \
           "mode change '%s','%s' for '%s'" \
           % (my_change, my_char, my_channel))
       elif my_char in self.CONST.irc_extra_modes:
         my_extra = my_array[my_index + 4]
         self.to_log_( \
           "mode change '%s','%s' extra '%s' for '%s'" \
           % (my_change, my_char, my_extra, my_channel))
         my_index += 1
       if my_unban != None:
         my_user = self.irc_cfg_get_user_struct_by_vuid_(my_unban)
         if my_user != None:
           my_opts = self.irc_get_useropts_from_user_struct_(my_user)
           if self.CONST.irc_unban in my_opts:
             in_ret = self.irc_send_("%s %s %s%s %s\r\n" \
               % (self.CONST.cmd_MODE, my_channel, \
                  self.CONST.irc_mode_del, \
                  self.CONST.irc_umode_ban, my_mask))
       if my_nick:
         self.irc_random_nick_(self.__irc_nick, True)
       if my_nick or my_unban:
         return (in_ret, in_init, 0)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait)
   #
   # End of func_on_mode_()

 def func_on_error_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if in_string.find("Closing ") or in_string.find("imeout"):
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
   self.irc_codes = [
    (C.code_ERR_NICKNAMEINUSE, "ERR_NICKNAMEINUSE", self.func_nick_in_use_),
    (C.code_ERR_NOTREGISTERED, "ERR_NOTREGISTERED", self.func_not_reg_),
    (C.code_ERR_BANNEDFROMCHAN,"ERR_BANNEDFROMCHAN",self.func_banned_),
    (C.code_NICKCHANGETOOFAST, "NICKCHANGETOOFAST", self.func_fast_nick_),
    (C.code_RPL_NAMREPLY,      "RPL_NAMREPLY",      self.func_chan_nicks_),
    (C.code_RPL_ISUPPORT,      "RPL_ISUPPORT",      self.func_featurelist_),
    (C.code_RPL_WHOISUSER,     "RPL_WHOISUSER",     self.func_whois_user_),
    (C.code_RPL_ENDOFNAMES,    "RPL_ENDOFNAMES",    self.func_end_nicks_),
    (C.code_RPL_WHOREPLY,      "RPL_WHOREPLY",      self.func_who_user_),
    (C.code_ERR_NOSUCHNICK,    "ERR_NOSUCHNICK",    self.func_no_such_nick_),
    (C.code_ERR_CHANNELISFULL, "ERR_CHANNELISFULL", self.func_banned_),
    (C.code_ERR_BADCHANNELKEY, "ERR_BADCHANNELKEY", self.func_banned_),
    (C.code_ERR_ERRONEUSNICKNAME,"ERR_ERRONEUSNICKNAME",self.func_nick_in_use_),
    (C.code_ERR_NOSUCHCHANNEL, "ERR_NOSUCHCHANNEL", self.func_banned_),
    (C.code_ERR_NOSUCHSERVER,  "ERR_NOSUCHSERVER",  None),
    (C.code_ERR_CANNOTSENDTOCHAN,"ERR_CANNOTSENDTOCHAN",None),
    (C.code_ERR_TOOMANYCHANNELS,"ERR_TOOMANYCHANNELS",None),
    (C.code_ERR_WASNOSUCHNICK, "ERR_WASNOSUCHNICK", None),
    (C.code_ERR_TARGETTOOFAST, "ERR_TARGETTOOFAST", None),
    (C.code_ERR_TOOMANYTARGETS,"ERR_TOOMANYTARGETS",None),
    (C.code_ERR_NOORIGIN,      "ERR_NOORIGIN",      None),
    (C.code_ERR_NORECIPIENT,   "ERR_NORECIPIENT",   None),
    (C.code_ERR_NOTEXTTOSEND,  "ERR_NOTEXTTOSEND",  None),
    (C.code_NOOPLEVEL,         "NOOPLEVEL",         None),
    (C.code_ERR_WILDTOPLEVEL,  "ERR_WILDTOPLEVEL",  None),
    (C.code_ERR_UNKNOWNCOMMAND,"ERR_UNKNOWNCOMMAND",None),
    (C.code_ERR_NOMOTD,        "ERR_NOMOTD",        None),
    (C.code_ERR_NOADMININFO,   "ERR_NOADMININFO",   None),
    (C.code_ERR_FILEERROR,     "ERR_FILEERROR",     None),
    (C.code_NONICKNAMEGIVEN,   "NONICKNAMEGIVEN",   None),
    (C.code_ERR_NICKCOLLISION, "ERR_NICKCOLLISION", None),
    (C.code_UNAVAILRESOURCE,   "UNAVAILRESOURCE",   None),
    (C.code_USERNOTINCHANNEL,  "USERNOTINCHANNEL",  None),
    (C.code_ERR_NOTONCHANNEL,  "ERR_NOTONCHANNEL",  None),
    (C.code_ERR_NOLOGIN,       "ERR_NOLOGIN",       None),
    (C.code_ERR_SUMMONDISABLED,"ERR_SUMMONDISABLED",None),
    (C.code_ERR_USERSDISABLED, "ERR_USERSDISABLED", None),
    (C.code_NEEDMOREPARAMS,    "NEEDMOREPARAMS",    None),
    (C.code_ERR_USERSDONTMATCH,"ERR_USERSDONTMATCH",None),
    (C.code_ALREADYREGISTERED, "ALREADYREGISTERED", None),
    (C.code_PASSWDMISMATCH,    "PASSWDMISMATCH",    None),
    (C.code_YOUREBANNEDCREEP,  "YOUREBANNEDCREEP",  None),
    (C.code_ERR_YOUWILLBEBANNED,"ERR_YOUWILLBEBANNED",None),
    (C.code_ERR_KEYSET,        "ERR_KEYSET",        None),
    (C.code_ERR_UNKNOWNMODE,   "ERR_UNKNOWNMODE",   None),
    (C.code_ERR_INVITEONLYCHAN,"ERR_INVITEONLYCHAN",None),
    (C.code_BADCHANNELMASK,    "BADCHANNELMASK",    None),
    (C.code_ERR_BANLISTFULL,   "ERR_BANLISTFULL",   None),
    (C.code_ERR_NOPRIVILEGES,  "ERR_NOPRIVILEGES",  None),
    (C.code_ERR_CANTKILLSERVER,"ERR_CANTKILLSERVER",None),
    (C.code_UNIQOPPRIVSNEEDED, "UNIQOPPRIVSNEEDED", None),
    (C.code_ERR_NOOPERHOST,    "ERR_NOOPERHOST",    None),
    (C.code_ERR_NOSERVICEHOST, "ERR_NOSERVICEHOST", None),
    (C.code_ERR_UMODEUNKNOWNFLAG,"ERR_UMODEUNKNOWNFLAG", None) ]

   if self.CONST.irc_default_draft == "PyIRCIoT":
     self.irc_codes.extend( [
      (C.code_RPL_JSON,        "RPL_JSON",          None) ] )

   elif self.CONST.irc_default_draft == "ircu":
     self.irc_codes.extend( [
      (C.code_ERR_BANNICKCHANGE,"ERR_BANNICKCHANGE",self.func_restore_nick_),
      (C.code_RPL_USERIP,      "RPL_USERIP",        None),
      (C.code_ERR_INVALIDUSERNAME,"ERR_INVALIDUSERNAME",None) ] )

   elif self.CONST.irc_default_draft == "Unreal":
     self.irc_codes.extend( [
      (C.code_ERR_NONICKCHANGE,"ERR_NONICKCHANGE",self.func_restore_nick_),
      (C.code_RPL_WHOISBOT,    "RPL_WHOISBOT",      None),
      (C.code_RPL_USERIP,      "RPL_USERIP",        None),
      (C.code_RPL_REDIR,       "RPL_REDIR",         None)
      (C.code_ERR_NOSUCHSERVICE,"ERR_NOSUCHSERVICE",None),
      (C.code_ERR_NOINVITE,    "ERR_NOINVITE",      None),
      (C.code_RPL_COMMANDSYNTAX,"RPL_COMMANDSYNTAX",None),
      (C.code_RPL_STARTLS,     "RPL_STARTLS",       None),
      (C.code_RPL_DCCSTATUS,   "RPL_DCCSTATUS",     None),
      (C.code_RPL_TEXT,        "RPL_TEXT",          None) ] )

   elif self.CONST.irc_default_draft == "Bahamut":
     self.irc_codes.extend( [
      (C.code_RPL_STATSCLONE,  "RPL_STATSCLONE",    None),
      (C.code_RPL_TEXT,        "RPL_TEXT",          None) ] )

   elif self.CONST.irc_default_draft == "Insp":
     self.irc_codes.extend( [
      (C.code_RPL_AUTOOPLIST,  "RPL_AUTOOPLIST",    None),
      (C.code_RPL_ENDOFAUTOOPLIST,"RPL_ENDOFAUTOOPLIST",None),
      (C.code_ERR_WORDFILTERED,"ERR_WORDFILTERED",  None) ] )

   else: # Unknown extending
     self.irc_codes.extend( [
      (C.code_NOCHANMODES,    "NOCHANMODES",        None),
      (C.code_RESTRICTED,     "RESTRICTED",         None) ] )
   #
   if self.irc_layer_mode == self.CONST.irc_layer_modes[0]:
     self.irc_commands = [
      (C.cmd_INVITE,  None),
      (C.cmd_JOIN,    self.func_on_join_),
      (C.cmd_KICK,    self.func_on_kick_),
      (C.cmd_KILL,    self.func_on_kill_),
      (C.cmd_MODE,    self.func_on_mode_),
      (C.cmd_NICK,    self.func_on_nick_),
      (C.cmd_NOTICE,  None),
      (C.cmd_PART,    self.func_on_part_),
      (C.cmd_PONG,    None),
      (C.cmd_PRIVMSG, None),
      (C.cmd_QUIT,    self.func_on_quit_),
      (C.cmd_ERROR,   self.func_on_error_) ]
   #
   else: # RFC 2813
     self.irc_cmmands = [
      (C.cmd_PASS,    None), (C.cmd_SERVER,     None),
      (C.cmd_NICK,    None), (C.cmd_QUIT,       None),
      (C.cmd_SQUIT,   None), (C.cmd_JOIN,       None),
      (C.cmd_NJOIN,   None), (C.cmd_MODE,       None),
      (C.cmd_LINKS,   None), (C.cmd_KILL,       None),
      (C.cmd_NAMES,   None), (C.cmd_INVITE,     None),
      (C.cmd_STATS,   None), (C.cmd_CONNECT,    None),
      (C.cmd_TRACE,   None), (C.cmd_ADMIN,      None),
      (C.cmd_WHO,     None), (C.cmd_INFO,       self.func_on_srv_info_),
      (C.cmd_WHOIS,   None), (C.cmd_WHOWAS,     None),
      (C.cmd_AWAY,    None), (C.cmd_RESTART,    None),
      (C.cmd_SUMMON,  None), (C.cmd_USERS,      None),
      (C.cmd_WALLOPS, None), (C.cmd_USERHOST,   None),
      (C.cmd_TOPIC,   None), (C.cmd_KICK,       None),
      (C.cmd_PONG,    None), (C.cmd_PART,       None),
      (C.cmd_ERROR,   None), (C.cmd_PRIVMSG,    None),
      (C.cmd_PUBMSG,  None), (C.cmd_PUBNOTICE,  None),
      (C.cmd_NOTICE,  None), (C.cmd_PRIVNOTICE, None),
      (C.cmd_ISON,    None), (C.cmd_REHASH,     None) ]
   #
   self.irc_features = [
      (C.feature_CASEMAPPING, C.featt_STRING, None),
      (C.feature_CHANMODES,   C.featt_FLAGS,  None),
      (C.feature_CHANTYPES,   C.featt_FLAGS,  None),
      (C.feature_NICKLEN,     C.featt_NUMBER, self.func_feature_nicklen_),
      (C.feature_PREFIX,      C.featt_FLAGS,  None) ]

   if self.CONST.irc_default_draft == "ircu":
     self.irc_features.extend( [
      (C.feature_AWAYLEN,     C.featt_NUMBER, None),
      (C.feature_CHANNELLEN,  C.featt_NUMBER, None),
      (C.feature_CNOTICE,     C.featt_EMPTY,  None),
      (C.feature_CPRIVMSG,    C.featt_EMPTY,  None),
      (C.feature_MAXCHANLEN,  C.featt_NUMBER, None),
      (C.feature_KICKLEN,     C.featt_NUMBER, None),
      (C.feature_MODES,       C.featt_NUMBER, None),
      (C.feature_MAXCHANS,    C.featt_NUMBER, None),
      (C.feature_MAXBNANS,    C.featt_NUMBER, None),
      (C.feature_MAXNICKLEN,  C.featt_NUMBER, self.func_feature_nicklen_),
      (C.feature_NETWORK,     C.featt_STRING, self.func_feature_network_),
      (C.feature_SILENCE,     C.featt_NUMBER, None),
      (C.feature_STATUSMSG,   C.featt_FLAGS,  None),
      (C.feature_TOPICLEN,    C.featt_NUMBER, self.func_feature_topiclen_),
      (C.feature_USERIP,      C.featt_EMPTY,  None),
      (C.feature_WALLCHOPS,   C.featt_EMPTY,  None),
      (C.feature_WALLVOICES,  C.featt_EMPTY,  None),
      (C.feature_WHOX,        C.featt_EMPTY,  None) ] )
   #
   # End of init_rfc1459_()

 def irc_output_all_(self, in_messages_packs, in_wait = None):
   if not isinstance(in_messages_packs, list):
     return
   if not isinstance(in_wait, int) and \
      not isinstance(in_wait, float):
     in_wait = self.CONST.irc_default_wait
   for my_pack in in_messages_packs:
     (my_messages, my_vuid) = my_pack
     if isinstance(my_messages, str):
       my_messages = [ my_messages ]
     if isinstance(my_messages, list):
       for my_message in my_messages:
         self.irc_add_to_queue_( \
           self.CONST.irc_queue_output, \
           my_message, in_wait, my_vuid)
   #
   # End of irc_output_all_()

 def irc_process_(self):
   #
   self.init_rfc1459_()
   #
   try:
     irc_init = 0
     irc_wait = self.CONST.irc_first_wait
     irc_input_buffer = ""
     irc_ret = 0
     irc_vuid = "%s0" % self.CONST.api_vuid_cfg

     self.delta_time = 0

     # app.run(host='0.0.0.0', port=50000, debug=True)
     # must be FIXed for Unprivileged user

     self.irc = self.irc_socket_(self.irc_server)

     while (self.irc_run):
     
       if not self.irc:
         sleep(self.CONST.irc_first_wait)
         self.irc = self.irc_socket_(self.irc_server)
         irc_init = 0

       if irc_init < 6:
         irc_init += 1

       if irc_init == 1:
         try:
           self.irc_connect_(self.irc_server_ip, self.irc_port)
         except socket.error:
           self.irc_disconnect_()
           self.irc = self.irc_socket_(self.irc_server)
           irc_init = 0

       elif irc_init == 2:
         if self.irc_password:
           self.irc_send_(self.CONST.cmd_PASS \
            + " " + self.irc_password)
         self.irc_user = self.irc_tolower_(self.__irc_nick)
         if self.irc_send_(self.CONST.cmd_USER \
          + " " + self.irc_user \
          + " " + self.irc_host + " 1 :" \
          + self.irc_info) == -1:
           irc_init = 0

       elif irc_init == 3:
         self.join_retry = 0
         if self.irc_send_(self.CONST.cmd_NICK \
          + " " + self.__irc_nick) == -1:
           irc_init = 0

       elif irc_init == 4:
         irc_wait = self.CONST.irc_default_wait
         self.join_retry += 1
         if self.irc_send_(self.CONST.cmd_JOIN \
          + " " + self.irc_channel + str(" " \
          + self.irc_chankey if self.irc_chankey else "")) == -1:
           irc_init = 0

       elif irc_init == 5:
         irc_wait = self.CONST.irc_default_wait
         self.join_retry += 1
         if self.irc_send_(self.CONST.cmd_JOIN \
          + " " + self.irc_channel + "%s\r" % str(" " \
          + self.irc_chankey if self.irc_chankey else "")) == -1:
           irc_init = 0

       elif irc_init == 6:
         self.ident_run = False

       if irc_init > 0:
         (irc_ret, irc_input_buffer, self.delta_time) \
          = self.irc_recv_(irc_wait)

       irc_wait = self.CONST.irc_default_wait

       if self.delta_time > 0:
         irc_wait = self.delta_time
       else:
         if irc_init == 6:
           self.irc_track_clarify_nicks_()

       if irc_ret == -1:
         self.irc_reconnect_()
         irc_input_buffer = ""
         irc_init = 0
         self.irc = self.irc_socket_(self.irc_server)

       for irc_input_split in re.split(r'[\r\n]', irc_input_buffer):

         if irc_input_split == "":
           irc_input_buff = ""
           continue

         if irc_input_split[:5] == self.CONST.cmd_PING + " ":
           self.delta_ping \
             = self.td2ms_(self.time_now - self.time_ping)
           self.time_ping = self.time_now
           if self.irc_pong_(irc_input_split) == -1:
             irc_ret = -1
             irc_init = 0
           else:
             self.irc_track_clarify_nicks_()

         try:
           irc_input_cmd = irc_input_split.split(' ')[1]
         except:
           irc_input_cmd = ""

         if irc_input_split[0] == ':':
           for irc_cod_pack in self.irc_codes:
             (irc_code, code_name, irc_function)  = irc_cod_pack
             if irc_function != None:
                if irc_input_cmd == irc_code:
                  irc_args = (irc_input_split, \
                   irc_ret, irc_init, irc_wait)
                  (irc_ret, irc_init, irc_wait) = irc_function(irc_args)

         for irc_cmd_pack in self.irc_commands:
           (irc_cmd, irc_function) = irc_cmd_pack
           if irc_function != None:
              if irc_input_cmd == irc_cmd:
                irc_args = (irc_input_split, \
                 irc_ret, irc_init, irc_wait)
                (irc_ret, irc_init, irc_wait) = irc_function(irc_args)

         if irc_input_cmd == self.CONST.cmd_PRIVMSG \
          or irc_input_split == "":

           irc_nick = ""
           irc_mask = "!@"
           irc_vuid = None
           irc_message = None

           if irc_input_split != "":
             (irc_nick, irc_mask) \
               = self.irc_extract_nick_mask_(irc_input_split)
             self.irc_track_fast_nick_(irc_nick, irc_mask)

             self.time_now = datetime.datetime.now()
             irc_message = self.irc_extract_message_(irc_input_split)

           if ((irc_message == None) and (irc_input_buffer == "")):
             self.time_now = datetime.datetime.now()
             irc_message = ""

           if irc_message != None:
             irc_vuid = self.irc_get_vuid_by_mask_(irc_mask, self.irc_channel)

           if ((irc_vuid != None) and (irc_init > 3) \
             and (self.is_json_(irc_message))):
             if self.irc_talk_with_strangers:
               self.irc_track_update_anons_by_vuid_(irc_vuid, \
                irc_mask, self.irc_channel, \
                None, None, None, None, None, None, None)
             self.irc_add_to_queue_(self.CONST.irc_queue_input, \
              irc_message, self.CONST.irc_default_wait, irc_vuid)

           irc_input_split = ""

         irc_input_buff = ""

       if irc_init > 5:
          (irc_message, irc_wait, irc_vuid) \
           = self.irc_check_queue_(self.CONST.irc_queue_output)
          irc_message = str(irc_message)
          if irc_message != "":
             my_private = False
             if irc_vuid != self.CONST.api_vuid_all:
               my_nick = self.irc_track_get_nick_by_vuid_(irc_vuid)
               if self.is_irc_nick_(my_nick):
                 my_private = True
             if my_private:
               self.irc_send_(self.CONST.cmd_PRIVMSG + " " \
                 + my_nick + " :" + irc_message)
             else:
               self.irc_send_(self.CONST.cmd_PRIVMSG + " " \
                 + self.irc_channel + " :" + irc_message)
          irc_message = ""
          if self.td2ms_(self.time_now - self.time_ping) \
           > self.delta_ping * 2 and self.delta_ping > 0:
             if self.irc_who_channel_(self.irc_channel) == -1:
               irc_init = 0
             else:
               self.irc_check_and_restore_nick_()
             self.delta_ping = 0

   except socket.error:
     self.irc_disconnect()
     irc_init = 0
   #
   # End of irc_process_()

