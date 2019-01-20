'''
'' PyIRCIoT
''
'' Copyright (c) 2018 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

# Those Global options override default behavior and memory usage
#
CAN_debug_library  = False
CAN_mid_blockchain = False # Creating a chain of cryptographic signatures
CAN_encrypt_datum  = False # Ability to encrypt and decrypt of "Datums"
CAN_compress_datum = True  # Ability to compress and decompress "Datums"
#
DO_always_encrypt  = False # Always encrypt "Datums" in IRC-IoT messages

import json
import random
import base64

if CAN_debug_library:
  from pprint import pprint
if CAN_compress_datum:
  import zlib
if CAN_mid_blockchain:
  import nacl.signing # Simple IRC-IoT blockchain signing by ED25519
if CAN_encrypt_datum or CAN_mid_blockchain:
  import hashlib
  from Crypto.PublicKey import RSA
  from Crypto.Hash import SHA as SHA1
  from Crypto.Signature import PKCS1_v1_5
if CAN_encrypt_datum:
  from Crypto.Cipher import AES
#from Crypto import Random
#from Crypto.Cipher import PKCS1_OAEP
#from twofish import Twofish

class PyIRCIoT(object):

 class CONST(object):
  #
  irciot_protocol_version = '0.3.18'
  #
  irciot_library_version  = '0.0.57'
  #
  # IRC-IoT TAGs
  #
  tag_MESSAGE_ID  = 'mid' # Message ID
  tag_MESSAGE_OC  = 'oc'  # Objects Count
  tag_MESSAGE_OP  = 'op'  # Objects Passed
  tag_OBJECT      = 'o'   # Object Tag
  tag_OBJECT_ID   = 'oid' # Object ID
  tag_OBJECT_TYPE = 'ot'  # Object Type
  tag_OBJECT_DC   = 'dc'  # Datums Count
  tag_OBJECT_DP   = 'dp'  # Datums Passed
  tag_DATUM       = 'd'   # Datum Tag
  tag_DATUM_ID    = 'did' # Datum ID
  tag_DATUM_BC    = 'bc'  # Bytes Count
  tag_DATUM_BP    = 'bp'  # Bytes Passed
  tag_DATE_TIME   = 't'   # Date and Time
  tag_SRC_ADDR    = 'src' # Source Address
  tag_DST_ADDR    = 'dst' # Destination Address
  tag_ENC_DATUM   = 'ed'  # Encrypted Datum
  tag_ENC_METHOD  = 'em'  # Encryption Method
  #
  tag_ENC_BASE64    = 'b64p'
  tag_ENC_BASE85    = 'b85p'
  tag_ENC_BASE122   = 'b122'
  #
  tag_ENC_B64_RSA   = 'b64r'
  tag_ENC_B64_2FISH = 'b64f'
  tag_ENC_B64_AES   = 'b64a'
  #
  tag_ENC_B64_ZLIB  = 'b64z'
  tag_ENC_B64_BZIP2 = 'b64b'
  #
  tag_mid_ED25519   = 'ed'
  tag_mid_RSA1024   = 'rA'
  #
  if CAN_compress_datum:
    tag_ENC_default = tag_ENC_B64_ZLIB
  else:
    tag_ENC_default = tag_ENC_BASE64
  #
  if CAN_mid_blockchain:
    tag_mid_default = tag_mid_ED25519
  else:
    tag_mid_default = ""
  #
  # IRC-IoT Base Types
  #
  type_UNDEFINED =  0
  type_NUMERIC   = 10
  type_FLOAT     = 11
  type_STRING    = 12
  type_TEXT      = 13
  type_OBJECT    = 14  # Link to other objects
  type_BINARY    = 15  # Binary data block
  type_ARRAY     = 16
  #
  b_LITTLE_ENDIAN = 0
  b_BIG_ENDIAN    = 1
  b_MIDDLE_ENDIAN = 2
  #
  # IRC-IoT Errors
  #
  err_DEFRAG_INVALID_DID  = 103
  err_CONTENT_MISSMATCH   = 104
  err_DEFRAG_OP_MISSING   = 111
  err_DEFRAG_DP_MISSING   = 112
  err_DEFRAG_BP_MISSING   = 113
  err_DEFRAG_OC_EXCEEDED  = 121
  err_DEFRAG_DC_EXCEEDED  = 122
  err_DEFRAG_BC_EXCEEDED  = 123
  err_OVERLAP_MISSMATCH   = 131
  err_COMP_ZLIB_HEADER    = 301
  err_COMP_ZLIB_INCOMP    = 303
  #
  pattern = "@"
  #
  default_mtu = 450
  #
  # Fragmented Message Delete Timeout (in seconds)
  #
  FMDT = 3600
  #
  # Message Fragment auto re-Request Time (in seconds)
  #
  MFRT = 60
  #
  def __setattr__(self, *_):
      pass

 def __init__(self):
  #
  self.CONST = self.CONST()
  #
  self.current_mid = 0 # Message ID
  self.current_oid = 0 # Object ID
  self.current_did = 0 # Datum ID
  self.mid_lock = 0
  self.oid_lock = 0
  self.did_lock = 0
  #
  self.defrag_pool = []
  self.defrag_lock = False
  #
  self.output_pool = []
  self.output_pool = False
  #
  self.ldict       = []
  self.ldict_lock  = False
  #
  self.ldict_types = []
  self.ldict_types_lock = False
  #
  self.mid_method  = self.CONST.tag_mid_default
  self.oid_method  = 0
  self.did_method  = 0
  #
  if CAN_encrypt_datum:
    self.crypt_method = self.CONST.tag_ENC_default
  else:
    self.crypt_method = self.CONST.tag_ENC_BASE64
  #
  # 0 is autoincrement
  #
  random.seed()
  #
  self.blockchain_private_key = None
  self.blockchain_public_key = None
  #
  if self.mid_method == "":
     self.current_mid = random.randint( 10000, 99999)
  elif self.mid_method == self.CONST.tag_mid_ED25519 \
    or self.mid_method == self.CONST.tag_mid_RSA1024:
     (self.blockchain_private_key, \
      self.blockchain_public_key) \
       = self.irciot_blockchain_generate_keys_()
     self.current_mid \
       = self.irciot_blockchain_sign_string_( \
         str(self.current_mid), self.blockchain_private_key)
  if self.oid_method == 0:
     self.current_oid = random.randint(  1000,  9999)
  if self.did_method == 0:
     self.current_did = random.randint(   100,   999)
  #
  if (self.crypt_method == self.CONST.tag_ENC_B64_AES):
     self.crypto_AES_BLOCK_SIZE = AES.block_size
     self.crypto_AES_iv = self.irciot_crypto_hasher_(None, \
     self.crypto_AES_BLOCK_SIZE )
  if (self.crypt_method == self.CONST.tag_ENC_B64_2FISH):
     pass
  if (self.crypt_method == self.CONST.tag_ENC_B64_RSA):
     self.crypto_RSA_KEY_SIZE = 2048
  #
  self.message_mtu = self.CONST.default_mtu
  #
  # Default Maximum IRC message size:
  #
  # 450 for Undernet IRCd at 2018
  # ... for RusNet IRCd at ...
  # ... for IRCNet IRCd at ...
  #
  self.integrity_check = 0
  #
  # 0 is No Integrity Check
  # 1 is CRC16 Check "c16"
  # 2 is CRC32 Check "c32"
  #
  # End of PyIRCIoT.__init__()

 def irciot_version_(self):
  return self.CONST.irciot_protocol_version

 def irciot_crypto_hasher_(self, in_password, hash_size):
  if in_password == None or in_password == "":
    return random.new().read( hash_size )
  if not isinstance(in_password, str):
    return None
  crypto_hash = None
  my_password = in_password.encode('utf-8')
  if hash_size == 20:
    crypto_hash = hashlib.sha1(my_password).digest()
  if hash_size == 28:
    crypto_hash = hashlib.sha224(my_password).digest()
  if hash_size == 32:
    crypto_hash = hashlib.sha256(my_password).digest()
  if hash_size == 48:
    crypto_hash = hashlib.sha384(my_password).digest()
  if hash_size == 64:
    crypto_hash = hashlib.sha512(my_password).digest()
  return crypto_hash
  #
  # End of irciot_crypto_hasher_()

 def irciot_crypto_hash_to_str_(self, in_hash):
  if in_hash == None:
    return ""
  try:
    my_string = str(base64.b64encode(in_hash))[2:-1]
    while (my_string[-1] == "="):
      my_string = my_string[:-1]
    return my_string
  except:
    return ""
  #
  # Endof irciot_crypto_hash_to_str_()

 def irciot_blockchain_generate_keys_(self):
  my_private_key = None
  my_public_key = None
  try:
    if self.mid_method == self.CONST.tag_mid_ED25519:
      my_private_key = nacl.signing.SigningKey.generate()
      my_public_key = my_private_key.verify_key
    if self.mid_method == self.CONST.tag_mid_RSA1024:
      my_private_key = RSA.generate(1024)
      my_public_key = my_private_key.publickey()
  except:
    pass
  return (my_private_key, my_public_key)
  #
  # End of irciot_blockchain_generate_keys_()

 def irciot_blockchain_place_key_to_repo_(self):
  pass
  #
  # End of irciot_blockchain_place_key_to_repo_()

 def irciot_blockchain_request_foreign_key_(self):
  pass
  #
  # End of irciot_blockchain_request_foreign_key_()

 def irciot_blockchain_update_foreign_key_(self):
  pass
  #
  # End of irciot_blockchain_update_foreign_key_()
  
 def irciot_blockchain_sign_string_(self, in_string, private_key):
  try:
    my_string = in_string.encode('utf-8')
    if self.mid_method == self.CONST.tag_mid_ED25519:
      my_signed = private_key.sign(my_string)
      my_sign = my_signed[:-len(my_string)]
    if self.mid_method == self.CONST.tag_mid_RSA1024:
      my_pkcs = PKCS1_v1_5.new(private_key)
      my_hash = SHA1.new(my_string)
      my_sign = my_pkcs.sign(my_hash)
    my_string = str(self.mid_method)
    my_string += self.irciot_crypto_hash_to_str_(my_sign)
  except:
    my_siring = None
  return my_string
  #
  # End of irciot_blockchain_sign_string_()
  
 def irciot_blockchain_verify_message_(self):
  pass
  #
  # End of irciot_blockchain_verify_message_()

 def irciot_crypto_AES_encrypt_(self, in_raw_data, in_encrypion_key):
  my_AES = AES.new(in_encryption_key, AES.MODE_CBC, self.crypto_AES_iv)
  return my_AES.encrypt(in_raw_data)
  
 def irciot_crypto_AES_decrypt_(self, in_encrypted_data, in_encryption_key):
  my_AES = AES.new(in_encryption_key, AES.MODE_CBC, self.crypto_AES_iv)
  return my_AES.decrypt(in_encrypted_data)

 def irciot_crypto_generate_keys_(self):
  #
  crypto_public_key = None
  crypto_private_key = None
  if (self.crypt_method == self.CONST.tag_ENC_B64_RSA):
    crypto_private_key = RSA.generate(self.CONST.crypto_RSA_KEY_SIZE)
    crypto_public_key = crypto_private_key.publickey()
  if (self.crypt_method == self.CONST.tag_ENC_B64_AES):
    pass
  if (self.crypt_method == self.CONST.tag_ENC_B64_2FISH):
    pass
  #
  return (crypto_public_key, crypto_private_key)
  #
  # End of irciot_crypto_generate_keys_()

 def irciot_crypto_place_key_to_repo_(self):
  pass
  #
  # End of irciot_crypto_place_key_to_repo_()

 def irciot_crypto_request_foreign_key_(self):
  pass
  #
  # End of irciot_crypto_request_foreign_key_()

 def irciot_crypto_update_foreign_key_(self):
  pass
  #
  # End of irciot_crypto_update_foreign_key_()
  
 def irciot_crypto_encrypt_datum_(self):
  pass
  #
  # End of irciot_crypto_encrypt_datum_()

 def irciot_crypto_decrypt_datum_(self):
  pass
  #
  # End of irciot_crypto_decrypt_datum_()

 def irciot_get_object_by_id_(self, in_object_id):
  if not isinstance(in_object_id, int):
    return None
  #
  return None

 def irciot_delete_object_by_id_(self, in_object_id):
  if not isinstance(in_object_id, int):
    return
  #
  pass
  
 def irciot_get_objects_count_(self):
  return 0
  
 def irciot_ldict_create_item_(self, in_ldict_item):
  try:
    (my_id, my_ot) = in_ldict_item
  except:
    return
  #
  pass

 def irciot_ldict_delete_items_by_ot_(self, in_object_type):
  if not isinstance(in_object_type, str):
    return
  #  
  pass

 def irciot_ldict_delete_item_by_id_(self, in_item_id):
  if not isinstance(in_item_id, int):
    return
  #
  pass

 def irciot_ldict_create_type_(self, in_ldict_type):
  try:
    (my_type_id, my_type_name) = in_ldict_type
  except:
    return
  if self.irciot_ldict_get_type_by_name(my_type_name):
    return
  #
  pass

 def irciot_ldict_delete_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return
  #
  pass

 def irciot_ldict_delete_type_by_id_(self, in_type_id):
  if not isinstance(in_type_id, int):
    return
  #
  pass
  
 def irciot_ldict_get_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return
  for ldict_type in self.ldict_types:
    (my_type_id, my_type_name) = ldict_type
    if my_type_name == in_type_name:
      return ldict_type
  return None

 def irciot_ldict_get_type_by_id_(self, in_type_id):
  if not isinstance(in_type_id, int):
    return
  for ldict_type in self.ldict_types:
    (my_type_id, my_type_name) = ldict_type
    if my_type_id == in_type_id:
      return ldict_type 
  return None

 def irciot_set_mtu_(self, in_mtu):
  if not isinstance(in_mtu, int):
    return
  if (in_mtu < 128):
    return
  self.message_mtu = in_mtu
  
 def is_irciot_datum_(self, in_datum, in_ot, in_src, in_dst):
  if self.CONST.tag_ENC_DATUM in in_datum:
     if isinstance(in_datum[self.CONST.tag_ENC_DATUM], str):
        return True # Stub
  # Object Type filed must exists or inherits
  if not self.CONST.tag_OBJECT_TYPE in in_datum:
     if (in_ot == None):
        return False
  else:
     if not isinstance(in_datum[self.CONST.tag_OBJECT_TYPE], str):
        return False
  # Fragmented message header:
  if self.CONST.tag_DATUM_BC in in_datum:
     if not isinstance(in_datum[self.CONST.tag_DATUM_BC], int):
        return False # Bytes Count must be int
     if self.CONST.tag_DATUM_BP in in_datum:
        if not isinstance(in_datum[self.CONST.tag_DATUM_BP], int):
           return False # Bytes Passed must be int
        if (in_datum[self.CONST.tag_DATUM_BP] \
          > in_datum[self.CONST.tag_DATUM_BC]):
           return False
  # Source address field must exists or inherits
  if not self.CONST.tag_SRC_ADDR in in_datum:
     if (in_src == None):
        return False
  else:
     if not isinstance(in_datum[self.CONST.tag_SRC_ADDR], str):
        return False
  # Destination address field must exits or ihnerits
  if not self.CONST.tag_DST_ADDR in in_datum:
     if (in_dst == None):
        return False
  else:
     if not isinstance(in_datum[self.CONST.tag_DST_ADDR], str):
        return False
  return True
  #
  # End of is_irciot_datum_()

 def is_irciot_(self, my_json):
  ''' Сhecks whether the text string is a IRC-IoT message or not '''
  
  def is_irciot_object_(self, in_object):
    if not self.CONST.tag_OBJECT_ID in in_object: # IRC-IoT Object ID
       return False
    if (in_object[self.CONST.tag_OBJECT_ID] == ""):
       return False
    if not self.CONST.tag_OBJECT_TYPE in in_object:
       in_object[self.CONST.tag_OBJECT_TYPE] = None
       # it will test all datums for "object type"
    if (in_object[self.CONST.tag_OBJECT_TYPE] == ""):
       return False
    if not self.CONST.tag_DATUM in in_object:
       return False
    my_datums = in_object[self.CONST.tag_DATUM] 
    my_src = None
    if self.CONST.tag_SRC_ADDR in in_object:
       my_src = in_object[self.CONST.tag_SRC_ADDR]
    my_dst = None
    if self.CONST.tag_DST_ADDR in in_object:
       my_dst = in_object[self.CONST.tag_DST_ADDR]
    # Fragmented message header:
    if self.CONST.tag_OBJECT_DC in in_object:
       if not isinstance(in_object[self.CONST.tag_OBJECT_DC], int):
          return False # Datums Count must be int
       if self.CONST.tag_DATUM_BP in in_object:
          if not isinstance(in_datum[self.CONST.tag_OBJECT_DP], int):
             return False # Datums Passed must be int
          if (in_object[self.CONST.tag_DATUM_BP] \
            > in_object[self.CONST.tag_DATUM_BC]):
             return False
    # Go deeper
    if isinstance(my_datums, list):
       for my_datum in my_datums:
          if (not self.is_irciot_datum_(my_datum, \
           in_object[self.CONST.tag_OBJECT_TYPE], my_src, my_dst)):
             return False
       return True
    if isinstance(my_datums, dict):
       if not self.is_irciot_datum_(my_datums, \
        in_object[self.CONST.tag_OBJECT_TYPE], my_src, my_dst):
          return False
    return True
    #
    # End of is_irciot_() :: is_irciot_object_()

  def is_irciot_container_(self, in_container):
    if not self.CONST.tag_MESSAGE_ID in in_container:
       return False
    if (in_container[self.CONST.tag_MESSAGE_ID] == ""):
       return False
    if self.CONST.tag_MESSAGE_OC in in_container:
       if not isinstance(in_container[self.CONST.tag_MESSAGE_OC], int):
          return False # Objects Count must be int
    else:
       in_container[self.CONST.tag_MESSAGE_OC] = 1
    if self.CONST.tag_MESSAGE_OP in in_container:
       if not isinstance(in_container[self.CONST.tag_MESSAGE_OP], int):
          return False # Objects Passed must be int
       if (in_container[self.CONST.tag_MESSAGE_OP] \
         > in_container[self.CONST.tag_MESSAGE_OC]):
          return False
    else:
       in_container[self.CONST.tag_MESSAGE_OP] = 1
    if not self.CONST.tag_OBJECT in in_container:
       return False # IRC-IoT Object must exists
    my_objects = in_container[self.CONST.tag_OBJECT]
    if isinstance(my_objects, list):
      for my_object in my_objects:
         if (not is_irciot_object_(self, my_object)):
           return False
      return True
    if isinstance(my_objects, dict):
      if not is_irciot_object_(self, my_objects):
         return False
      return True
    return False
    #
    # End of is_irciot_() :: is_irciot_container_()

  # Begin of is_irciot_()
  #
  try:
     irciot_message = json.loads(my_json)
  except ValueError:
     return False
  # This is Top-level JSON with ONE or more IRC-IoT message "containers"
  if isinstance(irciot_message, list):
     for my_container in irciot_message:
        if (not is_irciot_container_(self, my_container)):
           return False
     return True
  if isinstance(irciot_message, dict):
     if not is_irciot_container_(self, irciot_message):
        return False
  return True
  #
  # End of is_irciot_()
  
 def irciot_clear_defrag_chain_(self, in_did):
  try:
    if self.defrag_lock:
       return
    self.defrag_lock = True
    for my_item in self.defrag_pool:
       (test_enc, test_header, test_json) = my_item
       (test_dt, test_ot, test_src, test_dst, \
        test_dc, test_dp, test_bc, test_bp, test_did) = test_header
       if (in_did == test_did):
          self.defrag_pool.remove(my_item)
          break
    self.defrag_lock = False
  except:
    self.defrag_lock = False
  #
  # End of irciot_clear_defrag_chain_()

 def irciot_defragmentation_(self, in_enc, in_header, orig_json):
  (my_dt, my_ot, my_src, my_dst, \
   my_dc, my_dp, my_bc, my_bp, my_did) = in_header
  if ((my_dc == None) and (my_dp != None)) or \
     ((my_dc != None) and (my_dp == None)) or \
     ((my_bc == None) and (my_bp != None)) or \
     ((my_bc != None) and (my_bp == None)):
    return ""
  if not isinstance(self.defrag_pool, list):
    self.defrag_pool = [] # Drop broken defrag_pool
  my_dup = False
  my_new = False
  my_err = 0
  my_ok  = 0
  defrag_array = []
  defrag_buffer = ""
  for my_item in self.defrag_pool: # IRC-IoT defragmentation loop
    (test_enc, test_header, test_json) = my_item
    (test_dt, test_ot, test_src, test_dst, \
     test_dc, test_dp, test_bc, test_bp, test_did) = test_header
    if (test_json == orig_json):
      my_dup = True
      break
    else:
      if (test_did == my_did):
         if ((test_ot  == my_ot)  and \
             (test_src == my_src) and \
             (test_dst == my_dst)):
            if ((test_dc == my_dc) and (test_dp == my_dp) and \
                (test_bp == my_bp) and (test_bc == my_bc)):
               if (test_enc == in_enc):
                  my_dup = True
               else:
                  my_err = self.CONST.err_DEFRAG_CONTENT_MISSMATCH
                  break
            else:
               if ((test_dc != None) and (test_dp != None) and \
                   (test_bc == None) and (test_bp == None)):
                  if (my_dp == None):
                     my_err = self.CONST.err_DEFRAG_DP_MISSING
                     break
                  if (defrag_array == []):
                     defrag_item = (my_dp, in_enc)
                     defrag_array.append(defrag_item)
                  defrag_item = (test_dp, test_enc)
                  defrag_array.append(defrag_item)
                  if len(defrag_array) == my_dc:
                     my_ok = 1
                     break
                  elif len(defrag_array) > my_dc:
                     my_err = self.CONST.err_DEFRAG_DC_EXCEEDED
                     break
               elif ((test_bc != None) and (test_bp != None) and \
                     (test_dc == None) and (test_dp == None)):
                  if (my_bp == None):
                     my_err = self.CONST.err_DEFRAG_BP_MISSING
                     break
                  if (defrag_buffer == ""):
                     defrag_buffer += self.CONST.pattern * my_bc
                     defrag_buffer = defrag_buffer[:my_bp] + \
                        in_enc + defrag_buffer[my_bp + len(in_enc):]
                  if (defrag_buffer != ""):
                     # here will be a comparison of overlapping buffer intervals
                     defrag_buffer = defrag_buffer[:test_bp] + \
                        str(test_enc) + defrag_buffer[test_bp + len(test_enc):]
                     if (defrag_buffer.count(self.CONST.pattern) == 0):
                        my_ok = 2
                     else:
                        my_new = True
               else: # Combo fragmentation method
                  pass                  
         else:
            my_err = self.CONST.err_DEFRAG_INVALID_DID
            break
  if (self.defrag_pool == []):
    if (len(in_enc) == my_bc):
       defrag_buffer = my_enc
       my_ok = 2
    else:
       my_new = True
  if (my_err > 0):
    self.irciot_clear_defrag_chain_(my_did)
    return ""
  if my_new:
    my_item = (in_enc, in_header, orig_json)
    self.defrag_lock = True
    self.defrag_pool.append(my_item)
    self.defrag_lock = False
  if (my_ok > 0):
    if (my_ok == 1):
       pass
    elif (my_ok == 2):
       self.irciot_clear_defrag_chain_(my_did)
       try:
          if (self.crypt_method == self.CONST.tag_ENC_BASE64):
             out_json = str(base64.b64decode(defrag_buffer))[2:-1]
          elif (self.crypt_method == self.CONST.tag_ENC_B64_AES):
             return ""
          elif (self.crypt_method == self.CONST.tag_ENC_B64_ZLIB):
             out_zlib = base64.b64decode(defrag_buffer)
             out_json = str(zlib.decompress(out_zlib))[2:-1]
             del out_zlib
          else:
             return ""
          # Adding missing fields to the "Datum" from parent object
          my_datum = json.loads(out_json)
          if ((not self.CONST.tag_OBJECT_TYPE in my_datum) \
           and (my_ot != None)):
              my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
          if ((not self.CONST.tag_DATE_TIME in my_datum) \
           and (my_dt != None)):
              my_datum[self.CONST.tag_DATE_TIME] = my_dt
          if ((not self.CONST.tag_SRC_ADDR in my_datum) \
           and (my_src != None)):
              my_datum[self.CONST.tag_SRC_ADDR] = my_src
          if ((not self.CONST.tag_DST_ADDR in my_datum) \
           and (my_dst != None)):
              my_datum[self.CONST.tag_DST_ADDR] = my_dst
          return json.dumps(my_datum, separators=(',',':'))
       except:
          return ""
    else:
       return ""
    self.irciot_clear_defrag_chain_(my_did)
    return ""
  if my_dup:
    return ""
  return ""
  #
  # End of irciot_defragmentation_()

 def irciot_decrypt_datum_(self, in_datum, in_header, orig_json):
  (my_dt, my_ot, my_src, my_dst, my_dc, my_dp) = in_header
  my_bc  = None
  my_bp  = None
  my_did = None
  if not self.CONST.tag_ENC_DATUM in in_datum.keys():
     return ""
  if self.CONST.tag_DATUM_BC in in_datum.keys():
     my_bc = in_datum[self.CONST.tag_DATUM_BC]
  if self.CONST.tag_DATUM_BP in in_datum.keys():
     my_bp = in_datum[self.CONST.tag_DATUM_BP]
  if self.CONST.tag_DATUM_ID in in_datum.keys():
     my_did = in_datum[self.CONST.tag_DATUM_ID]
  if not self.CONST.tag_ENC_METHOD in in_datum.keys():
     my_em = self.CONST.tag_ENC_BASE64
  else:
     my_em = in_datum[self.CONST.tag_ENC_METHOD]
  my_defrag_header = (my_dt, my_ot, my_src, my_dst, \
   my_dc, my_dp, my_bc, my_bp, my_did)
  my_in = in_datum[self.CONST.tag_ENC_DATUM]
  return self.irciot_defragmentation_(my_in, \
     my_defrag_header, orig_json)
  return my_dec
  #
  # End of irciot_decrypt_datum_()

 def irciot_prepare_datum_(self, in_datum, in_header, orig_json):
  if not self.CONST.tag_ENC_DATUM in in_datum.keys():
     (my_dt, my_ot, my_src, my_dst, my_dc, my_dp) = in_header
     if not self.CONST.tag_DATE_TIME in in_datum.keys():
        in_datum[self.CONST.tag_DATE_TIME] = my_dt
     if not self.CONST.tag_OBJECT_TYPE in in_datum.keys():
        in_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
     if not self.CONST.tag_SRC_ADDR in in_datum.keys():
        in_datum[self.CONST.tag_SRC_ADDR] = my_src
     if not self.CONST.tag_DST_ADDR in in_datum.keys():
        in_datum[self.CONST.tag_DST_ADDR] = my_dst
     if (in_datum[self.CONST.tag_DATE_TIME] == None):
        del in_datum[self.CONST.tag_DATE_TIME]
  else:
     return self.irciot_decrypt_datum_(in_datum, in_header, orig_json)
  return json.dumps(in_datum, separators=(',',':'))
  #
  # End of irciot_prepare_datum_()

 def irciot_deinencap_object_(self, in_object, orig_json):
  iot_dt  = None
  iot_src = None
  iot_dst = None
  iot_dc  = None
  iot_dp  = None
  try:
     iot_datums = in_object[self.CONST.tag_DATUM]
     iot_ot = in_object[self.CONST.tag_OBJECT_TYPE]
     if self.CONST.tag_DATE_TIME in in_object.keys():
        iot_dt  = in_object[self.CONST.tag_DATE_TIME]
     if self.CONST.tag_SRC_ADDR in in_object.keys():
        iot_src = in_object[self.CONST.tag_SRC_ADDR]
     if self.CONST.tag_DST_ADDR in in_object.keys():
        iot_dst = in_object[self.CONST.tag_DST_ADDR]
  except:
     return ""
  if self.CONST.tag_OBJECT_DC in in_object:
     if not isinstance(in_object[self.CONST.tag_OBJECT_DC], int):
        return ""
     iot_dc = in_object[self.CONST.tag_OBJECT_DC]
  else:
     in_object[self.CONST.tag_OBJECT_DC] = None
     iot_dc = None
  if self.CONST.tag_OBJECT_DP in in_object:
     if not isinstance(in_object[self.CONST.tag_OBJECT_DP], int):
        return ""
     iot_dp = in_object[self.CONST.tag_OBJECT_DP]
  else:
     in_object[self.CONST.tag_OBJECT_DP] = None
     iot_dp = None
  if isinstance(iot_datums, list):
     str_datums = ""
     for iot_datum in iot_datums:
        str_datum = self.irciot_prepare_datum_(iot_datum, \
         (iot_dt, iot_ot, iot_src, iot_dst, iot_dc, iot_dp), orig_json)
        if (str_datum != ""):
           if (str_datums != ""):
              str_datums += ","
           str_datums += str_datum
     return str_datums
  if isinstance(iot_datums, dict):
     return self.irciot_prepare_datum_(iot_datums, \
      (iot_dt, iot_ot, iot_src, iot_dst, iot_dc, iot_dp), orig_json)
  return ""
  #
  # End of irciot_deinencap_object_()

 def irciot_deinencap_container_(self, in_container, orig_json):
  try:
     iot_objects = in_container[self.CONST.tag_OBJECT]
  except:
     return ""
  if isinstance(iot_objects, list):
    str_datums = ""
    for iot_object in iot_objects:
       str_datum = self.irciot_deinencap_object_(iot_object, orig_json)
       if (str_datum != ""):
          if (str_datums != ""):
             str_datums += ","
          str_datums += str_datum
    #if (str_datums != ""):
    #   str_datums = "[" + str_datums + "]"
    return str_datums
  if isinstance(iot_objects, dict):
    return self.irciot_deinencap_object_(iot_objects, orig_json)
    if (str_datums != ""):
       str_datums = "[" + str_datums + "]"
    return str_datums
  return ""
  #
  # End of irciot_deinencap_container_()
 
 def irciot_deinencap_(self, in_json):
  ''' First/simple implementation of IRC-IoT "Datum" deinencapsulator '''
  try:
     iot_containers = json.loads(in_json)
  except ValueError:
     return ""
  if isinstance(iot_containers, list):
    str_datums = "["
    for iot_container in iot_containers:
       str_datum = self.irciot_deinencap_container_(iot_container, in_json)
       if (str_datum != ""):
          if (str_datums != "["):
             str_datums += ","
          str_datums += str_datum
    return str_datums + "]"
  if isinstance(iot_containers, dict):
    return self.irciot_deinencap_container_(iot_containers, in_json)
  return ""
  #
  # End of irciot_deinencap_container_()

 def is_irciot_datumset_(self, in_json):
  try:
     my_datums = json.loads(in_json)
  except ValueError:
     return ""
  if isinstance(my_datums, list):
     for my_datum in my_datums:
        if (not self.is_irciot_datum_(my_datum, None, None, None)):
           return False
     return True
  if isinstance(my_datums, dict):
     if (not self.is_irciot_datum_(my_datums, None, None, None)):
        return False
     return True
  return False
  #
  # End of is_irciot_datumset_()
  
 def irciot_encap_datum_(self, in_datum, in_ot, in_src, in_dst):
  if not self.CONST.tag_ENC_DATUM in in_datum.keys():
   if (in_ot == in_datum[self.CONST.tag_OBJECT_TYPE]):
      del in_datum[self.CONST.tag_OBJECT_TYPE]
   if (in_src == in_datum[self.CONST.tag_SRC_ADDR]):
      del in_datum[self.CONST.tag_SRC_ADDR]
   if (in_dst == in_datum[self.CONST.tag_DST_ADDR]):
      del in_datum[self.CONST.tag_DST_ADDR]
  return json.dumps(in_datum, separators=(',',':'))
  #
  # End of irciot_encap_datum_()

 def irciot_encap_internal_(self, in_datumset):
  ''' First/simple implementation of IRC-IoT "Datum" set encapsulator '''
  try:
     my_datums = json.loads(in_datumset)
  except ValueError:
     return ""
  my_irciot = ""
  my_ot  = None
  my_src = None
  my_dst = None
  if isinstance(my_datums, list):
     my_datums_cnt = 0
     my_ot_cnt  = 0
     my_src_cnt = 0
     my_dst_cnt = 0
     for my_datum in my_datums:
        if (my_datums_cnt == 0):
           my_ot  = my_datum[self.CONST.tag_OBJECT_TYPE]
           my_ot_cnt  = 1
           my_src = my_datum[self.CONST.tag_SRC_ADDR]
           my_src_cnt = 1
           my_dst = my_datum[self.CONST.tag_DST_ADDR]
           my_dst_cnt = 1
        else:
           if (my_ot  == my_datum[self.CONST.tag_OBJECT_TYPE]):
              my_ot_cnt += 1
           if (my_src == my_datum[self.CONST.tag_SRC_ADDR]):
              my_src_cnt += 1
           if (my_dst == my_datum[self.CONST.tag_DST_ADDR]):
              my_dst_cnt += 1
        my_datums_cnt += 1
     my_datums_cnt = len(my_datums)
     if (my_ot_cnt  < my_datums_cnt):
        my_ot  = None
     if (my_src_cnt < my_datums_cnt):
        my_src = None
     if (my_dst_cnt < my_datums_cnt):
        my_dst = None
     for my_datum in my_datums:
        if (my_irciot != ""):
           my_irciot += ","
        my_irciot += self.irciot_encap_datum_( \
          my_datum, my_ot, my_src, my_dst)
     if (my_datums_cnt > 1):
        my_irciot = "[" + my_irciot + "]"
     my_irciot = '"' + self.CONST.tag_DATUM + '":' + my_irciot
  if isinstance(my_datums, dict):
     if self.CONST.tag_OBJECT_TYPE in my_datums:
        my_ot  = my_datums[self.CONST.tag_OBJECT_TYPE]
        if self.CONST.tag_ENC_DATUM in my_datums.keys():
           del my_datums[self.CONST.tag_OBJECT_TYPE]
     if self.CONST.tag_SRC_ADDR in my_datums:
         my_src = my_datums[self.CONST.tag_SRC_ADDR]
     if self.CONST.tag_DST_ADDR in my_datums:
         my_dst = my_datums[self.CONST.tag_DST_ADDR]
     if (self.is_irciot_datum_(my_datums, my_ot, my_src, my_dst)):
        my_irciot = '"' + self.CONST.tag_DATUM + '":' \
         + self.irciot_encap_datum_(my_datums, my_ot, my_src, my_dst)
  str_object  = '"' + self.CONST.tag_OBJECT
  str_object += '":{"' + self.CONST.tag_OBJECT_ID
  str_object += '":"' + str(self.current_oid) + '",'
  if (my_ot  != None):
     str_object += '"' + self.CONST.tag_OBJECT_TYPE
     str_object += '":"'  + my_ot  + '",'
  if (my_src != None):
     str_object += '"' + self.CONST.tag_SRC_ADDR
     str_object += '":"' + my_src + '",'
  if (my_dst != None):
     str_object += '"' + self.CONST.tag_DST_ADDR
     str_object += '":"' + my_dst + '",'
  save_mid = self.current_mid
  str_container = '{"' + self.CONST.tag_MESSAGE_ID + '":"'
  str_for_sign  = str_container + str(save_mid)
  str_for_sign += '",' + str_object + my_irciot + "}}"
  if self.mid_method == "": # Default mid method
    if not isinstance(self.current_mid, int):
      self.current_mid = random.randint( 10000, 99999)
    self.current_mid += 1
  elif self.mid_method == self.CONST.tag_mid_ED25519 \
    or self.mid_method == self.CONST.tag_mid_RSA1024:
    sign_hash = self.irciot_blockchain_sign_string_( \
      str_for_sign, self.blockchain_private_key)
    if sign_hash == None:
      return ""
    self.current_mid = sign_hash
  str_container += str(self.current_mid) + '",'
  my_irciot = str_container + str_object + my_irciot + "}}"
  # + '"oc":1,"op":1,'  # Must be implemented later
  return my_irciot
  #
  # End of irciot_encap_internal_()

 def irciot_encap_bigdatum_(self, my_bigdatum, my_part):
  ''' Hidden part of encapsulator creates mutlipart "Datum" '''
  save_mid  = self.current_mid
  big_datum = {}
  big_ot = None
  if isinstance(my_bigdatum, dict):
     big_datum = my_bigdatum
     big_ot = my_bigdatum[self.CONST.tag_OBJECT_TYPE]
     del my_datum[self.CONST.tag_OBJECT_TYPE]
  if isinstance(my_bigdatum, list):
     my_current = 0
     for my_datum in my_bigdatum:
        if (my_current == 0):
           big_datum = my_datum
           big_ot = my_datum[self.CONST.tag_OBJECT_TYPE]
           del my_datum[self.CONST.tag_OBJECT_TYPE]
        my_current += 1
  if (big_ot == None):
     return ("", 0)
  str_big_datum  = json.dumps(big_datum, separators=(',',':'))
  if (self.crypt_method == self.CONST.tag_ENC_B64_ZLIB):
     bin_big_datum  = zlib.compress(bytes(str_big_datum, "utf-8"))
     b64_big_datum  = base64.b64encode(bin_big_datum)
     del bin_big_datum
  else:
     b64_big_datum  = base64.b64encode(bytes(str_big_datum, "utf-8"))
  raw_big_datum  = str(b64_big_datum)[2:-1]
  del b64_big_datum
  my_bc = len(raw_big_datum)
  out_big_datum  = '{"' + self.CONST.tag_ENC_DATUM
  out_big_datum += '":"' + raw_big_datum + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum)
  self.current_mid = save_mid # mid rollback
  out_skip  = len(my_irciot)
  out_head  = len(big_ot)
  out_head += len(str(self.current_mid))
  out_head += len(self.CONST.tag_OBJECT_TYPE) + 6 #"":"",#
  out_head += len(str(self.current_did))
  out_head += len(self.CONST.tag_DATUM_ID) + 6 #"":"",#
  out_head += len(str(my_bc)) + 4 #"":,#
  out_head += len(self.CONST.tag_DATUM_BC)
  out_head += len(str(my_part)) + 4 #"":,#
  out_head += len(self.CONST.tag_DATUM_BP)
  out_skip += out_head - self.message_mtu
  out_big_datum = '{'
  out_big_datum += '"' + self.CONST.tag_OBJECT_TYPE + '":"' + big_ot
  out_big_datum += '","' + self.CONST.tag_DATUM_ID
  out_big_datum += '":"' + str(self.current_did)
  out_big_datum += '","' + self.CONST.tag_DATUM_BC + '":' + str(my_bc)
  out_big_datum += ',"' + self.CONST.tag_DATUM_BP + '":' + str(my_part)
  out_big_datum += ',"' + self.CONST.tag_ENC_DATUM + '":"'
  my_okay = self.message_mtu - out_head - 43 # Must be calculated
  my_size = my_bc - my_part
  if (my_size > my_okay):
     my_size = my_okay
  out_big_datum += raw_big_datum[my_part:my_part + my_size] + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum)
  if (my_size < my_okay):
    return (my_irciot, 0)
  return (my_irciot, len(raw_big_datum) + my_part - out_skip)
  #
  # End of irciot_encap_bigdatum_()

 def irciot_encap_all_(self, in_datumset):
  result = []
  if (isinstance(in_datumset, dict)):
    in_datumset = [in_datumset]
  in_datumset = json.dumps(in_datumset, separators=(',',':'))
  json_text, my_skip, my_part \
    = self.irciot_encap_(in_datumset, 0, 0)
  if (json_text != ""):
    result.append(json_text)
  while ((my_skip > 0) or (my_part > 0)):
    json_text, my_skip, my_part \
      = self.irciot_encap_(in_datumset, my_skip, my_part)
    if (json_text != ""):
      result.append(json_text)
  return result
  #
  # End of irciot_encap_all_()

 def irciot_encap_(self, in_datumset, my_skip, my_part):
  ''' Public part of encapsulator with per-"Datum" fragmentation '''
  my_datums_set  = in_datumset
  my_datums_skip = 0
  my_datums_part = 0
  save_mid  = self.current_mid
  my_irciot = ""
  my_datums = json.loads(in_datumset)
  my_total  = len(my_datums)
  if (my_skip > 0):
     my_datums_obj = []
     my_datums_cnt = 0
     for my_datum in my_datums:
        my_datums_cnt += 1
        if (my_datums_cnt > my_skip):
           my_datums_obj.append(my_datum)
     my_datums_set = json.dumps(my_datums_obj, separators=(',',':'))
     my_datums = json.loads(my_datums_set)
     del my_datums_obj
     del my_datums_cnt
  my_irciot = self.irciot_encap_internal_(my_datums_set)
  if (len(my_irciot) > self.message_mtu):
     if (my_skip == 0):
        self.current_mid = save_mid # mid rollback
     my_datums = json.loads(my_datums_set)
     one_datum = 0
     if isinstance(my_datums, list):
        my_datums_total = len(my_datums)
        if (my_datums_total > 1):
           my_datums_skip = my_datums_total
           while (len(my_irciot) > self.message_mtu) \
             and (my_datums_skip <= my_datums_total):
              part_datums = []
              my_datums_cnt = 0
              for my_datum in my_datums:
                 if (my_datums_cnt < my_datums_skip):
                    part_datums.append(my_datum)
                 my_datums_cnt += 1
              if (part_datums == []):
                 break
              str_part_datums = json.dumps(part_datums, separators=(',',':'))
              self.current_mid = save_mid # mid rollback
              my_irciot = self.irciot_encap_internal_(str_part_datums)
              if (len(my_irciot) <= self.message_mtu):
                test_len = len(my_datums)
                my_skip_out = my_skip + my_datums_skip
                if (my_skip_out >= my_total):
                   my_skip_out = 0
                return my_irciot, my_skip_out, 0
              my_datums_skip -= 1
           one_datum = 1 # Multidatum, but current "Datum" is too large
        else:
           one_datum = 1 # One "Datum" in list, and it is too large
     if isinstance(my_datums, dict):
        one_datum = 1    # One large "Datum" without list
     if (one_datum == 1):
        self.current_mid = save_mid # Message ID rollback
        (my_irciot, my_datums_part) \
         = self.irciot_encap_bigdatum_(my_datums, my_part)
        if (my_datums_part == 0):
          my_datums_skip += 1
  else:
     my_datums_skip = my_total - my_skip
     self.current_did += 1 # Default Datum ID changing method
  if (my_skip + my_datums_skip >= my_total):
    my_skip = 0
    my_datums_skip = 0
  return my_irciot, my_skip + my_datums_skip, my_datums_part
  #
  # End of irciot_encap_()

