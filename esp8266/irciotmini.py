# PyLayerIRCIoT mini (c) 2019 Alexey Y. Woronov
import json
F=False
T=True
N=None
class PyLayerIRCIoT(object):
 class CONST(object):
  ii_proto_ver='0.3.29'
  ii_lib_ver='0.0.145'
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
 def ii_pointer(self,in_msg,in_nick,in_mask):
  print('ii_pointer$%s$%s$%s$'%(in_msg,in_nick,in_mask))
  if self.is_ii_(in_msg):
   print('IRC-IoT object!')
 def is_ii_datum_(self,in_datum,in_ot,in_src,in_dst):
  if not 'ot' in in_datum:
   if in_ot==N:
    return F
   my_ot=in_ot
  else:
   my_ot=in_datum['ot']
  if not type(my_ot)==str:
   return F
  if not 'src' in in_datum:
   if in_src==N:
    return F
  else:
   if not type(in_datum['src'])==str:
    return F
  if not 'dst' in in_datum:
   if in_dst==N:
    return F
  else:
   if not type(in_datum['dst'])==str:
    return F
  return T
 def is_ii_(self,in_str):
  def is_ii_obj_(self,in_obj):
   if not 'oid' in in_obj:
    return F
   if not 'ot' in in_obj:
    in_obj['ot']=N
   my_ot=in_obj['ot']
   if not 'd' in in_obj:
    return F
   my_datums=in_obj['d']
   my_src=N
   if 'src' in in_obj:
    my_src=in_obj['src']
   my_dst=N
   if 'dst' in in_obj:
    my_dst=in_obj['dst']
   if type(my_datums)==dict:
    my_datums=[my_datums]
   if type(my_datums)==list:
    for my_datum in my_datums:
     if not self.is_ii_datum_(my_datum,my_ot,my_src,my_dst):
      return F
   else:
    return F
   return T
  def is_ii_cont_(self,in_cont):
   if not 'mid' in in_cont:
    return F
   if not 'o' in in_cont:
    return F
   my_objs=in_cont['o']
   if type(my_objs)==dict:
    my_objs=[my_objs]
   if type(my_objs)==list:
    for my_obj in my_objs:
     if not is_ii_obj_(self,my_obj):
      return F
   else:
    return F
   return T
  try:
   ii_msg=json.loads(str(in_str))
  except:
   return F
  if type(ii_msg)==dict:
   ii_msg=[ii_msg]
  if type(ii_msg)==list:
   for my_cont in ii_msg:
    if not is_ii_cont_(self,my_cont):
     return F
  else:
   return F
  return T
 def ii_deinencap_obj_(self,in_obj,in_json):
  pass
 def ii_deinencap_cont_(self,in_cont):
  pass
 def ii_deinencap_(self,in_json):
  pass
 def ii_encap_datum_(self,in_datum,in_ot,in_src,in_dst):
  pass
 def ii_encap_internal_(self,in_datumset):
  pass
 def ii_encap_(self,in_datumset,my_skip,my_part):
  pass
