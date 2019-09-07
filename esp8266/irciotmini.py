# PyLayerIRCIoT mini (c) 2019 Alexey Y. Woronov
class PyLayerIRCIoT(object):
 class CONST(object):
  ii_proto_ver='0.3.29'
  ii_lib_ver='0.0.137'
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
 def ii_pointer(self,in_msg,in_nick,in_mask):
  pass
 def is_ii_datum_(self,in_datum,in_ot,in_src,in_dst):
  if not 'did' in in_datum:
   return False
  if not 'ot' in datum:
   if in_ot==None:
    return False
   my_ot=in_ot
  else:
   my_ot=in_datum['ot']
  if not isinstance(my_ot,str):
   return False
  return True
 def is_ii_(self,in_str):
  def is_ii_obj_(self,in_obj):
   if not 'oid' in in_obj:
    return False
   if not 'ot' in in_obj:
    in_obj['ot']=None
   my_ot=in_obj['ot']
   if not 'd' in in_obj:
    return False
   my_datums=in_obj['d']
   my_src=None
   if 'src' in in_obj:
    my_src=in_obj['src']
   my_dst=None
   if 'dst' in in_obj:
    my_dst=in_obj['dst']
   if isinstance(my_datums,list):
    for my_datum in my_datums:
     if not self.is_ii_datum_(my_datum,my_ot,my_src,my_dst):
      return False
   elif isinstance(my_datums,dict):
    if not self.is_ii_datum_(my_datum,my_ot,my_src,my_dst):
     return False
   return True
  def is_ii_cont_(self,in_cont):
   if not 'mid' in in_cont:
    return False
   if not 'o' in in_cont:
    return False
   my_objs=in_cont['o']
   if isinstance(my_objs,list):
    for my_obj in my_objs:
     if not is_ii_obj_(self,my_obj):
      return False
   elif isinstnace(my_objs,dict):
    if not is_ii_obj_(self,my_objs):
     return False
   return True
  try:
   ii_msg=json.loads(in_str)
  except:
   return False
  if isinstance(ii_msg,list):
   for my_cont in ii_msg:
    if not is_ii_cont_(self,my_cont):
     return False
    return True
  elif isinstance(ii_msg,dict):
   if not is_ii_cont_(self,my_cont):
    return False
  return True
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
