'''
'' PyIRCIoT (PyLayerIRCIoT class)
''
'' Copyright (c) 2018-2021 Alexey Y. Woronov
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
CAN_mid_blockchain = False # Creating a chain of cryptographic signatures
CAN_encrypt_datum  = False # Ability to encrypt and decrypt of "Datums"
CAN_compress_datum = True  # Ability to compress and decompress "Datums"
#
DO_always_encrypt  = False # Always encrypt "Datums" in IRC-IoT messages
DO_auto_encryption = False # Automatic loading of modules for encryption
DO_auto_blockchain = False # Automatic loading of modules for Block Chain
DO_auto_compress   = False # Automatic loading of modules for compression
DO_debug_library   = False # Issuing debug messages to console and other

import json
import random
import base64
import datetime
try:
 import json
except:
 import simplejson as json

from ctypes import c_ushort

if DO_debug_library:
 from pprint import pprint

class PyLayerIRCIoT(object):

 class CONST(object):
  #
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.235'
  #
  # IRC-IoT characters
  #
  irciot_chars_lower = "abcdefghijklmnopqrstuvwxyz"
  irciot_chars_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  irciot_chars_digit = "0123456789"
  irciot_chars_cell_addon = "-_."
  irciot_chars_base_addon = "/\+-"
  irciot_chars_lhex_addon = "abcdef"
  irciot_chars_cell_addr  = \
    irciot_chars_lower + irciot_chars_upper + \
    irciot_chars_digit + irciot_chars_cell_addon
  irciot_chars_lhex = irciot_chars_digit + \
    irciot_chars_lhex_addon
  irciot_chars_base = irciot_chars_digit + \
    irciot_chars_lower + irciot_chars_upper + \
    irciot_chars_base_addon
  #
  irciot_default_encoding = "utf-8"
  #
  irciot_default_language = "en"
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
  tag_VERSION     = 'ver' # IRC-IoT Protocol Version
  tag_RETRY_LOST  = 'lst' # Request to resend LoST data
  tag_LIVES_COUNT = 'ttl' # Time-To-Live counter
  tag_ENC_DATUM   = 'ed'  # Encrypted Datum
  #
  # Special TAGs, not reserved for "Object" level
  # Will be replaced by "Dictionaries" mechanism:
  #
  tag_ERROR_CODE  = 'ec'  # Error code
  tag_DESCRIPTION = 'dsc' # Description (e.g. error)
  tag_ENC_METHOD  = 'em'  # Encryption Method
  tag_ENC_PUBKEY  = 'ek'  # Encryption Public Key
  tag_BCH_METHOD  = 'bm'  # Blockchain Method
  tag_BCH_PUBKEY  = 'bk'  # Blockchain Public Key
  #
  # Container Integrity Checks:
  #
  tag_CHK_CRC16   = 'c1'
  tag_CHK_CRC32   = 'c2'
  #
  # Only Basecoding methods:
  #
  tag_ENC_BASE32    = 'b32p'
  tag_ENC_BASE64    = 'b64p'
  tag_ENC_BASE85    = 'b85p'
  tag_ENC_BASE122   = 'b122'
  #
  # Basecoding + Compression:
  #
  tag_ENC_B32_ZLIB  = 'b32z'
  tag_ENC_B64_ZLIB  = 'b64z'
  tag_ENC_B85_ZLIB  = 'b85z'
  tag_ENC_B32_BZIP2 = 'b32b'
  tag_ENC_B64_BZIP2 = 'b64b'
  tag_ENC_B85_BZIP2 = 'b85b'
  #
  # Basecoding + Encryption:
  #
  tag_ENC_B64_RSA   = 'b64r'
  tag_ENC_B85_RSA   = 'b85r'
  tag_ENC_B64_2FISH = 'b64f'
  tag_ENC_B85_2FISH = 'b85f'
  tag_ENC_B64_AES   = 'b64a'
  tag_ENC_B85_AES   = 'b85a'
  tag_ENC_B64_USER  = 'b64u'
  tag_ENC_B85_USER  = 'b85u'
  #
  # Basecoding + Two Stage Encryption:
  #
  tag_ENC_B64_RSA_AES   = '6ra'
  tag_ENC_B85_RSA_AES   = '8ra'
  tag_ENC_B64_RSA_2FISH = '6rf'
  tag_ENC_B85_RSA_2FISH = '8rf'
  #
  # Basecoding + Encryption + Compression:
  #
  tag_ENC_B64Z_RSA  = 'b64Z'
  tag_ENC_B85Z_RSA  = 'b85Z'
  tag_ENC_B64Z_AES  = 'b64A'
  tag_ENC_B85Z_AES  = 'b85A'
  tag_ENC_B64Z_2FISH = 'b64F'
  tag_ENC_B85Z_2FISH = 'b85F'
  tag_ENC_B64Z_USER = 'b64U'
  tag_ENC_B85Z_USER = 'b85U'
  #
  # Basecoding + Two Stage Encryption + Compression:
  #
  tag_ENC_B64Z_RSA_AES   = '6raz'
  tag_ENC_B85Z_RSA_AES   = '8raz'
  tag_ENC_B64Z_RSA_2FISH = '6rfz'
  tag_ENC_B85Z_RSA_2FISH = '8rfz'
  #
  tag_ALL_BASE32_ENC = [
    tag_ENC_BASE32,
    tag_ENC_B32_ZLIB,
    tag_ENC_B32_BZIP2 ]
  #
  tag_ALL_BASE64_ENC = [
    tag_ENC_BASE64,
    tag_ENC_B64_AES,
    tag_ENC_B64Z_AES,
    tag_ENC_B64_ZLIB,
    tag_ENC_B64_BZIP2,
    tag_ENC_B64_RSA,
    tag_ENC_B64Z_RSA,
    tag_ENC_B64_2FISH,
    tag_ENC_B64Z_2FISH,
    tag_ENC_B64_RSA_AES,
    tag_ENC_B64Z_RSA_AES,
    tag_ENC_B64_RSA_2FISH,
    tag_ENC_B64Z_RSA_2FISH ]
  #
  tag_ALL_BASE85_ENC = [
    tag_ENC_BASE85,
    tag_ENC_B85_AES,
    tag_ENC_B85Z_AES,
    tag_ENC_B85_ZLIB,
    tag_ENC_B85_BZIP2,
    tag_ENC_B85_RSA,
    tag_ENC_B85Z_RSA,
    tag_ENC_B85_2FISH,
    tag_ENC_B85Z_2FISH,
    tag_ENC_B85_RSA_AES,
    tag_ENC_B85Z_RSA_AES,
    tag_ENC_B85_RSA_2FISH,
    tag_ENC_B85Z_RSA_2FISH ]
  #
  tag_ALL_BASE122_ENC = [
    tag_ENC_BASE122 ]
  #
  tag_ALL_nocompress_ENC = [
    tag_ENC_BASE32,
    tag_ENC_BASE64,
    tag_ENC_BASE85,
    tag_ENC_BASE122,
    tag_ENC_B64_RSA,
    tag_ENC_B85_RSA,
    tag_ENC_B64_AES,
    tag_ENC_B85_AES,
    tag_ENC_B64_2FISH,
    tag_ENC_B85_2FISH,
    tag_ENC_B64_RSA_AES,
    tag_ENC_B85_RSA_AES,
    tag_ENC_B64_RSA_2FISH,
    tag_ENC_B85_RSA_2FISH ]
  #
  tag_ALL_ZLIB_ENC = [
    tag_ENC_B64_ZLIB,
    tag_ENC_B85_ZLIB,
    tag_ENC_B64Z_RSA,
    tag_ENC_B85Z_RSA,
    tag_ENC_B64Z_AES,
    tag_ENC_B85Z_AES,
    tag_ENC_B64Z_2FISH,
    tag_ENC_B85Z_2FISH,
    tag_ENC_B64Z_RSA_AES,
    tag_ENC_B85Z_RSA_AES,
    tag_ENC_B64Z_RSA_2FISH,
    tag_ENC_B85Z_RSA_2FISH ]
  #
  tag_ALL_BZIP2_ENC = [
    tag_ENC_B32_BZIP2,
    tag_ENC_B64_BZIP2,
    tag_ENC_B85_BZIP2 ]
  #
  tag_ALL_RSA_ENC = [
    tag_ENC_B64_RSA,
    tag_ENC_B85_RSA,
    tag_ENC_B64Z_RSA,
    tag_ENC_B85Z_RSA,
    tag_ENC_B64_RSA_AES,
    tag_ENC_B85_RSA_AES,
    tag_ENC_B64Z_RSA_AES,
    tag_ENC_B85Z_RSA_AES,
    tag_ENC_B64_RSA_2FISH,
    tag_ENC_B85_RSA_2FISH,
    tag_ENC_B64Z_RSA_2FISH,
    tag_ENC_B85Z_RSA_2FISH ]
  #
  tag_ALL_AES_ENC = [
    tag_ENC_B64_AES,
    tag_ENC_B85_AES,
    tag_ENC_B64Z_AES,
    tag_ENC_B85Z_AES,
    tag_ENC_B64_RSA_AES,
    tag_ENC_B85_RSA_AES,
    tag_ENC_B64Z_RSA_AES,
    tag_ENC_B85Z_RSA_AES ]
  #
  tag_ALL_2FISH_ENC = [
    tag_ENC_B64_2FISH,
    tag_ENC_B85_2FISH,
    tag_ENC_B64Z_2FISH,
    tag_ENC_B85Z_2FISH,
    tag_ENC_B64_RSA_2FISH,
    tag_ENC_B85_RSA_2FISH,
    tag_ENC_B64Z_RSA_2FISH,
    tag_ENC_B85Z_RSA_2FISH ]
  #
  tag_ALL_nocrypt_ENC = [
    tag_ENC_BASE32,
    tag_ENC_BASE64,
    tag_ENC_BASE85,
    tag_ENC_BASE122,
    tag_ENC_B32_ZLIB,
    tag_ENC_B64_ZLIB,
    tag_ENC_B85_ZLIB,
    tag_ENC_B32_BZIP2,
    tag_ENC_B64_BZIP2,
    tag_ENC_B85_BZIP2 ]
  #
  tag_ALL_two_stage_ENC = [
    tag_ENC_B64_RSA_AES,
    tag_ENC_B85_RSA_AES,
    tag_ENC_B64_RSA_2FISH,
    tag_ENC_B85_RSA_2FISH,
    tag_ENC_B64Z_RSA_AES,
    tag_ENC_B85Z_RSA_AES,
    tag_ENC_B64Z_RSA_2FISH,
    tag_ENC_B85Z_RSA_2FISH ]
  #
  # Blockchain signing methods:
  #
  tag_mid_ED25519   = 'ed' # RFC 8032
  tag_mid_RSA1024   = 'rA'
  tag_mid_GOST12    = 'gT' # RFC 7091 (GOST 34.10-2012)
  # ID of signing-algorithm that was added by User:
  tag_mid_USERSIGN  = 'us'
  #
  mid_ED25519_hash_length = 88
  mid_RSA1024_hash_length = 173
  mid_GOST12_hash_length  = 173
  #
  # Conditional defaults:
  #
  if CAN_compress_datum:
    if CAN_encrypt_datum:
      tag_ENC_default = tag_ENC_B85Z_RSA
    else:
      tag_ENC_default = tag_ENC_B85_ZLIB
  else:
    if CAN_encrypt_datum:
      tag_ENC_default = tag_ENC_B85_RSA
    else:
      tag_ENC_default = tag_ENC_BASE85
  #
  if CAN_mid_blockchain:
    tag_mid_default = tag_mid_ED25519
    # Simple IRC-IoT blockchain signing by ED25519
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
  crypto_GOST12_curve = "id-tc26-gost-3410-12-512-paramSetA"
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
  crypto_ALL_asymmetric  = [ crypto_RSA ]
  crypto_ALL_symmetric   = []
  crypto_ALL_private_key = [ crypto_AES, crypto_2FISH ]
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
  ot_ERROR       = "err"    # General errors
  #
  api_GET_LMID = 101 # Get Last Message ID
  api_SET_LMID = 102 # Set Last Message ID
  api_GET_OMID = 111 # Get Own last Message ID
  api_SET_OMID = 112 # Set Own last Message ID
  api_GET_EKEY = 301 # Get Encryption Key
  api_SET_EKEY = 302 # Set Encryption Key
  api_GET_EKTO = 351 # Get Encryption Key Timeout
  api_SET_EKTO = 352 # Set Encryption Key Timeout
  api_GET_BKEY = 501 # Get Blockchain Key
  api_SET_BKEY = 502 # Set Blockchain Key
  api_GET_BKTO = 551 # Get Blockchain Key Timeout
  api_SET_BKTO = 552 # Set Blockchain Key Timeout
  api_GET_iMTU = 600 # Get initial Maximum Transmission Unit
  api_GET_iENC = 601 # Get initial Encoding
  api_GET_VUID = 700 # Get list of Virtual User IDs
  #
  api_vuid_cfg = 'c' # VUID prefix for users from config
  api_vuid_tmp = 't' # VUID prefix for temporal users
  api_vuid_srv = 's' # VUID prefix for IRC-IoT Services
  api_vuid_all = '*' # Means All users VUIDs when sending messages
  #
  api_vuid_self = 'c0' # Default preconfigured VUID
  #
  # Basic IRC-IoT Services
  #
  api_vuid_CRS = 'sC' # Cryptographic Repository Service
  api_vuid_GDS = 'sD' # Global Dictionary Service
  api_vuid_GRS = 'sR' # Global Resolving Service
  api_vuid_GTS = 'sT' # Global Time Service
  #
  api_vuid_PRS = 'sr' # Primary Routing Service
  #
  # IRC-IoT Base Types
  #
  type_UNDEFINED =  0
  type_NUMERIC   = 10
  type_FLOAT     = 11
  type_STRING    = 12
  type_TEXT      = 13
  type_OBJECT    = 14 # Link to other objects
  type_BINARY    = 15 # Binary data block
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
  ldict_ITEM_ID      = "item_id"
  ldict_ITEM_OT      = "item_ot"
  ldict_ITEM_NAME    = "item_name"
  ldict_ITEM_PARENT  = "parent_item_id"
  ldict_ITEM_TYPEID  = "type_id"
  ldict_ITEM_TYPEPR  = "type_parameters"
  ldict_ITEM_DEFVAL  = "default_value"
  ldict_ITEM_CHILD   = "child_object_id"
  ldict_ITEM_METHOD  = "method"
  ldict_ITEM_LANG    = "method_language"
  ldict_ITEM_SECTS   = "sections"
  #
  ldict_TYPE_ID      = "type_id"
  ldict_TYPE_NAME    = "type_name"
  ldict_TYPE_TYPE    = "type_of_type"
  ldict_TYPE_ARR     = "is_it_array"
  ldict_TYPE_DYNSIZE = "is_variable_dynamically_sized"
  ldict_TYPE_DYNARR  = "is_array_dynamically_sized"
  ldict_TYPE_ARRSIZE = "size_of_array"
  ldict_TYPE_SIZE    = "size"
  ldict_TYPE_MIN     = "interval_minimum"
  ldict_TYPE_MAX     = "interval_maximum"
  ldict_TYPE_PRECIS  = "precision"
  ldict_TYPE_EXPSIZE = "exponent"
  ldict_TYPE_ENDIAN  = "endianness"
  ldict_TYPE_ENCODE  = "encoding"
  #
  ldict_SECT_ID      = "section_id"
  ldict_SECT_ITEMS   = "items_ids"
  ldict_SECT_CHECKS  = "checking_values"
  ldict_SECT_METHOD  = "method"
  ldict_SECT_LANG    = "method_language"
  #
  # IRC-IoT Errors
  #
  err_PROTO_VER_MISMATCH = 101
  err_LIB_VER_MISMATCH   = 102
  err_DEFRAG_INVALID_DID = 103
  err_CONTENT_MISSMATCH  = 104
  err_DEFRAG_OP_MISSING  = 111
  err_DEFRAG_DP_MISSING  = 112
  err_DEFRAG_BP_MISSING  = 113
  err_DEFRAG_OC_EXCEEDED = 121
  err_DEFRAG_DC_EXCEEDED = 122
  err_DEFRAG_BC_EXCEEDED = 123
  err_OVERLAP_MISSMATCH  = 131
  err_DEFRAG_MISSMATCH   = 133
  err_BASE64_DECODING    = 251
  err_BASE32_DECODING    = 252
  err_BASE85_DECODING    = 253
  err_BASE122_DECODING   = 254
  err_ENC_UNIMPLEMENTED  = 300
  err_COMP_ZLIB_HEADER   = 301
  err_COMP_ZLIB_INCOMP   = 303
  err_RSA_KEY_FORMAT     = 351
  err_INVALID_MESSAGE    = 501
  err_INVALID_ADDRESS    = 503
  err_LDICT_VERIFY_OK    = 811
  err_LDICT_VERIFY_FAIL  = 812
  #
  err_LOAD_ZLIB_MODULE   = 701
  err_LOAD_BZIP2_MODULE  = 702
  err_LOAD_RSA_MODULE    = 731
  err_LOAD_AES_MODULE    = 732
  err_LOAD_2FISH_MODULE  = 733
  err_LOAD_GOST_MODULE   = 735
  err_LOAD_GOSTD_MODULE  = 737
  err_LOAD_USER_SIGN     = 755
  err_LOAD_USER_CRYPT    = 777
  #
  err_DESCRIPTIONS = {
   err_PROTO_VER_MISMATCH : "Protocol version mismatch",
   err_LIB_VER_MISMATCH   : "Library version mismatch",
   err_BASE64_DECODING    : "BASE64 decoding problem",
   err_BASE85_DECODING    : "BASE85 decoding problem",
   err_BASE32_DECODING    : "BASE32 decoding problem",
   err_BASE122_DECODING   : "BASE122 decoding problem",
   err_ENC_UNIMPLEMENTED  : "This encryption is not implemented",
   err_DEFRAG_INVALID_DID : "Invalid 'dp' when defragmenting",
   err_CONTENT_MISSMATCH  : "Content missmatch",
   err_DEFRAG_OP_MISSING  : "No tag 'op' when defragmenting",
   err_DEFRAG_DP_MISSING  : "No tag 'dp' when defragmenting",
   err_DEFRAG_BP_MISSING  : "No tag 'bp' when defragmenting",
   err_DEFRAG_OC_EXCEEDED : "Exceeded 'oc' field value",
   err_DEFRAG_DC_EXCEEDED : "Exceeded 'dc' field value",
   err_DEFRAG_BC_EXCEEDED : "Exceeded 'bc' field value",
   err_OVERLAP_MISSMATCH  : "Overlapping fragments missmatch",
   err_DEFRAG_MISSMATCH   : "Defragmentation content missmatch",
   err_INVALID_MESSAGE    : "Invalid IRC-IoT message format",
   err_INVALID_ADDRESS    : "Invalid IRC-IoT address format",
   err_COMP_ZLIB_HEADER   : "Invalid Zlib header",
   err_COMP_ZLIB_INCOMP   : "Zlib incomplete block",
   err_RSA_KEY_FORMAT     : "Invalid RSA Key format",
   err_LOAD_ZLIB_MODULE   : "Loading Zlib module",
   err_LOAD_BZIP2_MODULE  : "Loading BZIP2 module",
   err_LOAD_RSA_MODULE    : "Loading RSA module",
   err_LOAD_AES_MODULE    : "Loading AES module",
   err_LOAD_2FISH_MODULE  : "Loading Twofish module",
   err_LOAD_GOST_MODULE   : "Loading GOST3410 module",
   err_LOAD_GOSTD_MODULE  : "Loading GOST3411 module",
   err_LOAD_USER_SIGN     : "Loading UserSign module",
   err_LOAD_USER_CRYPT    : "Loading UserCrypt module",
   err_LDICT_VERIFY_OK    : "Local Dictionary verification OK",
   err_LDICT_VERIFY_FAIL  : "Local Dictionary verification failed"
  }
  #
  pattern = chr(0) # or "@", chr(255)
  #
  # Default Maximum IRC message size (in bytes)
  #
  irciot_default_MTU = 440 # Undernet IRCd at 2019
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
  BCHT = 86400
  # ENCryption key publication Timeout (in seconds)
  ENCT = 86400
  #
  mod_ZLIB  = 'zlib'
  mod_BZIP2 = 'bz2'
  mod_RSA   = 'Crypto.PublicKey.RSA'
  mod_AES   = 'Crypto.Cipher.AES'
  mod_OAEP  = 'Crypto.Cipher.PKCS1_OAEP'
  mod_PKCS  = 'Crypto.Signature.PKCS1_v1_5'
  mod_SHA   = 'Crypto.Hash.SHA'
  mod_NACE  = 'nacl.encoding'
  mod_NACS  = 'nacl.signing'
  mod_2FISH = 'twofish'
  mod_HASH  = 'hashlib'
  mod_GOST  = 'pygost.gost3410'
  mod_GOSTD = 'pygost.gost34112012256'
  #
  mod_USERSIGN  = 'irciot-usersign'
  mod_USERCRYPT = 'irciot-usercrypt'
  #
  err_LOAD_modules = {
   mod_ZLIB : err_LOAD_ZLIB_MODULE,
   mod_BZIP2 : err_LOAD_BZIP2_MODULE,
   mod_RSA : err_LOAD_RSA_MODULE,
   mod_AES : err_LOAD_AES_MODULE,
   mod_2FISH : err_LOAD_2FISH_MODULE,
   mod_GOST : err_LOAD_GOST_MODULE,
   mod_GOSTD : err_LOAD_GOSTD_MODULE,
   mod_USERSIGN : err_LOAD_USER_SIGN,
   mod_USERCRYPT : err_LOAD_USER_CRYPT
  }
  #
  # This timeout for automatic unloading of modules
  # when they where automatically loaded (in seconds)
  mod_uload_timeout = 1800
  #
  crc16_poly = 0xA001
  # crc16_reversed = False
  # 0xA001 -- x^16 + x^15 + x^2 + 1 (CRC-16-IBM)
  # 0xC002 -- x^16 + x^14 + x   + 1 (CRC-16-IBM reversed)
  # 0x8408 -- x^16 + x^12 + x^5 + 1 (CRC-16-CCITT) SDLC/HDLC
  # 0x8810 -- x^16 + x^11 + x^4 + 1 (CRC-16-CCITT reversed)
  # 0x8000 -- x^16 + 1 (LRCC-16)
  # 0x8005
  #
  virtual_mid_pipeline_size = 16
  #
  default_integrity_check = 0
  default_integrity_stamp = 0
  #
  # 0 is No Integrity Check
  # 1 is CRC16 Check "c1": +12 bytes
  # 2 is CRC32 Check "c2": +16 bytes
  #
  def __setattr__(self, *_):
    pass

 def __init__(self):
  #
  self.CONST = self.CONST()
  #
  self.current_mid = '0' # Message ID
  self.current_oid =  0  # Object ID
  self.current_did =  0  # Datum ID
  #
  self.defrag_pool = []
  self.__defrag_lock = False
  #
  self.output_pool = []
  self.__output_lock = False
  #
  self.virtual_lmid = [] # Virtual Last Message IDs pipeline
  self.virtual_omid = [] # Virtual Own Message IDs pipeline
  #
  self.__encoding = self.CONST.irciot_default_encoding
  #
  self.lang  = self.CONST.irciot_default_language
  #
  self.ldict = []
  self.ldict_types = []
  self.ldict_sections = []
  self.ldict_file  = None
  self.__ldict_lock = False
  #
  self.__mid_method = self.CONST.tag_mid_default
  self.__oid_method = 0
  self.__did_method = 0
  #
  self.__crypt_HASH = None
  self.__crypt_RSA  = None
  self.__crypt_SHA1 = None
  self.__crypt_S256 = None
  self.__crypt_RIPE = None
  self.__crypt_PKCS = None
  self.__crypt_OAEP = None
  self.__crypt_AES  = None
  self.__crypt_FISH = None
  self.__crypt_NACS = None
  self.__crypt_NACE = None
  self.__crypt_GOST = None
  self.__crypt_GSTD = None
  # Compression modules
  self.__crypt_ZLIB = None
  self.__crypt_BZ2  = None
  #
  self.crypt_method = self.CONST.tag_ENC_default
  self.crypt_model \
    = self.irciot_crypto_get_model_(self.crypt_method)
  self.crypt_algo \
    = self.irciot_crypto_get_algorithm_(self.crypt_method)
  self.crypt_base \
    = self.irciot_crypto_get_base_(self.crypt_method)
  self.crypt_compress \
    = self.irciot_crypto_get_compress_(self.crypt_method)
  #
  if CAN_encrypt_datum:
    if self.crypt_algo != None:
      self.irciot_load_encryption_methods_(self.crypt_method)
  #
  if CAN_compress_datum:
    if self.crypt_compress != self.CONST.compress_NONE:
      self.irciot_load_compression_methods_(self.crypt_method)
  #
  self.__crypt_cache = None
  #
  # 0 is autoincrement
  #
  random.seed()
  #
  self.__blockchain_private_key = None
  self.__blockchain_public_key = None
  self.__blockchain_key_published = 0
  #
  self.__encryption_private_key = None
  self.__encryption_public_key = None
  self.__encryption_key_published = 0
  #
  if self.__mid_method == "":
    self.current_mid = random.randint( 10000, 99999)
  elif self.__mid_method in [
       self.CONST.tag_mid_ED25519,
       self.CONST.tag_mid_RSA1024,
       self.CONST.tag_mid_GOST12 ]:
    self.irciot_load_blockchain_methods_(self.__mid_method)
    self.irciot_init_blockchain_method_(self.__mid_method)
  self.mid_hash_length \
   = self.irciot_get_blockchain_hash_length_(self.__mid_method)
  #
  if self.__oid_method == 0:
    self.current_oid = random.randint(  1000,  9999)
  #
  if self.__did_method == 0:
    self.current_did = random.randint(   100,   999)
  #
  self.irciot_init_encryption_method_(self.crypt_method)
  #
  self.__initial_MTU = None
  self.__message_MTU = self.CONST.irciot_default_MTU
  #
  self.integrity_check = self.CONST.default_integrity_check
  self.integrity_stamp = self.CONST.default_integrity_stamp
  #
  self.__crc16_table = []
  #
  self.errors = self.CONST.err_DESCRIPTIONS
  #
  self.irciot_set_locale_(self.lang)
  #
  self._error_handler_ = self.irciot_error_
  #
  # End of PyLayerIRCIoT.__init__()

 def irc_pointer (self, in_compatibility, in_messages_pack):
  # Warning: interface may be changed while developing
  return False

 def user_pointer (self, in_compatibility, in_action, in_vuid, in_params):
  # Warning: method parameters and API may be changed while developing
  # Below is Virtualization Mechanism for the Loopback MIDs Pipelines:
  if   in_action == self.CONST.api_SET_LMID:
    self.virtual_lmid.append(in_params)
    if len(self.virtual_lmid) \
     > self.CONST.virtual_mid_pipeline_size:
      del self.virtual_lmid[0]
  elif in_action == self.CONST.api_GET_LMID:
    return (True, self.virtual_lmid)
  elif in_action == self.CONST.api_SET_OMID:
    self.virtual_omid.append(in_params)
    if len(self.virtual_omid) \
     > self.CONST.virtual_mid_pipeline_size:
      del self.virtual_omid[0]
    return (True, None)
  elif in_action == self.CONST.api_GET_OMID:
    return (True, self.virtual_omid)
  elif in_action == self.CONST.api_GET_VUID:
    return (True, [ self.CONST.api_vuid_self ])
  elif in_action == self.CONST.api_GET_iMTU:
    return (False, None)
  elif in_action == self.CONST.api_GET_iENC:
    return (True, self.CONST.irciot_default_encoding)
  return (False, None)

 def irciot_error_(self, in_error_code, in_mid, \
    in_vuid = None, in_addon = None):
  # Warning: This version of error handler is made for
  # testing and does not comply with the specification
  my_message = ""
  my_datum = {}
  if in_error_code in self.errors.keys():
    my_descr = self.errors[in_error_code]
    if isinstance(in_addon, str):
      my_descr += " ({})".format(in_addon)
    my_datum.update({ self.CONST.tag_DESCRIPTION : my_descr })
  else:
    return
  my_datum[self.CONST.tag_OBJECT_TYPE] = self.CONST.ot_ERROR
  my_datum[self.CONST.tag_ERROR_CODE] = in_error_code
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  # Incomplete code
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  # The destination-address must be taken from
  # the source-address of the message that caused the problem
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  my_message = json.dumps(my_datum, separators=(',',':'))
  my_compat = self.irciot_compatibility_()
  my_pack = (my_message, in_vuid)
  if not self.irc_pointer (my_compat, my_pack):
    # Handler not inserted
    self.output_pool.append(my_pack)
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

 def irciot_check_mtu_(self):
  if isinstance(self.__initial_MTU, int):
    return
  my_status = False
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_iMTU, self.CONST.api_vuid_self, None)
  try:
    (my_status, my_answer) = my_result
  except:
    pass
  if my_status:
    if isinstance(my_answer, int):
      if my_answer > 128:
        self.__initial_MTU = my_answer
        self.__message_MTU = my_answer
        return
  self.__initial_MTU = self.CONST.irciot_default_MTU
  #
  # End of irciot_check_mtu_()

 def irciot_set_locale_(self, in_lang):
  if not isinstance(in_lang, str):
    return
  self.lang = in_lang
  try:
    from PyIRCIoT.irciot_errors \
    import irciot_get_common_error_descriptions_
    from PyIRCIoT.irciot_shared import irciot_shared_
  except:
    return
  my_desc = {}
  try:
    my_desc = irciot_get_common_error_descriptions_(in_lang)
    my_desc = irciot_shared_.validate_descriptions_(my_desc)
    if my_desc != {}:
      self.errors.update(my_desc)
  except:
    pass

 def irciot_check_encoding_(self):
  my_status = False
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_iENC, self.CONST.api_vuid_self, None)
  try:
    (my_status, my_answer) = my_result
  except:
    pass
  if my_status:
    if isinstance(my_answer, str):
      if my_answer != "":
        self.__encoding = my_answer
        return
  #
  # End of irciot_check_encoding_()

 def irciot_crc16_init_(self):
  for my_idx1 in range(0, 256):
    my_crc = c_ushort(my_idx1).value
    for my_idx2 in range(0, 8):
      my_tab = c_ushort(my_crc >> 1).value
      if (my_crc & 0x0001):
        my_crc = my_tab ^ self.CONST.crc16_poly
      else:
        my_crc = my_tab
    self.__crc16_table.append(hex(my_crc))
  #
  # End of irciot_crc16_init_()

 def irciot_crc32_init_(self):
  if self.__crypt_ZLIB == None:
    self.__crypt_ZLIB = self.import_( \
      self.__crypt_ZLIB, self.CONST.mod_ZLIB)
  #
  # End of irciot_crc32_init_()

 def irciot_crc16_(self, in_data):
  if not isinstance(in_data, bytes):
    return None
  try:
    my_crc = 0x0000
    for my_ch in in_data:
      my_rot = c_ushort(my_crc >> 8).value
      my_idx = ((my_crc ^ my_ch) & 0x00ff)
      my_tab = self.__crc16_table[my_idx]
      my_crc = my_rot ^ int(my_tab, 0)
    my_crc = my_crc.to_bytes(2,'little')
    return "%2.2x%2.2x" % (my_crc[1], my_crc[0])
  except:
    return None
  #
  # End of irciot_crc16_()

 def irciot_crc32_(self, in_data):
  if not isinstance(in_data, bytes):
    return None
  try:
    my_crc = self.__crypt_ZLIB.crc32(in_data) & 0xFFFFFFFF
    my_crc = my_crc.to_bytes(4,'little')
    my_out = ""
    for my_idx in range(3, -1, -1):
      my_out += "%2.2x" % my_crc[my_idx]
    return my_out
  except:
    return None
  #
  # End of irciot_crc32_()

 def irciot_init_encryption_method_(self, in_crypt_method):
  if in_crypt_method in self.CONST.tag_ALL_two_stage_ENC:
    self.irciot_error_(self.CONST.err_ENC_UNIMPLEMENTED, in_crypt_method)
    return False
  my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    self.crypto_RSA_KEY_SIZE = self.CONST.crypto_RSA_KEY_SIZE
  elif my_algo == self.CONST.crypto_AES:
    if self.__crypt_AES == None:
      return False
    self.crypto_AES_BLOCK_SIZE = self.__crypt_AES.block_size
    self.crypto_AES_iv = self.irciot_crypto_hasher_(None, \
    self.crypto_AES_BLOCK_SIZE )
  elif my_algo == self.CONST.crypto_2FISH:
    pass
  (self.__encryption_private_key, \
   self.__encryption_public_key) \
    = self.irciot_encryption_generate_keys_(in_crypt_method)
  if not isinstance(self.__encryption_private_key, object):
    return False
  return True
  #
  # End of irciot_init_encryption_method_()

 def __check_crypto_key_(self, in_key):
  if in_key is None: return False
  if not isinstance(in_key, object):
    return False
  return True

 def irciot_check_blockchain_private_key_(self, in_key):
  if not self.__check_crypto_key_(in_key):
    return False
  return True

 def irciot_check_blockchain_public_key_(self, in_key):
  if not self.__check_crypto_key_(in_key):
    return False
  return True

 def irciot_check_encryption_private_key_(self, in_key):
  if not self.__check_crypto_key_(in_key):
    return False
  return True

 def irciot_check_encryption_public_key_(self, in_key):
  if not self.__check_crypto_key_(in_key):
    return False
  return True

 def irciot_get_blockchain_private_key_(self):
  # It is need to exclude illegal access to the key
  return self.__blockchain_private_key

 def irciot_get_blockchain_public_key_(self):
  return self.__blockchain_public_key

 def irciot_get_encryption_private_key_(self):
  # It is need to exclude illegal access to the key
  return self.__encryption_private_key

 def irciot_get_encryption_public_key_(self):
  return self.__encryption_public_key

 def irciot_set_blockchain_private_key_(self, in_key):
  if not self.irciot_check_blockchain_private_key_(in_key):
    return False
  # It is need to exclude illegal replacement of the key
  self.__blockchain_private_key = in_key
  return True

 def irciot_set_blockchain_public_key_(self, in_key):
  if not self.irciot_check_blockchain_public_key_(in_key):
    return False
  self.__blockchain_public_key = in_key
  return True

 def irciot_set_encryption_private_key_(self, in_key):
  if not self.irciot_check_encryption_private_key_(in_key):
    return False
  # It is need to exclude illegal replacement of the key
  self.__encryption_private_key = in_key
  return True

 def irciot_set_encryption_public_key_(self, in_key):
  if not self.irciot_check_encryption_public_key_(in_key):
    return False
  self.__encryption_public_key = in_key
  return True

 def irciot_get_blockchain_hash_length_(self, in_mid_method):
  if in_mid_method == self.CONST.tag_mid_ED25519:
    return self.CONST.mid_ED25519_hash_length
  elif in_mid_method == self.CONST.tag_mid_RSA1024:
    return self.CONST.mid_RSA1024_hash_length
  elif in_mid_method == self.CONST.tag_mid_GOST12:
    return self.CONST.mid_GOST12_hash_length
  else:
    return len(str(self.current_mid))

 def irciot_init_blockchain_method_(self, in_mid_method):
  if not in_mid_method in [
    self.CONST.tag_mid_ED25519,
    self.CONST.tag_mid_RSA1024,
    self.CONST.tag_mid_GOST12 ]:
    return False
  (self.__blockchain_private_key, \
   self.__blockchain_public_key) \
    = self.irciot_blockchain_generate_keys_(in_mid_method)
  if not isinstance(self.__blockchain_private_key, object):
    return False
  self.current_mid \
    = self.irciot_blockchain_sign_string_( \
      str(self.current_mid), self.__blockchain_private_key)
  self.mid_hash_length \
    = self.irciot_get_blockchain_hash_length_(in_mid_method)
  return True
  #
  # End of irciot_init_blockchain_method_()
  
 def import_(self, in_pointer, in_module_name):
  if in_pointer == None:
    import importlib
    try:
      my_pointer = importlib.import_module(in_module_name)
    except ImportError:
      my_pointer = None
    if my_pointer == None:
      if in_module_name in self.CONST.err_LOAD_modules:
        self.irciot_error_(self.CONST.err_LOAD_modules[in_module_name], 0)
      return in_pointer
    return my_pointer
  else:
    return in_pointer
  #
  # End of import_()

 def irciot_load_blockchain_methods_(self, in_mid_method):
  if in_mid_method == self.CONST.tag_mid_ED25519:
    if self.__crypt_NACS != None and self.__crypt_NACE != None:
      return False
    if self.__crypt_NACS == None:
      self.__crypt_NACS = self.import_(self.__crypt_NACS, \
       self.CONST.mod_NACS)
    if self.__crypt_NACE == None:
      self.__crypt_NACE = self.import_(self.__crypt_NACE, \
        self.CONST.mod_NACE)
  elif in_mid_method == self.CONST.tag_mid_RSA1024:
    if self.__crypt_HASH != None and self.__crypt_RSA  != None and \
       self.__crypt_PKCS != None and self.__crypt_SHA1 != None:
      return False
    if self.__crypt_HASH == None:
      self.__crypt_HASH = self.import_(self.__crypt_HASH, \
       self.CONST.mod_HASH)
    if self.__crypt_RSA == None:
      self.__crypt_RSA  = self.import_( \
      self.__crypt_RSA, self.CONST.mod_RSA )
    if self.__crypt_PKCS == None:
      self.__crypt_PKCS = self.import_(self.__crypt_PKCS, \
       self.CONST.mod_PKCS)
    if self.__crypt_SHA1 == None:
      self.__crypt_SHA1 = self.import_(self.__crypt_SHA1, \
       self.CONST.mod_SHA)
  elif in_mid_method == self.CONST.tag_mid_GOST12:
    if self.__crypt_GSTD != None and self.__crypt_GOST != None:
      return False
    if self.__crypt_GOST == None:
      self.__crypt_GOST = self.import_(self.__crypt_GOST, \
        self.CONST.mod_GOST)
    if self.__crypt_GSTD == None:
      self.__crypt_GSTD = self.import_(self.__crypt_GSTD, \
       self.CONST.mod_GOSTD)
  if self.irciot_init_blockchain_method_(in_mid_method):
    return True
  return False
  #
  # End of irciot_load_blockchian_methods_()

 def irciot_load_encryption_methods_(self, in_crypt_method):
  if not isinstance(in_crypt_method, str):
    return False
  my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
  if my_algo == self.CONST.crypto_RSA:
    if self.__crypt_RSA  != None and \
       self.__crypt_OAEP != None and \
       self.__crypt_HASH != None:
      return False
    if self.__crypt_RSA == None:
      self.__crypt_RSA = self.import_( \
      self.__crypt_RSA, self.CONST.mod_RSA )
    if self.__crypt_OAEP == None:
      self.__crypt_OAEP = self.import_(self.__crypt_OAEP, \
       self.CONST.mod_OAEP)
    if self.__crypt_HASH == None:
      self.__crypt_HASH = self.import_(self.__crypt_HASH, \
       self.CONST.mod_HASH)
  elif my_algo == self.CONST.crypto_AES:
    if self.__crypt_AES != None:
      return False
    self.__crypt_AES = self.import_( \
    self.__crypt_AES, self.CONST.mod_AES )
  elif my_algo == self.CONST.crypto_2FISH:
    if self.__crypt_FISH != None:
      return False
    self.__crypt_FISH = self.import_( \
    self.__crypt_FISH, self.CONST.mod_2FISH )
  self.irciot_init_encryption_method_(in_crypt_method)
  return True
  #
  # End of irciot_load_encryption_methods_()

 def irciot_load_compression_methods_(self, in_crypt_method):
  if not isinstance(in_crypt_method, str):
    return False
  my_compress \
    = self.irciot_crypto_get_compress_(in_crypt_method)
  try:
    if my_compress == self.CONST.compress_ZLIB:
      if self.__crypt_ZLIB != None:
        return False
      self.__crypt_ZLIB = self.import_( \
      self.__crypt_ZLIB, self.CONST.mod_ZLIB)
    elif my_compress == self.CONST.compress_BZIP2:
      if self.__crypt_BZ2 != None:
        return False
      self.__crypt_BZ2 = self.import_( \
      self.__crypt_BZ2, self.CONST.mod_BZIP2)
    return False
  except:
    return False
  return True
  #
  # End of irciot_load_compression_methods_()

 def irciot_enable_blockchain_(self, in_mid_method):
  if not self.irciot_load_blockchain_methods_(in_mid_method):
    self.irciot_init_blockchain_method_(in_mid_method)
  self.__mid_method = in_mid_method
  self.__blockchain_key_published = 0
  #
  # End of irciot_enable_blockchain_()
  
 def irciot_enable_encryption_(self, in_crypt_method):
  self.irciot_load_encryption_methods_(in_crypt_method)
  self.irciot_load_compression_methods_(in_crypt_method)
  self.crypt_method = in_crypt_method
  self.crypt_model \
    = self.irciot_crypto_get_model_(in_crypt_method)
  self.crypt_algo \
    = self.irciot_crypto_get_algorithm_(in_crypt_method)
  self.crypt_base \
    = self.irciot_crypto_get_base_(in_crypt_method)
  self.crypt_compress \
    = self.irciot_crypto_get_compress_(in_crypt_method)
  if self.crypt_algo == self.CONST.crypt_ASYMMETRIC:
    self.__encryption_key_published = 0
  #
  # End of irciot_enable_encryption_()

 def irciot_disable_blockchain_(self):
  self.__mid_method = ""
  self.__blockchain_key_published = self.CONST.BCHT
  self.current_mid = random.randint( 10000, 99999)

 def irciot_disable_encryption_(self):
  self.crypt_method = ""
  self.__encryption_key_published = self.CONST.ENCT

 def irciot_crypto_hasher_(self, in_password, in_hash_size):
  if not isinstance(in_hash_size, int):
    return None
  if in_password in [ None, "" ] or \
   not (self.crypt_model != self.CONST.crypt_NO_ENCRYPTION \
     or self.__mid_method != ""):
    my_RHASH = ""
    my_ASCII = ''.join([chr(my_idx) \
      for my_idx in range(0, 127)])
    for my_i in range(0, in_hash_size):
      my_RHASH += random.choice(my_ASCII)
    return my_RHASH
  if not isinstance(in_password, str):
    return None
  my_hash = None
  my_password = in_password.encode(self.__encoding)
  if in_hash_size == 16:
    my_hash = self.__crypt_HASH.md5(my_password).digest()
  elif in_hash_size == 20:
    my_hash = self.__crypt_HASH.sha1(my_password).digest()
  elif in_hash_size == 28:
    my_hash = self.__crypt_HASH.sha224(my_password).digest()
  elif in_hash_size == 32:
    my_hash = self.__crypt_HASH.sha256(my_password).digest()
  elif in_hash_size == 48:
    my_hash = self.__crypt_HASH.sha384(my_password).digest()
  elif in_hash_size == 64:
    my_hash = self.__crypt_HASH.sha512(my_password).digest()
  elif in_hash_size == 160:
    my_hash = self.__crypt_HASH.ripemod160(my_password).digest()
  return my_hash
  #
  # End of irciot_crypto_hasher_()

 def irciot_crypto_hash_to_str_(self, in_hash):
  my_hash = in_hash
  if isinstance(in_hash, str):
    my_hash = bytes(in_hash, self.__encoding)
  if not isinstance(my_hash, bytes):
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
  if len(in_string) < 6:
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
      if self.__crypt_NACS == None:
        return (None, None)
      my_private_key \
        = self.__crypt_NACS.SigningKey.generate()
      my_public_key = my_private_key.verify_key
    elif in_mid_method == self.CONST.tag_mid_RSA1024:
      if self.__crypt_RSA == None:
        return (None, None)
      my_private_key = self.__crypt_RSA.generate(1024)
      my_public_key = my_private_key.publickey()
    elif in_mid_method == self.CONST.tag_mid_GOST12:
      if self.__crypt_GOST == None:
        return (None, None)
      my_curve = self.__crypt_GOST.CURVES[self.CONST.crypto_GOST12_curve]
      my_random = bytes(random.getrandbits(8) for my_idx in range(32))
      my_private_key = self.__crypt_GOST.prv_unmarshal(my_random)
      (my_int1, my_int2) = self.__crypt_GOST.public_key(my_curve, my_private_key)
      my_public_key = my_int1.to_bytes(64,'little') + my_int2.to_bytes(64,'little')
  except:
    my_private_key = None
    my_public_key = None
  return (my_private_key, my_public_key)
  #
  # End of irciot_blockchain_generate_keys_()

 def irciot_get_current_datetime_(self):
  return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

 # incomplete
 def irciot_blockchain_request_to_messages_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_BCH_REQUEST
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_BCH_METHOD] = self.__mid_method

  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  # Copy destination address from last message source address?!
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  return self.irciot_encap_all_(my_datum, in_vuid)
  #
  # End of irciot_blockchain_request_to_messages_()

 def irciot_encryption_request_to_messages_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return []
  my_datum = {}
  my_ot = self.CONST.ot_ENC_REQUEST
  my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_ENC_METHOD] = self.crypt_method
  # Incomplete code
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  # Copy destination address from last message source address?!
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  return self.irciot_encap_all_(my_datum, in_vuid)
  #
  # End of irciot_encryption_request_to_messages_()

 def irciot_blockchain_key_to_messages_(self, in_key_string, \
   in_ot, in_vuid = None):
  if not isinstance(in_key_string, str) or \
     not isinstance(in_ot, str):
    return []
  my_datum = {}
  my_datum[self.CONST.tag_OBJECT_TYPE] = in_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_BCH_METHOD] = self.__mid_method
  my_datum[self.CONST.tag_BCH_PUBKEY] = in_key_string
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  return self.irciot_encap_all_(my_datum, in_vuid)
  #
  # End of irciot_blockchain_key_to_messages_()

 def irciot_encryption_key_to_messages_(self, in_key_string, \
   in_ot, in_vuid = None):
  if not isinstance(in_key_string, str) or \
     not isinstance(in_ot, str):
    return []
  my_datum = {}
  my_datum[self.CONST.tag_OBJECT_TYPE] = in_ot
  my_datum[self.CONST.tag_DATUM_ID] = random.randint(100, 999)
  my_datum[self.CONST.tag_ENC_METHOD] = self.crypt_method
  my_datum[self.CONST.tag_ENC_PUBKEY] = in_key_string
  my_datum[self.CONST.tag_SRC_ADDR] = ""
  my_datum[self.CONST.tag_DST_ADDR] = ""
  my_datum[self.CONST.tag_DATE_TIME] \
    = self.irciot_get_current_datetime_()
  save_crypt_method = self.crypt_method
  self.crypt_method \
    = self.irciot_crypto_wo_encryption_(self.crypt_method)
  my_messages = self.irciot_encap_all_(my_datum, in_vuid)
  self.crypt_method = save_crypt_method
  return my_messages
  #
  # End of irciot_encryption_key_to_messages_()

 def irciot_blockchain_key_publication_(self, in_public_key, \
   in_ot, in_vuid = None):
  if not self.irciot_check_blockchain_public_key_(in_public_key):
    return
  if self.__mid_method == self.CONST.tag_mid_ED25519:
    my_key = in_public_key.encode( \
      encoder = self.__crypt_NACE.HexEncoder )
    my_key_string = my_key.decode(self.__encoding)
  elif self.__mid_method == self.CONST.tag_mid_RSA1024:
    my_key_string = self.irciot_crypto_hash_to_str_(in_public_key)
    return
  elif self.__mid_method == self.CONST.tag_mid_GOST12:
    my_key_string = self.irciot_crypto_hash_to_str_(in_public_key)
  else:
    return
  my_packs = self.irciot_blockchain_key_to_messages_( \
    my_key_string, in_ot, in_vuid)
  if my_packs == []:
    return
  my_compat = self.irciot_compatibility_()
  if not self.irc_pointer (my_compat, my_packs):
    # Handler not inserted
    self.output_pool += my_packs
  #
  # End of irciot_blockchain_key_publication_()

 def irciot_encryption_key_publication_(self, in_public_key, \
   in_ot, in_vuid = None):
  if not self.irciot_check_encryption_public_key_(in_public_key):
    return
  my_key_string = ""
  if self.crypt_algo == self.CONST.crypto_RSA:
    my_key_bytes = in_public_key.exportKey(format='DER')
    my_key_string = self.irciot_crypto_hash_to_str_(my_key_bytes)
  else:
    return
  my_packs = self.irciot_encryption_key_to_messages_( \
    my_key_string, in_ot, in_vuid)
  if my_packs == []:
    return
  my_compat = self.irciot_compatibility_()
  if not self.irc_pointer (my_compat, my_packs):
    # Handler not inserted
    self.output_pool += my_packs
  #
  # End of irciot_encryption_key_publication_()

 def irciot_blockchain_check_publication_(self):
  if self.__blockchain_key_published > 0:
    return
  if not self.irciot_check_blockchain_public_key_( \
   self.__blockchain_public_key):
    return
  if not self.__mid_method in [
    self.CONST.tag_mid_ED25519,
    self.CONST.tag_mid_RSA1024,
    self.CONST.tag_mid_GOST12 ]:
    return
  self.__blockchain_key_published = self.CONST.BCHT
  self.irciot_blockchain_key_publication_( \
  self.__blockchain_public_key, self.CONST.ot_BCH_INFO)
  #
  # End of irciot_blockchain_check_publication_()

 def irciot_encryption_check_publication_(self):
  if self.__encryption_key_published > 0:
    return
  if not self.irciot_check_encryption_public_key_( \
   self.__encryption_public_key):
    return
  if self.crypt_model != self.CONST.crypt_ASYMMETRIC:
    return
  self.__encryption_key_published = self.CONST.ENCT
  self.irciot_encryption_key_publication_( \
  self.__encryption_public_key, self.CONST.ot_ENC_INFO)
  #
  # End of irciot_encryption_check_publication_()

 def irciot_blockchain_is_key_published_(self):
  return (self.__blockchain_key_published > 0)

 def irciot_encryption_is_key_published_(self):
  return (self.__encryption_key_published > 0)

 # incomplete
 def irciot_blockchain_place_key_to_repo_(self, in_public_key):
  if in_public_key == None:
    return
  #
  # End of irciot_blockchain_place_key_to_repo_()

 # incomplete
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
  my_packs = self.irciot_blockchain_request_to_messages_(in_vuid)
  if my_packs == []:
    return
  my_compat = self.irciot_compatibility_()
  if not self.irc_pointer (my_compat, my_packs):
    # Handler not inserted
    self.output_pool += my_packs
  #
  # End of irciot_blockchain_request_foreign_key_()

 def irciot_encryption_request_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return
  my_packs = self.irciot_encryption_request_to_messages_(in_vuid)
  if my_packs == []:
    return
  my_compat = self.irciot_compatibility_()
  if not self.irc_pointer (my_compat, my_packs):
    # Handler not inserted
    self.output_pool += my_packs
  #
  # End of irciot_encryption_request_foreign_key_()

 def irciot_blockchain_get_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  if in_vuid == self.CONST.api_vuid_self:
    try:
      if self.__mid_method == self.CONST.tag_mid_ED25519:
        my_key = self.__blockchain_public_key.encode( \
          encoder = self.__crypt_NACE.HexEncoder )
        my_key_string = my_key.decode(self.__encoding)
      else:
        return None
    except:
      return None
    return my_key_string
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_BKEY, in_vuid, None)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if my_status:
    if my_answer is None:
      self.irciot_blockchain_request_foreign_key_(in_vuid)
  else:
    return None
  if isinstance(my_answer, str):
    return my_answer
  return None
  #
  # End of irciot_blockchain_get_foreign_key_()

 def irciot_encryption_get_foreign_key_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return None
  if in_vuid == self.CONST.api_vuid_self:
    try:
      if self.crypt_algo == self.CONST.crypto_RSA:
        my_key_bytes \
          = self.__encryption_public_key.exportKey(format='DER')
        my_key_string \
          = self.irciot_crypto_hash_to_str_(my_key_bytes)
      else:
        return None
    except:
      return None
    return my_key_string
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_EKEY, in_vuid, None)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if my_status:
    if my_answer == None:
      self.irciot_encryption_request_foreign_key_(in_vuid)
  else:
    return None
  if isinstance(my_answer, str):
    return my_answer
  return None
  #
  # End of irciot_encryption_get_foreign_key_()

 def irciot_blockchain_get_last_mids_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return [ str(self.current_mid) ]
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_LMID, in_vuid, None)
  try:
    (my_status, my_answer) = my_result
  except:
    return None
  if not my_status:
    return None
  if isinstance(my_answer, list):
    return my_answer
  return None
  #
  # End of irciot_blockchain_get_last_mid_()

 def irciot_blockchain_get_own_mids_(self, in_vuid):
  if not isinstance(in_vuid, str):
    return [ str(self.current_mid) ]
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_OMID, in_vuid, None)
  try:
    (my_status, my_answer) = my_result
  except:
    return [ str(self.current_mid) ]
  if not my_status:
    return [ str(self.current_mid) ]
  if isinstance(my_answer, list):
    return my_answer
  return [ str(self.current_mid) ]
  #
  # End of irciot_blockchain_get_own_mids_()

 def irciot_get_vuid_list_(self, in_vuid_mask):
  if not isinstance(in_vuid_mask, str):
    return []
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_GET_VUID, in_vuid_mask, None)
  try:
    (my_status, my_answer) = my_result
  except:
    return []
  if not my_status:
    return []
  if isinstance(my_answer, list):
    return my_answer
  return []
  #
  # End of irciot_get_vuid_list_()

 def irciot_blockchain_update_last_mid_(self, in_vuid, \
   in_message_id):
  if not isinstance(in_vuid, str):
    return
  if not isinstance(in_message_id, str):
    return
  my_compat = self.irciot_compatibility_()
  self.user_pointer (my_compat, \
    self.CONST.api_SET_LMID, in_vuid, in_message_id)
  try:
    (my_status, my_answer) = my_result
  except:
    return
  if not my_status:
    return
  #
  # End of irciot_blockchain_update_last_mid_()

 def irciot_blockchain_update_own_mid_(self, in_vuid, \
   in_message_id):
  if not isinstance(in_vuid, str):
    return
  if not isinstance(in_message_id, str):
    return
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_OMID, in_vuid, in_message_id)
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
  if not isinstance(in_public_key, str):
    return
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_BKEY, in_vuid, in_public_key)
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
  if not isinstance(in_public_key, str):
    return
  my_compat = self.irciot_compatibility_()
  my_result = self.user_pointer (my_compat, \
    self.CONST.api_SET_EKEY, in_vuid, in_public_key)
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
    my_string = in_string.encode(self.__encoding)
    if self.__mid_method == self.CONST.tag_mid_ED25519:
      my_signed = in_private_key.sign(my_string)
      my_sign = my_signed[:-len(my_string)]
    elif self.__mid_method == self.CONST.tag_mid_RSA1024:
      my_hash = self.__crypt_SHA1.new(my_string)
      my_pkcs = self.__crypt_PKCS.new(in_private_key)
      my_sign = my_pkcs.sign(my_hash)
      del my_hash
    elif self.__mid_method == self.CONST.tag_mid_GOST12:
      my_curve = self.__crypt_GOST.CURVES[self.CONST.crypto_GOST12_curve]
      my_hash = self.__crypt_GSTD.new(my_string).digest()[::-1]
      my_sign = self.__crypt_GOST.sign(my_curve, in_private_key, my_hash, mode=2012)
      del my_hash
    else:
      return ""
    my_string = str(self.__mid_method)
    my_string += self.irciot_crypto_hash_to_str_(my_sign)
  except:
    my_siring = None
  return my_string
  #
  # End of irciot_blockchain_sign_string_()

 def irciot_blockchain_save_defaults_(self):
  return (self.__mid_method, \
   self.__blockchain_private_key, \
   self.__blockchain_public_key)

 def irciot_encryption_save_defaults_(self):
  return (self.crypt_method, \
   self.__encryption_private_key, \
   self.__encryption_public_key)

 def irciot_blockchain_restore_defaults_(self, in_defaults):
  (self.__mid_method, \
   self.__blockchain_private_key, \
   self.__blockchain_public_key) = in_defaults

 def irciot_encryption_restore_defaults_(self, in_defaults):
  (self.crypt_method, \
   self.__encryption_private_key, \
   self.__encryption_public_key) = in_defaults

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
  my_string_bin = bytes(in_string, self.__encoding)
  my_save = self.irciot_blockchain_save_defaults_()
  my_result = False
  if my_method == self.CONST.tag_mid_ED25519:
    self.__mid_method = my_method
    if DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    try:
      in_public_key.verify(my_string_bin, my_sign)
      my_result = True
    except:
      pass
  elif my_method == self.CONST.tag_mid_RSA1024:
    self.__mid_method = my_method
    if DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    try:
      my_hash = self.__crypt_SHA1.new(my_string_bin)
      my_pkcs = self.__crypt_PKCS.new(in_public_key)
      if my_pkcs.verify(my_hash, my_sign):
        my_result = True
      del my_hash
    except:
      pass
  elif my_method == self.CONST.tag_mid_GOST12:
    try:
      my_curve = self.__crypt_GOST.CURVES[self.CONST.crypto_GOST12_curve]
      my_int1 = int.from_bytes(in_public_key[0:64], byteorder='little')
      my_int2 = int.from_bytes(in_public_key[64:128], byteorder='little')
      my_hash = self.__crypt_GSTD.new(my_string_bin).digest()[::-1]
      if self.__crypt_GOST.verify(my_curve, ( my_int1, my_int2 ), \
        my_hash, my_sign, mode=2012):
        my_result = True
      del my_hash
    except:
      pass
  self.irciot_blockchain_restore_defaults_(my_save)
  return my_result
  #
  # End of irciot_blockchain_verify_string_()
  
 def irciot_crypto_wo_encryption_(self, in_crypt_method):
  if not isinstance(in_crypt_method, str):
    return self.CONST.tag_ENC_BASE64
  my_base = self.irciot_crypto_get_base_(in_crypt_method)
  my_compress \
    = self.irciot_crypto_get_compress_(in_crypt_method)
  if my_base == self.CONST.base_BASE32:
    if my_compress == self.CONST.compress_ZLIB:
      return self.CONST.tag_ENC_B32_ZLIB
    elif my_compress == self.CONST.compress_BZIP2:
      return self.CONST.tag_ENC.B32_BZIP2
    else:
      return self.CONST.tag_ENC.BASE32
  elif my_base == self.CONST.base_BASE64:
    if my_compress == self.CONST.compress_ZLIB:
      return self.CONST.tag_ENC_B64_ZLIB
    elif my_compress == self.CONST.compress_BZIP2:
      return self.CONST.tag_ENC_B64_BZIP2
  elif my_base == self.CONST.base_BASE85:
    if my_compress == self.CONST.comress_ZLIB:
      return self.CONST.tag_ENC_B85_ZLIB
    elif my_compress == self.CONST.compress_BZIP2:
      return self.CONST.tag_ENC_B85_BZIP2
    else:
      return self.CONST.tag_ENC_BASE85
  return self.CONST.tag_ENC_BASE64
  #
  # End of irciot_crypto_wo_encryption_()

 def irciot_crypto_get_base_(self, in_crypt_method):
  my_base = None
  if in_crypt_method in self.CONST.tag_ALL_BASE32_ENC:
    my_base = self.CONST.base_BASE32
  elif in_crypt_method in self.CONST.tag_ALL_BASE64_ENC:
    my_base = self.CONST.base_BASE64
  elif in_crypt_method in self.CONST.tag_ALL_BASE85_ENC:
    my_base = self.CONST.base_BASE85
  elif in_crypt_method in self.CONST.tag_ALL_BASE122_ENC:
    my_base = self.CONST.base_BASE122
  return my_base
  #
  # End of irciot_crypto_get_base_()

 def irciot_crypto_get_compress_(self, in_crypt_method):
  my_compress = None
  if in_crypt_method in self.CONST.tag_ALL_nocompress_ENC:
    my_compress = self.CONST.compress_NONE
  elif in_crypt_method in self.CONST.tag_ALL_ZLIB_ENC:
    my_compress = self.CONST.compress_ZLIB
  elif in_crypt_method in self.CONST.tag_ALL_BZIP2_ENC:
    my_compress = self.CONST.compress_BZIP2
  return my_compress
  #
  # End of irciot_crypto_get_compress_()
  
 def irciot_crypto_get_algorithm_(self, in_crypt_method):
  my_algorithm = None
  if in_crypt_method in self.CONST.tag_ALL_RSA_ENC:
    my_algorithm = self.CONST.crypto_RSA
  elif in_crypt_method in self.CONST.tag_ALL_AES_ENC:
    my_algorithm = self.CONST.crypto_AES
  elif in_crypt_method in self.CONST.tag_ALL_2FISH_ENC:
    my_algorithm = self.CONST.crypto_2FISH
  return my_algorithm
  #
  # End of irciot_crypto_get_algorithm_()

 def irciot_crypto_get_model_(self, in_crypt_method):
  my_model = None
  if in_crypt_method in self.CONST.tag_ALL_nocrypt_ENC:
    my_model = self.CONST.crypt_NO_ENCRYPTION
  else:
    my_algo = self.irciot_crypto_get_algorithm_(in_crypt_method)
    if my_algo in self.CONST.crypto_ALL_asymmetric:
      my_model = self.CONST.crypt_ASYMMETRIC
    elif my_algo in self.CONST.crypto_ALL_symmetric:
      my_model = self.CONST.crypt_SYMMETRIC
    elif my_algo in self.CONST.crypto_ALL_private_key:
      my_model = self.CONST.crypt_PRIVATE_KEY
  return my_model
  #
  # End of irciot_crypto_get_model_()

 def irciot_crypto_AES_encrypt_(self, in_raw_data, in_secret_key):
  if self.__crypt_AES == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_AES)
    else:
      return None
  my_encrypted = bytes()
  my_size   = len(in_raw_data)
  my_chunk  = 16
  my_offset = 0
  my_loop   = True
  try:
    my_KEY = str(in_secret_key, self.__encoding)
    my_AES = self.__crypt_AES.new(in_secret_key, \
      self.__crypt_AES.MODE_CBC, bytes(self.crypto_AES_iv, \
      self.__encoding))
    while my_loop:
      my_block = in_raw_data[my_offset:my_offset + my_chunk]
      my_bsize = len(my_block) % my_chunk
      my_rest = my_chunk - my_bsize
      if my_rest < my_chunk:
        my_addon = self.irciot_crypto_hasher_(None, my_rest)
        my_block += bytes(my_addon, self.__encoding)
        my_loop = False
      my_encrypted += my_AES.encrypt(my_block)
      my_offset += my_chunk
      if my_offset > my_size:
        my_loop = False
    my_encrypted += bytes(self.crypto_AES_iv, self.__encoding)
    my_encrypted += my_rest.to_bytes(1, 'little')
  except:
    return None
  if my_encrypted == bytes():
    return None
  return my_encrypted
  #
  # End of irciot_crypto_AES_encrypt_()

 def irciot_crypto_AES_decrypt_(self, in_encrypted_data, in_secret_key):
  if self.__crypt_AES == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_AES)
    else:
      return None
  my_decrypted = bytes()
  my_chunk = 16
  my_loop  = True
  try:
    my_KEY   = str(in_secret_key, self.__encoding)
    my_size  = len(in_encrypted_data)-my_chunk-1
    if my_size - my_chunk < 0:
      return None
    my_AES_iv = in_encrypted_data[my_size:my_size+my_chunk]
    my_offset = my_size + my_chunk
    my_rawcut = in_encrypted_data[my_offset:my_offset+1]
    my_cut = int.from_bytes(my_rawcut, byteorder='little')
    my_AES = self.__crypt_AES.new(bytes(my_KEY, self.__encoding), \
      self.__crypt_AES.MODE_CBC, my_AES_iv)
    my_offset = 0
    while my_loop:
      my_block = in_encrypted_data[my_offset:my_offset + my_chunk]
      my_decrypted += my_AES.decrypt(my_block)
      my_offset += my_chunk
      if my_offset >= my_size:
        break
    if my_cut < my_chunk:
      my_decrypted = my_decrypted[:-my_cut]
  except:
    return None
  return my_decrypted
  #
  # End of irciot_crypto_AES_decrypt_()

 def irciot_crypto_2fish_encrypt_(self, in_raw_data, in_secret_key):
  if self.__crypt_FISH == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_2FISH)
    else:
      return None
  my_encrypted = bytes()
  my_size   = len(in_raw_data)
  my_chunk  = 16
  my_rest   = 0
  my_offset = 0
  my_loop   = True
  try:
    my_2fish = self.__crypt_FISH.Twofish(in_secret_key)
    while my_loop:
      my_block = in_raw_data[my_offset:my_offset+my_chunk]
      my_bsize = len(my_block) % my_chunk
      my_rest  = my_chunk - my_bsize
      if my_rest < 16:
        my_addon = self.irciot_crypto_hasher_(None, my_rest)
        my_block += bytes(my_addon, self.__encoding)
        my_loop = False
      my_encrypted += my_2fish.encrypt(my_block)
      my_offset += my_chunk
      if my_offset >= my_size:
        break
    my_encrypted += my_rest.to_bytes(1, 'little')
  except:
    return None
  return my_encrypted
  #
  # End of irciot_crypto_2fish_encrypt_()

 def irciot_crypto_2fish_decrypt_(self, in_encrypted_data, in_secret_key):
  if self.__crypt_FISH == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_2FISH)
    else:
      return None
  my_encrypted = bytes(in_encrypted_data)
  my_decrypted = bytes()
  my_size   = len(in_encrypted_data)-1
  my_chunk  = 16
  my_offset = 0
  my_loop   = True
  try:
    my_2fish = self.__crypt_FISH.Twofish(in_secret_key)
    my_rawcut = in_encrypted_data[my_size:my_size+1]
    my_cut = int.from_bytes(my_rawcut, byteorder='little')
    while my_loop:
      my_block = my_encrypted[my_offset:my_offset+my_chunk]
      my_crypt = my_2fish.decrypt(my_block)
      my_decrypted += my_crypt
      my_offset += my_chunk
      if my_offset >= my_size:
        break
    if my_cut < my_chunk:
      my_decrypted = my_decrypted[:-my_cut]
  except:
    return None
  return my_decrypted
  #
  # End of irciot_crypto_2fish_decrypt_()

 def irciot_crypto_RSA_encrypt_(self, in_raw_data, in_public_key):
  if self.__crypt_RSA == None or self.__crypt_OAEP == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_RSA)
    else:
      return None
  my_size = len(in_raw_data)
  my_hash = self.irciot_crypto_hasher_(str(in_raw_data), 16)
  if self.__crypt_cache != None:
    ( my_size_cached, my_hash_cached, my_encrypted ) \
      = self.__crypt_cache
    if my_size == my_size_cached and my_hash == my_hash_cached:
      return my_encrypted
  my_encrypted = bytes()
  my_chunk  = self.CONST.crypto_RSA_CHUNK_IN
  my_offset = 0
  my_loop   = True
  try:
    my_encryptor = self.__crypt_OAEP.new(in_public_key)
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
  self.__crypt_cache = ( my_size, my_hash, my_encrypted )
  return my_encrypted
  #
  # End of irciot_crypto_RSA_encrypt_()

 def irciot_crypto_RSA_decrypt_(self, in_encrypted_data, in_private_key):
  if self.__crypt_RSA == None or self.__crypt_OAEP == None:
    if DO_auto_encryption:
      self.irciot_load_encryption_methods_(self.CONST.tag_ENC_B64_RSA)
    else:
      return None
  my_decrypted = bytes()
  my_chunk  = self.CONST.crypto_RSA_CHUNK
  my_offset = 0
  my_loop   = True
  try:
    my_decryptor = self.__crypt_OAEP.new(in_private_key)
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
      if len(my_block) != 0:
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
    if self.__crypt_RSA == None:
      return (None, None)
    crypto_private_key \
      = self.__crypt_RSA.generate(self.crypto_RSA_KEY_SIZE)
    crypto_public_key = crypto_private_key.publickey()
  elif my_algo == self.CONST.crypto_AES \
    or my_algo == self.CONST.crypto_2FISH:
    crypto_private_key \
      = self.irciot_crypto_hasher_(None, 32).encode()
  return (crypto_private_key, crypto_public_key)
  #
  # End of irciot_crypto_generate_keys_()

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

 def irciot_ldict_get_item_max_id_(self):
  my_max_id = 0
  for my_ldict_item in self.ldict:
    my_id = my_ldict_item[self.CONST.ldict_ITEM_ID]
    if not isinstance(my_id, int):
      my_id = 0
    if my_max_id < my_id:
      my_max_id = my_id
  return my_max_id

 def irciot_ldict_create_item_(self, in_ldict_item_pack):
  try:
   ( my_id, my_ot, my_name, my_parent_id, my_type_id, \
     my_type_param, my_default, my_child_obj_id, my_method, \
     my_method_lang, my_sections ) = in_ldict_item_pack
  except:
    return
  my_item = {
    self.CONST.ldict_ITEM_ID : my_id,
    self.CONST.ldict_ITEM_OT : my_ot,
    self.CONST.ldict_ITEM_NAME : my_name,
    self.CONST.ldict_ITEM_PARENT : my_parent_id,
    self.CONST.ldict_ITEM_TYPEID : my_type_id,
    self.CONST.ldict_ITEM_TYPEPR : my_type_param,
    self.CONST.ldict_ITEM_DEFVAL : my_default,
    self.CONST.ldict_ITEM_CHILD  : my_child_obj_id,
    self.CONST.ldict_ITEM_METHOD : my_method,
    self.CONST.ldict_ITEM_LANG   : my_method_lang,
    self.CONST.ldict_ITEM_SECTS  : my_sections
  }
  #
  # print('adding to ldict: ot="{}", field="{}"'.format(my_ot, my_name))
  if not self.irciot_ldict_check_item_(my_item):
    return
  if self.irciot_ldict_get_item_by_ot_(my_ot, my_name):
    return
  my_max_id = self.irciot_ldict_get_item_max_id_()
  if my_id <= my_max_id:
    my_item[self.CONST.ldict_ITEM_ID] = my_max_id + 1
  self.ldict.append(my_item)
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_create_item_()

 def irciot_ldict_get_item_by_ot_(self, in_object_type, \
  in_item_name = None):
  if not isinstance(in_object_type, str):
    return None
  for my_item in self.ldict:
    if my_item[self.CONST.ldict_ITEM_OT] == in_object_type:
      if isinstance(in_item_name, str):
        if my_item[self.CONST.ldict_ITEM_NAME] != in_item_name:
          continue
      return my_item
  return None
  #
  # End of irciot_ldict_get_item_by_ot_()

 def irciot_ldict_delete_item_by_ot_(self, in_object_type):
  if not isinstance(in_object_type, str):
    return
  for my_ldict_item in self.ldict:
    if my_ldict_item[self.CONST.ldict_ITEM_OT] == in_object_type:
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
    if my_ldict_item[self.CONST.ldict_ITEM_ID] == in_item_id:
      self.ldict.remove(my_ldict_item)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_item_by_id_()

 def irciot_ldict_get_sect_max_id_(self):
  my_max_id = 0
  for my_ldict_sect in self.ldict_sects:
    my_id = my_ldict_sect[self.CONST.ldict_SECT_ID]
    if not isinstance(my_id, int):
      my_id = 0
    if my_max_id < my_id:
      my_max_id = my_id
  return my_max_id

 def irciot_ldict_get_type_max_id_(self):
  my_max_id = 0
  for my_ldict_type in self.ldict_types:
    my_id = my_ldict_type[self.CONST.ldict_TYPE_ID]
    if not isinstance(my_id, int):
      my_id = 0
    if my_max_id < my_id:
      my_max_id = my_id
  return my_max_id

 def irciot_ldict_create_sect_(self, in_ldict_sect):
  try:
    ( my_id, my_items_ids, my_check_values, \
      my_method, my_method_laguage ) = in_ldict_sect
  except:
    return
  my_sect = {
    self.CONST.ldict_SECT_ID : my_id,
    self.CONST.ldict_SECT_ITEMS : my_items_ids,
    self.CONST.ldict_SECT_CHECKS : my_check_values,
    self.CONST.ldict_SECT_METHOD : my_method,
    self.CONST.ldict_SECT_LANG : my_method_language
  }
  #
  # Checks will be here
  my_max_id = self.irciot_ldict_get_sect_max_id_()
  if my_id <= my_max_id:
    my_type[self.CONST.ldict_SECT_ID] = my_max_id + 1
  self.ldict_sect.append(my_sect)
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_create_sect_()

 def irciot_ldict_create_type_(self, in_ldict_type_pack):
  try:
   ( my_id, my_name, my_type_type, my_is_array, my_is_dynamic, \
     my_is_dynarray, my_array_size, my_size, my_min, my_max, \
     my_precision, my_expsize, my_endianness, my_encoding ) \
      = in_ldict_type_pack
  except:
    return
  my_type = {
    self.CONST.ldict_TYPE_ID : my_id,
    self.CONST.ldict_TYPE_NAME : my_name,
    self.CONST.ldict_TYPE_TYPE : my_type_type,
    self.CONST.ldict_TYPE_ARR : my_is_array,
    self.CONST.ldict_TYPE_DYNSIZE : my_is_dynamic,
    self.CONST.ldict_TYPE_DYNARR : my_is_dynarray,
    self.CONST.ldict_TYPE_ARRSIZE : my_array_size,
    self.CONST.ldict_TYPE_SIZE : my_size,
    self.CONST.ldict_TYPE_MIN : my_min,
    self.CONST.ldict_TYPE_MAX : my_max,
    self.CONST.ldict_TYPE_PRECIS : my_precision,
    self.CONST.ldict_TYPE_EXPSIZE : my_expsize,
    self.CONST.ldict_TYPE_ENDIAN : my_endianness,
    self.CONST.ldict_TYPE_ENCODE : my_encoding
  }
  #
  if not self.irciot_ldict_check_type_(my_type):
    return
  if self.irciot_ldict_get_type_by_name_(my_name):
    return
  my_max_id = self.irciot_ldict_get_type_max_id_()
  if my_id <= my_max_id:
    my_type[self.CONST.ldict_TYPE_ID] = my_max_id + 1
  self.ldict_types.append(my_type)
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_create_type_()

 def irciot_ldict_delete_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return
  for my_ldict_type in self.ldict_types:
    if my_ldict_type[self.CONST.ldict_TYPE_NAME] == in_type_name:
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
    if my_ldict_type[self.CONST.ldict_TYPE_ID] == in_type_id:
      self.ldict_types.remove(my_ldict_type)
      break
  if isinstance(self.ldict_file, str):
    self.irciot_ldict_dump_to_file_(self.ldict_file)
  #
  # End of irciot_ldict_delete_type_by_id_()

 def irciot_ldict_get_type_by_name_(self, in_type_name):
  if not isinstance(in_type_name, str):
    return None
  for my_ldict_type in self.ldict_types:
    if my_ldict_type[self.CONST.ldict_TYPE_NAME] == in_type_name:
      return ldict_type
  return None
  #
  # End of irciot_ldict_get_type_by_name_()

 def irciot_ldict_check_item_(self, in_ldict_item):
  # Will be replaced by ldict self check
  if not isinstance(in_ldict_item, dict):
    return False
  if not self.CONST.ldict_ITEM_ID in in_ldict_item.keys():
    return False
  my_item_id = in_ldict_item[self.CONST.ldict_ITEM_ID]
  if not isinstance(my_item_id, int):
    return False
  if not self.CONST.ldict_ITEM_OT in in_ldict_item.keys():
    return False
  my_item_ot = in_ldict_item[self.CONST.ldict_ITEM_OT]
  if not isinstance(my_item_ot, str):
    return False
  if not self.CONST.ldict_ITEM_PARENT in in_ldict_item.keys():
    return False
  my_item_parent = in_ldict_item[self.CONST.ldict_ITEM_PARENT]
  if not isinstance(my_item_parent, int) \
   and my_item_parent != None:
    return False
  if not self.CONST.ldict_ITEM_TYPEID in in_ldict_item.keys():
    return False
  my_item_type_id = in_ldict_item[self.CONST.ldict_ITEM_TYPEID]
  if not isinstance(my_item_type_id, int):
    return False
  if not self.CONST.ldict_ITEM_TYPEPR in in_ldict_item.keys():
    return False
  my_item_type_pr = in_ldict_item[self.CONST.ldict_ITEM_TYPEPR]
  if not isinstance(my_item_type_pr, str) \
   and my_item_type_pr != None:
    return False
  if not self.CONST.ldict_ITEM_DEFVAL in in_ldict_item.keys():
    return False
  my_item_defval = in_ldict_item[self.CONST.ldict_ITEM_DEFVAL]
  if not isinstance(my_item_defval, str) \
   and my_item_defval != None:
    return False
  if not self.CONST.ldict_ITEM_CHILD in in_ldict_item.keys():
    return False
  my_item_child = in_ldict_item[self.CONST.ldict_ITEM_CHILD]
  if not isinstance(my_item_child, int) \
   and my_item_child != None:
    return False
  if not self.CONST.ldict_ITEM_METHOD in in_ldict_item.keys():
    return False
  my_item_method = in_ldict_item[self.CONST.ldict_ITEM_METHOD]
  if not isinstance(my_item_method, str) \
   and my_item_method != None:
    return False
  if not self.CONST.ldict_ITEM_LANG in in_ldict_item.keys():
    return False
  my_item_language = in_ldict_item[self.CONST.ldict_ITEM_LANG]
  if not isinstance(my_item_language, str) \
   and my_item_language != None:
    return False
  if not self.CONST.ldict_ITEM_SECTS in in_ldict_item.keys():
    return False
  my_item_sects = in_ldict_item[self.CONST.ldict_ITEM_SECTS]
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
  if not self.CONST.ldict_TYPE_ID in in_ldict_type.keys():
    return False
  my_type_id = in_ldict_type[self.CONST.ldict_TYPE_ID]
  if not isinstance(my_type_id, int):
    return False
  if not self.CONST.ldict_TYPE_NAME in in_ldict_type.keys():
    return False
  my_type_name = in_ldict_type[self.CONST.ldict_TYPE_NAME]
  if not isinstance(my_type_name, str):
    return False
  if not self.CONST.ldict_TYPE_TYPE in in_ldict_type.keys():
    return False
  if not self.CONST.ldict_TYPE_ARR in in_ldict_type.keys():
    return False
  my_type_is_array = in_ldict_type[self.CONST.ldict_TYPE_ARR]
  if not isinstance(my_type_is_array, bool):
    return False
  if not self.CONST.ldict_TYPE_DYNSIZE in in_ldict_type.keys():
    return False
  my_type_dynsize = in_ldict_type[self.CONST.ldict_TYPE_DYNSIZE]
  if not isinstance(my_type_dynsize, bool):
    return False
  if not self.CONST.ldict_TYPE_DYNARR in in_ldict_type.keys():
    return False
  my_type_dynarr = in_ldict_type[self.CONST.ldict_TYPE_DYNARR]
  if not isinstance(my_type_dynarr, bool):
    return False
  if not self.CONST.ldict_TYPE_ARRSIZE in in_ldict_type.keys():
    return False
  my_type_arrsize = in_ldict_type[self.CONST.ldict_TYPE_ARRSIZE]
  if not isinstance(my_type_arrsize, int) \
   and my_type_arrsize != None:
    return False
  if not self.CONST.ldict_TYPE_SIZE in in_ldict_type.keys():
    return False
  my_type_size = in_ldict_type[self.CONST.ldict_TYPE_SIZE]
  if not isinstance(my_type_size, int) \
     and my_type_size != None:
    return False
  if not self.CONST.ldict_TYPE_MIN in in_ldict_type.keys():
    return False
  my_type_min = in_ldict_type[self.CONST.ldict_TYPE_MIN]
  if not isinstance(my_type_min, str) \
     and my_type_min != None:
    return False
  if not self.CONST.ldict_TYPE_MAX in in_ldict_type.keys():
    return False
  my_type_max = in_ldict_type[self.CONST.ldict_TYPE_MAX]
  if not isinstance(my_type_max, str) \
   and my_type_max != None:
    return False
  if not self.CONST.ldict_TYPE_PRECIS in in_ldict_type.keys():
    return False
  my_type_precess = in_ldict_type[self.CONST.ldict_TYPE_PRECIS]
  if not isinstance(my_type_precess, str) \
   and my_type_precess != None:
    return False
  if not self.CONST.ldict_TYPE_ENDIAN in in_ldict_type.keys():
    return False
  my_type_endian = in_ldict_type[self.CONST.ldict_TYPE_ENDIAN]
  if not isinstance(my_type_endian, str) \
   and my_type_endian != None:
    return False
  if not self.CONST.ldict_TYPE_ENCODE in in_ldict_type.keys():
    return False
  my_type_encode = in_ldict_type[self.CONST.ldict_TYPE_ENCODE]
  if not isinstance(my_type_encode, str) \
   and my_type_encode != None:
    return False
  return True
  #
  # End of irciot_ldict_check_type_()

 def irciot_ldict_check_section_(self, in_ldict_section):
  if not isinstance(in_ldict_section, dict):
    return False
  if not self.CONST.ldict_SECT_ID in in_ldict_section.keys():
    return False
  my_section_id = in_ldict_section[self.CONST.ldict_SECT_ID]
  if not isinstance(my_section_id, int):
    return False
  if not self.CONST.ldict_SECT_ITEMS in in_ldict_section.keys():
    return False
  my_section_items = in_ldict_section[self.CONST.ldict_SECT_ITEMS]
  if not isinstance(my_section_items, list):
    return False
  for my_item_id in my_section_items:
    if not isinstance(my_item_id, int):
      return False
  if not self.CONST.ldict_SECT_CHECKS in in_ldict_section.keys():
    return False
  my_section_checks = in_ldict_section[self.CONST.ldict_SECT_CHECKS]
  if not isinstance(my_section_checks, list):
    return False
  for my_check in my_section_checks:
    if not isinstance(my_check, str):
      return False
  if not self.CONST.ldict_SECT_METHOD in in_ldict_section.keys():
    return False
  my_section_method = in_ldict_section[self.CONST.ldict_SECT_METHOD]
  if not isinstance(my_section_method, str):
    return False
  if not self.CONST.ldict_SECT_LANG in in_ldict_section.keys():
    return False
  my_section_language = in_ldict_section[self.CONST.ldict_SECT_LANG]
  if not isinstacne(my_section_language, str):
    return False
  return True
  #
  # End of irciot_ldict_check_section_()

 def irciot_ldict_validate_object_by_ot_(self, in_object, in_ot):
  if not isinstance(in_ot, str):
    return False
  if not self.is_irciot_ldict_object_(in_object, None, in_ot):
    return False
  return True
  #
  # End of irciot_ldict_validate_object_by_ot_()

 def irciot_ldict_validate_json_by_ot_(self, in_json, in_ot):
  if not isinstance(in_ot, str):
    return False
  try:
    my_object = json.loads(in_json)
  except:
    return False
  return self.irciot_ldict_validate_object_by_ot_(in_ot, my_object)
  #
  # End of irciot_ldict_validate_json_by_ot_()

 def irciot_ldict_load_from_file_(self, in_filename):
  if not isinstance(in_filename, str): return False
  ldict_addon = 'local dictionary: {}'.format(in_filename)
  if not os.path.isfile(in_filename):
    #
    return False
  if not os.access(in_filename, os.R_OK):
    #
    return False
  try:
    load_fd = open(in_filename, 'r')
    load_json = load_fd.read()
    load_dict = json.loads(load_json)
    load_fd.close()
  except:
    #
    return False
  if not isinstance(load_dict, dict):
    return False
  if not self.CONST.ldict_VERSION in load_dict.keys():
    #
    return False
  my_ldict_version = load_dict[self.CONST.ldict_VERSION]
  if my_ldict_version != self.CONST.irciot_protocol_version:
    self.irciot_error_(self.CONST.err_PROTO_VER_MISMATCH, 0, \
      in_addon = ldict_addon)
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
  my_lock = 0
  while self.__ldict_lock and my_lock < 8:
    random.seed()
    my_lock += 1
  if self.__ldict_lock:
    return False
  self.ldict_lock  = True
  self.ldict       = my_ldict_items
  self.ldict_types = my_ldict_types
  self.ldict_sections = my_ldict_sections
  self.ldict_lock  = False
  return True
  #
  # End of irciot_ldict_load_from_file_()

 def irciot_ldict_dump_to_file_(self, in_filename):
  if not isinstance(in_filename, str):
    return False
  my_ldict = {
    self.CONST.ldict_VERSION : self.CONST.irciot_protocol_version,
    self.CONST.ldict_ITEMS_TABLE : self.ldict,
    self.CONST.ldict_TYPES_TABLE : self.ldict_types,
    self.CONST.ldict_SECTS_TABLE : self.ldict_sections
  }
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
    return None
  for ldict_type in self.ldict_types:
    if ldict_type[self.CONST.ldict_TYPE_ID] == in_type_id:
      return ldict_type 
  return None
  #
  # End of irciot_ldict_get_type_by_id_()

 def irciot_set_mtu_(self, in_mtu):
  if not isinstance(in_mtu, int):
    return False
  if in_mtu < 128:
    return False
  self.__message_MTU = in_mtu
  return True

 def irciot_get_mtu_(self):
  return self.__message_MTU

 def irciot_get_imtu_(self):
  return self.__initial_MTU

 def is_irciot_ldict_type_(self, in_variable, in_type_id):
  my_type = self.irciot_ldict_get_type_by_id_(in_type_id)
  if my_type == None:
    return True
  my_id   = my_type[self.CONST.ldict_TYPE_ID]
  my_name = my_type[self.CONST.ldict_TYPE_NAME]
  my_size = my_type[self.CONST.ldict_TYPE_SIZE]
  my_min  = my_type[self.CONST.ldict_TYPE_MIN]
  my_max  = my_type[self.CONST.ldict_TYPE_MAX]
  my_type_type   = my_type[self.CONST.ldict_TYPE_TYPE]
  my_is_array    = my_type[self.CONST.ldict_TYPE_ARR]
  my_is_dynamic  = my_type[self.CONST.ldict_TYPE_DYNSIZE]
  my_is_dynarray = my_type[self.CONST.ldict_TYPE_DINARR]
  my_array_size  = my_type[self.CONST.ldict_TYPE_ARRSIZE]
  my_precision   = my_type[self.CONST.ldict_TYPE_PRECIS]
  my_expsize     = my_type[self.CONST.ldict_TYPE_EXPSIZE]
  my_endianness  = my_type[self.CONST.ldict_TYPE_ENDIAN]
  my_encoding    = my_type[self.CONST.ldict_TYPE_ENCODE]
  if my_is_array == True:
    if not isinstance(in_variable, list):
      return False
    if isinstance(my_array_size, int) \
     and not my_is_dynarray == True:
      if len(in_variable) != my_array_size:
        return False
    for my_elemet in in_variable:
      if not self.is_irciot_ldict_type_(my_element, my_type_type):
        return False
    return True
  if type(in_variable) in [ int, float ]:
    try:
      if my_min != None:
        if in_variable < float(my_min):
          return False
      if my_min != None:
        if in_variable > float(my_max):
          return False
    except:
      return False
  #
  # incomplete code
  #
  return True
  #
  # End of is_irciot_ldict_type_()

 def is_irciot_ldict_object_(self, in_object, in_id, in_ot):
  if not isinstance(in_object, dict):
    return False
  if in_ot == None:
    if not isinstance(in_id, int):
      return False
  else:
    if not isinstance(in_ot, str):
      return False
    if in_id != None:
      return False
  for my_item in self.ldict:
    if in_id != None:
      if my_item[self.CONST.ldict_ITEM_ID] != in_id:
        continue
    if in_ot != None:
      if my_item[self.CONST.ldict_ITEM_OT] != in_ot:
        continue
    my_item_name = my_item[self.CONST.ldict_ITEM_NAME]
    my_item_type = my_item[self.CONST.ldict_ITEM_TYPEID]
    try:
      my_variable = in_object[my_item_name]
    except:
      return False
    if not self.is_irciot_ldict_type_(my_variable, my_item_type):
      return False
  return True
  #
  # End of is_irciot_ldict_object_()

 def is_irciot_datum_(self, in_datum, in_ot, in_src, in_dst):
  if self.CONST.tag_ENC_DATUM in in_datum:
    if isinstance(in_datum[self.CONST.tag_ENC_DATUM], str):
      return True # Stub
  # Object Type filed must exists or inherits
  if self.CONST.tag_OBJECT_TYPE not in in_datum:
    if in_ot == None:
      return False
    my_ot = in_ot
  else:
    my_ot = in_datum[self.CONST.tag_OBJECT_TYPE]
  if not isinstance(my_ot, str):
    return False
  # Fragmented message header:
  if self.CONST.tag_DATUM_BC in in_datum:
    if not isinstance(in_datum[self.CONST.tag_DATUM_BC], int):
      return False # Bytes Count must be int
    if self.CONST.tag_DATUM_BP in in_datum:
      if not isinstance(in_datum[self.CONST.tag_DATUM_BP], int):
        return False # Bytes Passed must be int
      if in_datum[self.CONST.tag_DATUM_BP] \
       > in_datum[self.CONST.tag_DATUM_BC]:
        return False
  # Source address field must exists or inherits
  if not self.CONST.tag_SRC_ADDR in in_datum:
    if in_src == None:
      return False
  else:
    if not isinstance(in_datum[self.CONST.tag_SRC_ADDR], str):
      return False
  # Destination address field must exits or ihnerits
  if not self.CONST.tag_DST_ADDR in in_datum:
    if in_dst == None:
      return False
  else:
    if not isinstance(in_datum[self.CONST.tag_DST_ADDR], str):
      return False
  if self.irciot_ldict_get_item_by_ot_(my_ot) != None:
    if not self.is_irciot_ldict_object_(in_datum, None, my_ot):
      self.irciot_error_( \
        self.CONST.err_LDICT_VERIFY_FAIL, 0, None, my_ot)
      return False
  return True
  #
  # End of is_irciot_datum_()

 def is_irciot_hex_(self, in_hex):
  if not isinstance(in_hex, str):
    return False
  for my_ch in in_hex:
    if my_ch not in self.CONST.irciot_chars_lhex:
      return False
  return True

 def is_irciot_address_(self, in_addr):
  if not isinstance(in_addr, str):
    return False
  if in_addr == "":
    return True
  if '/' in in_addr:
    my_array = in_addr.split('/')
    for my_item in my_array:
      if not self.is_irciot_address_(my_item):
        return False
  elif '@' in in_addr:
    my_array = in_addr.split('@')
    if len(my_array) != 2:
      return False
    for my_item in my_array:
      for my_char in my_item:
        if not my_char in self.CONST.irciot_chars_cell_addr:
          return False
  return True
  #
  # End of is_irciot_address_()

 def is_irciot_(self, my_json):
  ''' Checks whether the text string is a IRC-IoT message or not '''
  
  def is_irciot_object_(self, in_object):
    if not self.CONST.tag_OBJECT_ID in in_object: # IRC-IoT Object ID
      return False
    if in_object[self.CONST.tag_OBJECT_ID] == "":
      return False
    if not self.CONST.tag_OBJECT_TYPE in in_object:
      in_object[self.CONST.tag_OBJECT_TYPE] = None
      # it will test all datums for "object type"
    if in_object[self.CONST.tag_OBJECT_TYPE] == "":
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
        if in_object[self.CONST.tag_DATUM_BP] \
         > in_object[self.CONST.tag_DATUM_BC]:
          return False
    # Go deeper
    if isinstance(my_datums, dict):
      my_datums = [ my_datums ]
    if isinstance(my_datums, list):
      for my_datum in my_datums:
        if not self.is_irciot_datum_(my_datum, \
          in_object[self.CONST.tag_OBJECT_TYPE], my_src, my_dst):
            return False
      return True
    return True
    #
    # End of is_irciot_() :: is_irciot_object_()

  def is_irciot_container_(self, in_container):
    if not self.CONST.tag_MESSAGE_ID in in_container:
      return False
    if in_container[self.CONST.tag_MESSAGE_ID] == "":
      return False
    if self.CONST.tag_MESSAGE_OC in in_container:
      if not isinstance(in_container[self.CONST.tag_MESSAGE_OC], int):
        return False # Objects Count must be int
    else:
      in_container[self.CONST.tag_MESSAGE_OC] = 1
    if self.CONST.tag_MESSAGE_OP in in_container:
      if not isinstance(in_container[self.CONST.tag_MESSAGE_OP], int):
        return False # Objects Passed must be int
      if in_container[self.CONST.tag_MESSAGE_OP] \
       > in_container[self.CONST.tag_MESSAGE_OC]:
        return False
    else:
      in_container[self.CONST.tag_MESSAGE_OP] = 1
    if not self.CONST.tag_OBJECT in in_container:
      if self.CONST.tag_VERSION in in_container:
        in_container[self.CONST.tag_OBJECT] = []
      elif self.CONST.tag_RETRY_LOST in in_container:
        in_container[self.CONST.tag_OBJECT] = []
        return True
      else: # IRC-IoT Object must exists
        return False
    my_objects = in_container[self.CONST.tag_OBJECT]
    if isinstance(my_objects, list):
      for my_object in my_objects:
        if not is_irciot_object_(self, my_object):
          return False
      return True
    elif isinstance(my_objects, dict):
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
  if isinstance(irciot_message, dict):
    irciot_message = [ irciot_message ]
    my_shift = 0
  else:
    my_shift = 1
  if isinstance(irciot_message, list):
    for my_container in irciot_message:
      if not is_irciot_container_(self, my_container):
        return False
      if self.integrity_check > 0:
        my_dump = json.dumps(my_container, separators=(',',':'))
        my_len  = len(my_dump)
        my_item = my_json[my_shift:my_len]
        del my_dump
        if not self.irciot_check_integrity_(my_item, my_container):
          return False
        my_shift = my_len + 1
    return True
  return True
  #
  # End of is_irciot_()

 def irciot_clear_defrag_chain_(self, in_did):
  try:
    if self.__defrag_lock:
      return
    self.__defrag_lock = True
    for my_item in self.defrag_pool:
      (test_enc, test_header, test_json) = my_item
      (test_dt, test_ot, test_src, test_dst, \
       test_dc, test_dp, test_bc, test_bp, test_did) = test_header
      if in_did == test_did:
        self.defrag_pool.remove(my_item)
        break
  except:
    pass
  self.__defrag_lock = False
  #
  # End of irciot_clear_defrag_chain_()

 def irciot_add_padding_(self, in_buffer, in_padding):
  my_count = in_padding - (len(in_buffer) % in_padding)
  if my_count > 0:
    for my_idx in range(my_count):
      in_buffer += '='
  return in_buffer

 def irciot_defragmentation_(self, in_enc, in_header, \
   orig_json, in_vuid = None):
  (my_dt, my_ot, my_src, my_dst, \
   my_dc, my_dp, my_bc, my_bp, my_did) = in_header
  if (my_dc == None and my_dp != None) or \
     (my_dc != None and my_dp == None) or \
     (my_bc == None and my_bp != None) or \
     (my_bc != None and my_bp == None):
    return ""
  if not isinstance(self.defrag_pool, list):
    self.defrag_pool = [] # Drop broken defrag_pool
  my_dup = False
  my_new = False
  my_err = 0
  my_ok  = 0
  my_fragments = False
  defrag_array = []
  defrag_buffer = ""
  for my_item in self.defrag_pool: # IRC-IoT defragmentation loop
    (test_enc, test_header, test_json) = my_item
    (test_dt, test_ot, test_src, test_dst, \
     test_dc, test_dp, test_bc, test_bp, test_did) = test_header
    if test_json == orig_json:
      my_dup = True
      break
    else:
      if test_did == my_did:
        my_fragments = True
        if test_ot  == my_ot and \
           test_src == my_src and \
           test_dst == my_dst:
          if test_dc == my_dc and test_dp == my_dp and \
             test_bp == my_bp and test_bc == my_bc:
            if test_enc == in_enc:
              my_dup = True
            else:
              my_err = self.CONST.err_DEFRAG_MISSMATCH
              break
          else:
            if test_dc != None and test_dp != None and \
               test_bc == None and test_bp == None:
              if my_dp == None:
                my_err = self.CONST.err_DEFRAG_DP_MISSING
                break
              if defrag_array == []:
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
            elif test_bc != None and test_bp != None and \
                 test_dc == None and test_dp == None:
              if my_bp == None:
                my_err = self.CONST.err_DEFRAG_BP_MISSING
                break
              if defrag_buffer == "":
                defrag_buffer += self.CONST.pattern * my_bc
                defrag_buffer = defrag_buffer[:my_bp] + \
                 in_enc + defrag_buffer[my_bp + len(in_enc):]
              if defrag_buffer != "":
                # here will be a comparison of overlapping buffer intervals
                defrag_buffer = defrag_buffer[:test_bp] + \
                 str(test_enc) + defrag_buffer[test_bp + len(test_enc):]
                if defrag_buffer.count(self.CONST.pattern) == 0:
                  my_ok = 2
                else:
                  my_new = True
            else: # Combo fragmentation method
              pass
        #else:
        #  my_err = self.CONST.err_DEFRAG_INVALID_DID
        #  break
  if self.defrag_pool == []:
    if len(in_enc) == my_bc:
      defrag_buffer = in_enc
      my_ok = 2
    else:
      my_new = True
  elif not my_fragments:
    my_new = True
  if my_err > 0:
    self.irciot_error_(my_err, 0)
    self.irciot_clear_defrag_chain_(my_did)
    return ""
  if my_new:
    my_item = (in_enc, in_header, orig_json)
    self.__defrag_lock = True
    self.defrag_pool.append(my_item)
    self.__defrag_lock = False
  if my_ok > 0:
    if my_ok == 1:
      pass
    elif my_ok == 2:
      self.irciot_clear_defrag_chain_(my_did)
      if DO_debug_library:
        print("\033[1;42m DEFRAGMENTATION COMPLETED \033[0m")
      my_crypt_method = self.crypt_method
      if my_ot in [
        self.CONST.ot_ENC_INFO, self.CONST.ot_ENC_ACK,
        self.CONST.ot_BCH_INFO, self.CONST.ot_BCH_ACK,
        self.CONST.ot_ENC_REQUEST,
        self.CONST.ot_BCH_REQUEST ]:
         my_crypt_method \
           = self.irciot_crypto_wo_encryption_(self.crypt_method)
      my_base = self.irciot_crypto_get_base_(my_crypt_method)
      if my_base == self.CONST.base_BASE64:
        try:
          defrag_buffer = self.irciot_add_padding_(defrag_buffer, 4)
          out_base = base64.b64decode(defrag_buffer)
        except:
          self.irciot_error_(self.CONST.err_BASE64_DECODING, 0)
          return ""
      elif my_base == self.CONST.base_BASE85:
        try:
          out_base = base64.b85decode(defrag_buffer)
        except:
          self.irciot_error_(self.CONST.err_BASE85_DECODING, 0)
          return ""
      elif my_base == self.CONST.base_BASE32:
        try:
          defrag_buffer = self.irciot_add_padding_(defrag_buffer, 8)
          out_base = base64.b32decode(defrag_buffer)
        except:
          self.irciot_error_(self.CONST.err_BASE32_DECODING, 0)
          return ""
      else:
        out_base = bytes(defrag_buffer, self.__encoding)
      my_algo = self.irciot_crypto_get_algorithm_(my_crypt_method)
      #if DO_auto_encryption and my_algo != None:
      #   self.irciot_load_encryption_methods_(my_crypt_method)
      if my_algo == self.CONST.crypto_RSA:
        out_base = self.irciot_crypto_RSA_decrypt_(out_base, \
         self.__encryption_private_key)
      elif my_algo == self.CONST.crypto_AES:
         out_base = self.irciot_crypto_AES_decrypt_(out_base, \
           self.__encryption_private_key)
      elif my_algo == self.CONST.crypto_2FISH:
         out_base = self.irciot_crypto_2fish_decrypt_(out_base, \
           self.__encryption_private_key)
      my_compress = self.irciot_crypto_get_compress_( \
         my_crypt_method )
      if my_compress == self.CONST.compress_NONE:
         out_json = str(out_base)[2:-1]
         del out_base
      elif my_compress == self.CONST.compress_ZLIB:
        if DO_auto_compress and self.__crypt_ZLIB == None:
          self.irciot_load_compression_methods_(my_crypt_method)
        if self.__crypt_ZLIB == None:
          return ""
        try:
          out_compress = str(self.__crypt_ZLIB.decompress(out_base))
          del out_base
        except self.__crypt_ZLIB.error as zlib_error:
          if DO_debug_library:
            print("\033[1;41m ZLIB COMPRESSION FAILED \33[0m")
            print("\033[1;35m{}\033[0m".format(zlib_error))
          if zlib_error.args[0].startswith("Error -3 "):
            self.irciot_error_(self.CONST.err_COMP_ZLIB_HEADER, 0)
          else:
            self.irciot_error_(self.CONST.err_COMP_ZLIB_INCOMP, 0)
          del zlib_error
          return ""
        except:
          return ""
        out_json = out_compress[2:-1]
        del out_compress
      elif my_compress == self.CONST.compress_BZIP2:
        if DO_auto_compress and self.__crypt_BZ2 == None:
          self.irciot_load_compression_methods_(my_crypt_method)
        if self.__crypt_BZ2 == None:
          return ""
        out_compress = str(self.__crypt_BZ2.decompress(out_base))
        out_json = out_compress[2:-1]
        del out_compress
      else:
        return ""
      try:
        # Adding missing fields to the "Datum" from parent object
        my_datum = json.loads(out_json)
        if self.CONST.tag_OBJECT_TYPE not in my_datum \
         and my_ot != None:
          my_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
        if self.CONST.tag_DATE_TIME not in my_datum \
         and my_dt != None:
          my_datum[self.CONST.tag_DATE_TIME] = my_dt
        if self.CONST.tag_SRC_ADDR not in my_datum \
         and my_src != None:
          my_datum[self.CONST.tag_SRC_ADDR] = my_src
        if self.CONST.tag_DST_ADDR not in my_datum \
         and my_dst != None:
          my_datum[self.CONST.tag_DST_ADDR] = my_dst
        self.irciot_check_datum_(my_datum, in_vuid, my_ot)
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

 def irciot_decrypt_datum_(self, in_datum, in_header, \
   orig_json, in_vuid = None):
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
  if self.CONST.tag_ENC_METHOD not in in_datum.keys():
    my_em = self.CONST.tag_ENC_BASE64
  else:
    my_em = in_datum[self.CONST.tag_ENC_METHOD]
  my_defrag_header = (my_dt, my_ot, my_src, my_dst, \
   my_dc, my_dp, my_bc, my_bp, my_did)
  my_in = in_datum[self.CONST.tag_ENC_DATUM]
  return self.irciot_defragmentation_(my_in, \
    my_defrag_header, orig_json, in_vuid)
  #
  # End of irciot_decrypt_datum_()

 def irciot_prepare_datum_(self, in_datum, in_header, \
   orig_json, in_vuid = None):
  if not self.CONST.tag_ENC_DATUM in in_datum.keys():
    (my_dt, my_ot, my_src, my_dst, my_dc, my_dp) = in_header
    if self.CONST.tag_DATE_TIME not in in_datum.keys():
      in_datum[self.CONST.tag_DATE_TIME] = my_dt
    if self.CONST.tag_OBJECT_TYPE not in in_datum.keys():
      in_datum[self.CONST.tag_OBJECT_TYPE] = my_ot
    if self.CONST.tag_SRC_ADDR not in in_datum.keys():
      in_datum[self.CONST.tag_SRC_ADDR] = my_src
    if self.CONST.tag_DST_ADDR not in in_datum.keys():
      in_datum[self.CONST.tag_DST_ADDR] = my_dst
    if in_datum[self.CONST.tag_DATE_TIME] == None:
      del in_datum[self.CONST.tag_DATE_TIME]
  else:
    return self.irciot_decrypt_datum_(in_datum, in_header, \
     orig_json, in_vuid)
  return json.dumps(in_datum, separators=(',',':'))
  #
  # End of irciot_prepare_datum_()

 def irciot_check_datum_(self, in_datum, in_vuid = None, in_ot = None):
  if not isinstance(in_vuid, str):
    return
  if not isinstance(in_datum, dict):
    return
  for my_key in [
    self.CONST.tag_DATUM_ID,
    self.CONST.tag_DATE_TIME ]:
    if not my_key in in_datum.keys():
      return
  if in_ot in [
     self.CONST.ot_BCH_INFO,
     self.CONST.ot_BCH_ACK ]:
    if in_ot == self.CONST.ot_BCH_ACK:
      # It is necessary to check whether the request
      # (ot == "bchreq") was, or is it a fake answer
      pass
    for my_key in [
      self.CONST.tag_BCH_METHOD,
      self.CONST.tag_BCH_PUBKEY ]:
      if my_key not in in_datum.keys():
        return
    my_method = in_datum[self.CONST.tag_BCH_METHOD]
    if my_method != self.__mid_method and DO_auto_blockchain:
      self.irciot_load_blockchain_methods_(my_method)
    my_public_key = in_datum[self.CONST.tag_BCH_PUBKEY]
    if not isinstance(my_public_key, str):
      return
    self.irciot_blockchain_update_foreign_key_( \
      in_vuid, my_public_key)
  elif in_ot == self.CONST.ot_BCH_REQUEST:
    self.irciot_blockchain_key_publication_( \
    self.__blockchain_public_key, \
    self.CONST.ot_BCH_ACK, in_vuid)
  elif in_ot in [
     self.CONST.ot_ENC_INFO,
     self.CONST.ot_ENC_ACK ]:
    if in_ot == self.CONST.ot_ENC_ACK:
      # It is necessary to check whether the request
      # (ot == "encreq") was, or is it a fake answer
      pass
    for my_key in [
      self.CONST.tag_ENC_METHOD,
      self.CONST.tag_ENC_PUBKEY ]:
      if my_key not in in_datum.keys():
        return
    my_method = in_datum[self.CONST.tag_ENC_METHOD]
    if my_method != self.crypt_method and DO_auto_encryption:
      self.irciot_load_encryption_methods_(my_method)
    my_string_key = in_datum[self.CONST.tag_ENC_PUBKEY]
    if not isinstance(my_string_key, str):
      return
    my_algo = self.irciot_crypto_get_algorithm_(my_method)
    if my_algo == self.CONST.crypto_RSA:
      if self.__crypt_RSA == None:
        return
      self.irciot_encryption_update_foreign_key_( \
        in_vuid, my_string_key)
  elif in_ot == self.CONST.ot_ENC_REQUEST:
    self.irciot_encryption_key_publication_( \
    self.__encryption_public_key, \
    self.CONST.ot_ENC_ACK, in_vuid)
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
  if isinstance(iot_datums, dict):
    iot_datums = [ iot_datums ]
  if isinstance(iot_datums, list):
    str_datums = ""
    for iot_datum in iot_datums:
      if in_vuid != None:
        self.irciot_check_datum_(iot_datum, in_vuid, iot_ot)
      str_datum = self.irciot_prepare_datum_(iot_datum, \
        (iot_dt, iot_ot, iot_src, iot_dst, iot_dc, iot_dp), \
          orig_json, in_vuid)
      if str_datum != "":
        if str_datums != "":
          str_datums += ","
        str_datums += str_datum
    return str_datums
  return ""
  #
  # End of irciot_deinencap_object_()

 def irciot_remove_text_tags_(self, in_json, in_tags):
   if not isinstance(in_json, str):
     return ""
   if not isinstance(in_tags, list):
     self.irciot_remove_text_tags_(in_json, [in_tags])
   my_json = in_json
   for my_item in in_tags:
     if not isinstance(my_item, str):
       continue
     my_mark = '"{}":'.format(my_item)
     my_parts = my_json.split(my_mark)
     if len(my_parts) != 2:
       continue
     my_out  = my_parts[0] + my_mark
     my_part = my_parts[1]
     skip_type = bool(my_part[0] == '"')
     skip_step = 0
     skip_chars = self.CONST.irciot_chars_base + '"'
     if not skip_type:
       skip_chars = self.CONST.irciot_chars_digit
       skip_step = 1
     for my_ch in my_part:
       if skip_type and my_ch == '"':
         if skip_step == 0:
           my_out += '"'
         skip_step += 1
       if skip_step != 1:
         my_out += my_ch
       elif not my_ch in skip_chars:
         break
     if skip_step > 1:
       my_json = my_out
   return my_json
   #
   # End of irciot_remove_tags_()

 def irciot_check_integrity_(self, in_json, in_dict):
   if not isinstance(in_json, str):
     return False
   if not isinstance(in_dict, dict):
     return False
   if self.integrity_check == 1:
     if self.CONST.tag_CHK_CRC16 in in_dict.keys():
       my_crc16 = in_dict[self.CONST.tag_CHK_CRC16]
       if not self.is_irciot_hex_(my_crc16) or len(my_crc16) != 4:
         return False
       my_json = self.irciot_remove_text_tags_(in_json, \
         [ self.CONST.tag_MESSAGE_ID, self.CONST.tag_CHK_CRC16 ])
       my_crc16_json = self.irciot_crc16_(bytes(my_json, self.__encoding))
       del my_json
       if my_crc16 != my_crc16_json:
         return False
   elif self.integrity_check == 2:
     if self.CONST.tag_CHK_CRC32 in in_dict.keys():
       my_crc32 = in_dict[self.CONST.tag_CHK_CRC32]
       if not self.is_irciot_hex_(my_crc32) or len(my_crc32) != 8:
         return False
       my_json = self.irciot_remove_text_tags_(in_json, \
         [ self.CONST.tag_MESSAGE_ID, self.CONST.tag_CHK_CRC32 ])
       my_crc32_json = self.irciot_crc32_(bytes(my_json, self.__encoding))
       del my_json
       if my_crc32 != my_crc32_json:
         return False
   return True
   #
   # End of rciot_check_integrity_()

 def irciot_check_container_(self, in_container, \
   orig_json = None, in_vuid = None):

  def check_blockchain_(self, in_json, in_mesmid, in_newmid, in_key):
    if in_mesmid == in_newmid:
      return False
    my_message = in_json.replace( \
      '"' + self.CONST.tag_MESSAGE_ID + '":"' + in_mesmid + '"', \
      '"' + self.CONST.tag_MESSAGE_ID + '":"' + in_newmid + '"')
    return self.irciot_blockchain_verify_string_( \
      my_message, in_mesmid, in_key)
    #
    # End of irciot_check_container:irciot_check_blockchain_()

  if not isinstance(orig_json, str):
    return False
  if not isinstance(in_container, dict):
    return False
  if in_vuid == None:
    return True
  if self.integrity_check > 0:
    if not self.irciot_check_integrity_(self, orig_json):
      return False
  try:
    my_hismid = str(in_container[self.CONST.tag_MESSAGE_ID])
  except:
    return False
  try:
    # Blockchain exchange has only one object in container
    # trying to get object type directly from IRC-IoT message
    my_object = in_container[self.CONST.tag_OBJECT]
    my_ot = my_object[self.CONST.tag_OBJECT_TYPE]
  except:
    my_ot = None
  if len(my_hismid) < 2:
    self.irciot_blockchain_update_last_mid_(in_vuid, my_hismid)
    my_hismid_method = ""
  else:
    my_hismid_method = my_hismid[:2]
  if not my_hismid_method in [
   self.CONST.tag_mid_ED25519,
   self.CONST.tag_mid_RSA1024,
   self.CONST.tag_mid_GOST12 ]:
    self.irciot_blockchain_update_last_mid_(in_vuid, my_hismid)
    return True
  if my_ot in [
   self.CONST.ot_BCH_INFO,
   self.CONST.ot_BCH_REQUEST,
   self.CONST.ot_BCH_ACK ]:
    if DO_debug_library:
      print("\033[1;33mBLOCKCHAIN TEST SKIPPED OT '{}' \033[0m".format(my_ot))
    self.irciot_blockchain_update_last_mid_(in_vuid, my_hismid)
    return True
  my_bkey = self.irciot_blockchain_get_foreign_key_(in_vuid)
  if my_bkey == None:
    # We trust the message signed by the blockchain without
    # any verification if we do not yet have a public key.
    # It is useful in order to accept a key for this user.
    return True
  if my_hismid_method == self.CONST.tag_mid_ED25519:
    try:
      # For performance optimization the public key may be
      # moved to Virtual User Database instead of string form
      my_verify_key = self.__crypt_NACS.VerifyKey(my_bkey, \
        encoder = self.__crypt_NACE.HexEncoder )
    except: # Incorrect Public Key
      return False
  elif my_hismid_method == self.CONST.tag_mid_RSA1024:
    # Not implemented yet
    return False
  elif my_hismid_method == self.CONST.tag_mid_GOST12:
    my_verify_key = my_bkey
    # return False
  self.irciot_blockchain_update_last_mid_(in_vuid, my_hismid)
  if my_hismid == None:
    return True
  if DO_debug_library:
    print('MAIN BLOCKCHAIN CHECK')
  my_newmids = self.irciot_blockchain_get_own_mids_(in_vuid)
  my_result  = False
  if isinstance(my_newmids, list):
    for my_newmid in reversed(my_newmids):
      if my_newmid == None:
        continue
      my_result = check_blockchain_( self, \
        orig_json, my_hismid, my_newmid, my_verify_key )
      if my_result:
        break
  if not my_result:
    if DO_debug_library:
      print("ALTERNATIVE BLOCKCHAIN CHECK")
    my_vuid_list = self.irciot_get_vuid_list_(self.CONST.api_vuid_all)
    my_vuid_list.append(self.CONST.api_vuid_self)
    my_mids = [ my_newmid, my_hismid ]
    for my_vuid in my_vuid_list:
      if my_vuid == in_vuid:
        continue # The User already checked
      if DO_debug_library:
        print("Checking blockcahin for VUID = '{}' ...".format(my_vuid))
      my_newmids = self.irciot_blockchain_get_own_mids_(in_vuid)
      if isinstance(my_newmids, list):
        for my_newmid in reversed(my_newmids):
          if not my_newmid in my_mids and my_newmid != None:
            my_result = check_blockchain_( self, \
              orig_json, my_hismid, my_newmid, my_verify_key )
            if my_result:
              break
        if my_result:
          break
        my_mids += my_newmids
      my_newmids = self.irciot_blockchain_get_last_mids_(in_vuid)
      if isinstance(my_newmids, list):
        for my_newmid in reversed(my_newmids):
          if not my_newmid in my_mids and my_newmid != None:
            my_result = check_blockchain_( self, \
              orig_json, my_hismid, my_newmid, my_verify_key )
            if my_result:
              break
        if my_result:
          break
        my_mids += my_newmids
    del my_mids
  if DO_debug_library:
    if my_result:
      print("\033[1;45m BLOCKCHAIN VERIFICATION OK \033[0m")
    else:
      print("\033[1;41m BLOCKCHAIN VERIFICATION FAILED \033[0m")
  return my_result
  #
  # End of irciot_check_container_()

 def irciot_deinencap_container_(self, in_container, \
   orig_json = None, in_vuid = None):
  if self.CONST.tag_VERSION in in_container.keys():
    if in_container[self.CONST.tag_VERSION] == "?":
      # Protocol Version Reply
      if self.__mid_method == "":
        self.current_mid += 1
        my_message = '{{"{}":"{}","{}":"{}"}}'.format( \
         self.CONST.tag_MESSAGE_ID, self.current_mid, \
         self.CONST.tag_VERSION, self.CONST.irciot_protocol_version)
        if len(in_container) == 2:
          return my_message
        else:
          my_pack = (my_message, in_vuid)
          self.output_pool.append(my_pack)
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
      if str_datum != "":
        if str_datums != "":
           str_datums += ","
        str_datums += str_datum
    #if str_datums != "":
    #   str_datums = "[" + str_datums + "]"
    return str_datums
  if isinstance(iot_objects, dict):
    return self.irciot_deinencap_object_(iot_objects, \
      orig_json, in_vuid)
    if str_datums != "":
      str_datums = "[" + str_datums + "]"
    return str_datums
  return ""
  #
  # End of irciot_deinencap_container_()

 def irciot_deinencap_(self, in_json, in_vuid = None):
  ''' First/simple implementation of IRC-IoT "Datum" deinencapsulator '''
  self.irciot_check_mtu_()
  self.irciot_check_encoding_()
  self.irciot_blockchain_check_publication_()
  self.irciot_encryption_check_publication_()
  try:
    iot_containers = json.loads(in_json)
  except ValueError:
    return ""
  if isinstance(iot_containers, dict):
    iot_containers = [ iot_containers ]
  if isinstance(iot_containers, list):
    str_datums = "["
    for iot_container in iot_containers:
      str_datum = self.irciot_deinencap_container_(iot_container, \
        in_json, in_vuid)
      # To check the blockchain id of each message, it is necessary
      # to cut the messages into separate substrings, exactly as they
      # came in, but not reassemble it by json.loads() and dumps()
      if str_datum != "":
        if str_datums != "[":
           str_datums += ","
        str_datums += str_datum
    return str_datums + "]"
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
      if not self.is_irciot_datum_(my_datum, None, None, None):
        return False
    return True
  if isinstance(my_datums, dict):
    if not self.is_irciot_datum_(my_datums, None, None, None):
      return False
    return True
  return False
  #
  # End of is_irciot_datumset_()

 def irciot_encap_datum_(self, in_datum, in_ot, in_src, in_dst):
  if not self.CONST.tag_ENC_DATUM in in_datum.keys():
    if in_ot == in_datum[self.CONST.tag_OBJECT_TYPE]:
      del in_datum[self.CONST.tag_OBJECT_TYPE]
    if in_src == in_datum[self.CONST.tag_SRC_ADDR]:
      del in_datum[self.CONST.tag_SRC_ADDR]
    if in_dst == in_datum[self.CONST.tag_DST_ADDR]:
      del in_datum[self.CONST.tag_DST_ADDR]
  return json.dumps(in_datum, separators=(',',':'))
  #
  # End of irciot_encap_datum_()

 def irciot_encap_internal_(self, in_datumset, in_vuid = None):
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
      if my_datums_cnt == 0:
        my_ot  = my_datum[self.CONST.tag_OBJECT_TYPE]
        my_ot_cnt  = 1
        my_src = my_datum[self.CONST.tag_SRC_ADDR]
        my_src_cnt = 1
        my_dst = my_datum[self.CONST.tag_DST_ADDR]
        my_dst_cnt = 1
      else:
        if my_ot  == my_datum[self.CONST.tag_OBJECT_TYPE]:
           my_ot_cnt += 1
        if my_src == my_datum[self.CONST.tag_SRC_ADDR]:
           my_src_cnt += 1
        if my_dst == my_datum[self.CONST.tag_DST_ADDR]:
           my_dst_cnt += 1
      my_datums_cnt += 1
    my_datums_cnt = len(my_datums)
    if my_ot_cnt  < my_datums_cnt:
       my_ot  = None
    if my_src_cnt < my_datums_cnt:
       my_src = None
    if my_dst_cnt < my_datums_cnt:
       my_dst = None
    for my_datum in my_datums:
      if my_irciot != "":
         my_irciot += ","
      my_irciot += self.irciot_encap_datum_( \
       my_datum, my_ot, my_src, my_dst)
    if my_datums_cnt > 1:
      my_irciot = "[" + my_irciot + "]"
    my_irciot = '"' + self.CONST.tag_DATUM + '":' + my_irciot
  elif isinstance(my_datums, dict):
    if self.CONST.tag_OBJECT_TYPE in my_datums.keys():
      my_ot  = my_datums[self.CONST.tag_OBJECT_TYPE]
      if self.CONST.tag_ENC_DATUM in my_datums.keys():
        del my_datums[self.CONST.tag_OBJECT_TYPE]
    if self.CONST.tag_SRC_ADDR in my_datums:
       my_src = my_datums[self.CONST.tag_SRC_ADDR]
    if self.CONST.tag_DST_ADDR in my_datums:
       my_dst = my_datums[self.CONST.tag_DST_ADDR]
    if self.is_irciot_datum_(my_datums, my_ot, my_src, my_dst):
       my_irciot = '"' + self.CONST.tag_DATUM + '":' \
        + self.irciot_encap_datum_(my_datums, my_ot, my_src, my_dst)
  str_object = '"' + self.CONST.tag_OBJECT \
   + '":{"' + self.CONST.tag_OBJECT_ID \
   + '":"' + str(self.current_oid) + '",'
  if my_ot  != None:
    str_object += '"' + self.CONST.tag_OBJECT_TYPE \
     + '":"'  + my_ot  + '",'
  if my_src != None:
    str_object += '"' + self.CONST.tag_SRC_ADDR \
     + '":"' + my_src + '",'
  if my_dst != None:
    str_object += '"' + self.CONST.tag_DST_ADDR \
     + '":"' + my_dst + '",'
  save_mid = self.current_mid
  sign_mid = self.current_mid
  if self.__mid_method in [
    self.CONST.tag_mid_ED25519,
    self.CONST.tag_mid_RSA1024,
    self.CONST.tag_mid_GOST12 ]:
    if in_vuid != None:
      my_mids = self.irciot_blockchain_get_last_mids_(in_vuid)
      if isinstance(my_mids, list) and my_mids != []:
        sign_mid = my_mids[-1]
  str_container = '{"' + self.CONST.tag_MESSAGE_ID + '":"'
  str_for_sign  = str_container + str(sign_mid)
  str_for_sign += '",' + str_object + my_irciot + "}}"
  if self.__mid_method == "": # Default mid method
    if not isinstance(self.current_mid, int):
      self.current_mid = random.randint( 10000, 99999)
    self.current_mid += 1
  elif self.__mid_method in [
    self.CONST.tag_mid_ED25519,
    self.CONST.tag_mid_RSA1024,
    self.CONST.tag_mid_GOST12 ]:
    sign_hash = self.irciot_blockchain_sign_string_( \
      str_for_sign, self.__blockchain_private_key)
    if sign_hash == None:
      return ""
    self.current_mid = sign_hash
    if not in_vuid in [ None, self.CONST.api_vuid_all ]:
      self.irciot_blockchain_update_own_mid_( \
        in_vuid, sign_hash )
    else:
      my_vuid_list = self.irciot_get_vuid_list_(self.CONST.api_vuid_all)
      if my_vuid_list != []:
        for my_vuid in my_vuid_list:
          self.irciot_blockchain_update_own_mid_( \
            my_vuid, sign_hash )
  str_container += str(self.current_mid) + '",'
  my_irciot = str_container + str_object + my_irciot + "}}"
  # + '"oc":1,"op":1,' # Must be implemented later
  return my_irciot
  #
  # End of irciot_encap_internal_()

 def irciot_encap_bigdatum_(self, my_bigdatum, my_part, \
    in_vuid = None):
  ''' Hidden part of encapsulator creates mutlipart "Datum" '''
  save_mid  = self.current_mid
  big_datum = {}
  big_ot = None
  if isinstance(my_bigdatum, dict):
    big_datum = my_bigdatum
    big_ot = my_bigdatum[self.CONST.tag_OBJECT_TYPE]
    del my_datum[self.CONST.tag_OBJECT_TYPE]
  if isinstance(my_bigdatum, list):
    for my_idx, my_datum in enumerate(my_bigdatum):
      if my_idx == 0:
        big_datum = my_datum
        big_ot = my_datum[self.CONST.tag_OBJECT_TYPE]
        del my_datum[self.CONST.tag_OBJECT_TYPE]
  if big_ot == None:
    return ("", 0)
  str_big_datum = json.dumps(big_datum, separators=(',',':'))
  if self.crypt_compress == self.CONST.compress_ZLIB:
    if DO_auto_compress and self.__crypt_ZLIB == None:
      self.irciot_load_compression_methods_(self.crypt_method)
    if self.__crypt_ZLIB == None:
      return ("", 0)
    bin_big_datum \
     = self.__crypt_ZLIB.compress(bytes(str_big_datum, \
       self.__encoding))
  elif self.crypt_compress == self.CONST.compress_BZIP2:
    if DO_auto_compress and self.__crypt_BZ2 == None:
      self.irciot_load_compression_methods_(self.crypt_method)
    if self.__crypt_BZ2 == None:
      return ("", 0)
    bin_big_datum \
     = self.__crypt_BZ2.compress(bytes(str_big_datum, \
       self.__encoding))
  elif self.crypt_compress == self.CONST.compress_NONE:
    bin_big_datum = bytes(str_big_datum, self.__encoding)
  else: # Unknwon compression
    return ("", 0)
  if big_ot in [
    self.CONST.ot_ENC_INFO, self.CONST.ot_ENC_ACK,
    self.CONST.ot_BCH_INFO, self.CONST.ot_BCH_ACK,
    self.CONST.ot_ENC_REQUEST,
    self.CONST.ot_BCH_REQUEST ]:
     pass
  elif self.crypt_algo == self.CONST.crypto_RSA:
    my_string_key \
     = self.irciot_encryption_get_foreign_key_(in_vuid)
    if not isinstance(my_string_key, str):
      return ("", 0)
    ( my_own, my_binary_key ) \
     = self.irciot_crypto_str_to_hash_('__' + my_string_key)
    try:
      my_object_key = self.__crypt_RSA.importKey(my_binary_key)
    except:
      self.irciot_error_(self.CONST.err_RSA_KEY_FORMAT, 0)
      return ("", 0)
    if not isinstance(my_object_key, object):
      self.irciot_error_(self.CONST.err_RSA_KEY_FORMAT, 0)
      return ("", 0)
    crypt_big_datum = self.irciot_crypto_RSA_encrypt_( \
      bin_big_datum, my_object_key )
    if crypt_big_datum == None:
      return ("", 0)
    bin_big_datum = crypt_big_datum
  elif self.crypt_algo == self.CONST.crypto_AES:
    crypt_big_datum = self.irciot_crypto_AES_encrypt_( \
     bin_big_datum, self.__encryption_private_key )
    if crypt_big_datum == None:
      return ("", 0)
    bin_big_datum = crypt_big_datum
  elif self.crypt_algo == self.CONST.crypto_2FISH:
    crypt_big_datum = self.irciot_crypto_2fish_encrypt_ ( \
      bin_big_datum, self.__encryption_private_key )
    if crypt_big_datum == None:
      return ("", 0)
    bin_big_datum = crypt_big_datum
  if self.crypt_base == self.CONST.base_BASE64:
    base_big_datum = base64.b64encode(bin_big_datum)
  elif self.crypt_base == self.CONST.base_BASE85:
    base_big_datum = base64.b85encode(bin_big_datum)
  elif self.crypt_base == self.CONST.base_BASE32:
    base_big_datum = base64.b32encode(bin_big_datum)
  else: # Unknown base encoding
    return ("", 0)
  del bin_big_datum
  raw_big_datum  = str(base_big_datum)[2:-1]
  if self.crypt_base == self.CONST.base_BASE32 \
  or self.crypt_base == self.CONST.base_BASE64:
    while (raw_big_datum[-1] == "="):
      raw_big_datum = raw_big_datum[:-1]
  del base_big_datum
  my_bc = len(raw_big_datum)
  out_big_datum  = '{"' + self.CONST.tag_ENC_DATUM
  out_big_datum += '":"' + raw_big_datum + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum, in_vuid)
  self.current_mid = save_mid # mid rollback
  out_skip  = len(my_irciot)
  out_head  = len(big_ot)
  if self.__mid_method in [
     self.CONST.tag_mid_ED25519,
     self.CONST.tag_mid_RSA1024,
     self.CONST.tag_mid_GOST12 ]:
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
  out_skip += out_head - self.__message_MTU
  out_big_datum = '{' \
   + '"' + self.CONST.tag_OBJECT_TYPE + '":"' + big_ot \
   + '","' + self.CONST.tag_DATUM_ID \
   + '":"' + str(self.current_did) \
   + '","' + self.CONST.tag_DATUM_BC + '":' + str(my_bc) \
   + ',"' + self.CONST.tag_DATUM_BP + '":' + str(my_part) \
   + ',"' + self.CONST.tag_ENC_DATUM + '":"'
  my_okay = self.__message_MTU - out_head - 43 # Must be calculated
  my_size = my_bc - my_part
  if my_size > my_okay:
    my_size = my_okay
  out_big_datum += raw_big_datum[my_part:my_part + my_size] + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum, in_vuid)
  if my_size < my_okay:
    return (my_irciot, 0)
  return (my_irciot, len(raw_big_datum) + my_part - out_skip)
  #
  # End of irciot_encap_bigdatum_()

 def irciot_encap_all_(self, in_datumset, in_vuid = None):
  self.irciot_check_mtu_()
  self.irciot_check_encoding_()
  if not in_vuid in [
   self.CONST.api_vuid_all,
   self.CONST.api_vuid_cfg,
   self.CONST.api_vuid_tmp ]:
    self.irciot_blockchain_check_publication_()
    self.irciot_encryption_check_publication_()
  result = self.output_pool
  self.output_pool = []
  if isinstance(in_datumset, dict):
    in_datumset = [ in_datumset ]
  my_datumset = json.dumps(in_datumset, separators=(',',':'))
  if in_vuid in [
   self.CONST.api_vuid_all,
   self.CONST.api_vuid_cfg,
   self.CONST.api_vuid_tmp ]:
    if in_vuid == self.CONST.api_vuid_all \
     and self.crypt_model == self.CONST.crypt_NO_ENCRYPTION:
      result += self.irciot_encap_all_(in_datumset, None)
      return result
    # If the message is to be encrypted with end-to-end encryption
    # then it is need to create a separate message for each VUID
    # Also, the same when no encryption but type of VUID is defined
    my_vuid_list = self.irciot_get_vuid_list_(in_vuid)
    if my_vuid_list == []:
      return result
    for my_vuid in my_vuid_list:
      if in_vuid in [
        self.CONST.api_vuid_cfg,
        self.CONST.api_vuid_tmp ]:
        if my_vuid[0] != in_vuid:
          continue
      result += self.irciot_encap_all_(in_datumset, my_vuid)
    return result
  json_text, my_skip, my_part \
   = self.irciot_encap_(my_datumset, 0, 0, in_vuid)
  if json_text != "":
    result.append((json_text, in_vuid))
  while (my_skip > 0 or my_part > 0):
    json_text, my_skip, my_part \
     = self.irciot_encap_(my_datumset, my_skip, my_part, in_vuid)
    if json_text != "":
      result.append((json_text, in_vuid))
  return result
  #
  # End of irciot_encap_all_()

 def irciot_encap_(self, in_datumset, in_skip, in_part, \
   in_vuid = None):
  ''' Public part of encapsulator with per-"Datum" fragmentation '''
  self.irciot_check_mtu_()
  self.irciot_check_encoding_()
  self.irciot_blockchain_check_publication_()
  self.irciot_encryption_check_publication_()
  # my_encrypt = CAN_encrypt_datum and DO_always_encrypt
  my_encrypt = False
  my_datums_set  = in_datumset
  my_datums_skip = 0
  my_datums_part = 0
  save_mid  = self.current_mid
  my_irciot = ""
  try:
    my_datums = json.loads(in_datumset)
  except:
    return "", 0, 0
  my_total  = len(my_datums)
  if in_skip > 0:
    my_datums_obj = []
    my_datums_cnt = 0
    for my_datum in my_datums:
      my_datums_cnt += 1
      if my_datums_cnt > in_skip:
        my_datums_obj.append(my_datum)
    my_datums_set = json.dumps(my_datums_obj, separators=(',',':'))
    my_datums = json.loads(my_datums_set)
    del my_datums_obj
    del my_datums_cnt
  my_irciot = self.irciot_encap_internal_(my_datums_set, in_vuid)
  if (len(my_irciot) > self.__message_MTU) or my_encrypt:
    if in_skip == 0:
      self.current_mid = save_mid # mid rollback
    my_datums = json.loads(my_datums_set)
    one_datum = 0
    if isinstance(my_datums, list):
      my_datums_total = len(my_datums)
      if my_datums_total > 1:
        my_datums_skip = my_datums_total
        while (len(my_irciot) > self.__message_MTU) \
         and (my_datums_skip <= my_datums_total):
          part_datums = []
          my_datums_cnt = 0
          for my_datum in my_datums:
            if my_datums_cnt < my_datums_skip:
              part_datums.append(my_datum)
            my_datums_cnt += 1
          if part_datums == []:
            break
          str_part_datums = json.dumps(part_datums, separators=(',',':'))
          self.current_mid = save_mid # mid rollback
          my_irciot = self.irciot_encap_internal_(str_part_datums, in_vuid)
          if len(my_irciot) <= self.__message_MTU:
            my_skip_out = in_skip + my_datums_skip
            if my_skip_out >= my_total:
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
    if one_datum == 1:
      self.current_mid = save_mid # Message ID rollback
      (my_irciot, my_datums_part) \
       = self.irciot_encap_bigdatum_(my_datums, in_part, in_vuid)
      if my_datums_part == 0:
        my_datums_skip += 1
  else:
    my_datums_skip = my_total - in_skip
    self.current_did += 1 # Default Datum ID changing method
  if my_datums_part == 0:
    self.current_oid += 1
  if in_skip + my_datums_skip >= my_total:
   in_skip = 0
   my_datums_skip = 0
   if CAN_encrypt_datum and my_datums_part == 0:
     self.__crypt_cache = None
  return my_irciot, in_skip + my_datums_skip, my_datums_part
  #
  # End of irciot_encap_()

