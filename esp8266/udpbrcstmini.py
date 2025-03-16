# Micro PyLayerUDPb (c) 2020 Alexey Y. Woronov
# this source is incomplete!!! cannot be used
import socket,select,time
T=True
F=False
N=None
class PyLayerUDPb(object):
 class CONST(object):
  ii_proto_ver='0.3.33'
  ii_lib_ver='0.0.231'
  u_big_wait=1
  u_min_wait=0.1
  u_port=12345
  u_ip=''
  u_ip_b='<broadcast>'
  u_buf_size=1520
  def __setattr__(self,*_):
   pass
 def __init__(self):
  self.CONST=self.CONST()
  self.u_port=self.CONST.u_port
  self.u_users=[]
  self.u_run=F
  self.us=N
  self.uc=N
 def u_start_(self):
  self.u_run=T
 def u_stop_(self):
  self.u_run=F
  time.sleep(self.CONST.u_min_wait)
 def __del__(self):
  self.u_stop_()
 def u_handler(self,in_msg):
  pass
 def u_pointer(self,in_msg):
  if not isinstance(in_msg,str): return -1
  return self.u_send_(in_msg)
 def u_disconnect_(self):
  try:
   for u in [self.us,self.uc]:
    u.shutdown()
    u.close()
  except: pass
 def u_reconnect_(self):
  if not self.u_run: return
  self.u_disconnect_()
  time.sleep(self.CONST.u_big_wait)
 def u_setup_(self):
  def u_sock_():
   s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
   for si in [socket.REUSEPORT,socket.SO_BROADCAST]:
    s.setsockopt(socket.SOL_SOCKET,si,1)
   return s
  try:
   self.uc=u_sock_()
   self.uc.bind((self.u_ip_b,self.u_port))
   self.us=u_sock_()
  except: pass
 def u_send_(self,u_out):
  try:
   self.uc.send(bytes(u_out,'utf-8'))
   print('send: '+u_out)
   time.sleep(self.CONST.u_min_wait)
   return 0
  except: return -1
 def u_recv_(self,u_w):
  try:
   r=select.select([self.us],[],[],0)
   w=0
   if u_w==0: u_w=self.CONST.u_big_wait
   while r[0]==[] and w<u_w:
    r=select.select([self.us],[],[],0)
    time.sleep(1)
    w+=1
   if r[0]:
    inp=self.us.recv(self.CONST.u_buf_size).decode('utf-8')
    inp=inp.strip('\r').strip('\n')
    return (0,inp,w)
  except: return(-1,'',0)
  return (0,'',0)
 def u_process_(self):
  try:
   u_i=0
   u_w=self.CONST.u_big_wait
   u_buf=""
   u_r=0
   self.u_setup_()
   while self.u_run:
    print(u_i)
    if not self.us or not self.uc:
     self.u_setup_()
     time.sleep(self.CONST.u_big_wait)
     u_i=0
    if u_i<2: u_i+=1
    u_dt=0
    if u_i>0: (u_r,u_buf,u_dt)=self.u_recv_(u_w)
    u_w=self.CONST.u_big_wait
    if (u_dt>0):
     u_w=u_dt
     u_dt=0
    if (u_r==-1):
     print('here,dt=%d.'%u_dt)
     self.setup_()
     u_i=0
    else:
     try:
      if u_buf not in [N,""]:
       print(u_buf)
       self.u_handler(u_buf)
       u_buf=''
     except: u_buf=''
  except:
   self.u_disconnect_()
   u_i=0
