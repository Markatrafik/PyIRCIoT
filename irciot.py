'''
'' PyIRCIoT
''
'' Copyright (c) 2018 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

import json
import random
import base64

#from copy import deepcopy
#from pprint import pprint

class PyIRCIoT(object):

 class CONST(object):
  #
  irciot_protocol_version = '0.3.10'
  #
  irciot_library_version  = '0.0.18'
  #
  # Errors
  #
  err_DEFRAG_INVALID_DID  = 103
  err_CONTENT_MISSMATCH   = 104
  err_DEFRAG_DP_MISSING   = 105
  err_DEFRAG_BP_MISSING   = 106
  err_DEFRAG_DC_EXCEEDED  = 107
  err_DEFRAG_BC_EXCEEDED  = 108
  err_OVERLAP_MISSMATCH   = 109
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
  self.mid_method  = 0
  self.oid_method  = 0
  self.did_method  = 0
  #
  # 0 is autoincrement
  #
  random.seed()
  if self.mid_method == 0:
     self.current_mid = random.randint( 10000, 99999)
  if self.oid_method == 0:
     self.current_oid = random.randint(  1000,  9999)
  if self.did_method == 0:
     self.current_did = random.randint(   100,   999)
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
  pass 
 
 def irciot_set_mtu_(self, my_mtu):
  if (my_mtu < 128):
     return
  self.message_mtu = my_mtu
 
 def is_irciot_datum_(self, in_datum, in_ot, in_src, in_dst):
  # Object Type filed must exists or inherits
  if "ed" in in_datum:
     if isinstance(in_datum['ed'], str):
        return True
  if not "ot" in in_datum:
     if (in_ot == None):
        return False
  else:
     if not isinstance(in_datum['ot'], str):
        return False
  # Fragmented message header:
  if "bc" in in_datum:    # Bytes Count must be int
     if not isinstance(in_datum['bc'], int):
        return False
     if "bp" in in_datum: # Bytes Passed must be int
        if not isinstance(in_datum['bp'], int):
           return False
        if (in_datum['bp'] > in_datum['bc']):
           return False
  # Source address field must exists or inherits
  if not "src" in in_datum:
     if (in_src == None):
        return False
  else:
     if not isinstance(in_datum['src'], str):
        return False
  # Destination address field must exits or ihnerits
  if not "dst" in in_datum:
     if (in_dst == None):
        return False
  else:
     if not isinstance(in_datum['dst'], str):
        return False
  return True
  # End of is_irciot_datum_()

 def is_irciot_(self, my_json):
  ''' Сhecks whether the text string is a IRC-IoT message or not '''
  
  def is_irciot_object_(self, in_object):
    if not "oid" in in_object:   # IRC-IoT Object ID
       return False
    if (in_object['oid'] == ""):
       return False
    if not "ot" in in_object:    # Default Object Type of Datums
       in_object['ot'] = None    # it will test all datums for 'ot'
    if (in_object['ot'] == ""):
       return False
    if not "d" in in_object:     # IRC-IoT Datum-set
       return False
    my_datums = in_object['d'] 
    my_src = None
    if "src" in in_object:
       my_src = in_object['src']
    my_dst = None
    if "dst" in in_object:
       my_dst = in_object['dst']
    # Fragmented message header:
    if "dc" in in_object:    # Datums Count must be int
       if not isinstance(in_object['dc'], int):
          return False
       if "dp" in in_object: # Datums Passed must be int
          if not isinstance(in_datum['dp'], int):
             return False
          if (in_object['bp'] > in_object['bc']):
             return False
    # Go deeper
    if isinstance(my_datums, list):
       for my_datum in my_datums:
          if (not self.is_irciot_datum_(my_datum, \
           in_object['ot'], my_src, my_dst)):
             return False
       return True
    if isinstance(my_datums, dict):
       if not self.is_irciot_datum_(my_datums, \
        in_object['ot'], my_src, my_dst):
          return False
    return True
    # End of is_irciot_object_()

  def is_irciot_container_(self, in_container):
    if not "mid" in in_container:
       return False
    if (in_container['mid'] == ""): # IRC-IoT Message ID
       return False
    if "oc" in in_container:        # Objects Count must be int
       if not isinstance(in_container['oc'], int):
          return False
    else:
       in_container['oc'] = 1
    if "op" in in_container:        # Objects Passed must be int
       if not isinstance(in_container['op'], int):
          return False
       if (in_container['op'] > in_container['oc']):
          return False
    else:
       in_container['op'] = 1
    if not "o" in in_container:     # IRC-IoT Object must exists
       return False
    my_objects = in_container['o']
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
    # End of is_irciot_container_()

  # Begin of is_irciot_()
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
  # End of is_irciot_()
  
 def irciot_clear_defrag_chain_(self, my_did):
  try:
    if self.defrag_lock:
       return
    self.defrag_lock = True
    for my_item in self.defrag_pool:
       (test_b64p, test_header, test_json) = my_item
       (test_dt, test_ot, test_src, test_dst, \
        test_dc, test_dp, test_bc, test_bp, test_did) = test_header
       if (my_did == test_did):
          self.defrag_pool.remove(my_item)
    self.defrag_lock = False
  except:
    self.defrag_lock = False
  
 def irciot_defragmentation_(self, my_b64p, my_header, orig_json):
  (my_dt, my_ot, my_src, my_dst, \
   my_dc, my_dp, my_bc, my_bp, my_did) = my_header
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
    (test_b64p, test_header, test_json) = my_item
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
               if (test_b64p == my_b64p):
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
                     defrag_item = (my_dp, my_b64p)
                     defrag_array.append(defrag_item)
                  defrag_item = (test_dp, test_b64p)
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
                        my_b64p + defrag_buffer[my_bp + len(my_b64p):]
                  if (defrag_buffer != ""):
                     # here will be a comparison of overlapping buffer intervals
                     defrag_buffer = defrag_buffer[:test_bp] + \
                        str(test_b64p) + defrag_buffer[test_bp + len(test_b64p):]
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
    my_new = True
  if (my_err > 0):
    self.irciot_clear_defrag_chain_(my_did)
    return ""
  if my_new:
    my_item = (my_b64p, my_header, orig_json)
    self.defrag_lock = True
    self.defrag_pool.append(my_item)
    self.defrag_lock = False
  if (my_ok > 0):
    if (my_ok == 1):
       pass
    elif (my_ok == 2):
       self.irciot_clear_defrag_chain_(my_did)
       try:
          out_json = str(base64.b64decode(defrag_buffer))[2:-1]
          # Adding missing fields to the Datum from parent object
          my_datum = json.loads(out_json)
          if ((not "ot" in my_datum) and (my_ot != None)):
              my_datum['ot'] = my_ot
          if ((not "dt" in my_datum) and (my_dt != None)):
              my_datum['dt'] = my_dt
          if ((not "src" in my_datum) and (my_src != None)):
              my_datum['src'] = my_src
          if ((not "dst" in my_datum) and (my_dst != None)):
              my_datum['dst'] = my_dst
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
  # End of irciot_defragmentation_()

 def irciot_decrypt_datum_(self, my_datum, my_header, orig_json):
  (my_dt, my_ot, my_src, my_dst, my_dc, my_dp) = my_header
  my_bc  = None
  my_bp  = None
  my_did = None
  if not 'ed' in my_datum.keys():
     return ""
  if 'bc' in my_datum.keys():
     my_bc = my_datum['bc']
  if 'bp' in my_datum.keys():
     my_bp = my_datum['bp']
  if 'did' in my_datum.keys():
     my_did = my_datum['did']
  if not 'em' in my_datum.keys():
     my_em = 'b64p'
  else:
     my_em = my_datum['em']
  if (my_em == 'b64p'):
     my_defrag_header = (my_dt, my_ot, my_src, my_dst, \
      my_dc, my_dp, my_bc, my_bp, my_did)
     my_b64p = my_datum['ed']
     return self.irciot_defragmentation_(my_b64p, \
      my_defrag_header, orig_json)
  return ""
  # End of irciot_decrypt_datum_()

 def irciot_prepare_datum_(self, my_datum, my_header, orig_json):
  if not 'ed' in my_datum.keys():
     (my_dt, my_ot, my_src, my_dst, my_dc, my_dp) = my_header
     if not 't' in my_datum.keys():
        my_datum['t'] = my_dt
     if not 'ot' in my_datum.keys():
        my_datum['ot'] = my_ot
     if not 'src' in my_datum.keys():
        my_datum['src'] = my_src
     if not 'dst' in my_datum.keys():
        my_datum['dst'] = my_dst
     if (my_datum['t'] == None):
        del my_datum['t']
  else:
     return self.irciot_decrypt_datum_(my_datum, my_header, orig_json)
  return json.dumps(my_datum, separators=(',',':'))
  
 def irciot_deinencap_object_(self, my_object, orig_json):
  iot_dt  = None
  iot_src = None
  iot_dst = None
  iot_dc  = None
  iot_dp  = None
  try:
     iot_datums = my_object['d']
     iot_ot = my_object['ot']
     if 't' in my_object.keys():
        iot_dt  = my_object['t']
     if 'src' in my_object.keys():
        iot_src = my_object['src']
     if 'dst' in my_object.keys():
        iot_dst = my_object['dst']
  except:
     return ""
  if "dc" in my_object:
     if not isinstance(my_object['dc'], int):
        return ""
     iot_dc = my_object['dc']
  else:
     my_object['dc'] = None
     iot_dc = None
  if "dp" in my_object:
     if not isinstance(my_object['dp'], int):
        return ""
     iot_dp = my_object['dp']
  else:
     my_object['dp'] = None
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
  # End of irciot_deinencap_object_()

 def irciot_deinencap_container_(self, my_container, orig_json):
  try:
     iot_objects = my_container['o']
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
  # End of irciot_deinencap_container_()
 
 def irciot_deinencap_(self, my_json):
  ''' First/simple implementation of IRC-IoT "datum" deinencapsulator '''
  try:
     iot_containers = json.loads(my_json)
  except ValueError:
     return ""
  if isinstance(iot_containers, list):
    str_datums = "["
    for iot_container in iot_containers:
       str_datum = self.irciot_deinencap_container_(iot_container, my_json)
       if (str_datum != ""):
          if (str_datums != "["):
             str_datums += ","
          str_datums += str_datum
    return str_datums + "]"
  if isinstance(iot_containers, dict):
    return self.irciot_deinencap_container_(iot_containers, my_json)
  return ""
  # End of irciot_deinencap_container_()
 
 def is_irciot_datumset_(self, my_json):
  try:
     my_datums = json.loads(my_json)
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
  # End of is_irciot_datumset_()
  
 def irciot_encap_datum_(self, in_datum, in_ot, in_src, in_dst):
  if not "ed" in in_datum.keys():
   if (in_ot == in_datum['ot']):
      del in_datum['ot']
   if (in_src == in_datum['src']):
      del in_datum['src']
   if (in_dst == in_datum['dst']):
      del in_datum['dst']
  return json.dumps(in_datum, separators=(',',':'))
  # End of irciot_encap_datum_()
 
 def irciot_encap_internal_(self, my_datumset):
  ''' First/simple implementation of IRC-IoT "datum" set encapsulator '''
  try:
     my_datums = json.loads(my_datumset)
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
           my_ot  = my_datum['ot']
           my_ot_cnt  = 1
           my_src = my_datum['src']
           my_src_cnt = 1
           my_dst = my_datum['dst']
           my_dst_cnt = 1
        else:
           if (my_ot  == my_datum['ot']):
              my_ot_cnt += 1
           if (my_src == my_datum['src']):
              my_src_cnt += 1
           if (my_dst == my_datum['dst']):
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
     my_irciot = '"d":' + my_irciot
  if isinstance(my_datums, dict):
     if "ot" in my_datums:
        my_ot  = my_datums['ot']
        if "ed" in my_datums.keys():
           del my_datums['ot']
     if "src" in my_datums:
         my_src = my_datums['src']
     if "dst" in my_datums:
         my_dst = my_datums['dst']
     if (self.is_irciot_datum_(my_datums, my_ot, my_src, my_dst)):
        my_irciot = '"d":' + self.irciot_encap_datum_( \
         my_datums, my_ot, my_src, my_dst)
  str_object = '"o":{"oid":"' + str(self.current_oid) + '",'
  if (my_ot  != None):
     str_object += '"ot":"'  + my_ot  + '",'
  if (my_src != None):
     str_object += '"src":"' + my_src + '",'
  if (my_dst != None):
     str_object += '"dst":"' + my_dst + '",'
  str_container = '{"mid":"' + str(self.current_mid) + '",'
  # + '"oc":1,"op":1,'  # Must be implemented later
  self.current_mid += 1 # Default mid method
  my_irciot = str_container + str_object + my_irciot + "}}"
  return my_irciot
  # End of irciot_encap_internal_()
  
 def irciot_encap_bigdatum_(self, my_bigdatum, my_part):
  ''' Hidden part of encapsulator creates mutlipart datum '''
  save_mid  = self.current_mid
  big_datum = {}
  big_ot = None
  if isinstance(my_bigdatum, dict):
     big_datum = my_bigdatum
     big_ot = my_bigdatum['ot']
     del my_datum['ot']
  if isinstance(my_bigdatum, list):
     my_current = 0
     for my_datum in my_bigdatum:
        if (my_current == 0):
           big_datum = my_datum
           big_ot = my_datum['ot']
           del my_datum['ot']
        my_current += 1
  if (big_ot == None):
     return ("", 0)
  str_big_datum = json.dumps(big_datum, separators=(',',':'))
  b64_big_datum = base64.b64encode(bytes(str_big_datum, "utf-8"))
  raw_big_datum = str(b64_big_datum)[2:-1]
  my_bc = len(raw_big_datum)
  out_big_datum = '{"ed":"' + raw_big_datum + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum)
  self.current_mid = save_mid # mid rollback
  out_skip  = len(my_irciot)
  out_head  = len(big_ot) + 8 #"ot":"",#
  out_head += len(str(self.current_did)) + 9 #"did":"",#
  out_head += len(str(my_bc)) + 6 #"bc":,#
  out_head += len(str(my_part)) + 6 #"bp":,#
  out_skip += out_head - self.message_mtu
  out_big_datum = '{'
  out_big_datum += '"ot":"' + big_ot + '",'
  out_big_datum += '"did":"' + str(self.current_did) + '",'
  out_big_datum += '"bc":' + str(my_bc) + ','
  out_big_datum += '"bp":' + str(my_part) + ','
  out_big_datum += '"ed":"'
  my_okay = self.message_mtu - out_head - 48 # Must be calculated
  my_size = my_bc - my_part
  if (my_size > my_okay):
     my_size = my_okay
  out_big_datum += raw_big_datum[my_part:my_part + my_size] + '"}'
  my_irciot = self.irciot_encap_internal_(out_big_datum)
  if (my_size < my_okay):
    return (my_irciot, 0)
  return (my_irciot, len(raw_big_datum) + my_part - out_skip)
  # End of irciot_encap_bigdatum_()

 def irciot_encap_(self, my_datumset, my_skip, my_part):
  ''' Public part of encapsulator with per-datum fragmentation '''
  my_datums_set  = my_datumset
  my_datums_skip = 0
  my_datums_part = 0
  save_mid  = self.current_mid
  my_irciot = ""
  my_datums = json.loads(my_datumset)
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
           one_datum = 1 # Multidatum, but current datum is too large
        else:
           one_datum = 1 # One datum in list, and it is too large
     if isinstance(my_datums, dict):
        one_datum = 1    # One large datum without list
     if (one_datum == 1):
        self.current_mid = save_mid # mid rollback
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
  # End of irciot_encap_()

