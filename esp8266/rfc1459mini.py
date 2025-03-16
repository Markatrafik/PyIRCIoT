# Micro PyLayerIRC (c) 2020 Alexey Y. Woronov
import socket,select,random,time
T=True
F=False
N=None
class PyLayerIRC(object):
 class CONST(object):
  ii_proto_ver='0.3.33'
  ii_lib_ver='0.0.231'
  i_big_wait=28
  i_min_wait=1
  i_keep_cnt=16
  i_server='irc-iot.nsk.ru'
  i_port=6667
  i_channel='#NSK'
  i_nick='esp0001'
  i_info='IRC-IoT device'
  i_buf_size=1350
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
  self.i_host='localhost'
  self.i_nick=self.CONST.i_nick
  self.i_user=self.i_nick
  self.i_info=self.CONST.i_info
  self.i_server=self.CONST.i_server
  self.i_port=self.CONST.i_port
  self.i_status=0
  self.i_keep=0
  self.i_recon=1
  self.i_channel=self.CONST.i_channel
  self.i_users=[]
  self.i_run=F
 def i_start_(self):
  self.i_run=T
 def i_stop_(self):
  self.i_run=F
  time.sleep(self.CONST.i_min_wait)
 def __del__(self):
  self.i_stop_()
 def i_handler(self,in_msg,in_nick,in_mask):
  pass
 def i_pointer(self,in_msg,in_dst):
  return self.i_send_('PRIVMSG '+in_dst+' :'+in_msg)
 def i_disconnect_(self):
  try:
   self.i.shutdown()
   self.i.close()
  except: pass
 def i_reconnect_(self):
  if not self.i_run: return
  self.i_disconnect_()
  time.sleep(self.CONST.i_big_wait)
  self.i_recon=1
 def i_socket_(self):
  try:
   i_s=socket.socket()
  except: return N
  return i_s
 def i_conn_(self,i_srv,i_prt):
  i_addr=socket.getaddrinfo(i_srv,i_prt)
  self.i.connect(i_addr[0][-1])
 def i_send_(self,i_out):
  try:
   self.i.send(bytes(i_out+'\n','utf-8'))
   print('send: '+i_out)
   time.sleep(self.CONST.i_min_wait)
   return 0
  except: return -1
 def i_recv_(self,i_w):
  try:
   r=select.select([self.i],[],[],0)
   w=0
   if i_w==0:
    i_w=self.CONST.i_big_wait
   while r[0]==[] and w<i_w:
    r=select.select([self.i],[],[],0)
    time.sleep(1)
    w+=1
   if r[0]:
    inp=self.i.recv(self.CONST.i_buf_size).decode('utf-8')
    inp=inp.strip('\r').strip('\n')
    return (0,inp,w)
  except: return(-1,'',0)
  return (0,'',0)
 def i_pong_(self,inp):
  str=inp.split(':')
  return self.i_send_("PONG %s\r\n"%str[1])
 def i_quit_(self):
  return self.i_send_("QUIT :CYL8R\r\n")
 def i_who_(self,in_str):
  return self.i_send_("WHO %s\r\n"%in_str)
 def i_join_(self,in_str):
  return self.i_send_("JOIN %s\r\n"%in_str)
 def i_extract_nm_(self,in_str):
  try:
   m=in_str.split(' ',1)[0][1:]
   n=m.split('!',1)[0]
  except:
   m='!@'
   n=''
  return (n,m)
 def i_extract_msg_(self,in_str):
  try:
   i_msg = in_str.split('PRIVMSG',1)[1].split(':',1)[1]
   return i_msg.strip()
  except: return N
 def i_process_(self):
  try:
   i_i=0
   i_w=self.CONST.i_big_wait
   i_buf=""
   i_r=0
   self.i=self.i_socket_()
   while self.i_run:
    print(i_i)
    if not self.i:
     time.sleep(self.CONST.i_big_wait)
     i_i=0
    if i_i<6: i_i+=1
    if i_i==1:
     try:
      self.i_conn_(self.i_server,self.i_port)
     except:
      self.i_disconnect_()
      self.i=self.i_socket_()
      i_i=0
    elif i_i==2:
     if self.i_send_('USER '+self.i_user+' '+self.i_host+' 1 :'+self.i_info)==-1: i_i=0
    elif i_i==3:
     if self.i_send_('NICK '+self.i_nick)==-1: i_i=0
    elif i_i in [4,5]:
     i_w=self.CONST.i_min_wait
     if self.i_join_(self.i_channel)==-1: i_i=0
    i_dt=0
    if i_i>0:
     (i_r,i_buf,i_dt)=self.i_recv_(i_w)
     if i_r==0:
      if i_buf=='':
       i=self.i_keep+1
       if i>self.CONST.i_keep_cnt:
        if self.i_join_(self.i_channel)==-1: i_i=0
        i=0
       self.i_keep=i
       continue
      else: self.i_keep=0
      print(i_buf)
    i_w=self.CONST.i_big_wait
    if (i_dt>0):
     i_w=i_dt
     i_dt=0
    if (i_r==-1):
     print('here,dt=%d.'%i_dt)
     self.i_reconnect_()
     i_buf=''
     i_i=0
     self.i=self.i_socket_()
    i_pref=':'+self.i_server+' '
    i_pref_l=len(i_pref)
    for i_item in i_buf.replace('\r','\n').split('\n'):
     if i_item[:5]=='PING ':
      if self.i_pong_(i_item)==-1:
       i_r=-1
       i_i=0
     if i_item[:6]=='ERROR ':
      self.i_reconnect_()
      i_i=0
     try:
      i_cmd=i_item.split(' ')[1]
     except: i_cmd=''
     if i_item[:i_pref_l]==i_pref:
      print('pref: '+i_cmd)
      if i_cmd=='451': i_i=1
     if i_cmd=='PRIVMSG':
      (i_n,i_m)=self.i_extract_nm_(i_item)
      i_msg=self.i_extract_msg_(i_item)
      if i_msg!=N: self.i_handler(i_msg,i_n,i_m)
  except:
   self.i_disconnect_()
   i_i=0
