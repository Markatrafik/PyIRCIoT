'''
'' PyIRCIoT (PyLayerIRCIoT class)
''
'' Copyright (c) 2018, 2019 Alexey Y. Woronov
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
DO_auto_encryption = False # Automatic loading of necessary modules
DO_auto_blockchain = False # Automatic loading of necessary modules

import json
import random
import base64
import datetime

if CAN_debug_library:
  from pprint import pprint
if CAN_compress_datum:
  import zlib
if CAN_mid_blockchain:
  import nacl.signing # Simple IRC-IoT blockchain signing by ED25519
  import nacl.encoding
if CAN_encrypt_datum or CAN_mid_blockchain:
  import hashlib
  from Crypto.PublicKey import RSA
  from Crypto.Hash import SHA as SHA1
  from Crypto.Signature import PKCS1_v1_5

class PyLayerIRCIoT(object):

 class CONST(object):
  #
  irciot_protocol_version = '0.3.23'
  #
  irciot_library_version  = '0.0.93'
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
  tag_ENC_PUBKEY  = 'ek'  # Encryption Public Key
  tag_BCH_METHOD  = 'bm'  # Blockchain Method
  tag_BCH_PUBKEY  = 'bk'  # Blockchain Public Key
  #
  tag_ENC_BASE32    = 'b32p'
  tag_ENC_BASE64    = 'b64p'
  tag_ENC_BASE85    = 'b85p'
  tag_ENC_BASE122   = 'b122'
  #
  tag_ENC_B64_RSA   = 'b64r'
  tag_ENC_B85_RSA   = 'b85r'
  tag_ENC_B64Z_RSA  = 'b64Z'
  tag_ENC_B85Z_RSA  = 'b85Z'
  tag_ENC_B64_2FISH = 'b64f'
  tag_ENC_B85_2FISH = 'b85f'
  tag_ENC_B64_AES   = 'b64a'
  tag_ENC_B85_AES   = 'b85a'
  tag_ENC_B64Z_AES  = 'b64A'
  tag_ENC_B85Z_AES  = 'b85A'
  #
  tag_ENC_B64_ZLIB  = 'b64z'
  tag_ENC_B85_ZLIB  = 'b85z'
  tag_ENC_B64_BZIP2 = 'b64b'
  tag_ENC_B85_BZIP2 = 'b85b'
  #
  tag_mid_ED25519   = 'ed'
  tag_mid_RSA1024   = 'rA'
  #
  mid_ED25519_hash_length = 88
  mid_RSA1024_hash_length = 173
  #
  if CAN_compress_datum:
    if CAN_encrypt_datum:
      tag_ENC_default = tag_ENC_B64Z_RSA
    else:
      tag_ENC_default = tag_ENC_B64_ZLIB
  else:
    if CAN_encrypt_datum:
      tag_ENC_default = tag_ENC_B64_RSA
    else:
      tag_ENC_default = tag_ENC_BASE64
  #
  if CAN_mid_blockchain:
    tag_mid_default = tag_mid_ED25519
  else:
    tag_mid_default = ""
  #
  # Encryption models:
  #
  crypt_NO_ENCRYPTION = 0
  crypt_PRIVATE_KEY   = 1
  crypt_SYMMETRIC     = 3
  crypt_ASYMMETRIC    = 5
  #
  crypto_RSA_KEY_SIZE = 2048 # RSA2048
  crypto_RSA_SHA_SIZE = 160  # SHA-1
  crypto_RSA_CHUNK \
   = crypto_RSA_KEY_SIZE // 8
  crypto_RSA_OVERHEAD \
   = (crypto_RSA_SHA_SIZE // 4) + 2
  crypto_RSA_CHUNK_IN \
   = crypto_RSA_CHUNK \
   - crypto_RSA_OVERHEAD
  #
  # The correlation table between
  # SHA Cipher and RSA algorithm key size
  #
  # Cipher |SIZE|OVER|1024|2048|3072|4096
  # SHA-1  | 160|  42|  86| 214| 342| 470
  # SHA-224| 224|  58|  70| 198| 326| 454
  # SHA-256| 256|  66|  62| 190| 318| 446
  # SHA-384| 384|  98|  30| 158| 286| 414
  # SHA-512| 512| 130| N/A| 126| 254| 382
  #
  crypto_RSA   = 1
  crypto_AES   = 5
  crypto_2FISH = 7
  #
  base_BASE32  = 32
  base_BASE64  = 64
  base_BASE85  = 85
  base_BASE122 = 122
  #
  compress_NONE  = 0
  compress_ZLIB  = 3
  compress_BZIP2 = 102
  #
  # The Object Types, will be replaced
  # by IRC-IoT "Dictionaries" mechanism
  #
  ot_BCH_INFO    = "bchnfo" # Blockchain Information
  ot_BCH_REQUEST = "bchreq" # Blockchain Request
  ot_BCH_ACK     = "bchack" # Blockchain Acknowledgment
  #
  ot_ENC_INFO    = "encnfo" # Encryption Information
  ot_ENC_REQUEST = "encreq" # Encryption Request
  ot_ENC_ACK     = "encack" # Encryption Acknowledgment
  #
  api_GET_LMID = 101 # Get last Message ID
  api_SET_LMID = 102 # Set last Message ID
  api_GET_EKEY = 301 # Get Encryption Key
  api_SET_EKEY = 302 # Set Encryption Key
  api_GET_BKEY = 501 # Get Blockchain Key
  api_SET_BKEY = 502 # Set Blockchain Key
  #
  api_vuid_cfg = "c" # VUID prefix for users from config
  api_vuid_tmp = "t" # VUID prefix for temporal users
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
  ldict_VERSION     = "irciot_protocol"
  #
  ldict_ITEMS_TABLE = "items"
  ldict_TYPES_TABLE = "types"
  ldict_SECTS_TABLE = "sections"
  #
  ldict_ITEMS_ID      = "item_id"
  ldict_ITEMS_OT      = "item_ot"
  ldict_ITEMS_PARENT  = "parent_item_id"
  ldict_ITEMS_TYPEID  = "type_id"
  ldict_ITEMS_TYPEPR  = "type_parameters"
  ldict_ITEMS_DEFVAL  = "default_value"
  ldict_ITEMS_CHILD   = "child_object_id"
  ldict_ITEMS_METHOD  = "method"
  ldict_ITEMS_LANG    = "method_language"
  ldict_ITEMS_SECTS   = "sections"
  #
  ldict_TYPES_ID      = "type_id"
  ldict_TYPES_NAME    = "type_name"
  ldict_TYPES_TYPE    = "type_of_type"
  ldict_TYPES_ARR     = "is_it_array"
  ldict_TYPES_DYNSIZE = "is_variable_dynamically_sized"
  ldict_TYPES_DYNARR  = "is_array_dynamically_sized"
  ldict_TYPES_ARRSIZE = "size_of_array"
  ldict_TYPES_SIZE    = "size"
  ldict_TYPES_MIN     = "interval_minimum"
  ldict_TYPES_MAX     = "interval_maximum"
  ldict_TYPES_PRECESS = "precession"
  ldict_TYPES_ENDIAN  = "endianness"
  ldict_TYPES_ENCODE  = "encoding"
  #
  ldict_SECTS_ID      = "section_id"
  ldict_SECTS_ITEMS   = "items_ids"
  ldict_SECTS_CHECKS  = "checking_values"
  idict_SECTS_METHOD  = "method"
  idict_SECTS_LANG    = "method_language"
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
  err_BASE64_DECODING     = 251
  err_BASE85_DECODING     = 253
  err_COMP_ZLIB_HEADER    = 301
  err_COMP_ZLIB_INCOMP    = 303
  #
  pattern = chr(0) # or "@", chr(255)
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
  # BlockCHain key publication Timeout (in seconds)
  #
  BCHT = 86400
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
  self.output_lock = False
  #
  self.ldict       = []
  self.ldict_types = []
  self.ldict_sections = []
  self.ldict_file  = None
  self.ldict_lock  = False
  #
  self.mid_method  = self.CONST.tag_mid_default
  self.oid_method  = 0
  self.did_method  = 0
  #
  self.crypt_HASH = None
  self.crypt_RSA  = None
  self.crypt_SHA1 = None
  self.crypt_S256 = None
  self.crypt_RIPE = None
  self.crypt_PKCS = None
  self.crypt_OAEP = None
  self.crypt_AES  = None
  self.crypt_FISH = None
  self.crypt_NACS = None
  self.crypt_NACE = None
  #
  self.crypt_method = self.CONST.tag_ENC_default
  #
  self.crypt_algo \
    = self.irciot_crypto_get_algorithm_(self.crypt_method)
  #
  if CAN_encrypt_datum:
    self.crypt_HASH = hashlib
    self.crypt_SHA1 = SHA1
    self.crypt_PKCS = PKCS1_v1_5
    if self.crypt_algo != None:
      self.irciot_load_encryption_methods_(self.crypt_method)
  #
  self.crypt_cache = None
  #
  # 0 is autoincrement
  #
  random.seed()
  #
  self.blockchain_private_key = None
  self.blockchain_public_key = None
  self.blockchain_key_published = 0
  #
  self.encryption_private_key = None
  self.encryption_public_key = None
  self.encryption_key_published = 0
  #
  if self.mid_method == "":
    self.current_mid = random.randint( 10000, 99999)
  elif self.mid_method == self.CONST.tag_mid_ED25519 \
    or self.mid_method == self.CONST.tag_mid_RSA1024:
     self.irciot_load_blockchain_methods_(self.mid_method)
     self.irciot_init_blockchain_method_(self.mid_method)
  self.mid_hash_length = len(str(self.current_mid))
  #
  if self.oid_method == 0:
     self.current_oid = random.randint(  1000,  9999)
  #
  if self.did_method == 0:
     self.current_did = random.randint(   100,   999)
  #
  self.irciot_init_encryption_method_(self.crypt_method)
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
  # End of PyLayerIRCIoT.__init__()

 def irc_pointer (self, in_compatibility, in_message):
  # Warning: interface may be changed while developing
  return False

 def user_pointer (self, in_compatibility, in_action, in_vuid, in_params):
  # Warning: method parameters and API may be changed while developing
  retrun (False, None)

 def irciot_error_(self, in_error_code, in_mid):
  my_message = ""
  my_datum = { }
  if in_error_code == self.CONST.err_BASE64_DECODING:
    return
  elif in_error_code == self.CONST.err_BASE85_DECODING:
    return
  elif in_error_code == self.CONST.err_DEFRAG_INVALID_DID:
    return
  elif in_error_code == self.CONST.err_CONTENT_MISSMATCH:
    return
  elif in_error_code == self.CONST.err_DEFRAG_OP_MISSING:
    return
  elif in_error_code == self.CONST.err_DEFRAG_DP_MISSING:
    return
  elif in_error_code == self.CONST.err_DEFRAG_BP_MISSING:
    return
  elif in_error_code == self.CONST.err_DEFRAG_OC_EXCEEDED:
    return
  elif in_error_code == self.CONST.err_DEFRAG_DC_EXCEEDED:
    return
  elif in_error_code == self.CONST.err_DEFRAG_BC_EXCEEDED:
    return
  elif in_error_code == self.CONST.err_OVERLAP_MISSMATCH:
    return
  elif in_error_code == self.CONST.err_COMP_ZLIB_HEADER:
    # my_datum.update({ "error" : "zlib_header" })
    return
  elif in_error_code == self.CONST.err_COMP_ZLIB_INCOMP:
    # my_datum.update({ "error" : "zlib_incomplete" })
    return
  else:
    return
  my_message = json.dumps(my_datum, separators=(',',':'))
  my_compat = self.irciot_compatibility_()
  if not self.irc_pointer (my_compat, my_message):
    # Handler not inserted
    self.output_pool.append(my_message)
  #
  # End of irciot_error_()

 def irciot_protocol_version_(self):
  return self.CONST.irciot_protocol_version

 def irciot_library_version_(self):
  return self.CONST.irciot_library_version

 def irciot_compatibility_(self):
  return ( \
    self.CONST.irciot_protocol_version, \
    self.CONST.irciot_library_version)

 def irciot_init_encryption_method_(self, in_crypt_method):
  my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    self.crypto_RSA_KEY_SIZE = self.CONST.crypto_RSA_KEY_SIZE
  elif my_algo == self.CONST.crypto_AES:
    self.crypto_AES_BLOCK_SIZE = self.crypt_AES.block_size
    self.crypto_AES_iv = self.irciot_crypto_hasher_(None, \
    self.crypto_AES_BLOCK_SIZE )
  elif my_algo == self.CONST.crypto_2FISH:
    pass
  (self.encryption_private_key, \
   self.encryption_public_key) \
    = self.irciot_encryption_generate_keys_(in_crypt_method)
  if not isinstance(self.encryption_private_key, object):
     return
  pass
  #
  # End of irciot_init_encryption_method_()

 def irciot_init_blockchain_method_(self, in_mid_method):
  if not in_mid_method in [ \
    self.CONST.tag_mid_ED25519, \
    self.CONST.tag_mid_RSA1024 ]:
    return
  (self.blockchain_private_key, \
   self.blockchain_public_key) \
    = self.irciot_blockchain_generate_keys_(in_mid_method)
  if not isinstance(self.blockchain_private_key, object):
    return
  self.current_mid \
    = self.irciot_blockchain_sign_string_( \
      str(self.current_mid), self.blockchain_private_key)
  if in_mid_method == self.CONST.tag_mid_ED25519:
    self.mid_hash_length = self.CONST.mid_ED25519_hash_length
  if in_mid_method == self.CONST.tag_mid_RSA1024:
    self.mid_hash_length = self.CONST.mid_RSA1024_hash_length
  #
  # End of irciot_init_blockchain_method_()
  
 def import_(self, in_pointer, in_module_name):
  if in_pointer == None:
    import importlib
    return importlib.import_module(in_module_name)
  else:
    return in_pointer

 def irciot_load_blockchain_methods_(self, in_mid_method):
  if in_mid_method == self.CONST.tag_mid_ED25519:
    if self.crypt_NACS != None and self.crypt_NACE != None:
      return False
    if self.crypt_NACS == None:
      self.crypt_NACS = self.import_(self.crypt_NACS, \
        'nacl.signing')
    if self.crypt_NACE == None:
      self.crypt_NACE = self.import_(self.crypt_NACE, \
        'nacl.encoding')
  elif in_mid_method == self.CONST.tag_mid_RSA1024:
    if self.crypt_HASH != None and self.crypt_RSA  != None and \
       self.crypt_PKCS != None and self.crypt_SHA1 != None:
      return False
    if self.crypt_HASH == None:
      self.crypt_HASH = self.import_(self.crypt_HASH, 'hashlib')
    if self.crypt_RSA == None:
      self.crypt_RSA  = self.import_(self.crypt_RSA, \
        'Crypto.PublicKey.RSA')
    if self.crypt_PKCS == None:
      self.crypt_PKCS = self.import_(self.crypt_PKCS, \
        'Crypto.Signature.PKCS1_v1_5')
    if self.crypt_SHA1 == None:
      self.crypt_SHA1 = self.import_(self.crypt_SHA1, \
        'Crypto.Hash.SHA')
  self.irciot_init_blockchain_method_(in_mid_method)
  return True
  #
  # End of irciot_load_blockchian_methods_()

 def irciot_load_encryption_methods_(self, in_crypt_method):
  my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    if self.crypt_RSA != None and self.crypt_RSA != None:
      return False
    if self.crypt_RSA == None:
      self.crypt_RSA = self.import_(self.crypt_RSA, \
        'Crypto.PublicKey.RSA')
    if self.crypt_OAEP == None:
      self.crypt_OAEP = self.import_(self.crypt_OAEP, \
        'Crypto.Cipher.PKCS1_OAEP')
  elif my_algo == self.CONST.crypto_AES:
    if self.crypt_AES != None:
      return False
    self.crypt_AES = self.import_(self.crypt_AES, \
      'Crypto.Cipher.AES')
  elif my_algo == self.CONST.crypto_2FISH:
    if self.crypt_FISH != None:
      return False
    self.crypt_FISH = self.import_(self.crypt_FISH, \
      'twofish.Twofish')
  self.irciot_init_encryption_method_(in_crypt_method)
  return True
  #
  # End of irciot_load_encryption_methods_()

 def irciot_enable_blockchain_(self, in_mid_method):
  if not self.irciot_load_blockchain_methods_(in_mid_method):
    self.irciot_init_blockchain_method_(in_mid_method)
  self.mid_method = in_mid_method
  self.blockchain_key_published = 0
  #
  # End of irciot_enable_blockchain_()
  
 def irciot_enable_encryption_(self, in_crypt_method):
  if CAN_encrypt_datum == True:
    return
  self.irciot_load_encryption_methods_(in_crypt_method)
  self.crypt_method = in_crypt_method
  #
  # End of irciot_enable_encryption_()

 def irciot_disable_blockchain_(self):
  self.mid_method = ""
  self.blockchain_key_published = self.CONST.BCHT
  self.current_mid = random.randint( 10000, 99999)

 def irciot_disable_encryption_(self):
  self.crypt_method = ""

 def irciot_crypto_hasher_(self, in_password, in_hash_size):
  if in_password == None or in_password == "" or \
   not (CAN_encrypt_datum or self.mid_method != ""):
    return ''.join(chr(random.randint(0,255)) \
      for my_chr in range(in_hash_size))
  if not isinstance(in_password, str):
    return None
  my_hash = None
  my_password = in_password.encode('utf-8')
  if in_hash_size == 16:
    my_hash = self.crypt_HASH.md5(my_password).digest()
  if in_hash_size == 20:
    my_hash = self.crypt_HASH.sha1(my_password).digest()
  if in_hash_size == 28:
    my_hash = self.crypt_HASH.sha224(my_password).digest()
  if in_hash_size == 32:
    my_hash = self.crypt_HASH.sha256(my_password).digest()
  if in_hash_size == 48:
    my_hash = self.crypt_HASH.sha384(my_password).digest()
  if in_hash_size == 64:
    my_hash = self.crypt_HASH.sha512(my_password).digest()
  if in_hash_size == 160:
    my_hash = self.crypt_HASH.ripemod160(my_password).digest()
  return my_hash
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
  # End of irciot_crypto_hash_to_str_()

 def irciot_crypto_str_to_hash_(self, in_string):
  if not isinstance(in_string, str):
    return None
  if (len(in_string) < 6):
    self.irciot_error_(self.CONST.err_BASE64_DECODING, 0)
    return None
  try:
    my_method = in_string[:2]
    my_hash   = in_string[2:]
    my_count  = 4 - (len(my_hash) % 4)
    if my_count > 0:
      for my_idx in range(my_count):
        my_hash += '='
    my_hash = base64.b64decode(my_hash)
  except:
    self.irciot_error_(self.CONST.err_BASE64_DECODING, 0)
    return None
  return (my_method, my_hash)
  #
  # End of irciot_crypto_str_to_hash_()

 def irciot_blockchain_generate_keys_(self, in_mid_method):
  try:
    if in_mid_method == self.CONST.tag_mid_ED25519:
      my_private_key \
        = self.crypt_NACS.SigningKey.generate()
      my_public_key = my_private_key.verify_key
    if in_mid_method == self.CONST.tag_mid_RSA1024:
      my_private_key = self.crypt_RSA.generate(1024)
      my_public_key = my_private_key.publickey()
  except:
    my_private_key = None
    my_public_key = None
  return (my_private_key, my_public_key)
  #
  # End of irciot_blockchain_generate_keys_()

 def irciot_get_current_datetime_(self):
  return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

 def irciot_blockchain_request_to_messages_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_BCH_REQUEST
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  # Incomplete code
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  # Copy destination address from last message source address?!
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  my_messages = self.irciot_encap_all_(my_datum)
  return my_messages
  #
  # End of irciot_blockchain_request_to_messages_()

 def irciot_encryption_request_to_messages_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_ENC_REQUEST
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  # Incomplete code
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  # Copy destination address from last message source address?!
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  my_messages = self.irciot_encap_all_(my_datum)
  return my_messages
  #
  # End of irciot_encryption_request_to_messages_()

 def irciot_blockchain_key_to_messages_(self, in_key_string):
  if not isinstance(in_key_string, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_BCH_INFO
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_BCH_METHOD] = self.mid_method
  my_datum[self.CONST.tag_BCH_PUBKEY] = in_key_string
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  my_messages = self.irciot_encap_all_(my_datum)
  return my_messages
  #
  # End of irciot_blockchain_key_to_message_()

 def irciot_encryption_key_to_messages_(self, in_key_string):
  if not isinstance(in_key_string, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_BCH_INFO
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_ENC_METHOD] = self.crypt_method
  my_datum[self.CONST.tag_ENC_PUBKEY] = in_key_string
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  my_messages = self.irciot_encap_all_(my_datum)
  return my_messages
  #
  # End of irciot_encryption_key_to_message_()

 def irciot_blockchain_key_publication_(self, in_public_key):
  if self.mid_method == self.CONST.tag_mid_ED25519:
    my_key_string = in_public_key.encode( \
      encoder = self.crypt_NACE.HexEncoder )
  elif self.mid_method == self.CONST.tag_mid_RSA1024:
    return
  else:
    return
  my_msgs = self.irciot_blockchain_key_to_messages_( \
    my_key_string.decode('utf-8'))
  if my_msgs == []:
    return
  my_compat = self.irciot_compatibility_()
  for my_msg in my_msgs:
    if not self.irc_pointer (my_compat, my_msg):
      # Handler not inserted
      self.output_pool.append(my_msg)
  #
  # End of irciot_blockchain_key_publication_()

 def irciot_encryption_key_publication_(self, in_public_key):
  my_key_string = ""
  my_algo = self.irciot_crypto_get_algorithm_(self.crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    return
  elif my_algo == self.CONST.crypto_AES:
    return
  elif my_algo == self.CONST.crypto_2FISH:
    return
  else:
    return
  my_msgs = self.irciot_encryption_key_to_messages_( \
    my_key_string.decode('utf-8'))
  if my_msgs == []:
    return
  my_compat = self.irciot_compatibility_()
  for my_msg in my_msgs:
    if not self.irc_pointer (my_compat, my_msg):
      # Handler not inserted
      self.output_pool.append(my_msg)
  #
  # End of irciot_encryption_key_publication_()

 def irciot_blockchain_check_publication_(self):
  if self.blockchain_key_published > 0:
    return
  try:
    if self.blockchain_public_key == None:
      return
  except:
    return
  if not self.mid_method == self.CONST.tag_mid_ED25519 and \
     not self.mid_method == self.CONST.tag_mid_RSA1024:
    return
  self.blockchain_key_published = self.CONST.BCHT
  self.irciot_blockchain_key_publication_( \
  self.blockchain_public_key)
  return
  #
  # End of irciot_blockchain_check_publication_()

 def irciot_encryption_check_publication_(self):
  pass

 def irciot_blockchain_place_key_to_repo_(self, in_public_key):
  if in_public_key == None:
    return
  #
  # End of irciot_blockchain_place_key_to_repo_()

 def irciot_encryption_place_key_to_repo_(self, in_public_key):
  if in_public_key == None:
    return
  #
  # End of irciot_encryption_place_key_to_repo_()

 def irciot_blockchain_request_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return
  # IRC-IoT messages of this type should be sent directly
  # to the user using private sending, but now they are passed
  # to the common message flow and appear in the channel
  my_msgs = self.irciot_blockchain_request_to_messages_(in_vuid)
  if my_msgs == []:
    return
  my_compat = self.irciot_compatibility_()
  for my_msg in my_msgs:
    if not self.irc_pointer (my_compat, my_msg):
      # Handler not inserted
      self.output_pool.append(my_msg)
  #
  # End of irciot_blockchain_request_foreign_key_()

 def irciot_encryption_request_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return
  my_msgs = self.irciot_encryption_request_to_messages_(in_vuid)
  if my_msgs == []:
    return
  my_compat = self.irciot_compatibility_()
  for my_msg in my_msgs:
    if not self.irc_pointer (my_compat, my_msg):
      # Handler not inserted
      self.output_pool.append(my_msg)
  #
  # End of irciot_encryption_request_foreign_key_()

 def irciot_blockchain_get_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  my_compat = self.irciot_compatibility_()
  my_params = None
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_BKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if not my_status:
    if my_answer == None:
      self.irciot_blockchain_request_foreign_key_(in_vuid)
    return None
  if isinstance(my_answer, str):
    return my_answer
  return None
  #
  # End of irciot_blockchain_get_foreign_key_()

 def irciot_encryption_get_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  my_compat = self.irciot_compatibility_()
  my_params = None
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_EKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if not my_status:
    if my_answer == None:
      self.irciot_encryption_request_foreign_key_(in_vuid)
    return None
  if isinstance(my_answer, str):
    return my_answer
  return None
  #
  # End of irciot_encryption_get_foreign_key_()

 def irciot_blockchain_get_last_mid_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  my_compat = self.irciot_compatibility_()
  my_params = None
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_LMID, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if not my_status:
    return None
  if isinstance(my_answer, str):
    return my_answer
  return None
  #
  # End of irciot_blockchain_get_last_mid_()

 def irciot_blockchain_update_last_mid_(self, in_vuid, \
   in_message_id):
  if not isinstance(in_vuid, str):
    return
  my_compat = self.irciot_compatibility_()
  my_params = in_message_id
  self.user_pointer (my_compat, \
    self.CONST.api_SET_LMID, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return
  if not my_status:
    return
  #
  # End of irciot_blockchain_update_last_mid_()

 def irciot_blockchain_update_foreign_key_(self, in_vuid, \
   in_public_key):
  if not isinstance(in_vuid, str):
    return
  my_compat = self.irciot_compatibility_()
  my_params = in_public_key
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_BKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return
  if not my_status:
    return
  #
  # End of irciot_blockchain_update_foreign_key_()

 def irciot_encryption_update_foreign_key_(self, in_vuid, \
   in_public_key):
  if not isinstance(in_vuid, str):
    return
  my_compat = self.irciot_compatibility_()
  my_params = in_public_key
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_EKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return
  if not my_status:
    return
  #
  # End of irciot_encryption_update_foreign_key_()

 def irciot_blockchain_sign_string_(self, in_string, in_private_key):
  if not isinstance(in_string, str):
    return ""
  try:
    my_string = in_string.encode('utf-8')
    if self.mid_method == self.CONST.tag_mid_ED25519:
      my_signed = in_private_key.sign(my_string)
      my_sign = my_signed[:-len(my_string)]
    elif self.mid_method == self.CONST.tag_mid_RSA1024:
      my_hash = self.crypt_SHA1.new(my_string)
      my_pkcs = self.crypt_PKCS.new(in_private_key)
      my_sign = my_pkcs.sign(my_hash)
      del my_hash
    else:
      return ""
    my_string = str(self.mid_method)
    my_string += self.irciot_crypto_hash_to_str_(my_sign)
  except:
    my_siring = None
  return my_string
  #
  # End of irciot_blockchain_sign_string_()

 def irciot_blockchain_save_defaults_(self):
  return (self.mid_method, \
   self.blockchain_private_key, \
   self.blockchain_public_key)

 def irciot_encryption_save_defaults_(self):
  return (self.crypt_method, \
   self.encryption_private_key, \
   self.encryption_public_key)

 def irciot_blockchain_restore_defaults_(self, in_defaults):
  (self.mid_method, \
   self.blockchain_private_key, \
   self.blockchain_public_key) = in_defaults

 def irciot_encryption_restore_defaults_(self, in_defaults):
  (self.crypt_method, \
   self.encryption_private_key, \
   self.encryption_public_key) = in_defaults

 def irciot_blockchain_verify_string_(self, \
   in_string, in_sign, in_public_key):
  if not isinstance(in_string, str):
    return False
  if not isinstance(in_sign, str):
    return False
  my_pair = self.irciot_crypto_str_to_hash_(in_sign)
  if my_pair == None:
    return False
  (my_method, my_sign) = my_pair
  my_string_bin = bytes(in_string, 'utf-8')
  my_save = self.irciot_blockchain_save_defaults_()
  my_result = False
  if my_method == self.CONST.tag_mid_ED25519:
    self.mid_method = my_method
    if DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    try:
      in_public_key.verify(my_string_bin, my_sign)
      my_result = True
    except:
      pass
  elif my_method == self.CONST.tag_mid_RSA1024:
    self.mid_method = my_method
    if DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    try:
      my_hash = self.crypt_SHA1.new(my_string_bin)
      my_pkcs = self.crypt_PKCS.new(in_public_key)
      if my_pkcs.verify(my_hash, my_sign):
        my_result = True
    except:
      pass
  self.irciot_blockchain_restore_defaults_(my_save)
  return my_result
  #
  # End of irciot_blockchain_verify_string_()

 def irciot_crypto_get_base_(self, in_crypt_method):
  my_base = None
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE32 ]:
    my_base = self.CONST.base_BASE32
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE64, \
     self.CONST.tag_ENC_B64_AES, \
     self.CONST.tag_ENC_B64Z_AES, \
     self.CONST.tag_ENC_B64_ZLIB, \
     self.CONST.tag_ENC_B64_RSA, \
     self.CONST.tag_ENC_B64Z_RSA, \
     self.CONST.tag_ENC_B64_2FISH ]:
    my_base = self.CONST.base_BASE64
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE85, \
     self.CONST.tag_ENC_B85_ZLIB, \
     self.CONST.tag_ENC_B85_2FISH ]:
    my_base = self.CONST.base_BASE85
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE122 ]:
    my_base = self.CONST.base_BASE122
  return my_base
  #
  # End of irciot_crypto_get_base_()

 def irciot_crypto_get_compress_(self, in_crypt_method):
  my_compress = None
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE32, \
     self.CONST.tag_ENC_BASE64, \
     self.CONST.tag_ENC_BASE85, \
     self.CONST.tag_ENC_BASE122, \
     self.CONST.tag_ENC_B64_RSA, \
     self.CONST.tag_ENC_B85_RSA, \
     self.CONST.tag_ENC_B64_AES, \
     self.CONST.tag_ENC_B85_AES, \
     self.CONST.tag_ENC_B64_2FISH, \
     self.CONST.tag_ENC_B85_2FISH ]:
    my_compress = self.CONST.compress_NONE
  elif in_crypt_method in [  \
     self.CONST.tag_ENC_B64_ZLIB, \
     self.CONST.tag_ENC_B85_ZLIB, \
     self.CONST.tag_ENC_B64Z_RSA, \
     self.CONST.tag_ENC_B85Z_RSA, \
     self.CONST.tag_ENC_B64Z_AES, \
     self.CONST.tag_ENC_B85Z_AES ]:
    my_compress = self.CONST.compress_ZLIB
  elif in_crypt_method in [ \
     self.tag_ENC_B64_BZIP2, \
     self.tag_ENC_B85_BZIP2 ]:
    my_compress = self.CONST.compress_BZIP2
  return my_compress
  #
  # End of irciot_crypto_get_compress_()
  
 def irciot_crypto_get_algorithm_(self, in_crypt_method):
  my_algorithm = None
  if in_crypt_method in [ \
     self.CONST.tag_ENC_B64_RSA, \
     self.CONST.tag_ENC_B85_RSA, \
     self.CONST.tag_ENC_B64Z_RSA, \
     self.CONST.tag_ENC_B85Z_RSA ]:
    my_algorithm = self.CONST.crypto_RSA
  elif in_crypt_method in [ \
     self.CONST.tag_ENC_B64_AES, \
     self.CONST.tag_ENC_B85_AES, \
     self.CONST.tag_ENC_B64Z_AES, \
     self.CONST.tag_ENC_B85Z_AES ]:
    my_algorithm = self.CONST.crypto_AES
  elif in_crypt_method in [ \
     self.CONST.tag_ENC_B64_2FISH, \
     self.CONST.tag_ENC_B85_2FISH ]:
    my_algorithm = self.CONST.crypto_2FISH
  return my_algorithm

 def irciot_crypto_get_model_(self, in_crypt_method):
  my_model = None
  if in_crypt_method in [ \
     self.CONST.tag_ENC_BASE32, \
     self.CONST.tag_ENC_BASE64, \
     self.CONST.tag_ENC_BASE85, \
     self.CONST.tag_ENC_BASE122, \
     self.CONST.tag_ENC_B64_ZLIB, \
     self.CONST.tag_ENC_B85_ZLIB, \
     self.CONST.tag_ENC_B64_BZIP2, \
     self.CONST.tag_ENC_B85_BZIP2 ]:
    my_model = self.CONST.crypt_NO_ENCRYPTION
  else:
    my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
    if my_algo == self.CONST.crypto_RSA:
      my_model = self.CONST.crypt_ASYMMETRIC
    elif my_algo in [ \
       self.CONST.crypto_AES, \
       self.CONST.crypto_2FISH ]:
      my_model = self.CONST.crypt_PRIVATE_KEY
  return my_model
  #
  # End of irciot_crypto_get_model_()

 def irciot_crypto_AES_encrypt_(self, in_raw_data, in_secret_key):
  if self.crypt_AES == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_AES)
    else:
      return None
  try:
    my_AES = self.crypt_AES.new(in_secret_key, \
      self.crypt_AES.MODE_CBC, self.crypto_AES_iv)
    my_encrypted = my_AES.encrypt(in_raw_data)
  except:
    return None
  return my_encrypted
  #
  # End of irciot_crypto_AES_encrypt_()

 def irciot_crypto_AES_decrypt_(self, in_encrypted_data, in_secret_key):
  if self.crypt_AES == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_AES)
    else:
      return None
  try:
    my_AES = self.crypt_AES.new(in_secret_key, \
      self.crypt_AES.MODE_CBC, self.crypto_AES_iv)
    my_decrypted = my_AES.decrypt(in_encrypted_data)
  except:
    return None
  return my_decrypted
  #
  # End of irciot_crypto_AES_decrypt_()

 def irciot_crypto_2fish_encrypt_(self, in_raw_data, in_secret_key):
  if self.crypt_FISH == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_2FISH)
    else:
      return None
  try:
    my_2fish = self.crypt_FISH(in_secret_key)
    my_encrypted = my_2fish.encrypt(in_raw_data)
  except:
    return None
  return my_encrypted
  #
  # End of irciot_crypto_2fish_encrypt_()

 def irciot_crypto_2fish_decrypt_(self, in_encrypted_data, in_secret_key):
  if self.crypt_FISH == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_2FISH)
    else:
      return None
  try:
    my_2fish = self.crypt_FISH(in_secret_key)
    my_decrypted = my_2fish.decrypt(in_encrypted_data).decode()
  except:
    return None
  return my_decrypted
  #
  # End of irciot_crypto_2fish_decrypt_()

 def irciot_crypto_RSA_encrypt_(self, in_raw_data, in_public_key):
  if self.crypt_RSA == None or self.crypt_OAEP == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_RSA)
    else:
      return None
  my_size = len(in_raw_data)
  my_hash = self.irciot_crypto_hasher_(str(in_raw_data), 16)
  if self.crypt_cache != None:
    ( my_size_cached, my_hash_cached, my_encrypted ) \
      = self.crypt_cache
    if ((my_size == my_size_cached) \
    and (my_hash == my_hash_cached)):
      return my_encrypted
  my_encrypted = bytes()
  my_chunk  = self.CONST.crypto_RSA_CHUNK_IN
  my_offset = 0
  my_loop   = True
  try:
    my_encryptor = self.crypt_OAEP.new(in_public_key)
    while my_loop:
      my_block = in_raw_data[my_offset:my_offset + my_chunk]
      my_part = len(my_block) % my_chunk
      if my_part != 0:
        my_loop = False
      else:
        if my_offset == my_size:
          my_chunk = 0
          my_loop = False
      my_encrypted += my_encryptor.encrypt(my_block)
      my_offset += my_chunk
  except:
    return None
  if my_encrypted == bytes():
    return None
  self.crypt_cache = ( my_size, my_hash, my_encrypted )
  return my_encrypted
  #
  # End of irciot_crypto_RSA_encrypt_()

 def irciot_crypto_RSA_decrypt_(self, in_encrypted_data, in_private_key):
  if self.crypt_RSA == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_RSA)
    else:
      return None
  my_decrypted = bytes()
  my_chunk  = self.CONST.crypto_RSA_CHUNK
  my_offset = 0
  my_loop   = True
  try:
    my_decryptor = self.crypt_OAEP.new(in_private_key)
    my_size = len(in_encrypted_data)
    while my_loop:
      my_block = in_encrypted_data[my_offset:my_offset + my_chunk]
      my_part = len(my_block) % my_chunk
      if my_part != 0:
        return None
      else:
        if my_offset == my_size:
          my_chunk = 0
          my_loop = False
      if (len(my_block) != 0):
        my_decrypted += my_decryptor.decrypt(my_block)
      my_offset += my_chunk
  except:
    return None
  if my_decrypted == bytes():
    return None
  return my_decrypted
  #
  # End of irciot_crypto_RSA_decrypt_()

 def irciot_encryption_generate_keys_(self, in_crypt_method):
  if self.irciot_crypto_get_model_(in_crypt_method) \
    == self.CONST.crypt_NO_ENCRYPTION:
    return (None, None)
  crypto_public_key = None
  crypto_private_key = None
  my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    crypto_private_key \
      = self.crypt_RSA.generate(self.crypto_RSA_KEY_SIZE)
    crypto_public_key = crypto_private_key.publickey()
  elif my_algo == self.CONST.crypto_AES:
    pass
  elif my_algo == self.CONST.crypto_2FISH:
    pass
  #
  return (crypto_private_key, crypto_public_key)
  #
  # End of irciot_crypto_generate_keys_()

 def irciot_crypto_place_key_to_repo_(self, in_public_key):
  pass
  #
  # End of irciot_crypto_place_key_to_repo_()

 def irciot_crypto_request_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return
  #
  # End of irciot_crypto_request_foreign_key_()

 def irciot_crypto_get_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  my_compat = self.irciot_compatibility_()
  my_params = None
  my_result = self.user_pointer (in_compat, \
    self.CONST.api_GET_EKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if not my_status:
    return None
  if my_answer == None:
    self.irciot_crypto_request_foreign_key_(in_vuid)
  else:
    return my_answer
  return None
  #
  # End of irciot_crypto_get_foreign_key_()

 def irciot_crypto_update_foreign_key_(self, in_vuid, \
   in_public_key):
  if not isinstance(in_vuid, str):
    return
  my_compat = self.irciot_compatibility_()
  my_params = in_public_key
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_EKEY, in_vuid, my_params)
  try:
    (my_status, my_answer) = my_result
  except:
    return
  if not my_status:
    return
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
  return None
  #
  # End of irciot_get_object_by_id_()

 def irciot_delete_object_by_id_(self, in_object_id):
  if not isinstance(in_object_id, int):
    return
  #
  pass

 def irciot_get_objects_count_(self):
  return 0

 def irciot_ldict_get_item_max_id_(self):
  my_max_id = 0
  for my_ldict_item in self.ldict:
    ( my_id, my_ot, my_parent_id, my_type_id, my_type_param, \
      my_default, my_child_obj_id, my_method, my_method_lang, \
      my_sections ) = my_ldict_item
    if my_max_id < my_id:
      my_max_id = my_id
  return my_max_id

 def irciot_ldict_create_item_(self, in_ldict_item):
  try:
   ( my_id, my_ot, my_parent_id, my_type_id, my_type_param, \
     my_default, my_child_obj_id, my_method, my_method_lang, \
     my_sections ) = in_ldict_item
  except:
    return
  my_item = {}
  my_item.update({self.CONST.ldict_ITEMS_ID : my_id })
  my_item.update({self.CONST.ldict_ITEMS_OT : my_ot })
  my_item.update({self.CONST.ldict_ITEMS_PARENT : my_parent_id })
  my_item.update({self.CONST.ldict_ITEMS_TYPEID : my_type_id })
  my_item.update({self.CONST.ldict_ITEMS_TYPEPR : my_type_param })
  my_item.update({self.CONST.ldict_ITEMS_DEFVAL : my_default })
  my_item.update({self.CONST.ldict_ITEMS_CHILD : my_child_obj_id })
  my_item.update({self.CONST.ldict_ITEMS_METHOD : my_method })
  my_item.update({self.CONST.ldict_ITEMS_LANG : my_method_lang })
  my_item.update({self.CONST.ldict_ITEMS_SECTS : my_sections })
  #
  if not self.irciot_ldict_check_item_(my_item):
    return
  if self.irciot_ldict_get_item_by_ot_(my_ot):
    return
  my_max_id = self.irciot_ldict_get_item_max_id_()
  if my_id <= my_max_id:
    my_item[self.CONST.ldict_ITEMS_OT] = my_max_id + 1
  self.ldict.append(my_item)
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_create_item_()

 def irciot_ldict_get_item_by_ot_(self, in_object_type):
  if not isinstance(in_object_type, str):
    return None
  for my_ldict_item in self.ldict:
    ( my_id, my_ot, my_parent_id, my_type_id, my_type_param, \
      my_default, my_child_obj_id, my_nmethod, my_method_lang, \
      my_sections ) = my_ldict_item
    if my_ot == in_object_type:
      return my_ldict_item
  #
  # End of irciot_ldict_get_item_by_ot_()

 def irciot_ldict_delete_item_by_ot_(self, in_object_type):
  if not isinstance(in_object_type, str):
    return
  for my_ldict_item in self.ldict:
    ( my_id, my_ot, my_parent_id, my_type_id, my_type_param, \
      my_default, my_child_obj_id, my_nmethod, my_method_lang, \
      my_sections ) = my_ldict_item
    if my_ot == in_object_type:
      self.ldict.remove(my_ldict_item)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_items_by_ot_()

 def irciot_ldict_delete_item_by_id_(self, in_item_id):
  if not isinstance(in_item_id, int):
    return
  for my_ldict_item in self.ldict:
    ( my_id, my_ot, my_parent_id, my_type_id, my_type_param, \
      my_default, my_child_obj_id, my_nmethod, my_method_lang, \
      my_sections ) = my_ldict_item
    if my_id == in_item_id:
      self.ldict.remove(my_ldict_item)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_item_by_id_()

 def irciot_ldict_get_type_max_id_(self):
  my_max_id = 0
  for my_ldict_type in self.ldict_types:
    ( my_id, my_name, my_type, my_is_array, my_is_dynamic, \
      my_is_dynarray, my_array_size, my_size, my_min, my_max, \
      my_precession, my_edianness, my_encoding ) = my_ldict_type
    if my_max_id < my_id:
      my_max_id = my_id
  return my_max_id

 def irciot_ldict_create_type_(self, in_ldict_type):
  try:
   ( my_id, my_name, my_type, my_is_array, my_is_dynamic, \
     my_is_dynarray, my_array_size, my_size, my_min, my_max, \
     my_precession, my_endianness, my_encoding ) = in_ldict_type
  except:
    return
  my_type = {}
  my_type.update({ self.CONST.ldict_TYPES_ID : my_id })
  my_type.update({ self.CONST.ldict_TYPES_NAME : my_name })
  my_type.update({ self.CONST.ldict_TYPES_TYPE : my_type })
  my_type.update({ self.CONST.ldict_TYPES_ARR : my_is_array })
  my_type.update({ self.CONST.ldict_TYPES_DYNSIZE : my_is_dynamic })
  my_type.update({ self.CONST.ldict_TYPES_DYN_ARR : my_is_dynarray })
  my_type.update({ self.CONST.ldict_TYPES_ARRSIZE : my_array_size })
  my_type.update({ self.CONST.ldict_TYPES_SIZE : my_size })
  my_type.update({ self.CONST.ldict_TYPES_MIN : my_min })
  my_type.update({ self.CONST.ldict_TYPES_MAX : my_max })
  my_type.update({ self.CONST.ldict_TYPES_PRECESS : my_precession })
  my_type.update({ self.CONST.ldict_TYPES_ENDIAN : my_endianness })
  my_type.update({ self.CONST.ldict_TYPES_ENCODE : my_encoding })
  #
  if not self.irciot_ldict_check_type_(my_type):
    return
  if self.irciot_ldict_get_type_by_name(my_name):
    return
  my_max_id = self.irciot_ldict_get_type_max_id_()
  if my_id <= my_max_id:
    my_type[self.CONST.ldict_TYPES_ID] = my_max_id + 1
  self.ldict_types.append(my_type)
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_create_type_()

 def irciot_ldict_delete_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return
  for my_ldict_type in self.ldict_types:
    ( my_id, my_name, my_type, my_is_array, my_is_dynamic, \
      my_is_dynarray, my_array_size, my_size, my_min, my_max, \
      my_precession, my_edianness, my_encoding ) = my_ldict_type
    if my_name == in_type_name:
      self.ldict_types.remove(my_ldict_type)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_type_by_name_()

 def irciot_ldict_delete_type_by_id_(self, in_type_id):
  if not isinstance(in_type_id, int):
    return
  for my_ldict_type in self.ldict_types:
    ( my_id, my_name, my_type, my_is_array, my_is_dynamic, \
      my_is_dynarray, my_array_size, my_size, my_min, my_max, \
      my_precession, my_edianness, my_encoding ) = my_ldict_type
    if my_id == in_type_id:
      self.ldict_types.remove(my_ldict_type)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_type_by_id_()

 def irciot_ldict_get_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return
  for my_ldict_type in self.ldict_types:
    ( my_id, my_name, my_type, my_is_array, my_is_dynamic, \
      my_is_dynarray, my_array_size, my_size, my_min, my_max, \
      my_precession, my_edianness, my_encoding ) = my_ldict_type
    if my_name == in_type_name:
      return ldict_type
  return None
  #
  # End of irciot_ldict_get_type_by_name_()

 def irciot_ldict_check_item_(self, in_ldict_item):
  # Will be replaced by Python SCHEMA analyzer
  if not isinstance(in_ldict_item, dict):
    return False
  if not self.CONST.ldict_ITEMS_ID in in_ldict_item.keys():
    return False
  my_item_id = in_ldict_item[self.CONST.ldict_ITEMS_ID]
  if not isinstance(my_item_id, int):
    return False
  if not self.CONST.ldict_ITEMS_OT in in_ldict_item.keys():
    return False
  my_item_ot = in_ldict_item[self.CONST.ldict_ITEMS_OT]
  if not isinstance(my_item_ot, str):
    return False
  if not self.CONST.ldict_ITEMS_PARENT in in_ldict_item.keys():
    return False
  my_item_parent = in_ldict_item[self.CONST.ldict_ITEMS_PARENT]
  if not isinstance(my_item_parent, int) \
     and my_item_parent != None:
    return False
  if not self.CONST.ldict_ITEMS_TYPEID in in_ldict_item.keys():
    return False
  my_item_type_id = in_ldict_item[self.CONST.ldict_ITEMS_TYPEID]
  if not isinstance(my_item_type_id, int):
    return False
  if not self.CONST.ldict_ITEMS_TYPEPR in in_ldict_item.keys():
    return False
  my_item_type_pr = in_ldict_item[self.CONST.ldict_ITEMS_TYPEPR]
  if not isinstance(my_item_type_pr, str) \
     and my_item_type_pr != None:
    return False
  if not self.CONST.ldict_ITEMS_DEFVAL in in_ldict_item.keys():
    return False
  my_item_defval = in_ldict_item[self.CONST.ldict_ITEMS_DEFVAL]
  if not isinstance(my_item_defval, str) \
     and my_item_defval != None:
    return False
  if not self.CONST.ldict_ITEMS_CHILD in in_ldict_item.keys():
    return False
  my_item_child = in_ldict_item[self.CONST.ldict_ITEMS_CHILD]
  if not isinstance(my_item_child, int) \
     and my_item_child != None:
    return False
  if not self.CONST.ldict_ITEMS_METHOD in in_ldict_item.keys():
    return False
  my_item_method = in_ldict_item[self.CONST.ldict_ITEMS_METHOD]
  if not isinstance(my_item_method, str) \
     and my_item_method != None:
    return False
  if not self.CONST.ldict_ITEMS_LANG in in_ldict_item.keys():
    return False
  my_item_language = in_ldict_item[self.CONST.ldict_ITEMS_LANG]
  if not isinstance(my_item_language, str) \
     and my_item_language != None:
    return False
  if not self.CONST.ldict_ITEMS_SECTS in in_ldict_item.keys():
    return False
  my_item_sects = in_ldict_item[self.CONST.ldict_ITEMS_SECTS]
  if not isinstance(my_item_sects, list):
    return False
  for my_section_id in my_item_sects:
    if not isinstance(my_section_id, int):
      return False
  return True
  #
  # End of irciot_ldict_check_item_()

 def irciot_ldict_check_type_(self, in_ldict_type):
  if not isinstance(in_ldict_type, dict):
    return False
  if not self.CONST.ldict_TYPES_ID in in_ldict_type.keys():
    return False
  my_type_id = in_ldict_type[self.CONST.ldict_TYPES_ID]
  if not isinstance(my_type_id, int):
    return False
  if not self.CONST.ldict_TYPES_NAME in in_ldict_type.keys():
    return False
  my_type_name = in_ldict_type[self.CONST.ldict_TYPES_NAME]
  if not isinstance(my_type_name, str):
    return False
  if not self.CONST.ldict_TYPES_TYPE in in_ldict_type.keys():
    return False
  if not self.CONST.ldict_TYPES_ARR in in_ldict_type.keys():
    return False
  my_type_is_array = in_ldict_type[self.CONST.ldict_TYPES_ARR]
  if not isinstance(my_type_is_array, bool):
    return False
  if not self.CONST.ldict_TYPES_DYNSIZE in in_ldict_type.keys():
    return False
  my_type_dynsize = in_ldict_type[self.CONST.ldict_TYPES_DINSIZE]
  if not isinstance(my_type_dynsize, bool):
    return False
  if not self.CONST.ldict_TYPES_DYN_ARR in in_ldict_type.keys():
    return False
  my_type_dynarr = in_ldict_type[self.CONST.ldict_TYPES_DYN_ARR]
  if not isinstance(my_type_dynarr, bool):
    return False
  if not self.CONST.ldict_TYPES_ARRSIZE in in_ldict_type.keys():
    return False
  my_type_arrsize = in_ldict_type[self.CONST.lidict_TYPES_ARRSIZE]
  if not isinstance(my_type_arrsize, int) \
     and my_type_arrsize != None:
    return False
  if not self.CONST.lidct_TYPES_SIZE in in_ldict_type.keys():
    return False
  my_type_size = in_ldict_type[self.CONST.ldict_TYPES_SIZE]
  if not isinstance(my_type_size, int) \
     and my_type_size != None:
    return False
  if not self.CONST.ldict_TYPES_MIN in in_ldict_type.keys():
    return False
  my_type_min = in_ldict_type[self.CONST.ldict_TYPES_MIN]
  if not isinstance(my_type_min, str) \
     and my_type_min != None:
    return False
  if not self.CONST.ldict_TYPES_MAX in in_ldict_type.keys():
    return False
  my_type_max = in_ldict_type[self.CONST.lidct_TYPES_MAX]
  if not isinstance(my_type_max, str) \
     and my_type_max != None:
    return False
  if not self.CONST.ldict_TYPES_PRECESS in in_ldict_type.keys():
    return False
  my_type_precess = in_ldict_type[self.CONST.TYPES_PRECESS]
  if not isinstance(my_type_precess, str) \
     and my_type_precess != None:
    return False
  if not self.CONST.ldict_TYPES_ENDIAN in in_ldict_type.keys():
    return False
  my_type_endian = in_ldict_type[self.CONST.ldict_TYPES_ENDIAN]
  if not isinstance(my_type_endian, str) \
     and my_type_endian != None:
    return False
  if not self.CONST.ldict_TYPES_ENCODE in in_ldict_type.keys():
    return False
  my_type_encode = in_ldict_type[self.CONST.ldict_TYPES_ENCODE]
  if not isinstance(my_type_encode, str) \
     and my_type_encode != None:
    return False
  return True
  #
  # End of irciot_ldict_check_type_()

 def irciot_ldict_check_section_(self, in_ldict_section):
  if not isinstance(in_ldict_section, dict):
    return False
  if not self.CONST.ldict_SECTS_ID in in_ldict_section.keys():
    return False
  my_section_id = in_ldict_section[self.CONST.ldict_SECTS_ID]
  if not isinstance(my_section_id, int):
    return False
  if not self.CONST.ldict_SECTS_ITEMS in in_ldict_section.keys():
    return False
  my_section_items = in_ldict_section[self.CONST.ldict_SECTS_ITEMS]
  if not isinstance(my_section_items, list):
    return False
  for my_item_id in my_section_items:
    if not isinstance(my_item_id, int):
      return False
  if not self.CONST.ldict_SECTS_CHECKS in in_ldict_section.keys():
    return False
  my_section_checks = in_ldict_section[self.CONST.ldict_SECTS_CHECKS]
  if not isinstance(my_section_checks, list):
    return False
  for my_check in my_section_checks:
    if not isinstance(my_check, str):
      return False
  if not self.CONST.ldict_SECTS_METHOD in in_ldict_section.keys():
    return False
  my_section_method = in_ldict_section[self.CONST.ldict_SECTS_METHOD]
  if not isinstance(my_section_method, str):
    return False
  if not self.CONST.lidct_SECTS_LANG in in_ldict_section.keys():
    return False
  my_section_language = in_ldict_section[self.CONST.ldict_SECTS_LANG]
  if not isinstacne(my_section_language, str):
    return False
  return True
  #
  # End of irciot_ldict_check_section_()

 def irciot_ldict_load_from_file_(self, in_filename):
  if not isinstance(in_filename, str):
    return False
  if os.path.isfile(in_filename):
    try:
      load_fd = open(in_filename, 'r')
      load_json = load_fd.read()
      load_dict = json.loads(load_json)
    except:
      return False
    if not isinstance(load_dict, dict):
      return False
    if not self.CONST.ldict_VERSION in load_dict.keys():
      return False
    my_ldict_version = load_dict[self.CONST.lidcit_VERSION]
    if my_ldict_version != self.CONST.irciot_protocol_version:
      return False
    if self.CONST.ldict_ITEMS_TABLE in load_dict.keys():
      my_ldict_items = load_dict[self.CONST.ldict_ITEMS_TABLE]
      for my_ldict_item in my_ldict_items:
        if not self.irciot_ldict_check_item_(my_ldict_item):
          return False
    else:
      my_ldict = []
    if self.CONST.ldict_TYPES_TABLE in load_dict.keys():
      my_ldict_types = load_dict[self.CONST.ldict_TYPES_TABLE]
      for my_ldict_type in my_ldict_types:
        if not self.irciot_ldict_check_type_(my_ldict_type):
          return False
    else:
      my_ldict_types = []
    if self.CONST.ldict_SECTS_TABLE in load_dict.keys():
      my_ldict_sections = load_dict[self.CONST.ldict_SECTS_TABLE]
      for my_ldict_section in my_ldict_sections:
        if not self.irciot_ldict_check_section_(my_ldict_section):
          return False
    else:
      my_ldict_sections = []
    if not self.ldict_lock:
      return False
    self.ldict          = my_ldict_items
    self.ldict_types    = my_ldict_types
    self.ldict_sections = my_ldict_sections
  return True
  #
  # End of irciot_ldict_load_from_file_()

 def irciot_ldict_dump_to_file_(self, in_filename):
  if not isinstance(in_filename, str):
    return False
  my_ldict = {}
  my_ldict.update({self.CONST.ldict_VERSION \
    : self.CONST.irciot_protocol_version });
  my_ldict.update({self.CONST.ldict_ITEMS_TABLE \
    : self.ldict });
  my_ldict.update({self.CONST.ldict_TYPES_TABLE \
    : self.ldict_types });
  my_ldict.update({self.CONST.ldict_SECTS_TABLE \
    : self.ldict_sections });
  my_json = json.dumps(my_ldict, separators=(',',':'))
  del my_ldict
  try:
    dump_fd = open(in_filename, 'w')
    dump_fd.write(my_json + "\n")
    dump_fd.close()
  except:
    return False
  return True
  #
  # End of irciot_ldict_dump_to_file_()

 def irciot_ldict_get_type_by_id_(self, in_type_id):
  if not isinstance(in_type_id, int):
    return
  for ldict_type in self.ldict_types:
    (my_type_id, my_type_name) = ldict_type
    if my_type_id == in_type_id:
      return ldict_type 
  return None
  #
  # End of irciot_ldict_get_type_by_id_()

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
       defrag_buffer = in_enc
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
       my_base = self.irciot_crypto_get_base_(self.crypt_method)
       if (my_base == self.CONST.base_BASE64):
          try:
            out_base = base64.b64decode(defrag_buffer)
          except:
            self.irciot_error_(self.CONST.err_BASE64_DECODING, 0)
            return ""
       elif (my_base == self.CONST.base_BASE85):
          try:
            out_base = base64.b85decode(defrag_buffer)
          except:
            self.irciot_error_(self.CONST.err_BASE85_DECODING, 0)
            return ""
       elif (my_base == self.CONST.base_BASE32):
          try:
            out_base = base64.b32decode(defrag_buffer)
          except:
            return ""
       else:
          out_base = bytes(defrag_buffer, 'utf-8')
       my_algo = self.irciot_crypto_get_algorithm_(self.crypt_method)
       if my_algo == self.CONST.crypto_RSA:
          out_base = self.irciot_crypto_RSA_decrypt_(out_base, \
            self.encryption_private_key)
       elif my_algo == self.CONST.crypto_AES:
          pass
       elif my_algo == self.CONST.crypto_2FISH:
          pass
       my_compress = self.irciot_crypto_get_compress_( \
          self.crypt_method )
       if my_compress == self.CONST.compress_NONE:
          out_json = str(out_base, 'utf-8')
          del out_base
       elif my_compress == self.CONST.compress_ZLIB:
          try:
            out_compress = str(zlib.decompress(out_base))
            del out_base
          except zlib.error as zlib_error:
            # print("\033[1;35m" + str(zlib_error) + "\033[0m")
            if zlib_error.args[0].startswith("Error -3 "):
              self.irciot_error_(self.CONST.err_COMP_ZLIB_HEADER, 0)
            else:
              self.irciot_error_(self.CONST.err_COMP_ZLIB_INCOMP, 0)
            del zlib_error
            return ""
          out_json = out_compress[2:-1]
          del out_compress
       elif my_compress == self.CONST.compress_BZIP2:
          return ""
       else:
          return ""
       try:
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

 def irciot_check_datum_(self, in_datum, in_vuid = None, in_ot = None):
  if not isinstance(in_vuid, str):
    return
  if not isinstance(in_datum, dict):
    return
  my_check = [ \
    self.CONST.tag_DATUM_ID, \
    self.CONST.tag_DATE_TIME ]
  for in_key in my_check:
    if not in_key in in_datum.keys():
      return
  if in_ot == self.CONST.ot_BCH_INFO:
    if not self.CONST.tag_BCH_METHOD in in_datum.keys():
      return
    if not self.CONST.tag_BCH_PUBKEY in in_datum.keys():
      return
    my_method = in_datum[self.CONST.tag_BCH_METHOD]
    if my_method != self.mid_method and DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    my_public_key = in_datum[self.CONST.tag_BCH_PUBKEY]
    if not isinstance(my_public_key, str):
      return
    self.irciot_blockchain_update_foreign_key_( \
      in_vuid, my_public_key)
  elif in_ot == self.CONST.ot_BCH_REQUEST:
    # preparing answer to blockchain public key request
    # will be here
    pass
  elif in_ot == self.CONST.ot_BCH_ACK:
    pass
  #
  # End of irciot_check_datum_()

 def irciot_deinencap_object_(self, in_object, orig_json, \
  in_vuid = None):
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
       if in_vuid != None:
         self.irciot_check_datum_(iot_datum, in_vuid, iot_ot)
       str_datum = self.irciot_prepare_datum_(iot_datum, \
         (iot_dt, iot_ot, iot_src, iot_dst, iot_dc, iot_dp), orig_json)
       if (str_datum != ""):
         if (str_datums != ""):
           str_datums += ","
         str_datums += str_datum
     return str_datums
  if isinstance(iot_datums, dict):
     if in_vuid != None:
       self.irciot_check_datum_(iot_datums, in_vuid, iot_ot)
     return self.irciot_prepare_datum_(iot_datums, \
      (iot_dt, iot_ot, iot_src, iot_dst, iot_dc, iot_dp), orig_json)
  return ""
  #
  # End of irciot_deinencap_object_()

 def irciot_check_container_(self, in_container, \
   orig_json = None, in_vuid = None):
  if not isinstance(orig_json, str):
    return False
  if not isinstance(in_container, dict):
    return False
  if self.integrity_check:
    # Lite optional checks will be here
    pass
  if in_vuid == None:
    # or not CAN_mid_blockchain?
    return True
  try:
    my_mid = in_container[self.CONST.tag_MESSAGE_ID]
  except:
    return False
  if len(my_mid) < 2:
    self.irciot_blockchain_update_last_mid_(in_vuid, my_mid)
    return True
  my_mid_method = my_mid[:2]
  if my_mid_method != self.CONST.tag_mid_ED25519 and \
     my_mid_method != self.CONST.tag_mid_RSA1024:
    self.irciot_blockchain_update_last_mid_(in_vuid, my_mid)
    return True
  my_bkey = self.irciot_blockchain_get_foreign_key_(in_vuid)
  if my_bkey == None:
    # We trust the message signed by the blockchain without
    # any verification if we do not yet have a public key.
    # It is useful in order to accept a key for this user.
    return True
  if my_mid_method == self.CONST.tag_mid_ED25519:
    try:
      # For performance optimization the public key may be
      # moved to Virtual User Database instead of string form
      my_verify_key = self.crypt_NACS.VerifyKey(my_bkey, \
        encoder = self.crypt_NACE.HexEncoder )
    except: # Incorrect Public Key
      return False
  elif my_mid_method == self.CONST.tag_mid_RSA1024:
    # Not implemented yet
    return False
  my_oldmid = self.irciot_blockchain_get_last_mid_(in_vuid)
  if my_oldmid == None:
    self.irciot_blockchain_update_last_mid_(in_vuid, my_mid)
    return True
  my_message = orig_json.replace( \
    '"' + self.CONST.tag_MESSAGE_ID + '":"' + my_mid + '"', \
    '"' + self.CONST.tag_MESSAGE_ID + '":"' + my_oldmid + '"')
  my_result = self.irciot_blockchain_verify_string_( \
    my_message, my_mid, my_verify_key)
  if my_result:
    # print("\033[1;45m BLOCKCHAIN VERIFICATION OK \033[0m")
    self.irciot_blockchain_update_last_mid_(in_vuid, my_mid)
  return my_result
  #
  # End of irciot_check_container_()

 def irciot_deinencap_container_(self, in_container, \
   orig_json = None, in_vuid = None):
  try:
     iot_objects = in_container[self.CONST.tag_OBJECT]
  except:
     return ""
  if not self.irciot_check_container_(in_container, \
   orig_json, in_vuid):
    return ""
  if isinstance(iot_objects, list):
    str_datums = ""
    for iot_object in iot_objects:
       str_datum = self.irciot_deinencap_object_(iot_object, \
         orig_json, in_vuid)
       if (str_datum != ""):
          if (str_datums != ""):
             str_datums += ","
          str_datums += str_datum
    #if (str_datums != ""):
    #   str_datums = "[" + str_datums + "]"
    return str_datums
  if isinstance(iot_objects, dict):
    return self.irciot_deinencap_object_(iot_objects, \
      orig_json, in_vuid)
    if (str_datums != ""):
       str_datums = "[" + str_datums + "]"
    return str_datums
  return ""
  #
  # End of irciot_deinencap_container_()

 def irciot_deinencap_(self, in_json, in_vuid = None):
  ''' First/simple implementation of IRC-IoT "Datum" deinencapsulator '''
  self.irciot_blockchain_check_publication_()
  try:
     iot_containers = json.loads(in_json)
  except ValueError:
     return ""
  if isinstance(iot_containers, list):
    str_datums = "["
    for iot_container in iot_containers:
       str_datum = self.irciot_deinencap_container_(iot_container, \
         in_json, in_vuid)
       # To check the blockchain id of each message, it is necessary
       # to cut the messages into separate substrings, exactly as they
       # came in, but not reassemble it by json.loads() and dumps()
       if (str_datum != ""):
          if (str_datums != "["):
             str_datums += ","
          str_datums += str_datum
    return str_datums + "]"
  if isinstance(iot_containers, dict):
    return self.irciot_deinencap_container_(iot_containers, \
      in_json, in_vuid)
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
  elif self.mid_method in [ \
       self.CONST.tag_mid_ED25519, \
       self.CONST.tag_mid_RSA1024 ]:
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
  my_base = self.irciot_crypto_get_base_(self.crypt_method)
  my_algo = self.irciot_crypto_get_algorithm_(self.crypt_method)
  my_compress = self.irciot_crypto_get_base_(self.crypt_method)
  if self.crypt_method in [ \
     self.CONST.tag_ENC_B64_ZLIB, \
     self.CONST.tag_ENC_B85_ZLIB, \
     self.CONST.tag_ENC_B64Z_RSA, \
     self.CONST.tag_ENC_B85Z_RSA ]:
     bin_big_datum  = zlib.compress(bytes(str_big_datum, 'utf-8'))
     if my_algo == self.CONST.crypto_RSA:
       crypt_big_datum = self.irciot_crypto_RSA_encrypt_( \
         bin_big_datum, self.encryption_public_key )
       if crypt_big_datum == None:
         return ("", 0)
       bin_big_datum = crypt_big_datum
     elif my_algo == self.CONST.crypto_AES:
       pass
     elif my_algo == self.CONST.crypto_2FISH:
       pass
     if my_base == self.CONST.base_BASE64:
       base_big_datum = base64.b64encode(bin_big_datum)
     elif my_base == self.CONST.base_BASE85:
       base_big_datum = base64.b85encode(bin_big_datum)
     elif my_base == self.CONST.base_BASE32:
       base_big_datum = base32.b32encode(bin_big_datum)
     del bin_big_datum
  else:
     bin_big_datum = bytes(str_big_datum, 'utf-8')
     if my_algo == self.CONST.crypto_RSA:
       crypt_big_datum = self.irciot_crypto_RSA_encrypt_( \
         bin_big_datum, self.encryption_public_key )
       if crypt_big_datum == None:
         return ("", 0)
       bin_big_datum = crypt_big_datum
       del crypt_big_datum
     if my_base == self.CONST.base_BASE64:
       base_big_datum = base64.b64encode(bin_big_datum)
     elif my_base == self.CONST.base_BASE85:
       base_big_datum = base64.b85encode(bin_big_datum)
     del bin_big_datum
  raw_big_datum  = str(base_big_datum)[2:-1]
  del base_big_datum
  my_bc = len(raw_big_datum)
  out_big_datum  = '{"' + self.CONST.tag_ENC_DATUM
  out_big_datum += '":"' + raw_big_datum + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum)
  self.current_mid = save_mid # mid rollback
  out_skip  = len(my_irciot)
  out_head  = len(big_ot)
  if self.mid_method == self.CONST.tag_mid_ED25519 \
  or self.mid_method == self.CONST.tag_mid_RSA1024:
    out_head += self.mid_hash_length
  else:
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
  self.irciot_blockchain_check_publication_()
  result = self.output_pool
  self.output_pool = []
  if (isinstance(in_datumset, dict)):
    in_datumset = [ in_datumset ]
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
  self.irciot_blockchain_check_publication_()
  #my_encrypt = CAN_encrypt_datum and DO_always_encrypt
  my_encrypt = False
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
  if (len(my_irciot) > self.message_mtu) or my_encrypt:
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
     if my_encrypt:
        one_datum = 1
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
    if CAN_encrypt_datum and my_datums_part == 0:
      self.crypt_cache = None
  return my_irciot, my_skip + my_datums_skip, my_datums_part
  #
  # End of irciot_encap_()

