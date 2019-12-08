'''
'' PyIRCIoT (PyLayerIRC class)
''
'' Copyright (c) 2018-2019 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

# Those Global options override default behavior and memory usage
#
DO_debug_library = False

import socket
import select
import json
import random
import re
import threading
import ssl
from queue import Queue
from time import sleep

if DO_debug_library:
  from pprint import pprint

import datetime

class PyLayerIRC(object):

 class CONST(object):
   #
   irciot_protocol_version = '0.3.29'
   #
   irciot_library_version  = '0.0.147'
   #
   # Bot specific constants
   #
   irc_first_wait = 28
   irc_micro_wait = 0.12
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
      [ irc_aop ], None, None, None, None, None, None ) ]
   #
   irc_default_talk_with_strangers = False
   irc_first_temporal_vuid = 1000
   #
   api_GET_LMID = 101 # Get last Message ID
   api_SET_LMID = 102 # Set last Message ID
   api_GET_OMID = 111 # Get Own last Message ID
   api_SET_OMID = 112 # Set Own last Message ID
   api_GET_EKEY = 301 # Get Encryption Key
   api_SET_EKEY = 302 # Set Encryption Key
   api_GET_EKTO = 351 # Get Encryption Key Timeout
   api_SET_EKTO = 352 # Set Encyrption Key Timeout
   api_GET_BKEY = 501 # Get Blockchain key
   api_SET_BKEY = 502 # Set Blockchain Key
   api_GET_BKTO = 551 # Get Blockchain Key Timeout
   api_SET_BKTO = 552 # Set Blockchain Key Timeout
   api_GET_VUID = 700 # Get list of Virutal User IDs
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
   api_vuid_CRS = 'sC' # Сryptographic Repository Service
   api_vuid_GDS = 'sD' # Global Dictionary Service
   api_vuid_GRS = 'sR' # Global Resolving Service
   api_vuid_GTS = 'sT' # Global Time Service
   #
   api_vuid_RoS = 'sr' # Primary Routing Service
   #
   irc_queue_input  = 0
   irc_queue_output = 1
   #
   irc_recon_steps  = 8
   #
   irc_input_buffer = ""
   #
   irc_buffer_size  = 2048
   #
   irc_layer_modes  = [ "CLIENT", "SERVICE", "SERVER" ]
   #
   irc_default_nick_retry = 3600 # in seconds
   #
   # According RFC 1459
   #
   irc_ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
   irc_ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
   irc_ascii_letters = irc_ascii_lowercase + irc_ascii_uppercase
   irc_ascii_digits = "0123456789"
   irc_special_chars = "-[]\\`^{}"
   irc_nick_first_char = irc_ascii_letters + irc_special_chars
   irc_nick_chars = irc_ascii_letters \
     + irc_ascii_digits + irc_special_chars
   irc_translation = "".maketrans( \
     irc_ascii_uppercase + "[]\\^",
     irc_ascii_lowercase + "{}|~")
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
   irc_max_nick_length = 15
   #
   irc_default_draft   = "Undernet"
   #
   # "RFC1459", "Undernet",  "Unreal", "Bahamut",
   # "Inspl",   "Hybrid",    "RusNet", "Shadow",
   # "ircu",    "Nefarious", "Rock",   "Synchronet",
   # "solid",   "PieXus",    "ratbox", "Charybdis"
   # "pure",    "Rubl",      "ngl",    "ConfRoom"
   #
   default_mtu = 480
   if irc_default_draft == 'Undernet':
     default_mtu = 450
   #
   code_WELCOME            = "001"
   code_YOURHOST           = "002"
   code_CREATED            = "003"
   code_MYINFO             = "004"
   code_FEATURELIST        = "005" # Unknown
   if irc_default_draft == 'Undernet':
     code_MAP              = "005"
     code_MAPMORE          = "006"
     code_MAPEND           = "007"
     code_SNOMASK          = "008"
     code_STATMEMTOT       = "009"
     code_STATMEM          = "010"
   code_TRACELINK          = "200"
   code_TRACECONNECTING    = "201"
   code_TRACEHANDSHAKE     = "202"
   code_TRACEUNKNOWN       = "203"
   code_TRACEOPERATOR      = "204"
   code_TRACEUSER          = "205"
   code_TRACESERVER        = "206"
   code_TRACESERVICE       = "207"
   code_TRACENEWTYPE       = "208"
   code_TRACECLASS         = "209"
   code_TRACERECONNECT     = "210"
   code_STATSLINKINFO      = "211"
   code_STATSCOMMANDS      = "212"
   code_STATSCLINE         = "213"
   code_STATSNLINE         = "214"
   code_STATSILINE         = "215"
   code_STATSKLINE         = "216"
   code_STATSQLINE         = "217"
   code_STATSYLINE         = "218"
   code_ENDOFSTATS         = "219"
   if irc_default_draft == 'Unreal':
     code_STATSBLINE       = "220"
   code_UMODEIS            = "221"
   if irc_default_draft == 'Unreal':
     code_SQLINE_NICK      = "222"
     code_STATSGLINE       = "223"
     code_STATSTLINE       = "224"
     code_STATSELINE       = "225"
     code_STATSNLINE       = "226"
     code_STATSVLINE       = "227"
   code_SERVICEINFO        = "231"
   code_ENDOFSERVICES      = "232"
   code_SERVICE            = "233"
   code_SERVLIST           = "234"
   code_SERVLISTEND        = "235"
   code_STATSLLINE         = "241"
   code_STATSUPTIME        = "242"
   code_STATSOLINE         = "243"
   code_STATSHLINE         = "244"
   code_STATSSLINE         = "245" # Unknown
   if irc_default_draft == 'Undernet':
     code_STATSTLINE       = "246"
     code_STATSGLINE       = "247"
   if irc_default_draft == 'Unreal':
     code_STATSXLINE       = "247"
   if irc_default_draft == 'Undernet':
     code_STATSULINE       = "248"
   code_STATSDEBUG         = "249" # Unknown
   code_LUSERCONNS         = "250"
   code_LUSERCLIENT        = "251"
   code_LUSEROP            = "252"
   code_LUSERUNKNOWN       = "253"
   code_LUSERCHANNELS      = "254"
   code_LUSERME            = "255"
   code_ADMINME            = "256"
   code_ADMINLOC1          = "257"
   code_ADMINLOC2          = "258"
   code_ADMINEMAIL         = "259"
   code_TRACELOG           = "261"
   code_ENDOFTRACE         = "262"
   code_TRYAGAIN           = "263"
   code_N_LOCAL            = "265"
   code_N_GLOBAL           = "266"
   if irc_default_draft == 'Undernet':
     code_SILELIST         = "271"
     code_ENDOFSILELIST    = "272"
     code_STATUSDLINE      = "275"
     code_GLIST            = "280"
     code_ENDOFGLIST       = "281"
   if irc_default_draft == 'Unreal':
     code_HELPHDR          = "290"
     code_HELPOP           = "291"
     code_HELPTLR          = "292"
     code_HELPHLP          = "293"
     code_HELPFWD          = "294"
     code_HELPIGN          = "295"
   code_NONE               = "300"
   code_AWAY               = "301"
   code_USERHOST           = "302"
   code_ISON               = "303"
   if irc_default_draft == 'Bahamut':
     code_RPL_TEXT         = "304"
   code_UNAWAY             = "305"
   code_NOAWAY             = "306"
   if irc_default_draft == 'Undernet':
     code_USERIP           = "307"
   if irc_default_draft == 'Unreal':
     code_RULESSTART       = "308"
     code_ENDOFRULES       = "309"
   code_WHOISHELP          = "310" # Unknown
   code_WHOISUSER          = "311"
   code_WHOISSERVER        = "312"
   code_WHOISOPERATOR      = "313"
   code_WHOWASUSER         = "314"
   code_ENDOFWHO           = "315"
   code_WHOISCHANOP        = "316"
   code_WHOISIDLE          = "317"
   code_ENDOFWHOIS         = "318"
   code_WHOISCHANNELS      = "319"
   code_WHOISWORLD         = "320" # Unknown
   code_LISTSTART          = "321"
   code_LIST               = "322"
   code_LISTEND            = "323"
   code_CHANNELMODEIS      = "324"
   code_CHANNELCREATE      = "329"
   code_NOTOPIC            = "331"
   code_CURRENTTOPIC       = "332"
   code_TOPICINFO          = "333"
   if irc_default_draft == 'Undernet':
     code_LISTUSAGE        = "334"
   if irc_default_draft == 'Unreal':
     code_WHOISBOT         = "335"
   code_INVITING           = "341"
   code_SUMMONING          = "342"
   if irc_default_draft == 'Unreal':
     code_INVITELIST       = "346"
     code_ENDOFINVITELIST  = "347"
     code_EXCEPTLIST       = "348"
     code_ENDOFEXCEPTLIST  = "349"
   code_VERSION            = "351"
   code_WHOREPLY           = "352"
   code_NAMREPLY           = "353"
   if irc_default_draft == 'Undernet':
     code_WHOSPCRP1        = "354"
   code_KILLDONE           = "361"
   code_CLOSING            = "362"
   code_CLOSEEND           = "363"
   code_LINKS              = "364"
   code_ENDOFLINKS         = "365"
   code_ENDOFNAMES         = "366"
   code_BANLIST            = "367"
   code_ENDOFBANLIST       = "368"
   code_ENDOFWHOWAS        = "369"
   code_INFO               = "371"
   code_MOTD               = "372"
   code_INFOSTART          = "373"
   code_ENDOFINFO          = "374"
   code_MOTDSTART          = "375"
   code_ENDOFMOTD          = "376"
   code_MOTD2              = "377" # Unknown
   code_AUSTMOTD           = "378" # Unknown
   if irc_default_draft == 'Unreal':
     code_WHOISMODES       = "379"
   code_YOUREOPER          = "381"
   code_REHASHING          = "382"
   if irc_default_draft == 'Unreal':
     code_YOURESERVICE     = "383"
   code_MYPORTIS           = "384"
   code_NOTOPERANYMORE     = "385" # Unknown
   if irc_default_draft == 'Unreal':
     code_QLIST            = "386"
     code_ENDOFQLIST       = "387"
     code_ALIST            = "388"
     code_ENDOFALIST       = "389"
   code_TIME               = "391"
   code_USERSSTART         = "392"
   code_USERS              = "393"
   code_ENDOFUSERS         = "394"
   code_NOUSER             = "395"
   code_NOSUCHNICK         = "401"
   code_NOSUCHSERVER       = "402"
   code_NOSUCHCHANNEL      = "403"
   code_CANNOTSENDTOCHAN   = "404"
   code_TOOMANYCHANNELS    = "405"
   code_WASNOSUCHNICK      = "406"
   code_TOOMANYTARGETS     = "407"
   if irc_default_draft == 'Unreal':
     code_NOSUCHSERVICE    = "408"
   code_NOORIGIN           = "409"
   code_NORECIPIENT        = "411"
   code_NOTEXTTOSEND       = "412"
   code_NOOPLEVEL          = "413"
   code_WILDTOPLEVEL       = "414"
   if irc_default_draft == 'Undernet':
     code_QUERYTOOLONG     = "416"
   code_UNKNOWNCOMMAND     = "421"
   code_NOMOTD             = "422"
   code_NOADMININFO        = "423"
   code_FILEERROR          = "424"
   if irc_default_draft == 'Unreal':
     code_NOOPERMOTD       = "425"
   code_NONICKNAMEGIVEN    = "431"
   code_ERRONEUSNICKNAME   = "432"
   code_NICKNAMEINUSE      = "433"
   if irc_default_draft == 'Unreal':
     code_NORULES          = "434"
     code_SERVICECONFUSED  = "435"
   code_NICKCOLLISION      = "436"
   code_UNAVAILRESOURCE    = "437" # Unknown
   if irc_default_draft == 'Undernet':
     code_BANNICKCHANGE    = "437"
     code_NICKCHANGETOOFAST = "438"
     code_TARGETTOOFAST    = "439"
   if irc_default_draft == 'Bahamut':
     code_SERVICESDOWN     = "440"
   code_USERNOTINCHANNEL   = "441"
   code_NOTONCHANNEL       = "442"
   code_USERONCHANNEL      = "443"
   code_NOLOGIN            = "444"
   code_SUMMONDISABLED     = "445"
   code_USERSDISABLED      = "446"
   if irc_default_draft == 'Unreal':
     code_NONICKCHANGE     = "447"
   code_NOTREGISTERED      = "451"
   if irc_default_draft == 'Unreal':
     code_HOSTILENAME      = "455"
     code_NOHIDING         = "459"
     code_NOTFORHALFOPS    = "460"
   code_NEEDMOREPARAMS     = "461"
   code_ALREADYREGISTERED  = "462"
   code_NOPERMFORHOST      = "463"
   code_PASSWDMISMATCH     = "464"
   code_YOUREBANNEDCREEP   = "465"
   code_YOUWILLBEBANNED    = "466"
   code_KEYSET             = "467"
   if irc_default_draft == 'Undernet':
     code_INVALIDUSERNAME  = "468"
   if irc_default_draft == 'Unreal':
     code_LINKSET          = "469"
     code_LINKCHANNEL      = "470"
   code_CHANNELISFULL      = "471"
   code_UNKNOWNMODE        = "472"
   code_INVITEONLYCHAN     = "473"
   code_BANNEDFROMCHAN     = "474"
   code_BADCHANNELKEY      = "475"
   code_BADCHANNELMASK     = "476"
   if irc_default_draft == 'Bahamut':
     code_NEEDREGGEDNICK   = "477"
   else:
     code_NOCHANMODES      = "477" # Unknown
   code_BANLISTFULL        = "478"
   if irc_default_draft == 'pircd':
     code_SECUREONLYCHANNEL = "479"
   if irc_default_draft == 'Unreal':
     code_LINKFULL         = "479"
     code_CANNOTKNOCK      = "480"
   code_NOPRIVILEGES       = "481"
   code_CHANOPRIVSNEEDED   = "482"
   code_CANTKILLSERVER     = "483"
   code_RESTRICTED         = "484" # Unknown
   if irc_default_draft == 'Undernet':
     code_ISCHANSERVICE    = "484"
   code_UNIQOPPRIVSNEEDED  = "485" # Unknown
   if irc_default_draft == 'Unreal':
     code_KILLDENY         = "485"
     code_HTMDISABLED      = "486"
     code_SECUREONLYCHAN   = "489"
   code_NOOPERHOST         = "491"
   code_NOSERVICEHOST      = "492"
   code_UMODEUNKNOWNFLAG   = "501"
   code_USERSDONTMATCH     = "502"
   if irc_default_draft == 'Undernet':
     code_SILELISTFULL     = "511"
     code_NOSUCHGLINE      = "513"
     code_BADPING          = "513"
   code_TOOMANYWATCH       = "512" # Unknown
   if irc_default_draft == 'Unreal':
     code_NOINVITE         = "518"
     code_ADMONLY          = "519"
     code_OPERONLY         = "520"
     code_LISTSYTAX        = "521"
     code_OPERSPVERIFY     = "524"
     code_RPL_LOGON        = "600"
     code_RPL_LOGOFF       = "601"
     code_RPL_WATCHOFF     = "602"
     code_RPL_WATCHSTAT    = "603"
   if irc_default_draft == 'Bahamut':
     code_RPL_NOWON        = "604"
     code_RPL_NOWOFF       = "605"
   if irc_default_draft == 'Unreal':
     code_RPL_WATCHLIST    = "606"
     code_RPL_ENDOFWATCHLIST = "607"
     code_MAPMORE          = "610"
     code_RPL_DUMPING      = "640"
     code_RPL_DUMPRPL      = "641"
     code_RPL_EODUMP       = "642"
   if irc_default_draft == 'Bahamut':
     code_NUMERICERROR     = "999"
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
   if irc_default_draft == 'Undernet':
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
     cmd_WALLUSERS = "WALLUSERS"
     cmd_WALLCHOPS = "WALLCHOPS"
     cmd_WALLVOICE = "WALLVOICE"
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
   self.irc_user = self.irc_tolower_(self.CONST.irc_default_nick)
   self.irc_info = self.CONST.irc_default_info
   self.irc_quit = self.CONST.irc_default_quit
   self.irc_nick_old = self.irc_nick
   self.irc_nick_base = self.irc_nick
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
     self.CONST.irc_first_temporal_vuid
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
   self.irc_layer_mode \
     = self.CONST.irc_layer_modes[0]
   #
   self.irc_task  = None
   self.irc_run   = False
   self.irc_debug = self.CONST.irc_default_debug
   #
   self.irc_mid_pipeline_size \
     = self.CONST.irc_default_mid_pipeline_size
   #
   self.time_now   = datetime.datetime.now()
   self.time_ping  = self.time_now
   self.delta_time = 0
   self.delta_ping = 0
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
   if isinstance(in_message_pack, list):
     for my_pack in in_message_pack:
       (my_message, my_vuid) = my_pack
       self.irc_add_to_queue_( \
         self.CONST.irc_queue_output, my_message, \
         self.CONST.irc_micro_wait, my_vuid)
   else:
     (my_message, my_vuid) = in_message_pack
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
   if in_vuid in [ \
     self.CONST.api_vuid_cfg, \
     self.CONST.api_vuid_tmp, \
     self.CONST.api_vuid_all ]:
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
   if   in_action == self.CONST.api_GET_LMID:
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
     if in_vuid in [ \
       self.CONST.api_vuid_all, \
       self.CONST.api_vuid_cfg, \
       self.CONST.api_vuid_tmp ]:
       my_vuid_list = []
       for my_nick in self.irc_nicks:
         (in_nick, my_mask, my_vuid, my_info) = my_nick
         if not self.irc_talk_with_strangers:
           if my_vuid[0] != self.CONST.api_vuid_cfg:
             continue
         if my_vt in [ \
           self.CONST.api_vuid_cfg,
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
   return (False, None)
   #
   # End of user_handler_()

 def irc_tolower_(self, in_input):
   return in_input.translate(self.CONST.irc_translation)

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

 def irc_define_nick_(self, in_nick):
   if not self.is_irc_nick_(in_nick):
     return
   self.irc_nick = in_nick
   self.irc_nick_old = in_nick
   self.irc_nick_base = in_nick
   if self.irc_run:
     self.irc_send_(self.CONST.cmd_NICK + " " + in_nick)

 def irc_check_mask_(self, in_from, in_mask):
   str_from = self.irc_tolower_(in_from)
   str_mask = self.irc_tolower_(in_mask).replace("\\", "\\\\")
   for char in ".$|[](){}+":
     str_mask = str_mask.replace(char, "\\" + char)
   str_mask = str_mask.replace("?", ".")
   str_mask = str_mask.replace("*", ".*")
   irc_regexp = re.compile(str_mask, re.IGNORECASE)
   return irc_regexp.match(str_from)

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
   if in_nick == self.irc_nick:
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
   if in_nick == self.irc_nick:
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
     if ((my_mask == None) or (my_info == None)):
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

 def is_json_(self, in_message):
   if not isinstance(in_message, str):
     return False
   try:
     json_object = json.loads(in_message)
   except ValueError:
     return False
   return True

 def irc_disconnect_(self):
   try:
     self.irc.shutdown(2)
   except:
     pass
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

 def irc_td2ms_(self, td):
   return td.days * 86400 + td.seconds + td.microseconds / 1000000

 def irc_send_(self, irc_out):
   try:
     if irc_out == "":
       return -1
     if self.irc_debug:
       self.to_log_("Sending to IRC: [" + irc_out + "]")
     self.irc.send(bytes(irc_out + "\n", 'UTF-8'))
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
     ready = select.select([self.irc], [], [], 0)
     my_timerest = recv_timeout
     while ready[0] == [] and my_timerest > 0:
       my_timeout = my_timerest % self.CONST.irc_latency_wait
       if my_timeout == 0:
         my_timeout = self.CONST.irc_latency_wait
       ready = select.select([self.irc], [], [], my_timeout)
       if not self.irc_queue[self.CONST.irc_queue_output].empty():
         break
       my_timerest -= my_timeout
     time_out_recv = datetime.datetime.now()
     delta_time_in = self.irc_td2ms_(time_out_recv - time_in_recv)
     delta_time = self.CONST.irc_default_wait
     if recv_timeout < self.CONST.irc_default_wait:
       delta_time = 0
     if delta_time_in < recv_timeout:
       delta_time = recv_timeout - delta_time_in
     if delta_time_in < 0:
       delta_time = 0
     if ready[0]:
       irc_input \
        = self.irc.recv(self.CONST.irc_buffer_size).decode('UTF-8')
       irc_input = irc_input.strip("\n")
       irc_input = irc_input.strip("\r")
       if irc_input != "":
         if self.irc_debug:
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
   ret = self.irc_send_("%s %s\r\n" \
     % (self.CONST.cmd_PONG, irc_string[1]))
   return ret

 def irc_quit_(self):
   ret = self.irc_send_("%s :%s\r\n" \
     % (self.CONST.cmd_QUIT, self.irc_quit))
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
   irc_nick = in_nick + "%d" % random.randint(0, 999)
   if (self.join_retry > 2) or in_force:
     nick_length = random.randint(2, self.irc_nick_length)
     irc_nick = random.choice(self.CONST.irc_nick_first_char)
     irc_nick += ''.join( \
      random.choice(self.CONST.irc_nick_chars) \
      for i in range(nick_length))
   ret = self.irc_send_(self.CONST.cmd_NICK + " " + irc_nick)
   if ret == 0:
     self.irc_nick_old = self.irc_nick
     self.irc_nick = irc_nick
   return ret
   #
   # End of irc_random_nick_()

 def irc_socket_(self):
   try:
     irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     if self.irc_ssl:
       irc_socket = ssl.wrap_socket(irc_socket)
   except socket.error:
     self.to_log_("Cannot create socket for IRC")
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
       (irc_message, irc_wait, irc_vuid) = check_queue.get()
       self.irc_queue_lock[queue_id] = old_queue_lock
       return (irc_message, irc_wait, irc_vuid)
     else:
       if old_queue_lock:
          check_queue.task_done()
     self.irc_queue_lock[queue_id] = old_queue_lock
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

 def irc_check_and_return_nick_(self):
   if self.irc_nick != self.irc_nick_base:
     if self.irc_send_(self.CONST.cmd_NICK \
      + " " + self.irc_nick_base) != -1:
      self.irc_nick_old = self.irc_nick
      self.irc_nick = self.irc_nick_base

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

 def func_nick_in_use_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if self.irc_random_nick_(self.irc_nick_base) == 1:
     return (-1, 0, in_wait)
   return (in_ret, in_init, in_wait)

 def func_restore_nick_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   self.irc_nick = self.irc_nick_old
   return (in_ret, 3, in_wait)

 def func_not_reg_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   #if (self.irc_random_nick_(self.irc_nick) == 1):
   #  return (-1, 0, in_wait)
   return (in_ret, 1, self.CONST.irc_default_wait)

 def func_banned_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if self.join_retry > 1:
     if (self.irc_random_nick_(self.irc_nick) == 1):
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
     self.irc_check_and_return_nick_()
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
     self.irc_check_and_return_nick_()
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
           my_pseudo  = self.irc_nick + '!'
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
         self.irc_random_nick_(self.irc_nick, True)
       if my_nick or my_unban:
         return (in_ret, in_init, 0)
   except:
     return (in_ret, in_init, in_wait)
   return (in_ret, in_init, self.CONST.irc_default_wait)
   #
   # End of func_on_mode_()

 def func_on_error_(self, in_args):
   (in_string, in_ret, in_init, in_wait) = in_args
   if in_string.find("Closing ") or in_string.find(" timeout"):
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
    (C.code_NOSUCHNICK,       "NOSUCHNICK",       self.func_no_such_nick_), \
    (C.code_CHANNELISFULL,    "CHANNELISFULL",    self.func_banned_), \
    (C.code_BADCHANNELKEY,    "BADCHANNELKEY",    self.func_banned_), \
    (C.code_ERRONEUSNICKNAME, "ERRONEUSNICKNAME", self.func_nick_in_use_), \
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
    (C.code_UNKNOWNMODE,      "UNKNOWNMODE",      None), \
    (C.code_INVITEONLYCHAN,   "INVITEONLYCHAN",   None), \
    (C.code_BADCHANNELMASK,   "BADCHANNELMASK",   None), \
    (C.code_BANLISTFULL,      "BANLISTFULL",      None), \
    (C.code_NOPRIVILEGES,     "NOPRIVILEGES",     None), \
    (C.code_CANTKILLSERVER,   "CANTKILLSERVER",   None), \
    (C.code_UNIQOPPRIVSNEEDED,"UNIQOPPRIVSNEEDED",None), \
    (C.code_NOOPERHOST,       "NOOPERHOST",       None), \
    (C.code_NOSERVICEHOST,    "NOSERVICEHOST",    None), \
    (C.code_UMODEUNKNOWNFLAG, "UMODEUNKNOWNFLAG", None) ]

   if self.CONST.irc_default_draft == 'Undernet':
     self.irc_codes.extend( [ \
      (C.code_BANNICKCHANGE,  "BANNICKCHANGE",    self.func_restore_nick_), \
      (C.code_USERIP,         "USERIP",           None), \
      (C.code_INVALIDUSERNAME,"INVALIDUSERNAME",  None) ] )

   elif self.CONST.irc_default_draft == 'Unreal':
     self.irc_codes.extend( [ \
      (C.code_NONICKCHANGE,   "NONICKCHANGE",     self.func_restore_nick_), \
      (C.code_WHOISBOT,       "WHOISBOT",         None), \
      (C.code_NOSUCHSERVICE,  "NOSUCHSERVICE",    None), \
      (C.code_NOINVITE,       "NOINVITE",         None) ] )

   else: # Unknown extending
     self.irc_codes.extend( [ \
      (C.code_NOCHANMODES,    "NOCHANMODES",      None), \
      (C.code_RESTRICTED,     "RESTRICTED",       None) ] )
   #
   if self.irc_layer_mode == self.CONST.irc_layer_modes[0]:
     self.irc_commands = [ \
      (C.cmd_INVITE,  None), \
      (C.cmd_JOIN,    self.func_on_join_), \
      (C.cmd_KICK,    self.func_on_kick_), \
      (C.cmd_KILL,    self.func_on_kill_), \
      (C.cmd_MODE,    self.func_on_mode_), \
      (C.cmd_NICK,    self.func_on_nick_), \
      (C.cmd_NOTICE,  None), \
      (C.cmd_PART,    self.func_on_part_), \
      (C.cmd_PONG,    None), \
      (C.cmd_PRIVMSG, None), \
      (C.cmd_QUIT,    self.func_on_quit_), \
      (C.cmd_ERROR,   self.func_on_error_) ]
   #
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
      (C.cmd_ISON,    None), (C.cmd_REHASH,     None) ]
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
       self.irc_add_to_queue_( \
         self.CONST.irc_queue_output, \
         my_messages, in_wait, my_vuid)
     elif isinstance(my_messages, list):
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

     self.irc = self.irc_socket_()

     while (self.irc_run):
     
       if not self.irc:
         sleep(self.CONST.irc_first_wait)
         self.irc = self.irc_socket_()
         irc_init = 0

       if irc_init < 6:
         irc_init += 1

       if irc_init == 1:
         try:
           self.irc_connect_(self.irc_server, self.irc_port)
         except socket.error:
           self.irc_disconnect_()
           self.irc = self.irc_socket_()
           irc_init = 0

       elif irc_init == 2:
         if self.irc_password:
           self.irc_send_(self.CONST.cmd_PASS \
            + " " + self.irc_password)
         self.irc_user = self.irc_tolower_(self.irc_nick)
         if self.irc_send_(self.CONST.cmd_USER \
          + " " + self.irc_user \
          + " " + self.irc_host + " 1 :" \
          + self.irc_info) == -1:
           irc_init = 0

       elif irc_init == 3:
         self.join_retry = 0
         if self.irc_send_(self.CONST.cmd_NICK \
          + " " + self.irc_nick) == -1:
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
          + " " + self.irc_channel + "%s\r\n" % str(" " \
          + self.irc_chankey if self.irc_chankey else "")) == -1:
           irc_init = 0

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
         self.irc = self.irc_socket_()

       irc_prefix = ":" + self.irc_server + " "
       irc_prefix_len = len(irc_prefix)

       for irc_input_split in re.split(r'[\r\n]', irc_input_buffer):

         if irc_input_split[:5] == self.CONST.cmd_PING + " ":
           self.delta_ping \
             = self.irc_td2ms_(self.time_now - self.time_ping)
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

         if irc_input_split[:irc_prefix_len] == irc_prefix:
           # Parse codes only from valid server
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
          if self.irc_td2ms_(self.time_now - self.time_ping) \
           > self.delta_ping * 2 and self.delta_ping > 0:
             if self.irc_who_channel_(self.irc_channel) == -1:
               irc_init = 0
             else:
               self.irc_check_and_return_nick_()
             self.delta_ping = 0

   except socket.error:
     self.irc_disconnect()
     irc_init = 0
   #
   # End of irc_process_()

