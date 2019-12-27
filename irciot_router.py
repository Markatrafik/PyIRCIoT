'''
'' PyIRCIoT-router (PyIRCIoT_router class)
''
'' Copyright (c) 2019 Alexey Y. Woronov
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
  self.input_routes  = []
  # This is list ot tuples each of which contains an source and
  # destination IRC-IoT address or mask in the input messages
  #
  self.router_graph  = [ self.do_forwarding ]
  # This is list of functions sequentially performed on the
  # message flow. Each function must have a specified inbound
  # and outbound interface. If another list is used as a list
  # item, then the first item of a nested list must contain a
  # function defining the conditions to perform the list, the
  # remaining items in such a list are used to process messages
  #
  self.output_routes = []
  # This is list ot tuples each of which contains an source and
  # destination IRC-IoT address or mask in the output messages
  #
  self.output_plugin = None
  # This is an object that defines routing and postfiltering
  # of output messages at an external level outside of this
  # IRC-IoT router class
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

 def do_translation(self, in_message):
  out_message = in_message
  return out_message

 def do_forwarding(self, in_message):
  out_message = in_message
  return out_message

