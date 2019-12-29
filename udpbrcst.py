'''
'' PyIRCIoT (PyLayerUDPb class)
''
'' Copyright (c) 2019 Alexey Y. Woronov
''
'' By using this file, you agree to the terms and conditions set
'' forth in the LICENSE file which can be found at the top level
'' of this package
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

import socket
import select
import json
import threading
import ssl
from queue import Queue
from time import sleep

#from pprint import pprint

import datetime

def udpb_setup_(self):
 # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
 # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
 # sock.bind(("", 12345))

def udpb_receive_(self):
 # data, addr = sock.recvfrom(1024)
 pass
 
def udpb_send_(self, in_data):
 # sock.sendto(in_data, ('<broadcast>', 12345))
 # sleep(small_sleep)
 pass

