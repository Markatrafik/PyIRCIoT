
import socket
import struct
import ifaddr
import ipaddress
import datetime
import json
import sys
import os

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
   ### OS depended:
   #
   os_linux   = 'Linux'
   #
   os_linux_proc_ipv4_route = '/proc/net/route'
   os_linux_proc_ipv6_route = '/proc/net/ipv6_route'
   #
   def __setattr__(self, *_):
     pass

 def __init__(self):
   #
   self.bot_name = self.CONST.default_bot_name
   self.bot_python = self.CONST.default_bot_python
   self.bot_background_parameter \
     = self.CONST.default_bot_background_parameter
   # Only for testing:
   self.os_override = None
   self.os_linux_proc_ipv4_route \
     = self.CONST.os_linux_proc_ipv4_route
   self.os_linux_proc_ipv6_route \
     = self.CONST.os_linux_proc_ipv6_route

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
        + "/%d" % my_netmask, False)
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
  # but it’s more correct to take the desired routing table
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
        my_network_str = my_ip.ip + "/%d" % my_ip.network_prefix
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
          my_network_str = my_ipv6 + "/%d" % my_ip.network_prefix
          my_netbase = ipaddress.ip_network(my_network_str, False)
          if my_ip_mask in my_netbase:
            return my_ipv6
          if my_adapter.name == my_if_name:
            if my_gateway == None:
              my_ip_out = my_ipv6
            else:
              my_netbase = ipaddress.ip_network(my_network \
                + "/%d" % my_netmask, False)
              my_ip_check = ipaddress.ip_address(my_ipv6)
              if my_ip_check in my_netbase:
                return my_ipv6
  return my_ip_out
  #
  # End of get_src_ip_by_dst_ip_()

 def bot_usage_handler (self):
  print('%s (based on IRC-IoT demo library)' % self.bot_name)
  print('\nUsage: %s [<options>]\n' % sys.argv[0])

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

 def bot_background_start_(self):
  import subprocess
  if len(sys.argv) == 0:
    self.bot_usage_handler ()
  else:
    my_list = [ self.bot_python ]
    my_count = len(sys.argv)
    for my_idx in range(1, my_count):
      my_list += [ sys.argv[my_idx] ]
    if my_list[ my_count - 1 ] != self.bot_background_parameter:
      my_list  = [ os.path.expanduser(sys.argv[0]) ] + my_list
      my_list += [ self.bot_background_parameter ]
      print("Starting %s ..." % self.bot_name)
      my_process = subprocess.Popen( my_list )
      sys.exit(0)

