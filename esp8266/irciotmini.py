# PyLayerIRCIoT mini (c) 2020 Alexey Y. Woronov
import json,re
F=False
T=True
N=None
class PyLayerIRCIoT(object):
 class CONST(object):
  ii_proto_ver='0.3.33'
  ii_lib_ver='0.0.231'
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
  self.ii_mtu=450
  self.ii_mid=100
  self.ii_oid=500
  self.ii_did=700
  self.o_pool=[]
 def ii_handler(self,in_datum,in_nick,in_mask):
  pass
 def ii_pointer(self,in_msg,in_nick,in_mask):
  my_obj=N
  try:
   if self.is_ii_(in_msg):
    my_obj=self.ii_deinencap_(in_msg)
   elif self.is_ii_datumset_(in_msg): my_obj=in_msg
  except: pass
  if my_obj!=N: self.ii_handler(my_obj,in_nick,in_mask)
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
  if not 'ot' in in_datum.keys():
   if in_ot==N: return F
   my_ot=in_ot
  else: my_ot=in_datum['ot']
  if type(my_ot)!=str: return F
  if not 'src' in in_datum.keys():
   if in_src==N: return F
  else:
   if type(in_datum['src'])!=str: return F
  if not 'dst' in in_datum.keys():
   if in_dst==N: return F
  else:
   if type(in_datum['dst'])!=str: return F
  return T
 def is_ii_(self,in_str):
  def is_ii_obj_(self,in_obj):
   if not 'oid' in in_obj.keys(): return F
   if not 'ot' in in_obj.keys(): in_obj['ot']=N
   my_ot=in_obj['ot']
   if not 'd' in in_obj.keys(): return F
   my_datums=in_obj['d']
   my_src=N
   if 'src' in in_obj.keys(): my_src=in_obj['src']
   my_dst=N
   if 'dst' in in_obj.keys(): my_dst=in_obj['dst']
   if type(my_datums)==dict: my_datums=[my_datums]
   if type(my_datums)==list:
    for my_datum in my_datums:
     if not self.is_ii_datum_(my_datum,my_ot,my_src,my_dst): return F
   else: return F
   return T
  def is_ii_cont_(self,in_cont):
   if not 'mid' in in_cont.keys(): return F
   if not 'o' in in_cont.keys(): return F
   my_objs=in_cont['o']
   if type(my_objs)==dict: my_objs=[my_objs]
   if type(my_objs)==list:
    for my_obj in my_objs:
     if not is_ii_obj_(self,my_obj): return F
   else: return F
   return T
  try:
   ii_msg=json.loads(str(in_str))
  except: return F
  if type(ii_msg)==dict: ii_msg=[ii_msg]
  if type(ii_msg)==list:
   for my_cont in ii_msg:
    if not is_ii_cont_(self,my_cont): return F
  else: return F
  return T
 def is_ii_datumset_(self,in_json):
  try:
   my_datums=json.loads(in_json)
  except: return F
  if type(my_datums)==dict: my_datums=[my_datums]
  if type(my_datums)==list:
   for my_datum in my_datums:
    if not self.is_ii_datum_(my_datum,N,N,N): return F
   return T
  return F
 def ii_prepare_datum_(self,in_datum,in_header,in_json):
  if 'ed' in in_datum.keys(): return ''
  (my_dt,my_ot,my_src,my_dst)=in_header
  if not 't' in in_datum.keys(): in_datum['t']=my_dt
  if not 'ot' in in_datum.keys(): in_datum['ot']=my_ot
  if not 'src' in in_datum.keys(): in_datum['src']=my_src
  if not 'dst' in in_datum.keys(): in_datum['dst']=my_dst
  if in_datum['t']==N: del in_datum['t']
  return self.jdumps(in_datum)
 def ii_deinencap_obj_(self,in_obj,in_json):
  i_dt=N
  i_ot=N
  i_src=N
  i_dst=N
  try:
   i_datums=in_obj['d']
   if 'ot' in in_obj.keys(): i_ot=in_obj['ot']
   if 't' in in_obj.keys(): i_dt=in_obj['t']
   if 'src' in in_obj.keys(): i_src=in_obj['src']
   if 'dst' in in_obj.keys(): i_dst=in_obj['dst']
  except: return ''
  if type(i_datums)==dict: i_datums=[i_datums]
  if type(i_datums)==list:
   s_datums=''
   for i_datum in i_datums:
    s_datum=self.ii_prepare_datum_(i_datum,\
     (i_dt,i_ot,i_src,i_dst),in_json)
    if s_datum!='':
     if s_datums!='': s_datums+=','
     s_datums+=s_datum
   return s_datums
  return ''
 def ii_deinencap_cont_(self,in_cont,in_json=N):
  try:
   i_objs=in_cont['o']
  except: return ''
  if type(i_objs)==dict: i_objs=[i_objs]
  if type(i_objs)==list:
   s_objs=''
   for i_obj in i_objs:
    s_obj=self.ii_deinencap_obj_(i_obj,in_json)
    if s_obj!='':
     if s_objs!='': s_objs+=','
     s_objs+=s_obj
   return s_objs
  return ''
 def ii_deinencap_(self,in_json):
  try:
   i_conts=json.loads(in_json)
  except: return '[]'
  if type(i_conts)==dict: i_conts=[i_conts]
  if type(i_conts)==list:
   s_datums='['
   for i_cont in i_conts:
    s_datum=self.ii_deinencap_cont_(i_cont,in_json)
    if s_datum!='':
     if s_datums!='[': s_datums+=','
     s_datums+=s_datum
   s_datums+=']'
   return s_datums
  return '[]'
 def ii_encap_datum_(self,in_datum,in_ot,in_src,in_dst):
  if 'ed' in in_datum.keys(): return ''
  if in_ot==in_datum['ot']: del in_datum['ot']
  if in_src==in_datum['src']: del in_datum['src']
  if in_dst==in_datum['dst']: del in_datum['dst']
  return self.jdumps(in_datum)
 def ii_encap_int_(self,in_datumset):
  try:
   i_dats=json.loads(in_datumset)
  except: return ''
  i_ii=''
  i_ot=N
  i_src=N
  i_dst=N
  if type(i_dats)==dict: i_dats=[i_dats]
  if type(i_dats)==list:
   i_dats_cnt=0
   i_ot_cnt=0
   i_src_cnt=0
   i_dst_cnt=0
   for i_dat in i_dats:
    if i_dats_cnt==0:
     i_ot=i_dat['ot']
     i_ot_cnt=1
     i_src=i_dat['src']
     i_src_cnt=1
     i_dst=i_dat['dst']
     i_dst_cnt=1
    else:
     if i_ot==i_dat['ot']: i_ot_cnt+=1
     if i_src==i_dat['src']: i_src_cnt+=1
     if i_dst==i_dat['dst']: i_dst_cnt+=1
    i_dats_cnt+=1
   i_dats_cnt=len(i_dats)
   if i_ot_cnt<i_dats_cnt: i_ot=N
   if i_src_cnt<i_dats_cnt: i_src=N
   if i_dst_cnt<i_dats_cnt: i_dst=N
   for i_dat in I_dats:
    if i_ii!='': i_ii+=','
    i_ii+=self.ii_encap_datum_(i_dat,i_ot,i_src,i_dst)
    if i_dats_cnt>1: i_ii='['+i_ii+']'
  s_obj='"o":{"oid":"%d",'%self.ii_oid
  if i_ot!=N: s_obj+='"ot":"%s",'%i_ot
  if i_src!=N: s_obj+='"src":"%s",'%i_src
  if i_dst!=N: s_obj+='"dst":"%s",'%i_dst
  s_mid=self.ii_mid
  s_cont='{"mid":"%d",'%s_mid
  i_ii=s_cont+s_obj+i_ii+'}}'
  return i_ii
 def ii_encap_all_(self,in_datums):
  result=self.o_pool
  if type(in_datums)==dict: in_datums=[in_datums]
  my_dats=jdumps(in_datums)
  j_text,my_skip,my_part=self.ii_encap_(my_dats,0,0)
  if j_text!='': result.append(j_text)
  while my_skip>0 or my_part>0:
   j_text,my_skip,my_part=self.ii_encap_(my_dats,my_skip,my_part)
   if j_text!='': result.append(j_text)
  return result
 def ii_encap_(self,in_datumset,in_skip,in_part):
  i_save_mid=self.ii_mid
  i_dats=json.loads(in_datumset)
  i_dats_set=in_datumset
  i_dats_part=0
  i_dats_skip=0
  i_tot=len(i_dats)
  if in_skip>0:
   i_dats_obj=[]
   i_dats_cnt=0
   for i_dat in i_dats:
    i_dats_cnt+=1
    if i_dats_cnt>in_skip: i_dats_obj.append(i_dat)
   i_dats_set=self.jdumps(i_dats_obj)
   i_dats=json.loads(i_dats_set)
   del i_dats_obj
   del i_dats_cnt
  i_ii=self.ii_encap_int_(in_datumset)
  if len(i_ii)>self.ii_mtu: return None,0,0
  else:
   i_dats_skip=i_tot-in_skip
   self.ii_did+=1
  if in_skip+i_dats_skip>=i_tot:
   in_skip=0
   i_dats_skip=0
  return i_ii,in_skip+i_dats_skip,i_dats_part
