# PyLayerIRC mini (c) 2019 Alexey Y. Woronov
import socket,select,random,time
class PyLayerIRC(object):
 class CONST(object):
  ii_proto_ver='0.3.28'
  ii_lib_ver='0.0.123'
  i_big_wait=28
  i_min_wait=1
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
  self.i_recon=1
  self.i_channel=self.CONST.i_channel
  self.i_users=[]
  self.i_run=False
 def i_start_(self):
  self.i_run=True
 def i_stop_(self):
  self.i_run=False
  time.sleep(self.CONST.i_min_wait)
 def __del__(self):
  self.i_stop_()
 def i_disconnect_(self):
  try:
   self.i.shutdown()
   self.i.close()
  except:
   pass
 def i_reconnect_(self):
  if not self.i_run:
   return
  self.i_disconnect_()
  time.sleep(self.CONST.i_big_wait)
  self.i_recon=1
 def i_socket_(self):
  try:
   i_s=socket.socket()
  except:
   return None
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
  except:
   return -1
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
    inp=inp.strip('\r')
    inp=inp.strip('\n')
    return (0,inp,w)
  except:
   return(-1,'',0)
  return (0,'',0)
 def i_pong_(self,inp):
  str=inp.split(':')
  r=self.i_send_("PONG %s\r\n" % str[1])
  return r
 def i_quit_(self):
  r=self.i_send_("QUIT :CYL8R\r\n")
  return r
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
    if i_i<6:
     i_i+=1
    if i_i==1:
     try:
      self.i_conn_(self.i_server,self.i_port)
     except:
      self.i_disconnect_()
      self.i=self.i_socket_()
      i_i=0
    elif i_i==2:
     if self.i_send_('USER '+self.i_user+' '+self.i_host+' 1 :'+self.i_info)==-1:
      i_i=0
    elif i_i==3:
     if self.i_send_('NICK '+self.i_nick)==-1:
      i_i=0
    elif i_i==4:
     i_w=self.CONST.i_min_wait
     if self.i_send_('JOIN '+self.i_channel)==-1:
      i_i=0
    elif i_i==5:
     i_w=self.CONST.i_min_wait
     if self.i_send_('JOIN '+self.i_channel+'\r\n')==-1:
      i_i=0
    i_dt=0
    if i_i>0:
     (i_r,i_buf,i_dt)=self.i_recv_(i_w)
     if i_r==0:
      if i_buf=='':
       continue
      print(i_buf)
    i_w=self.CONST.i_big_wait
    if (i_dt>0):
     i_w=i_dt
     i_dt=0
    if (i_r==-1):
     print('here,dt=%d.' % i_dt)
     self.i_reconnect_()
     i_buf=''
     i_i=0
     self.i=self.i_socket_()
    i_pref=':'+self.i_server+' '
    i_pref_l=len(i_pref)
    for i_item in i_buf.split(r'[\r\n]'):
     if i_item[:5]=='PING ':
      if self.i_pong_(i_item)==-1:
       i_r=-1
       i_i=0
     if i_item[:6]=='ERROR ':
      self.i_reconnect_()
      i_i=0
     try:
      i_cmd=i_item.split(' ')[1]
     except:
      i_cmd=''
     if i_item[:i_pref_l]==i_pref:
      print('pref: '+i_cmd)
      if i_cmd=='451':
       i_i=1
     if i_cmd=='PRIVMSG':
      print('msg: '+i_item)
  except:
   self.i_disconnect_()
   i_i=0
