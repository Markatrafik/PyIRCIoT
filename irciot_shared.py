
import socket
import datetime
import json

class irciot_shared_(object):

 class CONST(object):
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
   def __setattr__(self, *_):
     pass

 def __init__(self):
   #
   self.CONST = self.CONST()

 def td2ms_(self, in_td):
   return in_td.days * 86400 + in_td.seconds + in_td.microseconds / 1000000

 def is_json_(self, in_message):
   if not isinstance(in_message, str):
     return False
   try:
     json_object = json.loads(in_message)
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

