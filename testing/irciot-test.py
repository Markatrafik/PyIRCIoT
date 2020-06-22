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

  def test002_unary_crc_(self):
    self.assertEqual(ii_test_unary_crc_(), True)

  def test003_unary_aes_(self):
    self.assertEqual(ii_test_unary_aes_(), True)

  def test004_unary_rsa_(self):
    self.assertEqual(ii_test_unary_rsa_(), True)

  def test005_unary_2fish_(self):
    warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
    warnings.filterwarnings('ignore', category=ResourceWarning)
    self.assertEqual(ii_test_unary_2fish_(), True)

  def test006_c1integrity_(self):
    self.assertEqual(ii_test_c1integrity_(), True)
    ii.integrity_check = 0
    ii.integrity_stamp = 0

  def test007_c2integrity_(self):
    self.assertEqual(ii_test_c2integrity_(), True)
    ii.integrity_check = 0
    ii.integrity_stamp = 0

  def test011_test_libirciot_(self):
    self.assertEqual(ii_test_libirciot_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def JSON_TEST_is_irciot_(my_json_text):
 to_log_("Testing JSON for IRC-IoT: @\033[1m{}\033[0m@len={}@".format( \
   my_json_text, len(my_json_text)))
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
 to_log_("Testing Datums set: @\033[1m{}\033[0m@len={}@".format( \
   my_datumset_text, len(my_datumset_text)))
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
    to_log_("irciot_encap_(): skip = {}, part = {}.".format( \
     my_skip, my_part))
    if JSON_TEST_is_irciot_(json_text):
     to_log_("TEST_IS_OK")
     return True
  return False

def ii_test_unary_2fish_():
  my_password = b'my_password&'
  for i in range(0, 5):
    my_password += my_password
  to_log_("original==@\033[1;33m{}\033[0m@".format(str(my_password, 'utf-8')))
  ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64_2FISH)
  ( my_method, my_private_key, my_public_key ) \
    = ii.irciot_encryption_save_defaults_()
  my_encbuf = ii.irciot_crypto_2fish_encrypt_( my_password, my_private_key )
  to_log_("encrypted(TwoFish)==@\033[1;35m{}\033[0m@".format(my_encbuf))
  my_decrypt = ii.irciot_crypto_2fish_decrypt_( my_encbuf, my_private_key )
  if my_decrypt == None:
    return False
  to_log_("decrypted==@\033[1;32m{}\033[0m@".format(str(my_decrypt, 'utf-8')))
  if my_password == my_decrypt:
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_unary_rsa_():
  my_password = b'my_password&'
  for i in range(0, 3):
    my_password += my_password
  to_log_("original==@\033[1;33m{}\033[0m@".format(str(my_password, 'utf-8')))
  ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64Z_RSA)
  ( my_method, my_private_key, my_public_key ) \
    = ii.irciot_encryption_save_defaults_()
  my_encbuf = ii.irciot_crypto_RSA_encrypt_( my_password, my_public_key )
  to_log_("encrypted(RSA)==@\033[1;35m{}\033[0m@".format(my_encbuf))
  my_decrypt = ii.irciot_crypto_RSA_decrypt_( my_encbuf, my_private_key )
  if my_decrypt == None:
    return False
  to_log_("decrypted==@\033[1;32m{}\033[0m@".format(str(my_decrypt, 'utf-8')))
  if my_password == my_decrypt:
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_unary_aes_():
  my_password = b'my_password&'
  for i in range(0, 5):
    my_password += my_password
  to_log_("original==@\033[1;33m{}\033[0m@".format(str(my_password, 'utf-8')))
  ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64_AES)
  ( my_method, my_private_key, my_public_key ) \
    = ii.irciot_encryption_save_defaults_()
  my_encbuf = ii.irciot_crypto_AES_encrypt_( my_password, my_private_key )
  to_log_("encrypted(AES)==@\033[1;35m{}\033[0m@".format(my_encbuf))
  if my_encbuf == None:
    return False
  my_decrypt = ii.irciot_crypto_AES_decrypt_( my_encbuf, my_private_key )
  to_log_("decrypted==@\033[1;32m{}\033[0m@".format(str(my_decrypt, 'utf-8')))
  if my_password == my_decrypt:
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_unary_crc_():
  my_test = 0
  my_password = b'MY_password-inside-stringxxx@'
  to_log_('\nmy_password: [\033[1;41m{}\033[0m]\n'.format( \
    str(my_password, 'utf-8')))
  ii.irciot_crc16_init_()
  my_crc16 = ii.irciot_crc16_(my_password)
  if my_crc16 != None:
    my_addon = '"c1":"%s",' % my_crc16
    to_log_("CRC16 internal: [\033[1;1;44m{}\033[0m] (len={})\n".format( \
      my_addon, len(my_addon)))
  if my_addon == '"c1":"5c66",':
    my_test += 1
  my_crc32 = ii.irciot_crc32_(my_password)
  if my_crc32 != None:
    my_addon = '"c2":"%s",' % my_crc32
    to_log_("CRC32 by Zlib: [\033[1;1;44m" \
     + "{}\033[0m] (len={})\n".format(my_addon, len(my_addon)))
  if my_addon == '"c2":"08623ca6",':
    my_test += 1
  if my_test == 2:
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_c1integrity_():
  ii.irciot_crc16_init_()
  ii.integrity_check = 1
  json_lead  = '{"mid":"'
  json_text  = '","oc":0,"op":0,"optkey1st":"test",'
  json_text += '"optkey2nd":8015,"optkey5x":392,"o":[{"oid":111281,'
  json_text += '"d":{"datkey":"aaa","src":"@xxx","dst":"@yyy"},'
  json_text += '"ok2nd":727,"ok5x":761,"ot":"test1"},{"oid":111282,'
  json_text += '"d":{"datkey2":"bbb","src":"@xxx","dst":"@yyy"},'
  json_text += '"objkey1":"abcdef","ot":"test2"}],'
  json_calc  = json_lead + json_text + '"c1":""}'
  to_log_("Calculating JSON: #\033[2;33m{}\033[0m#len={}#".format( \
    json_calc, len(json_calc)))
  my_crc16   = ii.irciot_crc16_(bytes(json_calc, 'utf-8'))
  to_log_("Calculated CRC16: 0x{}".format(my_crc16))
  json_test  = json_lead + "abcdef" + json_text + '"c1":"%s"}' % my_crc16
  to_log_("Tested JSON: #\033[2;36m{}\033[0m#len={}#".format( \
    json_test, len(json_test)))
  if ii.is_irciot_(json_test) and my_crc16 == 'f564':
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_c2integrity_():
  ii.irciot_crc32_init_()
  ii.integrity_check = 2
  json_lead  = '{"mid":"'
  json_text  = '","oc":0,"op":0,"optkey1st":"test",'
  json_text += '"optkey2nd":8015,"optkey5x":392,"o":[{"oid":111281,'
  json_text += '"d":{"datkey":"aaa","src":"@xxx","dst":"@yyy"},'
  json_text += '"ok2nd":727,"ok5x":761,"ot":"test1"},{"oid":111282,'
  json_text += '"d":{"datkey2":"bbb","src":"@xxx","dst":"@yyy"},'
  json_text += '"objkey1":"abcdef","ot":"test2"}],'
  json_calc  = json_lead + json_text + '"c1":""}'
  to_log_("Calculating JSON: #\033[2;33m{}\033[0m#len={}#".format( \
    json_calc, len(json_calc)))
  my_crc32   = ii.irciot_crc32_(bytes(json_calc, 'utf-8'))
  to_log_("Calculated CRC32: 0x{}".format(my_crc32))
  json_test  = json_lead + "abcdef" + json_text + '"c1":"%s"}' % my_crc32
  to_log_("Tested JSON: #\033[2;36m{}\033[0m#len={}#".format( \
    json_test, len(json_test)))
  if ii.is_irciot_(json_test) and my_crc32 == 'fa7fda88':
    to_log_("TEST_IS_OK")
    return True
  return False

def ii_test_libirciot_():
  json_text  = '{"mid":107770,"oc":0,"op":0,"optkey1st":"test",'
  json_text += '"optkey2nd":801,"optkey5x":392,"o":[{"oid":111281,'
  json_text += '"d":{"datkey":"aaa","src":"@xxx","dst":"@yyy"},'
  json_text += '"ok2nd":727,"ok5x":761,"ot":"test1"},{"oid":111282,'
  json_text += '"d":{"datkey2":"bbb","src":"@xxx","dst":"@yyy"},'
  json_text += '"objkey1":"abcdef","ot":"test2"}]}'
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

 to_log_("TEST NAME: '{}'".format(my_command))

 if my_command == 'default':
   ii_test_default_()

 if my_command == 'libirciot':
   ii_test_libirciot_()

 if my_command == 'c1integrity':
   ii_test_c1integrity_()

 if my_command == 'c2integrity':
   ii_test_c2integrity_()

 if my_command == 'test4rsa':
   ii_test_unary_rsa_()

 if my_command == 'test4aes':
   ii_test_unary_aes_()

 if my_command == 'test2fish':
   ii_test_unary_2fish_()

 if my_command == 'crc':
   ii_test_unary_crc_()
 #
 # End of main()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()

