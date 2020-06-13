#!/usr/bin/python3

import sys
import os
import json
import base64
import warnings
import unittest
from pprint import pprint
from irciot import PyLayerIRCIoT

ii = PyLayerIRCIoT()

# UNITTEST:

class PyLayerIRCIoTTest(unittest.TestCase):

  _testMethodName = ''

  def __init__(self, in_name):
   global _log_mode
   global ii
   _log_mode = 1
   super(PyLayerIRCIoTTest, self).__init__(in_name)
   #
   # End of PyLayerIRCIoTTest.__init__()

  def test001_default_(self):
    self.assertEqual(ii_test_default_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def JSON_TEST_is_irciot_(my_json_text):
 to_log_("Testing JSON for IRC-IoT: @\033[1m%s\033[0m@len=%d@" \
  % (my_json_text, len(my_json_text)))
 if (len(my_json_text) > ii.irciot_get_mtu_()):
   to_log_("IRC-IoT Message length out of MTU range.")
   return False
 if (not ii.is_irciot_(my_json_text)):
   to_log_("is_irciot_() = *** This is not an IRC-IoT message ...")
   return False
 else:
   to_log_("is_irciot_() = !!! Yes, this is IRC-IoT message !!!")
   return True

def JSON_TEST_is_irciot_datumset_(my_datumset_text):
 to_log_("Testing Datums set: @\033[1m%s\033[0m@len=%d@" \
  % (my_datumset_text, len(my_datumset_text)))
 if (not ii.is_irciot_datumset_(my_datumset_text)):
   to_log_("is_irciot_datumset_() = *** This is not IRC-IoT datum set ...")
   return False
 else:
   to_log_("is_irciot_datumset_() = !!! Yes, this is IRC-IoT datum set !!!")
   return True

def ii_test_default_():
  my_skip = 0
  my_part = 0
  json_text  = '[{"mid":"1","oc":1,"op":1,"o":[{"oid":"x","ot":"maireq",'
  json_text += '"dst":"yyy","d":[{"src":"xxx","help":"super-string"}]}]}]'
  ii.is_irciot_(json_text)
  if JSON_TEST_is_irciot_(json_text):
   datumset_text = ii.irciot_deinencap_(json_text, \
     ii.CONST.api_vuid_self)
   to_log_("irciot_deinencap_()")
   if (JSON_TEST_is_irciot_datumset_(datumset_text)):
    json_text, my_skip, my_part \
     = ii.irciot_encap_(datumset_text, 0, 0, \
       ii.CONST.api_vuid_self)
    to_log_("irciot_encap_(): skip = %d, part = %d." \
     % (my_skip, my_part))
    if JSON_TEST_is_irciot_(json_text):
     to_log_("TEST_IS_OK")
     return True
  return False

my_command = ""
my_params  = []

def main():

 global my_command
 global my_params

 my_params = []
 if (len(sys.argv) > 1):
   my_command = sys.argv[1]
 for my_idx in range(2, 6):
   if len(sys.argv) > my_idx:
     my_params += [ sys.argv[my_idx] ]
 if (my_command == ""):
   my_command = 'default'

 if 'gost12' in my_params:
   ii.irciot_enable_blockchain_(ii.CONST.tag_mid_GOST12)
 if 'rsa1024' in my_params:
   ii.irciot_enable_blockchain_(ii.CONST.tag_mid_RSA1024)
 if 'ed25519' in my_params:
   ii.irciot_enable_blockchain_(ii.CONST.tag_mid_ED25519)
 if 'big_mtu' in my_params:
   ii.irciot_set_mtu_(10000)
 if 'cryptrsa' in my_params or 'test4rsa' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64Z_RSA)
 if 'cryptaes' in my_params or 'test4aes' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64Z_AES)
 if 'crypt2fish' in my_params or 'test2fish' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64Z_2FISH)
 if 'cryptbz2' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64_BZIP2)
 if 'base32' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_BASE32)
 if 'base64' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_BASE64)
 if 'base85' in my_params:
   ii.irciot_enable_encryption_(ii.CONST.tag_ENC_BASE85)
 if 'c1check' in my_params:
   ii.irciot_crc16_init_()
   ii.integrity_check = 1
   ii.integrity_stamp = 1
 if 'c1check' in my_params:
   ii.irciot.crc32_init_()
   ii.integrity_check = 2
   ii.integrity_stamp = 2

 to_log_("TEST NAME: '%s'" % my_command)

 if my_command == 'default':
   ii_test_default_()
 #
 # End of main()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()

