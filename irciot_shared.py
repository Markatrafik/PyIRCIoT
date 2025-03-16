
import socket
import struct
import ifaddr
import ipaddress
import datetime
import sys
import os
try:
 import json
except:
 import simplejson as json

class irciot_shared_(object):

 class CONST(object):
   #
   ### IRC-IoT API:
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
   api_GET_iMTU = 600 # Get initial Maximum Transmission Unit
   api_GET_iENC = 601 # Get initial Encoding
   api_GET_VUID = 700 # Get list of Virutal User IDs
   #
   api_vuid_cfg = 'c' # VUID prefix for users from config
   api_vuid_tmp = 't' # VUID prefix for temporal users
   api_vuid_srv = 's' # VUID prefix for IRC-IoT Services
   api_vuid_all = '*' # Means All users VUIDs when sending messages
   #
   api_vuid_any = [ api_vuid_cfg, api_vuid_tmp, api_vuid_srv ]
   api_vuid_not_srv = [ api_vuid_cfg, api_vuid_tmp, api_vuid_all ]
   #
   api_vuid_self = 'c0' # Default preconfigured VUID
   #
   ### Basic IRC-IoT Services
   #
   api_vuid_CRS = 'sC' # Cryptographic Repository Service
   api_vuid_GDS = 'sD' # Global Dictionary Service
   api_vuid_GRS = 'sR' # Global Resolving Service
   api_vuid_GTS = 'sT' # Global Time Service
   #
   api_vuid_PRS = 'sr' # Primary Routing Service
   #
   api_first_temporal_vuid = 1000
   #
   # for Python 3.x: 19 Jan 3001 08:00 UTC
   api_epoch_maximal = 32536799999
   #
   ### For IoT Bot creation:
   #
   default_bot_name = 'iotBot'
   default_bot_python = 'python3'
   default_bot_background_parameter = 'background'
   #
   default_max_config_size = 1024 * 1024 # bytes
   #
   ### OS depended:
   #
   os_aix     = 'AIX'
   os_android = 'Android'
   os_freebsd = 'FreeBSD'
   os_hpux    = 'HP-UX'
   os_hurd    = 'GNU'
   os_irix    = 'IRIX'
   os_linux   = 'Linux'
   os_macosx  = 'Darwin'
   os_minix3  = 'Minix3'
   os_netbsd  = 'NetBSD'
   os_openbsd = 'OpenBSD'
   os_os400   = 'OS400'
   os_solaris = 'SunOS'
   os_windows = 'WindowsNT'
   os_qnx     = 'QNX'
   #
   os_all_UNIX = [
    os_aix,     os_hpux,   os_freebsd, os_linux,
    os_macosx,  os_minix3, os_netbsd,  os_openbsd,
    os_solaris, os_qnx ]
   #
   os_linux_proc_ipv4_route = '/proc/net/route'
   os_linux_proc_ipv6_route = '/proc/net/ipv6_route'
   #
   ### Human Languages (ISO 639-1):
   #
   hl_Arabic   = 'ar'
   hl_Armenian = 'hy'
   hl_Basque   = 'eu'
   hl_Bashkir  = 'ba'
   hl_Bengali  = 'bn'
   hl_Chinese  = 'cn' # Simplified
   hl_Church   = 'cu' # Slavonic
   hl_Croatian = 'hr'
   hl_Czech    = 'cz'
   hl_Danish   = 'dk'
   hl_Deutsch  = 'de'
   hl_English  = 'en'
   hl_Estonian = 'ee'
   hl_Finnish  = 'fi'
   hl_French   = 'fr'
   hl_Georgian = 'ka'
   hl_Greek    = 'gr'
   hl_Hrvatski = 'hr'
   hl_Hebrew   = 'il'
   hl_Ido      = 'io'
   hl_Irish    = 'ga'
   hl_Italian  = 'it'
   hl_Kazakh   = 'kk'
   hl_Korean   = 'ko'
   hl_Kurdish  = 'ku'
   hl_Kyrgyz   = 'ky'
   hl_Latvian  = 'lv'
   hl_Maltese  = 'mt'
   hl_Nauru    = 'na'
   hl_Persian  = 'fa'
   hl_Polish   = 'pl'
   hl_Pushto   = 'ps'
   hl_Romanian = 'ro'
   hl_Russian  = 'ru'
   hl_Sanskrit = 'sa'
   hl_Serbian  = 'rs'
   hl_Slovak   = 'sk'
   hl_Somali   = 'so'
   hl_Swahili  = 'sw'
   hl_Swedish  = 'se'
   hl_Spanish  = 'es'
   hl_Tamil    = 'ta'
   hl_Tajik    = 'tg'
   hl_Thai     = 'th'
   hl_Turkish  = 'tr'
   hl_Turkmen  = 'tk'
   hl_Urdu     = 'ur'
   hl_Uzbek    = 'uz'
   hl_Japanese = 'jp'
   #
   hl_default = hl_English
   #
   enc_ASCII = "ascii"
   for enc in [ "7", "8", "8a", "16u" ]:
     locals()["enc_ArmSCII{}".format(enc.upper())] \
      = "armscii-{}".format(enc)
   for enc in [ "CN", "TW", "JP", "KR" ]:
     locals()["enc_EUC{}".format(enc)] = "EUC-{}".format(enc)
   for enc in [ "c", "r", "ru", "t", "u" ]:
     locals()["enc_KOI8{}".format(enc.upper())] \
      = "koi8-{}".format(enc)
   for enc in [  7,  8, 16, 32 ]:
     locals()["enc_UTF{}".format(enc)] = "utf-{}".format(enc)
   for enc in [  273,  278,  280,  297,  423,  437,  737,  775,
     850,  851,  852,  855,  856,  857,  858,  860,  861,  862,
     863,  865,  866,  869,  874,  875,  880,  905,  922,  935,
    1025, 1097, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257,
    1258, 1259 ]:
     locals()["enc_{}".format(enc)] = "cp{}".format(enc)
   for enc in [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15 ]:
     locals()["enc_ISO{}".format(enc)] = "iso-8859-{}".format(enc)
   enc_ISO22 = "iso-2022"
   #
   enc_aliases = {
    enc_ASCII : [ "cp-367", "cp367", "us-ascii" ],
    enc_273   : [ "cp-273", "ibm273", "ibm-273" ],
    enc_278   : [ "cp-278", "ibm278", "ibm-278" ],
    enc_280   : [ "cp-280", "ibm280", "ibm-280" ],
    enc_297   : [ "cp-297", "ibm297", "ibm-297" ],
    enc_423   : [ "cp-423", "ibm423", "ibm-423" ],
    enc_437   : [ "cp-437", "ibm437", "ibm-437" ],
    enc_737   : [ "cp-737", "windows-737", "ibm737", "ibm-737" ],
    enc_775   : [ "cp-775", "windows-755", "ibm775", "ibm-775" ],
    enc_850   : [ "cp-850", "windows-850", "ibm850", "ibm-850" ],
    enc_851   : [ "cp-851", "ibm851", "ibm-851" ],
    enc_852   : [ "cp-852", "windows-852", "ibm852", "ibm-852" ],
    enc_855   : [ "cp-855", "windows-855", "ibm855", "ibm-855" ],
    enc_856   : [ "cp-856", "ibm856", "ibm-856" ],
    enc_857   : [ "cp-857", "windows-857", "ibm857", "ibm-857" ],
    enc_858   : [ "cp-858", "windows-858", "ibm-858" ],
    enc_860   : [ "cp-860", "ibm860", "ibm-860" ],
    enc_861   : [ "cp-861", "windows-861", "ibm861", "ibm-861" ],
    enc_862   : [ "cp-862", "windows-862", "dos-862", "ibm862" ],
    enc_863   : [ "cp-863", "ibm863", "ibm-863" ],
    enc_865   : [ "cp-865", "ibm865", "ibm-865" ],
    enc_866   : [ "cp-866", "windows-866", "ibm866", "ibm-866" ],
    enc_869   : [ "cp-869", "windows-869", "ibm869", "ibm-869" ],
    enc_874   : [ "cp-874", "windows-874"  ],
    enc_875   : [ "cp-875", "ibm875", "ibm-875" ],
    enc_880   : [ "cp-880", "ibm880", "ibm-880" ],
    enc_905   : [ "cp-905", "ibm905", "ibm-905" ],
    enc_922   : [ "cp-922", "ibm922", "ibm-922" ],
    enc_935   : [ "cp-935", "ibm935", "ibm-935" ],
    enc_1025  : [ "cp-1025", "ibm1025", "ibm-1025" ],
    enc_1097  : [ "cp-1097", "ibm1097", "ibm-1097" ],
    enc_1250  : [ "cp-1250", "windows-1250", "cp5346" ],
    enc_1251  : [ "cp-1251", "windows-1251", "cp5347" ],
    enc_1252  : [ "cp-1252", "windows-1252", "cp5348" ],
    enc_1253  : [ "cp-1253", "windows-1253", "cp5349" ],
    enc_1254  : [ "cp-1254", "windows-1254", "cp5350" ],
    enc_1255  : [ "cp-1255", "windows-1255" ],
    enc_1256  : [ "cp-1256", "windows-1256" ],
    enc_1257  : [ "cp-1257", "windows-1257" ],
    enc_1258  : [ "cp-1258", "windows-1258" ],
    enc_1259  : [ "cp-1259", "windows-1259" ],
    enc_EUCCN : [ "euc_cn" ],
    enc_EUCTW : [ "euc_tw" ],
    enc_EUCJP : [ "euc_jp" ],
    enc_EUCKR : [ "euc_kr", "cp970" ],
    enc_ISO1  : [ "iso8859-1", "latin1", "ibm819", "ibm-819" ],
    enc_ISO2  : [ "iso8859-2", "latin2", "ibm912", "ibm-912" ],
    enc_ISO3  : [ "iso8859-3", "latin3", "ibm913", "ibm-913" ],
    enc_ISO4  : [ "iso8859-4", "latin4", "ibm914", "ibm-914" ],
    enc_ISO5  : [ "iso8859-5", "cp915", "ibm915", "ibm-915" ],
    enc_ISO6  : [ "iso8859-6", "cp1089", "cp-1089" ],
    enc_ISO7  : [ "iso8859-7", "greek8", "ibm813", "ibm-813" ],
    enc_ISO8  : [ "iso8859-8", "hebrew8" ],
    enc_ISO9  : [ "iso8859-9", "latin5", "ibm920", "ibm-920" ],
    enc_ISO10 : [ "iso8859-10", "latin6" ],
    enc_ISO13 : [ "iso8859-13", "cp921", "cp-921" ],
    enc_ISO15 : [ "iso8859-15", "latin9", "ibm923", "ibm-923" ],
    enc_ISO22 : [ "iso2022" ],
    enc_KOI8R : [ "koi8r", "cp878", "ibm-878" ],
    enc_KOI8U : [ "koi8u", "cp1168", "ibm-1168" ],
    enc_UTF7  : [ "utf7"  ],
    enc_UTF8  : [ "utf8"  ],
    enc_UTF16 : [ "utf16" ],
    enc_UTF32 : [ "utf32" ],
   }
   #
   default_encoding = enc_UTF8
   #
   hl_old_enc = {
    hl_Arabic   : [ enc_ISO6 ],
    hl_Armenian : [ enc_ArmSCII7, enc_ArmSCII8, enc_ArmSCII8A ],
    hl_Basque   : [ enc_ISO1 ],
    hl_Bashkir  : [],
    hl_Bengali  : [],
    hl_Chinese  : [ enc_935, enc_EUCTW ],
    hl_Church   : [],
    hl_Croatian : [ enc_ISO2 ],
    hl_Czech    : [ enc_ISO2 ],
    hl_Danish   : [ enc_ISO1 ],
    hl_Deutsch  : [ enc_ISO1, enc_273 ],
    hl_English  : [ enc_ISO1, enc_437, enc_UTF7, enc_ASCII ],
    hl_Estonian : [ enc_ISO15, enc_ISO13, enc_922, enc_775 ],
    hl_Finnish  : [ enc_ISO1, enc_278 ],
    hl_French   : [ enc_ISO1, enc_863, enc_297 ],
    hl_Georgian : [],
    hl_Greek    : [ enc_ISO7, enc_423, enc_737, enc_869,
     enc_875, enc_1253 ],
    hl_Hrvatski : [ enc_ISO1 ],
    hl_Hebrew   : [ enc_ISO8, enc_862, enc_856, enc_1255 ],
    hl_Ido      : [],
    hl_Irish    : [ enc_ISO14 ],
    hl_Italian  : [ enc_ISO1, enc_280 ],
    hl_Kazakh   : [],
    hl_Korean   : [ enc_EUCKR ],
    hl_Kurdish  : [],
    hl_Kyrgyz   : [],
    hl_Latvian  : [ enc_1257, enc_ISO13, enc_775 ],
    hl_Maltese  : [ enc_ISO3 ],
    hl_Nauru    : [],
    hl_Persian  : [ enc_1097 ],
    hl_Polish   : [ enc_ISO2 ],
    hl_Pushto   : [],
    hl_Romanian : [ enc_ISO2 ],
    hl_Russian  : [ enc_ISO5, enc_855, enc_866, enc_1251,
     enc_880, enc_KOI8C, enc_KOI8R, enc_KOI8RU ],
    hl_Sanskrit : [],
    hl_Serbian  : [ enc_1025 ],
    hl_Slovak   : [ enc_ISO2 ],
    hl_Somali   : [],
    hl_Swahili  : [],
    hl_Swedish  : [ enc_ISO1, enc_278 ],
    hl_Spanish  : [ enc_ISO1 ],
    hl_Tamil    : [],
    hl_Tajik    : [ enc_KOI8T ],
    hl_Thai     : [ enc_874 ],
    hl_Turkish  : [ enc_ISO9, enc_857, enc_905, enc_1254 ],
    hl_Turkmen  : [],
    hl_Urdu     : [],
    hl_Uzbek    : [],
    hl_Japanese : [ enc_EUCJP ]
   }
   #
   err_SEC     = 5
   err_MIN     = 6
   err_HOURS   = 7
   err_BYTES   = 8
   err_TRY     = 9
   err_CLOSED  = 10
   err_RECONN  = 11
   err_CONNTO  = 12
   err_DEVEL   = 13
   err_SENDTO  = 15
   err_USAGE   = 16
   err_OPTIONS = 17
   err_LOADCFG = 18
   err_IMPORT  = 19
   err_BASEDON = 64
   err_UNKNOWN = 100
   #
   err_DESCRIPTIONS = {
     err_SEC:     " sec.",
     err_MIN:     " min.",
     err_HOURS:   " hr.",
     err_BYTES:   " byte(s)",
     err_TRY:     " (try: {})",
     err_CLOSED:  "Connection closed",
     err_RECONN:  "reconnecting to ",
     err_CONNTO:  "Connecting to ",
     err_SENDTO:  "Sending to ",
     err_USAGE:   "Usage: ",
     err_OPTIONS: "[<options>]",
     err_LOADCFG: "Problem reading the configuration file",
     err_IMPORT:  "Library import error",
     err_BASEDON: "based on IRC-IoT demo library",
     err_UNKNOWN: "Unknown error",
     err_DEVEL:   "You are using the test part of library code" \
      + ", it may be unstable or insecure, if you are not sure" \
      + " - disable it"
   }
   #
   def __setattr__(self, *_):
     pass

 def __init__(self):
   #
   self.bot_name = self.CONST.default_bot_name
   self.bot_python = self.CONST.default_bot_python
   self.bot_background_parameter \
     = self.CONST.default_bot_background_parameter
   self.errors = self.CONST.err_DESCRIPTIONS
   self.max_config_size = self.CONST.default_max_config_size
   self.lang = self.CONST.hl_default
   # Only for testing:
   self.os_override = None
   self.os_linux_proc_ipv4_route \
     = self.CONST.os_linux_proc_ipv4_route
   self.os_linux_proc_ipv6_route \
     = self.CONST.os_linux_proc_ipv6_route
   self.__config = None
   self.__error_handler_ = self.__default_error_handler_

 def __default_error_handler_(self, in_error_code, in_mid, \
   in_vuid = None, in_addon = None):
  # Warning: This version of error handler is made for
  # testing and does not comply with the specification
  my_descr = ""
  if in_error_code in self.errors.keys():
   my_descr = self.errors[in_error_code]
   if isinstance(in_addon, str):
     my_descr += " ({})".format(in_addon)
  if my_descr != "":
    print('PyIRCIoT error:', my_descr)

 def copy_string_(self, from_string):
   if not isinstance(from_string, str):
     return None
   return '{}_'.format(from_string)[:-1]

 def wipe_string_(self, in_hash):
   try:
     import SecureString
     SecureString.clearmem(in_hash)
   except:
     pass
   return "U" * 128

 def td2ms_(self, in_td):
   return in_td.days * 86400 \
        + in_td.seconds \
        + in_td.microseconds / 1000000

 def is_json_(self, in_message):
   if not isinstance(in_message, str):
     return False
   try:
     my_json = json.loads(in_message)
   except ValueError:
     return False
   return True

 def get_enc_by_enc_(self, in_encoding):
   if not isinstance(in_encoding, str):
     return None
   my_encoding = in_encoding.lower()
   for my_key in self.CONST.enc_aliases.keys():
     if my_encoding in self.CONST.enc_aliases[ my_key ]:
       my_encoding = my_key
       break
   if my_encoding not in self.get_encs_list_():
     return None
   return my_encoding

 def get_langs_by_enc_(self, in_encoding):
   my_encoding = self.get_enc_by_enc_(in_encoding)
   if my_encoding == None:
     return []
   my_langs = []
   for my_key in self.CONST.hl_old_enc.keys():
     if my_encoding in self.CONST.hl_old_enc[ my_key ]:
       my_langs += [ my_key ]
   return my_langs

 def get_lang_by_enc_(self, in_encoding):
   my_langs = self.get_langs_by_enc_(in_encoding)
   if len(my_langs) != 1:
     return None
   return my_langs.pop()

 def get_encs_by_lang_(self, in_human_language):
   if not isinstance(in_human_language, str):
     return []
   my_encs = [ self.CONST.enc_UTF8 ]
   if in_human_language in self.CONST.hl_old_enc.keys():
     my_encs += self.CONST.hl_old_enc[ in_human_language ]
   return my_encs

 def get_langs_list_(self):
   my_langs = []
   for my_key in self.CONST.hl_old_enc.keys():
     my_langs += [ my_key ]
   return my_langs

 def get_encs_list_(self):
   my_encs = [ self.CONST.enc_UTF8 ]
   for my_lang in self.CONST.hl_old_enc.keys():
     for my_enc in self.CONST.hl_old_enc[ my_lang ]:
       if my_enc not in my_encs:
         my_encs += [ my_enc ]
   return my_encs

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

 def is_ip_port_(self, in_ip_port):
   if not isinstance(in_ip_port, int):
     return False
   if in_ip_port < 1 or in_ip_port > 65535:
     return False
   return True

 def is_hostname_(self, in_name):
   try:
     socket.gethostbyname(in_name)
     return True
   except socket.error:
     return False

 # incomplete
 def is_local_ip_address_(self, in_ip):
   return False

 def dns_ipv4_resolver_(self, in_name):
   if not isinstance(in_name, str):
     return None
   my_ip_list = []
   try:
     from dns import resolver
     my_result = resolver.query(in_name, 'A')
     for my_answer in my_result.response.answer:
       for my_item in my_answer.items:
         my_ip = my_item.address
         if not self.is_ipv4_address_(my_ip):
           continue
         if my_ip not in my_ip_list:
           my_ip_list += [ my_ip ]
     return my_ip_list
   except:
     return None

 def dns_reverse_resolver_(self, in_server_ip):
   if self.is_ip_address_(in_server_ip):
     try:
       from dns import resolver, reversename
       my_reverse = reversename.from_address(in_server_ip)
       my_answer = resolver.query(my_reverse, 'PTR')
       return str(my_answer[0])[:-1]
     except:
       pass
   return in_server_ip

 def get_os_name_(self):
   if self.os_override != None:
     return self.os_override
   try:
     return os.uname()[0]
   except:
     if os.name == 'nt':
       return self.CONST.os_windows
     return None

 def get_ipv6_route_linux_(self, in_server_ip):
  def unpack_ipv6_(in_string):
    my_unpack = ''
    for my_idx in range(8):
      if my_idx != 0:
        my_unpack += ':'
      my_unpack += in_string[my_idx*4:my_idx*4+4]
    return my_unpack
  my_proc = self.os_linux_proc_ipv6_route
  if self.get_os_name_() != self.CONST.os_linux:
    return None
  if not os.path.exists(my_proc):
    return None
  if not os.access(my_proc, os.R_OK):
    return None
  if not self.is_ipv6_address_(in_server_ip):
    return None
  my_route = None
  my_check = ipaddress.IPv6Address(in_server_ip)
  with open(my_proc) as my_handler:
    for my_line in my_handler:
      my_fields = my_line.strip().split()
      my_network = my_fields[0]
      my_netmask = my_fields[1]
      my_gateway = my_fields[4]
      if len(my_network) != 32 \
      or len(my_gateway) != 32 \
      or len(my_netmask) != 2:
        continue
      my_iunpack = unpack_ipv6_(my_network)
      my_gunpack = unpack_ipv6_(my_gateway)
      if my_gateway == '::':
        my_gateway = None
      my_netmask = int(my_netmask)
      my_metric  = int(my_fields[5], 16)
      my_netbase = ipaddress.ip_network(my_iunpack \
        + "/{:d}".format(my_netmask), False)
      my_gateway = ipaddress.ip_address(my_gunpack)
      my_network = my_iunpack
      my_if_name = my_fields[9]
      if my_check in my_netbase:
        my_get = False
        if my_route == None:
          my_get = True
        else:
          ( chk_if_name, chk_network, chk_netmask, \
            chk_metric, chk_gateway ) = my_route
          if my_netmask > chk_netmask:
            my_get = True
          elif my_netmask == chk_netmask:
            if my_metric < chk_metric:
              my_get = True
        if my_get:
          my_route = ( my_if_name, my_network, \
            my_netmask, my_metric, my_gateway )
  return my_route
  #
  # End of get_ipv6_route_linux_()

 def get_ipv4_route_linux_(self, in_server_ip):
  def unpack_ipv4_(in_string):
    return socket.inet_ntoa(struct.pack("<L", int(in_string, 16)))
  my_proc = self.os_linux_proc_ipv4_route
  if self.get_os_name_() != self.CONST.os_linux:
    return None
  if not os.path.exists(my_proc):
    return None
  if not os.access(my_proc, os.R_OK):
    return None
  if not self.is_ipv4_address_(in_server_ip):
    return None
  my_route = None
  my_check = ipaddress.ip_address(in_server_ip)
  # Warning: this method only checks the default routing table,
  # but it is more correct to take the desired routing table
  # by the number based on the current table selection rules,
  # which is often used in the routers and in the Android OS
  with open(my_proc) as my_handler:
    for my_line in my_handler:
      my_fields = my_line.strip().split()
      my_network = my_fields[1]
      my_netmask = my_fields[7]
      if len(my_network) != 8 or len(my_netmask) != 8:
        continue
      my_if_name = my_fields[0]
      my_gateway = my_fields[2]
      my_metric  = int(my_fields[6])
      my_network = unpack_ipv4_(my_network)
      my_gateway = unpack_ipv4_(my_gateway)
      my_netmask = unpack_ipv4_(my_netmask)
      if my_gateway == '0.0.0.0':
        my_gateway = None
      my_ip_mask = ipaddress.ip_address(my_netmask)
      my_netbase = ipaddress.ip_network(my_network \
       + '/' + my_netmask)
      if my_check in my_netbase:
        my_get = False
        if my_route == None:
          my_get = True
        else:
          ( chk_if_name, chk_network, chk_netmask, \
            chk_metric, chk_gateway ) = my_route
          chk_ip_mask = ipaddress.ip_address(chk_netmask)
          if my_ip_mask > chk_ip_mask:
            my_get = True
          elif chk_ip_mask == my_ip_mask:
            if my_metric < chk_metric:
              my_get = True
        if my_get:
          my_route = ( my_if_name, my_network, \
            my_netmask, my_metric, my_gateway )
  return my_route
  #
  # End of get_ipv4_route_linux_()

 def get_ipv4_route_(self, in_server_ip):
  if not self.is_ipv4_address_(in_server_ip):
    return None
  my_os = self.get_os_name_()
  if my_os == self.CONST.os_linux:
    return self.get_ipv4_route_linux_(in_server_ip)
  # Other OS's methods will be here
  return None

 def get_ipv6_route_(self,in_server_ip):
  if not self.is_ipv6_address_(in_server_ip):
    return None
  my_os = self.get_os_name_()
  if my_os == self.CONST.os_linux:
    return self.get_ipv6_route_linux_(in_server_ip)
  # Other OS's methods will be here
  return None

 def get_src_ip_by_dst_ip_(self,in_server_ip):
  my_ipv4_route = None
  my_ipv6_route = None
  if self.is_ipv4_address_(in_server_ip):
    my_ipv4_route = self.get_ipv4_route_(in_server_ip)
    if my_ipv4_route == None:
      return None
    ( my_if_name, my_network, my_netmask, \
      my_metric,  my_gateway ) = my_ipv4_route
  elif self.is_ipv6_address_(in_server_ip):
    my_ipv6_route = self.get_ipv6_route_(in_server_ip)
    if my_ipv6_route == None:
      return None
    ( my_if_name, my_network, my_netmask, \
      my_metric, my_gateway ) = my_ipv6_route
  else:
    return None
  my_ip_out = None
  my_ip_mask = ipaddress.ip_address(in_server_ip)
  my_adapters = ifaddr.get_adapters()
  for my_adapter in my_adapters:
    for my_ip in my_adapter.ips:
      if self.is_ipv4_address_(my_ip.ip) \
       and my_ipv4_route != None:
        my_network_str \
         = "{}/{:d}".format(my_ip.ip, my_ip.network_prefix)
        my_netbase = ipaddress.ip_network(my_network_str, False)
        if my_ip_mask in my_netbase:
          return my_ip.ip
        if my_adapter.name == my_if_name:
          if my_gateway == None:
            my_ip_out = my_ip.ip
          else:
            my_netbase = ipaddress.ip_network(my_network \
             + '/' + my_netmask)
            my_ip_check = ipaddress.ip_address(my_ip.ip)
            if my_ip_check in my_netbase:
              return my_ip.ip
      elif isinstance(my_ip.ip, tuple) \
       and my_ipv6_route != None:
        ( my_ipv6, my_ipv6_flowinfo, my_ipv6_scope_id ) = my_ip.ip
        if self.is_ipv6_address_(my_ipv6):
          my_network_str \
           = "{}/{:d}".format(my_ipv6, my_ip.network_prefix)
          my_netbase = ipaddress.ip_network(my_network_str, False)
          if my_ip_mask in my_netbase:
            return my_ipv6
          if my_adapter.name == my_if_name:
            if my_gateway == None:
              my_ip_out = my_ipv6
            else:
              my_netbase = ipaddress.ip_network(my_network \
               + "/{:d}".format(my_netmask), False)
              my_ip_check = ipaddress.ip_address(my_ipv6)
              if my_ip_check in my_netbase:
                return my_ipv6
  return my_ip_out
  #
  # End of get_src_ip_by_dst_ip_()

 def validate_descriptions_(self, in_dict):
  if not isinstance(in_dict, dict):
    return {}
  my_dict = in_dict
  for my_key in in_dict.keys():
    if not isinstance(my_key, int):
      del my_dict[ my_key ]
      continue
    my_item = in_dict[ my_key ]
    if not isinstance(my_item, str):
      del my_dict[ my_key ]
      continue
    my_a = my_item.count('{')
    my_b = my_item.count('}')
    my_c = my_item.count('{}')
    if my_a != my_c or my_b != my_c:
      del my_dict[ my_key ]
      continue
  return my_dict

 def irciot_set_locale_(self, in_lang):
  if not isinstance(in_lang, str): return
  self.lang = in_lang
  my_desc = {}
  try:
    from PyIRCIoT.irciot_errors \
    import irciot_get_all_error_descriptions_
    my_desc = irciot_get_all_error_descriptions_(in_lang)
    my_desc = self.validate_descriptions_(my_desc)
    if my_desc != {}:
      self.errors.update(my_desc)
  except:
    pass

 def get_config_value_(self, in_item, in_section = None):
  if not isinstance(self.__config, dict): return None
  if not isinstance(in_item, str): return None
  if not in_item in self.__config.keys(): return None
  return self.__config[in_item]

 def set_config_value_(self, in_item, in_value, in_section = None):
  if not isinstance(in_item, str): return False
  if not isinstance(self.__config, dict): self.__config = {}
  self.__config[in_item] = in_value
  return True

 def load_config_defaults_(self, in_defaults):
  if not isinstance(in_defaults, dict): return False
  self.__config = in_defaults
  return True

 # incomplete
 def load_config_file_(self, in_filename, in_defaults = None):
  if self.__config is None: self.__config = {}
  self.load_config_defaults_(in_defaults)
  if not isinstance(in_filename, str): return False
  if not os.path.isfile(in_filename): return False
  if not os.access(in_filename, os.R_OK):
    self._error_handler_(self.CONST.err_LOADCFG, 0)
    return False
  try:
    import configparser
    import random
  except Exception as my_ex:
    self._error_handler_(self.CONST.err_IMPORT, 0, in_addon = str(my_ex))
    return False
  random.seed()
  my_dummy = 'dummy{:d}'.format(random.randint(10000, 99999))
  my_parser = configparser.ConfigParser()
  try:
    file_fd = open(in_filename, 'r')
    my_cfg_str = '[{}]\n'.format(my_dummy)
    my_cfg_str += file_fd.read(self.max_config_size)
    file_fd.close()
    my_parser.read_string(my_cfg_str)
    my_config = my_parser._sections[my_dummy]
    if isinstance(my_config, dict):
      for config_key in my_config.keys():
        self.__config[config_key] = my_config[config_key]
      del my_config
  except Exception as my_ex:
    self.__error_handler_(self.CONST.err_LOADCFG, 0, in_addon = str(my_ex))
    return False
  return True

 def bot_usage_handler (self):
  print('{} ({})'.format(self.bot_name, \
   self.errors[self.CONST.err_BASEDON]))
  print('\n{}{} {}\n'.format( \
   self.errors[self.CONST.err_USAGE], \
   sys.argv[0], self.errors[self.CONST.err_OPTIONS]))

 def bot_set_options_(self, in_options):
  if not isinstance(in_options, str): return False
  self.errors[self.CONST.err_OPTIONS] = in_options
  return True

 def bot_redirect_output_(self, in_filename):
  if not isinstance(in_filename, str):
    return
  try:
    io_redir = open(in_filename, 'w+')
  except:
    return
  sys.stdout = io_redir
  sys.stderr = io_redir
  io_handler1 = io_redir.fileno()
  os.dup2(io_handler1, 1)
  os.close(1)
  io_handler2 = io_redir.fileno()
  os.dup2(io_handler2, 2)
  os.close(2)

 def bot_process_kill_(self):
  if self.get_os_name_() in self.CONST.os_all_UNIX:
    try:
      import signal
      os.kill(os.getpid(), signal.SIGKILL)
    except:
      pass

 def bot_process_kill_timeout_(self, in_timeout):
  if type(in_timeout) not in [ int, float ]: return
  if self.get_os_name_() in self.CONST.os_all_UNIX \
   and in_timeout > 0:
    try:
      import signal
      signal.signal(signal.SIGALRM, self.bot_process_kill_)
      signal.alarm(in_timeout)
    except:
      pass

 def bot_background_start_(self):
  import subprocess
  my_count = len(sys.argv)
  if my_count == 1:
    self.bot_usage_handler ()
  elif my_count > 1:
    my_list = [ self.bot_python ]
    for my_idx in range(1, my_count):
      my_list += [ sys.argv[my_idx] ]
    if my_list[ my_count - 1 ] != self.bot_background_parameter:
      my_list  = [ os.path.expanduser(sys.argv[0]) ] + my_list
      my_list += [ self.bot_background_parameter ]
      print("Starting {} ...".format(self.bot_name))
      my_process = subprocess.Popen( my_list )
      sys.exit(0)

