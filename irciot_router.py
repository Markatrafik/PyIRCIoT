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

try: # insecure, but for development
 from irciot import PyLayerIRCIoT
except:
 from PyIRCIoT.irciot import PyLayerIRCIoT
from copy import deepcopy
from time import time
import random
try:
 import json
except:
 import simplejson as json

class PyIRCIoT_router( PyLayerIRCIoT ):

 class CONST( PyLayerIRCIoT.CONST ):
  #
  irciot_router_protocol_version = '0.3.33'
  #
  irciot_router_library_version = '0.0.211'
  #
  default_maximal_detect_dup_messages = 128
  #
  default_maximal_connection_tracking = 8192 # items
  default_timeout_connection_tracking = 3600 # seconds
  #
  maximal_LMR_count = 256
  maximal_GMR_count = 16
  #
  dir_in   = 'i' # input traffic direction
  dir_out  = 'o' # output traffic direction
  dir_both = 'b' # input and output directions
  #
  dir_any  = [ dir_in, dir_out, dir_both ]
  #
  rgn_REQUEST_PARAMS = 'irciot_req_rgn_prm'
  #
  tag_IN_SCOPE  = 'iscp'
  tag_OUT_SCOPE = 'oscp'
  tag_LMR_ID = 'lmri'
  tag_GMR_ID = 'gmri'
  #
  err_ROUTER_DUP_DETECT = 10015
  err_MISSING_PARAMETER = 10505
  err_INVALID_PARAMETER = 10507
  err_INVALID_DIRECTION = 10508
  #
  err_LMR_INCORRECT_VER  = 10601
  err_LMR_INVALID_PARAM  = 10602
  err_LMR_AUTHENTICATION = 10604
  err_LMR_COMPATIBILITY  = 10605
  err_LMR_MAX_INSTANCES  = 10607
  err_LMR_INVALID_ID     = 10608
  err_LMR_LOOP_DETECTED  = 10611
  #
  err_GMR_INCORRECT_VER  = 10701
  err_GMR_INVALID_PARAM  = 10702
  err_GMR_BAD_INTERACTOR = 10703
  err_GMR_AUTHENTICATION = 10704
  err_GMR_COMPATIBILITY  = 10705
  err_GMR_MAX_INSTANCES  = 10707
  err_GMR_INVALID_ID     = 10708
  err_GMR_LOOP_DETECTED  = 10711
  err_GMR_INVALID_ORIGIN = 10712
  err_GMR_INVALID_PATH   = 10713
  err_GMR_INVALID_ATTR   = 10714
  #
  err_DESCRIPTIONS = PyLayerIRCIoT.CONST.err_DESCRIPTIONS
  err_DESCRIPTIONS.update({
   err_ROUTER_DUP_DETECT: "Router detected a duplicate while forwarding the message",
   err_MISSING_PARAMETER: "Missing required parameter for routing graph node",
   err_INVALID_PARAMETER: "Invalid required parameter for routing graph node",
   err_INVALID_DIRECTION: "Invalid direction parameter for routing graph node",
   err_LMR_INVALID_ID:    "Invalid LMR instance identificator",
   err_LMR_INCORRECT_VER: "Incorrect protocol version for LMR intercommunication",
   err_LMR_MAX_INSTANCES: "Cannot create LMR, maximum number of instances reached",
   err_GMR_INVALID_ID:    "Invalid GMR instance identificator",
   err_GMR_INCORRECT_VER: "Incorrect protocol version for GMR intercommunication",
   err_GMR_MAX_INSTANCES: "Cannot create GMR, maximum number of instances reached"
  })
  #
  default_LMR_id = 1000
  default_GMR_id = 5000
  #
  state_LMR_stopped = 0
  state_LMR_running = 1
  state_LMR_paused  = 3
  #
  state_GMR_stopped = 0
  state_GMR_running = 1
  state_GMR_paused  = 3
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
  self.router_graphs = [ ( self.do_router_forwarding_, {} ) ]
  # This is list of tuples each of which contains an function
  # and it's required parameters. Each function sequentially
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
  self.__connections_tracking = {}
  #
  self.__dup_detection_pipeline = []
  #
  super(PyIRCIoT_router, self).__init__()
  #
  self.maximal_detect_dup_messages \
    = self.CONST.default_maximal_detect_dup_messages
  #
  self.maximal_connection_tracking \
    = self.CONST.default_maximal_connection_tracking
  self.timeout_connection_tracking \
    = self.CONST.default_timeout_connection_tracking
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
  self.__encoding = self.CONST.irciot_default_encoding
  #
  try:
    self.err_DESCRIPTIONS.update(self.CONST.err_DESCRIPTIONS)
  except:
    self.err_DESCRIPTIONS = self.CONST.err_DESCRIPTIONS
  #
  self.__LMR_pool = {}
  self.__GMR_pool = {}
  #
  self.__primary_irciot_address = ""
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

 def do_router_graph_(self, in_datum, in_graph, \
    in_direction, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not self.is_router_graph_(in_graph):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  ( my_function_, my_params ) = in_graph
  my_keys = my_function_( None, self.CONST.rgn_REQUEST_PARAMS, None )
  for my_key in my_keys:
    if not my_key in my_params.keys():
      self.irciot_error_(self.CONST.err_MISSING_PARAMETER, 0, \
        in_addon = my_key)
      return None
  return my_function_( in_datum, my_params, in_direction, in_vuid )

 def do_router_route_(self, in_datum, in_route, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_route, tuple):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  return in_datum

 def do_router_graphs_(self, in_datum, in_graphs, \
    in_direction, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_graphs, list):
    return None
  my_datum = in_datum
  for my_index, my_graph in enumerate(in_graphs):
    if isinstance(my_graph, list):
      if my_graph == []:
        return None
      my_datum = self.do_router_graphs_(my_datum, my_graph, \
        in_derection, in_vuid)
    else:
      tmp_datum = self.do_router_graph_(my_datum, my_graph, \
        in_direction, in_vuid)
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
  self.irciot_check_encoding_()
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
    my_datum = self.do_router_graphs_(my_datum, self.router_graphs, \
      in_direction, in_vuid)
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

 def dup_detection_(self, in_datum, in_direction, in_vuid = None):
  if not isinstance(in_datum, dict):
    return True # Drop invalid messages
  if in_direction not in self.CONST.dir_any:
    self.irciot_error_(self.CONST.err_INVALID_DIRECTION, 0)
    return True
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
  my_bytes = bytes(my_string, self.__encoding)
  my_string = "%s" % self.irciot_crc16_(my_bytes)
  my_string += "%s" % self.irciot_crc32_(my_bytes)
  del my_bytes
  my_string += "%s" % my_dt
  if my_string in self.__dup_detection_pipeline:
    return True # Drop duplicate messages
  self.__dup_detection_pipeline.append(my_string)
  if len(self.__dup_detection_pipeline) \
   > self.maximal_detect_dup_messages:
    self.__dup_detection_pipeline.pop(0)
  return False
  #
  # End of PyIRCIoT_router.dup_detection_()

 # incomplete
 def local_message_router_(self):
  pass
  #
  # End of PyIRCIoT_router.local_message_router_()

 # incomplete
 def global_message_router_(self):
  pass
  #
  # End of PyIRCIoT_router.global_message_router_()

 def __invalid_LMR_id_(in_LMR_id):
  self.irciot_error_(self.CONST.err_LMR_INVALID_ID, 0, \
    in_addon = "{}".format(in_LMR_id))

 def __invalid_GMR_id_(in_GMR_id):
  self.irciot_error_(self.CONST.err_GMR_INVALID_ID, 0, \
    in_addon = "{}".format(in_GMR_id))

 # incomplete
 def init_LMR_(self, in_src = None):
  if in_src == None:
    my_src = self.__primary_irciot_address
  else:
    my_src = in_src
  if not self.is_irciot_address_(my_src):
    return None
  my_LMR_id = self.CONST.default_LMR_id
  my_LMR_count = 0
  for my_key in self.__LMR_pool.keys():
    my_LMR_count += 1
    if my_LMR_id < my_key:
      my_LMR_id = my_key
  my_LMR_id += 1
  if my_LMR_count >= self.CONST.maximal_LMR_count:
    self.irciot_error_(self.CONST.err_LMR_MAX_INSTANCES, \
      0, in_addon = "%d" % self.CONST.maximal_LMR_count )
    return None
  self.__LMR_pool.update({
    my_LMR_id: {
     'src': my_src,
     'status': self.CONST.state_LMR_stopped
    }
  })
  return my_LMR_id

 # incomplete
 def init_GMR_(self, in_src = None):
  if in_src == None:
    my_src = self.__primary_irciot_address
  else:
    my_src = in_src
  if not self.is_irciot_address_(my_src):
    return None
  my_GMR_id = self.CONST.default_GMR_id - 1
  my_GMR_count = 0
  for my_key in self.__GMR_pool.keys():
    my_GMR_count += 1
    if my_GMR_id < my_key:
      my_GMR_id = my_key
  my_GMR_id += 1
  if my_GMR_count >= self.CONST.maximal_GMR_count:
    self.irciot_error_(self.CONST.err_GMR_MAX_INSTANCES, \
      0, in_addon = "%d" % self.CONST.maximal_GMR_count )
    return None
  self.__GMR_pool.update({
    my_GMR_id: {
     'src': my_src,
     'status': self.CONST.state_GMR_stopped
    }
  })
  return my_GMR_id

 def get_LMR_list_(self):
  my_LMR_list = []
  for my_key in self.__LMR_pool.keys():
    my_LMR_list.append(my_key)
  return my_LMR_list

 def get_GMR_list_(self):
  my_GMR_list = []
  for my_key in self.__GMR_pool.keys():
    my_GMR_list.append(my_key)
  return my_GMR_list

 def __check_LMR_id_(self, in_LMR_id):
  if in_LMR_id == None:
    return False
  if not isinstance(in_LMR_id, int):
    self.__invalid_LMR_id_(in_LMR_id)
    return False
  if in_LMR_id not in self.__LMR_pool.keys():
    self.__invalid_LMR_id_(in_LMR_id)
    return False
  return True

 def __check_GMR_id_(self, in_GMR_id):
  if in_GMR_id == None:
    return False
  if not isinstance(in_GMR_id, int):
    self.__invalid_GMR_id_(in_GMR_id)
    return False
  if in_GMR_id not in self.__GMR_pool.keys():
    self.__invalid_GMR_id_(in_GMR_id)
    return False
  return True

 def __get_LMR_id_(self, in_LMR_id):
  if in_LMR_id != None:
    return in_LMR_id
  if len(self.__LMR_pool) == 1:
    return list(self.__LMR_pool)[0]
  return None

 def __get_GMR_id_(self, in_GMR_id):
  if in_GMR_id != None:
    return in_GMR_id
  if len(self.__GMR_pool) == 1:
    return list(self.__GMR_pool)[0]
  return None

 def get_LMR_status_(self, in_LMR_id = None):
  my_LMR_id = self.__get_LMR_id_(in_LMR_id)
  if not self.__check_LMR_id_(my_LMR_id):
    return None
  return self.__LMR_pool[my_LMR_id]['status']

 def get_GMR_status_(self, in_GMR_id = None):
  my_GMR_id = self.__get_GMR_id_(in_GMR_id)
  if not self.__check_GMR_id_(my_GMR_id):
    return None
  return self.__GMR_pool[my_GMR_id]['status']

 # incomplete
 def start_LMR_(self, in_LMR_id = None):
  my_LMR_id = self.__get_LMR_id_(in_LMR_id)
  if not self.__check_LMR_id_(my_LMR_id):
    return False
  self.__LMR_pool[my_LMR_id].update({
    'status': self.CONST.state_LMR_running
  })
  return True

 # incomplete
 def start_GMR_(self, in_GMR_id = None):
  my_GMR_id = self.__get_GMR_id_(in_GMR_id)
  if not self.__check_GMR_id_(my_GMR_id):
    return False
  self.__GMR_pool[my_GMR_id].update({
    'status': self.CONST.state_GMR_running
  })
  return True

 # incomplete
 def pause_LMR_(self, in_LMR_id = None):
  my_LMR_id = self.__get_LMR_id_(in_LMR_id)
  if not self.__check_LMR_id_(my_LMR_id):
    return False
  self.__LMR_pool[my_LMR_id].update({
    'status': self.CONST.state_LMR_running
  })
  return True

 # incomplete
 def pause_GMR_(self, in_GMR_id = None):
  my_GMR_id = self.__get_GMR_id_(in_GMR_id)
  if not self.__check_GMR_id_(my_GMR_id):
    return False
  self.__LMR_pool[my_LMR_id].update({
    'status': self.CONST.state_LMR_pasued
  })
  return True

 # incomplete
 def drop_LMR_(self, in_LMR_id = None):
  my_LMR_id = self.__get_LMR_id_(in_LMR_id)
  if not self.__check_LMR_id_(my_LMR_id):
    return False
  self.__LMR_pool.pop(my_LMR_id)
  return True

 # incomplete
 def drop_GMR_(self, in_GMR_id = None):
  my_GMR_id = self.__get_GMR_id_(in_GMR_id)
  if not self.__check_GMR_id_(my_GMR_id):
    return False
  self.__GMR_pool.pop(my_GMR_id)
  return True

 # incomplete
 def do_router_LMR_(self, in_datum, in_params, \
  in_direction, in_vuid = None):
  if not isinstance(in_params, dict):
    if in_params == self.CONST.rgn_REQUEST_PARAMS:
      return [ self.CONST.tag_LMR_ID ]
    return None
  if in_direction not in self.CONST.dir_any:
    self.irciot_error_(self.CONST.err_INVALID_DIRECTION, 0)
    return None
  my_id = in_params[ self.CONST.tag_LMR_ID ]
  if my_id not in self.__LMR_pool.keys():
    self.__invalid_LMR_id_(my_id)
    return in_datum
  my_LMR = self.__LMR_pool[my_id]

  return in_datum
  #
  # End of do_router_LMR_()

 # incomplete
 def do_router_GMR_(self, in_datum, in_params, \
  in_direction, in_vuid = None):
  if not isinstance(in_params, dict):
    if in_params == self.CONST.rgn_REQUEST_PARAMS:
      return [ self.CONST.tag_GMR_ID ]
    return None
  if in_direction not in self.CONST.dir_any:
    self.irciot_error_(self.CONST.err_INVALID_DIRECTION, 0)
    return None
  my_id = in_params[ self.CONST.tag_GMR_ID ]
  if my_id not in self.__GMR_pool.keys():
    self.__invalid_GMR_id_(my_id)
    return in_datum
  my_GMR = self.__GMR_pool[my_id]

  return in_datum
  #
  # End of do_router_GMR_()

 def connections_tracking_cleaner_(self):
  current_time = time()
  minimal_time = current_time
  minimal_key  = None
  my_count = 0
  for my_key in self.__connections_tracking.keys():
    ( my_addr, my_time ) = self.__connections_tracking[ my_key ]
    if current_time - my_time > self.timeout_connection_tracking:
      del self.__connections_tracking[ my_key ]
    else:
      if my_time < minimal_time:
        minimal_time = my_time
        minimal_key  = my_key
      my_count += 1
  if my_count > self.maximal_connection_tracking \
    and minimal_key != None:
      del self.__connections_tracking[ minimal_key ]
  #
  # End of connections_tracking_cleaner_()

 def do_router_translation_(self, in_datum, in_params, \
   in_direction, in_vuid = None):
  if not isinstance(in_params, dict):
    if in_params == self.CONST.rgn_REQUEST_PARAMS:
      return [ self.CONST.tag_IN_SCOPE, self.CONST.tag_OUT_SCOPE ]
    return None
  if in_direction not in self.CONST.dir_any:
    self.irciot_error_(self.CONST.err_INVALID_DIRECTION, 0)
    return None
  dst_addr = ''
  try:
    src_addr = in_datum[ self.CONST.tag_SRC_ADDR ]
  except:
    return None
  self.connections_tracking_cleaner_()
  if self.CONST.tag_DST_ADDR in in_datum.keys():
    dst_addr = in_datum[ self.CONST.tag_DST_ADDR ]
  if not self.is_irciot_address_(src_addr) \
  or not self.is_irciot_address_(dst_addr):
    self.irciot_error_(self.CONST.err_INVALID_ADDRESS, 0)
    return None
  in_scope = in_params[ self.CONST.tag_IN_SCOPE ]
  out_scope = in_params[ self.CONST.tag_OUT_SCOPE ]
  out_datum = in_datum
  in_scope_len = len(in_scope)
  src_addr_len = len(src_addr)
  my_translate = False
  #
  if in_direction in [ self.CONST.dir_in, self.CONST.dir_both ]:
    out_addr = src_addr
    if src_addr_len >= in_scope_len:
      if src_addr == in_scope:
        out_addr = out_scope
        my_translate == True
      elif src_addr_len > in_scope_len:
        if src_addr[:in_scope_len] == in_scope:
          if src_addr[in_scope_len] == '/':
            out_addr = out_scope + src_addr[in_scope_len:]
            my_translate = True
    if my_translate:
      my_key = out_addr + '@@' + dst_addr;
      if my_key in self.__connections_tracking.keys():
        my_translation = self.__connections_tracking[ my_key ]
      else:
        my_translation = ( src_addr, time() )
        self.__connections_tracking[ my_key ] = my_translation
      out_datum[ self.CONST.tag_SRC_ADDR ] = out_addr
  #
  if in_direction in [ self.CONST.dir_out, self.CONST.dir_both ]:
    my_key = dst_addr + '@@' + src_addr;
    if my_key in self.__connections_tracking.keys():
      ( my_src_addr, my_time ) = self.__connections_tracking[ my_key ]
      out_datum[ self.CONST.tag_DST_ADDR ] = my_src_addr
  #
  return out_datum
  #
  # End of do_router_translation_()

 # incomplete
 def do_router_hashcache_(self, in_datum, in_params, \
   in_direction, in_vuid = None):
  in_datum = out_datum
  return out_datum

 def do_router_forwarding_(self, in_datum, in_params, \
   in_direction, in_vuid = None):
  if not isinstance(in_params, dict):
    if in_params == self.CONST.rgn_REQUEST_PARAMS:
      return []
    return None
  if in_direction not in self.CONST.dir_any:
    self.irciot_error_(self.CONST.err_INVALID_DIRECTION, 0)
    return None
  if self.dup_detection_(in_datum, in_direction):
    self.irciot_error_(self.CONST.err_ROUTER_DUP_DETECT, 0)
    return None
  out_datum = in_datum
  return out_datum
  #
  # End of do_router_forwarding_()



