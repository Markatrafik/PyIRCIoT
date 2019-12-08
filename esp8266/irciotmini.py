# PyLayerIRCIoT mini (c) 2019 Alexey Y. Woronov
import json,re
F=False
T=True
N=None
class PyLayerIRCIoT(object):
 class CONST(object):
  ii_proto_ver='0.3.29'
  ii_lib_ver='0.0.147'
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
 def ii_handler(self,in_datum,in_nick,in_mask):
  pass
 def ii_pointer(self,in_msg,in_nick,in_mask):
  my_obj=N
  try:
   if self.is_ii_(in_msg):
    my_obj=self.ii_deinencap_(in_msg)
   elif self.is_ii_datumset_(in_msg):
    my_obj=in_msg
  except:
   pass
  if my_obj!=N:
   self.ii_handler(my_obj,in_nick,in_mask)
 def jdumps(self,in_datum):
  def r1(in_s):
   return '"'+in_s.group(1)+'":'
  def r2(in_s):
   return ',"'+in_s.group(1)+'":'
  my_s=json.dumps(in_datum)
  my_s=re.sub(r'\"([^"]*)\": ',r1,my_s)
  my_s=re.sub(r', \"([^"]*)\":',r2,my_s)
  return my_s
 def is_ii_datum_(self,in_datum,in_ot,in_src,in_dst):
  if not 'ot' in in_datum:
   if in_ot==N:
    return F
   my_ot=in_ot
  else:
   my_ot=in_datum['ot']
  if type(my_ot)!=str:
   return F
  if not 'src' in in_datum:
   if in_src==N:
    return F
  else:
   if type(in_datum['src'])!=str:
    return F
  if not 'dst' in in_datum:
   if in_dst==N:
    return F
  else:
   if type(in_datum['dst'])!=str:
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
 def is_ii_datumset_(self,in_json):
  try:
   my_datums=json.loads(in_json)
  except:
   return F
  if type(my_datums)==dict:
   my_datums=[my_datums]
  if type(my_datums)==list:
   for my_datum in my_datums:
    if not self.is_ii_datum_(my_datum,N,N,N):
     return F
   return T
  return F
 def ii_prepare_datum_(self,in_datum,in_header,in_json):
  if 'ed' in in_datum.keys():
   return ''
  (my_dt,my_ot,my_src,my_dst)=in_header
  if not 't' in in_datum.keys():
   in_datum['t']=my_dt
  if not 'ot' in in_datum.keys():
   in_datum['ot']=my_ot
  if not 'src' in in_datum.keys():
   in_datum['src']=my_src
  if not 'dst' in in_datum.keys():
   in_datum['dst']=my_dst
  if in_datum['t']==N:
   del in_datum['t']
  return self.jdumps(in_datum)
 def ii_deinencap_obj_(self,in_obj,in_json):
  i_dt=N
  i_src=N
  i_dst=N
  try:
   i_datums=in_obj['d']
   i_ot=in_obj['ot']
   if 't' in in_obj:
    i_dt=in_obj['t']
   if 'src' in in_obj:
    i_src=in_obj['src']
   if 'dst' in in_obj:
    i_dst=in_obj['dst']
  except:
   return ''
  if type(i_datums)==dict:
   i_datums=[i_datums]
  if type(i_datums)==list:
   s_datums=''
   for i_datum in i_datums:
    s_datum=self.ii_prepare_datum_(i_datum,\
     (i_dt,i_ot,i_src,i_dst),in_json)
    if s_datum!='':
     if s_datums!='':
      s_datums+=','
     s_datums+=s_datum
   return s_datums
  return ''
 def ii_deinencap_cont_(self,in_cont,in_json=N):
  try:
   i_objs=in_cont['o']
  except:
   return ''
  if type(i_objs)==dict:
   i_objs=[i_objs]
  if type(i_objs)==list:
   s_objs=''
   for i_obj in i_objs:
    s_obj=self.ii_deinencap_obj_(i_obj,in_json)
    if s_obj!='':
     if s_objs!='':
      s_objs+=','
     s_objs+=s_obj
   return s_objs
  return ''
 def ii_deinencap_(self,in_json):
  try:
   i_conts=json.loads(in_json)
  except:
   return ''
  if type(i_conts)==dict:
   i_conts=[i_conts]
  if type(i_conts)==list:
   s_datums='['
   for i_cont in i_conts:
    s_datum=self.ii_deinencap_cont_(i_cont,in_json)
    if s_datum!='':
     if s_datums!='[':
      s_datums+=','
     s_datums+=s_datum
   s_datums+=']'
   return s_datums
  return ''
 def ii_encap_datum_(self,in_datum,in_ot,in_src,in_dst):
  if 'ed' in in_datum.keys():
   return ''
  if in_ot==in_datum['ot']:
   del in_datum['ot']
  if in_src==in_datum['src']:
   del in_datum['src']
  if in_dst==in_datum['dst']:
   del in_datum['dst']
  return self.jdumps(in_datum)
 def ii_encap_int_(self,in_datumset):
  pass
 def ii_encap_all_(self,in_datumset):
  pass
 def ii_encap_(self,in_datumset,my_skip,my_part):
  pass
