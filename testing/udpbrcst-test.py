#!/usr/bin/env python3

import sys
import os
import unittest
from pprint import pprint
from udpbrcst import PyLayerUDPb

# FOR TESTING:

my_command = ""
my_params  = []

my_udpb = PyLayerUDPb()

# UNITTEST:

class PyLayerUDPbTest(unittest.TestCase):

  _testMethodName = ''

  def __init__(self, in_name):
    global _log_mode
    _log_mode = 1
    super(PyLayerUDPbTest, self).__init__(in_name)
    #
    # End of PyLayerUDPbTest.__init__()

  def test001_default_(self):
    self.assertEqual(udpb_test_default_(), True)

  def test003_unary_isitip_(self):
    self.assertEqual(udpb_unary_isitip_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def udpb_test_default_():
  to_log_("TEST_IS_OK")
  return True

def udpb_unary_isitip_():
  if my_udpb.is_ip_address_('::1') \
   and my_udpb.is_ipv4_address_("127.0.0.1") \
   and not my_udpb.is_ipv4_address_("235.345.63.1") \
   and my_udpb.is_ipv6_address_("2a00:1450:4010:c06::8b") \
   and my_udpb.is_ipv6_address_("1234:5678:90ab:cde::8b") \
   and my_udpb.is_ipv6_address_("ABCD:EFab:cdef:cde::81") \
   and not my_udpb.is_ipv6_address_("2a00:1450:4010:c06::8z"):
     to_log_("TEST_IS_OK")
     return True
  return False

def main():

 global my_command
 global my_params

 my_params = []
 if len(sys.argv) > 1:
   my_command = sys.argv[1]
 for my_idx in range(2, 6):
   if len(sys.argv) > my_idx:
     my_params += [ sys.argv[my_idx] ]
 if my_command == "":
   my_command = 'default'

 print ("TEST NAME: '{}'".format(my_command))

 if my_command == 'default':
   udpb_test_default_()

 if my_command == 'isitip':
   udpb_unary_isitip_()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()

