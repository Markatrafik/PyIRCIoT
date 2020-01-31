'''
'' PyIRCIoT-router (PyIRCIoT_router class)
''
'' Copyright (c) 2019-2020 Alexey Y. Woronov
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
CAN_debug_library  = False

from irciot import PyLayerIRCIoT
from copy import deepcopy
from time import time
import random
import json

class PyIRCIoT_router( PyLayerIRCIoT ):

 class CONST( PyLayerIRCIoT.CONST ):
  #
  irciot_router_protocol_version = '0.3.31'
  #
  irciot_router_library_version = '0.0.171'
  #
  default_detect_dup_messages = 128
  #
  dir_in   = 'i' # input traffic direction
  dir_out  = 'o' # output traffic direction
  dir_both = 'b' # input and output directions
  #
  err_ROUTER_DUP_DETECT = 10015
  #
  err_DESCRIPTIONS = PyLayerIRCIoT.CONST.err_DESCRIPTIONS
  err_DESCRIPTIONS[ err_ROUTER_DUP_DETECT ] = \
   'Router detected a duplicate while forwarding the message'
  #
  # End of PyIRCIoT_router.CONST()

 def __init__(self):
  #
  self.input_plugin  = None
  # This is an object that defines routing and prefiltering
  # of input messages at an external level outside of this
  # IRC-IoT router class
  #
  self.input_routes  = [ ( "*", "*" ) ]
  # This is list of tuples each of which contains an source and
  # destination IRC-IoT address or mask in the input messages
  #
  self.router_graphs = [ ( self.do_router_forwarding, {} ) ]
  # This is list of tuples each of which contains an function
  # and it's optional parameters. Each function sequentially
  # performed on the message flow and must have a same inbound
  # and outbound interface. If another list is used as a list
  # item, then the first item of a nested list may contain a
  # special tuple with a function that defining the conditions
  # to perform the list, the remaining items in such a list are
  # used to process IRC-IoT messages
  #
  self.output_routes = [ ( "*", "*" ) ]
  # This is list of tuples each of which contains an source and
  # destination IRC-IoT address or mask in the output messages
  #
  self.output_plugin = None
  # This is an object that defines routing and postfiltering
  # of output messages at an external level outside of this
  # IRC-IoT router class
  #
  self.connections_tracking = []
  #
  self.dup_detect_pipeline = []
  #
  super(PyIRCIoT_router, self).__init__()
  #
  self.detect_dup_messages = self.CONST.default_detect_dup_messages
  #
  self.irciot_crc16_init_()
  #
  if self.CONST.irciot_router_protocol_version \
   != self.CONST.irciot_protocol_version:
    self.irciot_error_(self.CONST.err_PROTO_VER_MISMATCH, 0)
  if self.CONST.irciot_router_library_version \
   != self.CONST.irciot_library_version:
    self.irciot_error_(self.CONST.err_LIB_VER_MISMATCH, 0)
    raise ValueError(self.CONST.irciot_library_version, \
     self.CONST.irciot_router_library_version)
  #
  # End of PyIRCIoT_router.__init__()

 def router_pointer (self, in_compatibility, in_messages_pack):
  # Warning: interface may be changed while developing
  return False

 def router_error_(self, in_error_code, in_addon = None):
  # Warning: interface may be changed while developing
  return

 def is_router_route_(self, in_route):
  try:
    ( left_addr, right_addr ) = in_route
  except:
    return False
  if not isinstance(left_addr, str):
    return False
  if not isinstance(right_addr, str):
    return False
  return True

 def is_router_routes_(self, in_routes):
  if not isinstance(in_routes, list):
    return False
  for my_route in in_routes:
    if not self.is_router_route_(my_route):
      return False
  return True

 def is_router_graph_(self, in_graph):
  try:
    ( my_func, my_params ) = in_graph
  except:
    return False
  if not isinstance(my_func, object):
    return False
  if not isinstance(my_params, dict):
    return False
  return True

 def is_router_graphs_(self, in_graphs):
  if not isinstance(in_graphs, list):
    return False
  for my_item in in_graphs:
    if isinstance(my_item, list):
      if not self.is_router_graphs_(my_item):
        return False
    else:
      if not self.is_router_graph_(my_item):
        return False
  return True

 def do_router_graph_(self, in_datum, in_graph, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not self.is_router_graph_(in_graph):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  ( my_function_, my_params ) = in_graph
  return my_function_( in_datum, my_params, in_vuid )

 def do_router_route_(self, in_datum, in_route, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_route, tuple):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  return in_datum

 def do_router_graphs_(self, in_datum, in_graphs, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_graphs, list):
    return None
  my_datum = in_datum
  for my_index, my_graph in enumerate(in_graphs):
    if isinstance(my_graph, list):
      if my_graph == []:
        return None
      my_datum = self.do_router_graphs_(my_datum, my_graph, in_vuid)
    else:
      tmp_datum = self.do_router_graph_(my_datum, my_graph, in_vuid)
      if my_index == 0 and isinstance(tmp_datum, bool):
        if not tmp_datum:
          break
      elif isinstance(tmp_datum, dict):
        my_datum = tmp_datum
      else:
        return None
      del tmp_datum
  return my_datum
  #
  # End of PyIRCIoT_router.do_router_graphs_()

 def do_router_routes_(self, in_datum, in_routes, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_routes, list):
    return None
  for my_route in in_routes:
    pass
  return in_datum

 def do_router_(self, in_message, in_direction, in_vuid = None):
  if in_direction in [ self.CONST.dir_in, self.CONST.dir_both ] \
   and not self.is_router_routes_(self.input_routes):
    return ""
  if in_direction in [ self.CONST.dir_out, self.CONST.dir_both ] \
   and not self.is_router_routes_(self.output_routes):
    return ""
  if not self.is_router_graphs_(self.router_graphs):
    return ""
  my_json = self.irciot_deinencap_(in_message, in_vuid)
  if my_json == "":
    return ""
  try:
    my_datums = json.loads(my_json)
  except:
    return ""
  if isinstance(my_datums, dict):
    my_datums = [ my_datums ]
  if not isinstance(my_datums, list):
    return ""
  my_outdat = []
  for my_datum in my_datums:
    if in_direction in [ self.CONST.dir_in, self.CONST.dir_both ]:
      my_datum = self.do_router_routes_(my_datum, self.input_routes, in_vuid)
    my_datum = self.do_router_graphs_(my_datum, self.router_graphs, in_vuid)
    if in_direction in [ self.CONST.dir_out, self.CONST.dir_both ]:
      my_datum = self.do_router_routes_(my_datum, self.output_routes, in_vuid)
    if my_datum != None:
      my_outdat.append(my_datum)
  if my_outdat == []:
    return ""
  out_message = ""
  out_pack = self.irciot_encap_all_(my_outdat, in_vuid)
  if isinstance(out_pack, list):
    if len(out_pack) > 0:
      ( out_message, out_vuid ) = out_pack[0]
  if not isinstance(out_message, str):
    out_message = ""
  return out_message
  #
  # End of PyIRCIoT_router.do_router_()

 def dup_detection_(self, in_datum, in_vuid = None):
  if not isinstance(in_datum, dict):
    return True # Drop invalid messages
  my_datum = deepcopy(in_datum)
  if self.CONST.tag_DATE_TIME in in_datum:
    my_dt = my_datum.pop(self.CONST.tag_DATE_TIME)
  else:
    my_dt = "%s" % time()
  if len(my_dt) > 11 and len(my_dt) < 21:
    my_dt = my_dt[:11] # cut to POSIX timestamp
  if len(my_dt) > 20:
    my_dt = my_dt[:19] # cut to ISO 8601:2004
  my_string = "%s" % in_vuid
  for my_key, my_value in sorted(my_datum.items()):
    my_string += "%s%s" % (my_key, my_value)
  del my_datum
  my_bytes = bytes(my_string, 'utf-8')
  my_string = "%s" % self.irciot_crc16_(my_bytes)
  my_string += "%s" % self.irciot_crc32_(my_bytes)
  del my_bytes
  my_string += "%s" % my_dt
  if my_string in self.dup_detect_pipeline:
    return True # Drop duplicate messages
  self.dup_detect_pipeline.append(my_string)
  if len(self.dup_detect_pipeline) > self.detect_dup_messages:
    self.dup_detect_pipeline.pop(0)
  return False
  #
  # End of PyIRCIoT_router.dup_detection_()

 def local_message_router_(self):
  pass
  #
  # End of PyIRCIoT_router.local_message_router_()

 def global_message_router_(self):
  pass
  #
  # End of PyIRCIoT_router.global_message_router_()

 # incomplete
 def do_router_translation(self, in_datum, in_params, in_vuid = None):
  if not isinstance(in_params, dict):
    return None
  dst_addr = ''
  try:
    src_addr = in_datum[ self.CONST.tag_SRC_ADDR ]
  except:
    return None
  if self.CONST.tag_DST_ADDR in in_datum.keys():
    dst_addr = in_datum[ self.CONST.tag_DST_ADDR ]
  if not self.is_irciot_address_(src_addr) \
  or not self.is_irciot_address_(dst_addr):
    self.irciot_error_(self.CONST.err_INVALID_ADDRESS, 0)
    return None
  #

  #
  out_datum = in_datum
  return out_datum

 def do_router_forwarding(self, in_datum, in_params, in_vuid = None):
  if self.dup_detection_(in_datum):
    self.irciot_error_(self.CONST.err_ROUTER_DUP_DETECT, 0)
    return None
  out_datum = in_datum
  return out_datum

