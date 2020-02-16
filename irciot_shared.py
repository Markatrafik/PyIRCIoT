
import socket
import datetime
import json

class irciot_shared_(object):

 def td2ms_(self, td):
   return td.days * 86400 + td.seconds + td.microseconds / 1000000

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

