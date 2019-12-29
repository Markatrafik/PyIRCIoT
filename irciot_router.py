'''
'' PyIRCIoT-router (PyIRCIoT_router class)
''
'' Copyright (c) 2019 Alexey Y. Woronov
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
import random
import json

class PyIRCIoT_router( PyLayerIRCIoT ):

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
  self.router_graphs = [ ( self.do_forwarding, {} ) ]
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
  super(PyIRCIoT_router, self).__init__()
  #
  # End of PyIRCIoT_router.__init__()

 def router_pointer (self, in_compatibility, in_messages_pack):
  # Warning: interface may be changed while developing
  return False

 def router_error_(self, in_error_code, in_addon = None):
  # Warning: interface may be changed while developing
  return

 def is_router_route_(self, in_route):
  if not isinstance(in_route, tuple):
    return False
  return True

 def is_router_routes_(self, in_routes):
  if not isinstance(in_routes, list):
    return False
  for my_route in in_routes:
    if not is_route_(self, my_route):
      return False
  return True

 def is_router_graph_(self, in_graph):
  try:
    ( my_func, my_params ) = in_tuple
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
      if not self.is_graphs_(my_item):
        return False
    else:
      if not self.is_graph_(my_item):
        return False
  return True

 def do_main_graph_(in_datum, in_graph, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not self.is_router_graph_(in_graph):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  ( my_function_, my_params ) = in_graph
  return my_function_( in_datum, my_params, in_vuid )

 def do_main_route_(in_datum, in_route, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_route, tuple):
    return None
  if not self.is_irciot_datum_(in_datum, None, None, None):
    return None
  return in_datum

 def do_main_graphs_(in_datum, in_graphs, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_graphs, list):
    return None
  my_datum = in_datum
  for my_index, my_graph in enumerate(my_graphs):
    if isinstance(my_graph, list):
      if my_graph == []:
        return None
      my_datum = self.do_main_graphs_(my_datum, my_graph, in_vuid)
    else:
      tmp_datum = self.do_main_graph_(my_datum, in_graph, in_vuid)
      if my_index == 0 and isinstance(tmp_datum, bool):
        if not tmp_datum:
          break
      elif isinstance(tmp_datum, dict):
        my_datum = tmp_datum
      else:
        my_datum = in_datum
      del tmp_datum
  return my_datum
  #
  # End of PyIRCIoT_router.do_main_graphs_()

 def do_main_routes_(in_datum, in_routes, in_vuid = None):
  if not isinstance(in_datum, dict):
    return None
  if not isinstance(in_routes, list):
    return None
  for my_route in in_routes:
    pass
  return in_datum

 def do_main(self, in_message, in_vuid = None):
  if not is_routes(self.in_routes) \
  or not is_routes(self.out_routes) \
  or not is_graphs(self.router_graphs):
    return
  my_json = self.irciot_deinencap_(in_message, in_vuid)
  if my_json == "":
    return
  try:
    my_datums = json.loads(my_json)
  except:
    return
  if isinstance(my_datums, dict):
    my_datums = [ my_datums ]
  if not isinstance(my_datums, list):
    return
  my_outdat = []
  for my_datum in my_datums:
    my_datum = self.do_main_routes_(my_datum, self.in_routes, in_vuid)
    my_datum = self.do_main_graphs_(my_datum, in_vuid)
    my_datum = self.do_main_routes_(my_datum, self.out_routes, in_vuid)
    if my_datum != None:
      my_outdat.append(my_datum)
  if my_outdat == []:
    return "[]"
  out_message = self.irciot_encap_all_(my_outdat, in_vuid)
  return out_message
  #
  # End of PyIRCIoT_router.do_main()

 def do_translation(self, in_datum, in_params, in_vuid = None):
  if not isinstance(in_parpams, dict):
    return None
  #
  out_datum = in_datum
  return out_datum

 def do_forwarding(self, in_datum, in_params, in_vuid = None):
  out_datum = in_datum
  return out_datum

