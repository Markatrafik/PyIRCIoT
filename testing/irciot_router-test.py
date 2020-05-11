#!/usr/bin/python3

import sys
import os
import json
import warnings
import unittest
from pprint import pprint
from irciot_router import PyIRCIoT_router

ii = PyIRCIoT_router()

# UNITTEST:

class PyLayerIRCIoTTest(unittest.TestCase):

  _testMethodName = ''

  def __init__(self, in_name):
   global _log_mode
   _log_mode = 1
   super(PyLayerIRCIoTTest, self).__init__(in_name)
   #
   # End of PyLayerIRCIoTTest.__init__()

  def test000_default_(self):
    self.assertEqual(ii_test_default_(), True)

  def test001_test_forwarding_(self):
    self.assertEqual(ii_test_forwarding_(), True)

  def test002_test_translation_(self):
    self.assertEqual(ii_test_translation_(), True)

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
  to_log_("TEST_IS_OK")
  return True

def ii_test_forwarding_():
  ii_router_graphs = [ ( ii.do_router_forwarding_, {} ) ]
  my_src = '@myflat/esp8266@bedroom/humidity'
  my_message  = '{"mid":101,"oc":1,"op":1,"o":{"ot":"mainfo",'
  my_message += '"src":"%s",' % my_src
  my_message += '"dst":"","d":{"value":57,"unit":"percent"}}}'
  to_log_("\nInput message(lanif): '%s'\n" % my_message)
  my_message  = ii.do_router_(my_message, ii.CONST.dir_in, None)
  if not JSON_TEST_is_irciot_(my_message):
    return False
  to_log_("\nOutput message(wanif): '%s'\n" % my_message)
  out_json = ii.irciot_deinencap_(my_message, ii.CONST.api_vuid_self)
  to_log_("OUT_JSON==@%s@\n" % out_json)
  if not out_json == "[]":
    if JSON_TEST_is_irciot_datumset_(out_json):
      my_json = json.loads(out_json)[0]
      if my_json['src'] == my_src and \
         my_json['dst'] == '' and \
         my_json['value'] == 57 and \
         my_json['unit'] == 'percent':
        to_log_("TEST_IS_OK")
        return True
  return False

def ii_test_translation_():
  my_from = 'controller@kitchen'
  my_to   = 'computer@house'
  my_dst  = 'flower@garden/yyy'
  to_log_("\nIn Scope:  '\033[1m%s\033[0m'" % my_from)
  to_log_("\nOut Scope: '\033[1m%s\033[0m'" % my_to)
  ii.router_graphs += [
    ( ii.do_router_translation_, { 
      ii.CONST.tag_IN_SCOPE  : my_from,
      ii.CONST.tag_OUT_SCOPE : my_to
  } ) ]
  my_message  = '{"mid":"1","oc":1,"op":1,"o":'
  my_message += '[{"oid":"x","ot":"maireq","dst":"%s","d":' % my_dst
  my_message += '[{"src":"%s/xxx","help":"super-string"}]}]}' % my_from
  to_log_("\nPASS(1) :: from insdie\n\nInput message(lanif): '%s'" % my_message)
  my_message  = ii.do_router_(my_message, ii.CONST.dir_in, None)
  to_log_("\nOutput message(wanif): '%s'" % my_message)
  if not JSON_TEST_is_irciot_(my_message):
    return False
  my_message  = '{"mid":"2","oc":1,"op":1,"o":'
  my_message += '[{"oid":"y","ot":"maiack","src":"%s",' % my_dst
  my_message += '"dst":"%s/xxx","d":{"help":"not-super-string"}}]}' % my_to
  to_log_("\nPASS(2) :: from outside\n\nInput message(wanif):  '%s'" % my_message)
  my_message = ii.do_router_(my_message, ii.CONST.dir_out, None)
  to_log_("\nOutput message(lanif): '%s'\n" % my_message)
  if not JSON_TEST_is_irciot_(my_message):
    return False
  out_json = ii.irciot_deinencap_(my_message, ii.CONST.api_vuid_self)
  to_log_("OUT_JSON==@%s@\n" % out_json)
  if not out_json == "[]":
    if JSON_TEST_is_irciot_datumset_(out_json):
      my_json = json.loads(out_json)[0]
      if my_json['src'] == 'flower@garden/yyy' and \
         my_json['dst'] == 'controller@kitchen/xxx':
        to_log_("TEST_IS_OK")
        return True
  return False
  # End of ii_test_translation_()

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

 if (my_command == 'default'):
   ii_test_default_()

 if (my_command == 'forwarding'):
   ii_test_forwarding_()
 if (my_command == 'translation'):
   ii_test_translation_()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()
