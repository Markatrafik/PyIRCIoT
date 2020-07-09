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

  def test008_bchsigning_with_ed25519_(self):
    ii.irciot_enable_blockchain_(ii.CONST.tag_mid_ED25519)
    self.assertEqual(ii_test_bchsigning_(), True)
    ii.irciot_disable_blockchain_()

  def test009_bchsigning_with_rsa1024_(self):
    ii.irciot_enable_blockchain_(ii.CONST.tag_mid_RSA1024)
    self.assertEqual(ii_test_bchsigning_(), True)
    ii.irciot_disable_blockchain_()

  def test010_bchsigning_with_gost12_(self):
    my_params.append('gost12')
    ii.irciot_enable_blockchain_(ii.CONST.tag_mid_GOST12)
    self.assertEqual(ii_test_bchsigning_(), True)
    ii.irciot_disable_blockchain_()

  def test011_test_libirciot_(self):
    self.assertEqual(ii_test_libirciot_(), True)

  def test013_test_multidatum_(self):
    self.assertEqual(ii_test_multidatum_(), True)

  def test014_test_multibigval_(self):
    self.assertEqual(ii_test_multibigval_(), True)

  def test015_test_multinextbig_(self):
    self.assertEqual(ii_test_multinextbig_(), True)

  def test016_test_new2018datums_(self):
    self.assertEqual(ii_test_new2018datums_(), True)

  def test017_test_defrag3loop_(self):
    ii.irciot_disable_blockchain_()
    ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B85_ZLIB)
    self.assertEqual(ii_test_defrag3loop_(), True)

  def test018_test_defrag1b64p_(self):
    ii.irciot_enable_encryption_(ii.CONST.tag_ENC_BASE64)
    self.assertEqual(ii_test_defrag1b64p_(), True)

  def test019_test_defrag2b64z_(self):
    ii.irciot_enable_encryption_(ii.CONST.tag_ENC_B64_ZLIB)
    self.assertEqual(ii_test_defrag2b64z_(), True)

  def test020_test_version_(self):
    self.assertEqual(ii_test_version_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def JSON_TEST_is_irciot_(my_json_text):
 to_log_("Testing JSON for IRC-IoT: @\033[1m{}\033[0m@len={}@".format( \
   my_json_text, len(my_json_text)))
 if len(my_json_text) > ii.irciot_get_mtu_():
   to_log_("IRC-IoT Message length out of MTU range.")
   return False
 if not ii.is_irciot_(my_json_text):
   to_log_("is_irciot_() = *** This is not an IRC-IoT message ...")
   return False
 else:
   to_log_("is_irciot_() = !!! Yes, this is IRC-IoT message !!!")
   return True

def JSON_TEST_is_irciot_datumset_(my_datumset_text):
 to_log_("Testing Datums set: @\033[1m{}\033[0m@len={}@".format( \
   my_datumset_text, len(my_datumset_text)))
 if not ii.is_irciot_datumset_(my_datumset_text):
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
   if JSON_TEST_is_irciot_datumset_(datumset_text):
    json_text, my_skip, my_part \
     = ii.irciot_encap_(datumset_text, 0, 0, \
       ii.CONST.api_vuid_self)
    to_log_("irciot_encap_(): skip = {}, part = {}.".format( \
     my_skip, my_part))
    if JSON_TEST_is_irciot_(json_text):
     to_log_("TEST_IS_OK")
     return True
  return False

def ii_test_version_():
  my_string = '{"mid":"53159", "ver": "?"}'
  if ii.is_irciot_(my_string):
    to_log_('IN: {}'.format(my_string))
    my_json = ii.irciot_deinencap_(my_string)
    to_log_('OUT: {}'.format(my_json))
    try:
      my_list = json.loads(my_json)
      my_dict = my_list[0]
      my_ver  = my_dict['ver']
      if my_ver == ii.irciot_protocol_version_():
        to_log_('TEST_IS_OK')
        return True
    except:
      return False
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

def ii_test_bchsigning_():
  my_range = range(80)
  if 'gost12' in my_params:
    my_range = [ 1, 100 ]
  for i in my_range:
    my_str = 'abcdef{}'.format(i)
    for j in range(i):
      my_str += "x"
    to_log_("Source String: '" + my_str + "'")
    ( my_method, my_private_key, my_public_key ) \
      = ii.irciot_blockchain_save_defaults_()
    my_hash = ii.irciot_blockchain_sign_string_( \
     my_str, my_private_key)
    to_log_("Sign Hash: %s<%d>" % (my_hash, len(my_hash)))
    my_ok = ii.irciot_blockchain_verify_string_( \
     my_str, my_hash, my_public_key)
    if my_ok:
      to_log_("Verify: OK")
    else:
      to_log_("Verifying failed")
      return False
    to_log_("")
  to_log_("Using PyLayerIRCIoT: \033[1m%s\033[0m" \
    % ii.CONST.irciot_library_version)
  to_log_("Protocol: %s\n" \
    % ii.CONST.irciot_protocol_version)
  to_log_("TEST_IS_OK")
  return True
  # End of ii_test_bchsigning_()

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

def ii_test_multidatum_():
  datumset_text  = '[{"ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.115959",'
  datumset_text += '"src":"maiengine","cnd":{"temperature":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.116012",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"IPC1002@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.116048",'
  datumset_text += '"src":"maiengine","cnd":{"kidsdoor":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:48:08.11253",'
  datumset_text += '"src":"maiengine","cnd":{"temperature":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:48:08.11752",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:48:08.11788",'
  datumset_text += '"src":"maiengine","cnd":{"motion":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:49:07.115959",'
  datumset_text += '"src":"maiengine","cnd":{"temperature":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:49:07.116012",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"IPC1002@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:49:07.116048",'
  datumset_text += '"src":"maiengine","cnd":{"kidsdoor":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:49:08.11253",'
  datumset_text += '"src":"maiengine","cnd":{"temperature":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:49:08.11752",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:49:08.11788",'
  datumset_text += '"src":"maiengine","cnd":{"motion":"?"}}]'
  if JSON_TEST_is_irciot_datumset_(datumset_text):
   json_text, my_skip, my_part \
    = ii.irciot_encap_(datumset_text, 0, 0, \
     ii.CONST.api_vuid_self)
   to_log_("irciot_encap_(): " \
    + "skip = {}, part = {}.".format(my_skip, my_part))
   if JSON_TEST_is_irciot_(json_text):
    test_ok = 1
    while ((my_skip > 0) or (my_part > 0)):
     json_text, my_skip, my_part \
      = ii.irciot_encap_(datumset_text, my_skip, my_part, \
       ii.CONST.api_vuid_self)
     to_log_("irciot_encap_(): " \
      + "skip = {}, part = {}.".format(my_skip, my_part))
     if not JSON_TEST_is_irciot_(json_text):
      test_ok = 0
    if test_ok == 1:
     to_log_("TEST_IS_OK")
     return True
  return False
  # End of ii_test_multidatum_()

def ii_test_multibigval_():
  datumset_text  = '[{"bigval":"realbigval-hello-world-big-string-NNN-xxx55'
  datumset_text += '55zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz-vvvvvvvvvvvvvvvv'
  datumset_text += 'vvvvv-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-xxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxx","ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.115959","src":"maiengine",'
  datumset_text += '"cnd":{"temperature":"?"}},{"ot":"maireq",'
  datumset_text += '"dst":"MUSICA@Kidsroom","t":"2018-08-23 14:48:07.116012",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"IPC1002@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.116048",'
  datumset_text += '"src":"maiengine","cnd":{"kidsdoor":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:48:08.11253","src":"maiengine",'
  datumset_text += '"cnd":{"temperature":"?"}},{"ot":"maireq",'
  datumset_text += '"dst":"TUX2@Livingroom","t":"2018-08-23 14:48:08.11752",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}}]'
  if JSON_TEST_is_irciot_datumset_(datumset_text):
   json_text, my_skip, my_part \
    = ii.irciot_encap_(datumset_text, 0, 0, \
     ii.CONST.api_vuid_self)
   to_log_("irciot_encap_(): " \
    + "skip = {}, part = {}.".format(my_skip, my_part))
   if JSON_TEST_is_irciot_(json_text):
    test_ok = 1
    while ((my_skip > 0) or (my_part > 0)):
     json_text, my_skip, my_part \
      = ii.irciot_encap_(datumset_text, my_skip, my_part, \
       ii.CONST.api_vuid_self)
     to_log_("irciot_encap_(): " \
      + "skip = {}, part = {}.".format(my_skip, my_part))
     if not JSON_TEST_is_irciot_(json_text):
      test_ok = 0
    if test_ok == 1:
     to_log_("TEST_IS_OK")
     return True
  return False
  # End of ii_test_multibigval_()

def ii_test_multinextbig_():
  datumset_text  = '[{"ot":"maireq","t":"2018-08-23 14:48:01.113333",'
  datumset_text += '"dst":"MUSICA@Kidsroom","src":"maiengine",'
  datumset_text += '"cnd":{"relay3":"?"}},'
  datumset_text += '{"bigval":"realbigval-hello-wolrd-big-string-NNN-xxx55'
  datumset_text += '55zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz-vvvvvvvvvvvvvvvv'
  datumset_text += 'vvvvv-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-xxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxx","ot":"maireq","dst":"MUSICA@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.115959","src":"maiengine",'
  datumset_text += '"cnd":{"temperature":"?"}},{"ot":"maireq",'
  datumset_text += '"dst":"MUSICA@Kidsroom","t":"2018-08-23 14:48:07.116012",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"IPC1002@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.116048",'
  datumset_text += '"src":"maiengine","cnd":{"kidsdoor":"?"}},'
  datumset_text += '{"ot":"maireq","dst":"TUX2@Livingroom",'
  datumset_text += '"t":"2018-08-23 14:48:08.11253","src":"maiengine",'
  datumset_text += '"cnd":{"temperature":"?"}},{"ot":"maireq",'
  datumset_text += '"dst":"TUX2@Livingroom","t":"2018-08-23 14:48:08.11752",'
  datumset_text += '"src":"maiengine","cnd":{"humidity":"?"}}]'
  if JSON_TEST_is_irciot_datumset_(datumset_text):
   json_text, my_skip, my_part \
    = ii.irciot_encap_(datumset_text, 0, 0, \
     ii.CONST.api_vuid_self)
   to_log_("irciot_encap_(): " \
    + "skip = {}, part = {}.".format(my_skip, my_part))
   if JSON_TEST_is_irciot_(json_text):
    test_ok = 1
    while ((my_skip > 0) or (my_part > 0)):
     json_text, my_skip, my_part \
      = ii.irciot_encap_(datumset_text, my_skip, my_part, \
       ii.CONST.api_vuid_self)
     to_log_("irciot_encap_(): " \
      + "skip = {}, part = {}.".format(my_skip, my_part))
     if not JSON_TEST_is_irciot_(json_text):
      test_ok = 0
    if test_ok == 1:
     to_log_("TEST_IS_OK")
     return True
  return False
  # End of ii_test_multinextbig_()

def ii_test_defrag3loop_():
  datumset_text  = '[{"bigval":"long-long-value-xxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxsensorxxxxxxxxnxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  datumset_text += 'xxxxxxxxxxxxxxxxxxx","ot":"request","dst":"PLAYER@Kidsroom",'
  datumset_text += '"t":"2018-08-23 14:48:07.115959","src":"myengine",'
  datumset_text += '"addonvar1":"value1","addonvar2":"val2","addonvar3":"val3",'
  datumset_text += '"x1":45,"x2":46,"x3":47,"x4":551,"x5l":0.000000001,"uu":"o",'
  datumset_text += '"middlevar":"text-text-text-text-text-text-text-text-text",'
  datumset_text += '"visionon1":"000001","vixicron2":"abcd","uptime645":"ffff",'
  datumset_text += '"garbagevar":"ejkqdfwjefkljwklefjklwejfklwejfkljwkljfeklw",'
  datumset_text += '"cnd":{"uri":"?"}},'
  datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:07.116012",'
  datumset_text += '"src":"myengine","cnd":{"temperature":"?"},"ot":"request"},'
  datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:08.157125",'
  datumset_text += '"src":"myengine","cnd":{"humidity":"?"},"ot":"request"}]'
  if 'big_mtu' in my_params:
    to_log_("TEST_IS_SKIPPED")
    return True
  JSON_cnt = 0
  to_log_("DATUMSET == @{}@".format(datumset_text))
  json_text, skip_param, part_param \
   = ii.irciot_encap_(datumset_text, 0, 0, \
    ii.CONST.api_vuid_self)
  if ii.is_irciot_(json_text):
    to_log_("JSON == @{}@".format(json_text))
    msg_text = ii.irciot_deinencap_(json_text, \
      ii.CONST.api_vuid_self)
    while ((skip_param > 0) or (part_param > 0)):
      json_text, skip_param, part_param \
       = ii.irciot_encap_(datumset_text, skip_param, part_param, \
        ii.CONST.api_vuid_self)
      to_log_("JSON_TEXT==@{}@".format(json_text))
      out_json = ii.irciot_deinencap_(json_text, \
        ii.CONST.api_vuid_self)
      to_log_("OUT_JSON==@{}@".format(out_json))
      if out_json != "[]":
        if JSON_TEST_is_irciot_datumset_(out_json):
          JSON_cnt += 1
          if JSON_cnt == 2:
            to_log_("TEST_IS_OK")
            return True
  return False
  # End of ii_test_defrag3loop_()

def ii_test_new2018datums_():
  datumset_text  = '[{"ot": "mainfo","t": "2018-08-01 00:00:33.228723",'
  datumset_text += '"src": "MP714@Kitchen/co2","dst": "","dt":"cnd","d":1162},'
  datumset_text += '{"ot": "mainfo","t": "2018-08-01 00:00:41.425239",'
  datumset_text += '"src": "MP714@Kitchen/adc2","dst": "","dt":"cnd","d":135},'
  datumset_text += '{"ot": "mainfo","t": "2018-08-01 00:00:51.797226",'
  datumset_text += '"src": "MP714@Kitchen/temperature","dst": "",'
  datumset_text += '"dt":"cnd","d":26.45 },'
  datumset_text += '{"ot": "mainfo","t": "2018-08-01 00:01:02.170460",'
  datumset_text += '"src": "MP714@Kitchen/cookerhood","dst": "",'
  datumset_text += '"dt":"cnd","d": 0},'
  datumset_text += '{"ot": "mainfo","t": "2018-08-01 00:15:47.977112",'
  datumset_text += '"src": "MP714@Kitchen/motion","dst": "",'
  datumset_text += '"dt":"prs","d":1},'
  datumset_text += '{"ot": "mainfo","t": "2018-08-01 00:15:47.977112",'
  datumset_text += '"src": "MP714@Kitchen/LIZA","dst": "",'
  datumset_text += '"dt":"prs","d":0.75},'
  datumset_text += '{"ot": "maicmd","t": "2018-08-01 00:15:50.186060",'
  datumset_text += '"src": "nooLite@Kitchen/toplight","dst": "",'
  datumset_text += '"dt":"act","d": 1}]'
  if JSON_TEST_is_irciot_datumset_(datumset_text):
   json_text, my_skip, my_part \
    = ii.irciot_encap_(datumset_text, 0, 0, \
     ii.CONST.api_vuid_self)
   to_log_("irciot_encap_(): skip = {}, part = {}.".format(my_skip, my_part))
   if JSON_TEST_is_irciot_(json_text):
    test_ok = 1
    while my_skip > 0 or my_part > 0:
     json_text, my_skip, my_part \
     = ii.irciot_encap_(datumset_text, my_skip, my_part, \
       ii.CONST.api_vuid_self)
     to_log_("irciot_encap_(): " \
      + "skip = {}, part = {}.".format(my_skip, my_part))
     if not JSON_TEST_is_irciot_(json_text):
       test_ok = 0
    if test_ok == 1:
     to_log_("TEST_IS_OK")
     return True
  return False
  # End of ii_test_new2018datums_()

def ii_test_defrag1b64p_():
  to_log_("Input datums to irciot_deinencap_() functions")
  msg_test  = '{"mid":"43907","o":{"oid":"5101","ot":"maireq",'
  msg_test += '"d":{"bp":0,"did":"248","bc":451,"ed":"'
  msg_test += 'eyJ0IjoiMjAxOC0wOC0yMyAxNDo0ODowNy4xMTU5NTkiLCJzcmMiOiJtYWllbmd'
  msg_test += 'pbmUiLCJjbmQiOnsidGVtcGVyYXR1cmUiOiI/In0sImRzdCI6Ik1VU0lDQUBLaW'
  msg_test += 'Rzcm9vbSIsImJpZ3ZhbCI6InJlYWxiaWd2YWwtaGVsbG8td29scmQtYmlnLXN0c'
  msg_test += 'mluZy1OTk4teHh4NTU1NXp6enp6enp6enp6enp6enp6enp6enp6enp6enp6enp6'
  msg_test += 'enp6ei12dnZ2dnZ2dnZ2dnYtYWFhYWFhYWFhYWFhYWFhYWFhYWF'
  msg_test += 'hYWFhYWFhYWFhYWFhYWFhYWEteHh4eHh4eHh4eHh4eHh4"}}}'
  if JSON_TEST_is_irciot_(msg_test):
    out_json  = ii.irciot_deinencap_(msg_test, \
      ii.CONST.api_vuid_self)
    if out_json == "[]":
      msg_test  = '{"mid":"43908","o":{"oid":"5101","ot":"maireq",'
      msg_test += '"d":{"bp":360,"did":"248","bc":451,"ed":"'
      msg_test += 'eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh'
      msg_test += '4eHh2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dn'
      msg_test += 'Z2dnZ2dnZ2dnZ2eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4e'
      msg_test += 'Hh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHgifQ=="}}}'
      if JSON_TEST_is_irciot_(msg_test):
        out_json = ii.irciot_deinencap_(msg_test, \
          ii.CONST.api_vuid_self)
        if JSON_TEST_is_irciot_datumset_(out_json):
          to_log_("TEST_IS_OK")
          return True
  return False
  # End of ii_test_defrag1b64p_()

def ii_test_defrag2b64z_():
  to_log_("Input datums to irciot_deinencap_() functions")
  msg_test  = '{"mid":"62742","o":{"oid":"1581","ot":"request",'
  msg_test += '"d":{"bp":0,"ed":"'
  msg_test += 'eJzFUrtSwzAQ/BXmapuxbCmJ1QAFFRQMHaVtnT2yZQnkR8xk8u+cEjJQMZA'
  msg_test += 'ibHGS9la7ze5gmkCCgwhGOtOEbeJkE6fZFeOSb2SyvmZM5CInwZKC5KsI1B'
  msg_test += 'CkT493L/fPtw9aDd65nvbT66h7XHFB25pAVGUVyB1MXhN3A/sICqWcnQvPi'
  msg_test += 'JgLMyEj2awXXXlnKQCKslIhjARcRDD4isj+HW2jLYaFMCAZxkke/g3aWWeD'
  msg_test += 'WRIQzErdkDExxtkmPoxDULxcCvPFks6JGtAOzp9e9icp/t3930EN6LVSBql'
  msg_test += 'kVIIRlzH+5Qjt4iCFYBE0hS+L5tME2+5N1dsW6860285g3XZmi219m",'
  msg_test += '"did":"687","bc":388}}}'
  if JSON_TEST_is_irciot_(msg_test):
    out_json  = ii.irciot_deinencap_(msg_test, \
      ii.CONST.api_vuid_self)
    if out_json == "[]":
      msg_test  = '{"mid":"62743","o":{"oid":"1581","ot":"request",'
      msg_test += '"d":{"bp":349,"ed":"'
      msg_test += 'oFsa6QnfFU8PVY8/UZlRyoLSXTn6/0HJ/xj+Q=='
      msg_test += '","did":"687","bc":388}}}'
      if JSON_TEST_is_irciot_(msg_test):
        out_json = ii.irciot_deinencap_(msg_test, \
          ii.CONST.api_vuid_self)
        if JSON_TEST_is_irciot_datumset_(out_json):
          to_log_("TEST_IS_OK")
          return True
  return False
  # End of ii_test_defrag2b64z_()

my_command = ""
my_params  = []

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

 if my_command == 'version':
   ii_test_version_()

 if my_command == 'libirciot':
   ii_test_libirciot_()

 if my_command == 'multidatum':
   ii_test_multidatum_()

 if my_command == 'multibigval':
   ii_test_multibigval_()

 if my_command == 'multinextbig':
   ii_test_multinextbig_()

 if my_command == 'new2018datums':
   ii_test_new2018datums_()

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

 if my_command == 'bchsigning':
   # The test is correct only if the appropriate
   # Blockchain signature method is selected:
   if len(set(['ed25519','rsa1024','gost12'])-set(my_params)) == 3:
     to_log_("TEST_IS_SKIPPED")
     return
   ii_test_bchsigning_()

 if my_command == 'defrag1b64p':
   if ii.crypt_method != ii.CONST.tag_ENC_BASE64:
     # The test is correct only for b64p encryption method
     to_log_("TEST_IS_SKIPPED")
     return
   ii_test_defrag1b64p_()

 if my_command == 'defrag2b64z':
   if ii.crypt_method != ii.CONST.tag_ENC_B64_ZLIB:
     # The test is correct only for b64z encryption method:
     # ZLIB + BASE64 required
     to_log_("TEST_IS_SKIPPED")
     return
   ii_test_defrag2b64z_()

 if my_command == 'defrag3loop':
   # The following workarounds should be resolved:
   if ('rsa1024' in my_params or 'gost12' in my_params) \
    and 'crypt2fish' in my_params:
     to_log_("TEST_IS_SKIPPED")
     return
   ii_test_defrag3loop_()

 if my_command == 'crc':
   ii_test_unary_crc_()
 #
 # End of main()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()

