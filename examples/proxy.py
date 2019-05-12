#!/usr/bin/python3

import sys
import os
import pickle
import json

try: # need for development
  from irciot import PyLayerIRCIoT
except:
  from PyIRCIoT.irciot import PyLayerIRCIoT

def main():

    irciot_mode = 0
    irciot_part = 0
    irciot_skip = 0

    if (len(sys.argv) != 4):
       print("\nUsage: %s " % sys.argv[0] + \
        "<mode> '<JSON>' '<state save file>'\n")
       print(" Where <mode> is:\n");
       print("  1 - Convert IRC-IoT \"Datum\" set to IRC-IoT \"Message\"")
       print("  2 - Convert IRC-IoT \"Message\" to IRC-IoT \"Datum\" set\n")
       return
    else:
       in_string = sys.argv[1]
       if in_string.isdigit():
          irciot_mode = int(in_string)
       del in_string
       input_json = sys.argv[2]
       save_file = sys.argv[3]
       
    irciot = PyLayerIRCIoT()

    if os.path.isfile(save_file):
      save_fd = open(save_file, 'r')
      save_json = save_fd.read()
      save_object = json.loads(save_json)
      try:
        irciot.current_mid = save_object['mid']
        irciot.currnet_oid = save_object['oid']
        irciot.current_did = save_object['did']
        irciot.defrag_pool = save_object['defrag_pool']
        irciot.blockchain_private_key \
          = save_object['blockchain_private_key']
        irciot.blockchain_public_key \
          = save_object['blockchain_public_key']
      except:
        pass

    if (irciot_mode == 1):   # "Datum" set to "Message"
      if (irciot.is_irciot_datumset_(input_json)):
        (output_json, irciot_skip, irciot_part) \
         = irciot.irciot_encap_(input_json, 0, 0)
        print(str(output_json))
        while ((irciot_skip > 0) or (irciot_part > 0)):
          (output_json, irciot_skip, irciot_part) \
           = irciot.irciot_encap_(input_json, \
             irciot_skip, irciot_part)
          print(str(output_json))
      else:
        exit(1)
    
    elif (irciot_mode == 2): # "Message" to "Datum" set
      if (irciot.is_irciot_(input_json)):
        output_json = irciot.irciot_deinencap_(input_json)
        print(str(output_json))
      else:
        exit(1)
        
    save_fd = open(save_file, 'w')
    save_object = {}
    save_object.update({'mid' : irciot.current_mid})
    save_object.update({'oid' : irciot.current_oid})
    save_object.update({'did' : irciot.current_did})
    save_object.update({'defrag_pool' : irciot.defrag_pool})
    save_object.update({'blockchain_private_key' : \
                  irciot.blockchain_private_key})
    save_object.update({'blockchain_pubilc_key' : \
                  irciot.blockchain_public_key})
    save_json = json.dumps(save_object, separators=(',',':'))
    save_fd.write(save_json + "\n")
    save_fd.close()

    del irciot
    
    exit(0)

if __name__ == '__main__':
  main()

