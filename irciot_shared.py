
import socket
import datetime
import json

class irciot_shared_(object):

 class CONST(object):
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
   api_vuid_any = [ api_vuid_cfg, api_vuid_tmp, api_vuid_srv ]
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
   api_first_temporal_vuid = 1000
   #
   # for Python 3.x: 19 Jan 3001 08:00 UTC
   api_epoch_maximal = 32536799999
   #
   def __setattr__(self, *_):
     pass

 def __init__(self):
   pass

 def td2ms_(self, in_td):
   return in_td.days * 86400 + in_td.seconds + in_td.microseconds / 1000000

 def is_json_(self, in_message):
   if not isinstance(in_message, str):
     return False
   try:
     my_json = json.loads(in_message)
   except ValueError:
     return False
   return True

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

