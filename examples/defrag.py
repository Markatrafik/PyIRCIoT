#!/usr/bin/python3

try: # need for development
  from irciot import PyLayerIRCIoT
except:
  from PyIRCIoT.irciot import PyLayerIRCIoT

def main():

 irciot = PyLayerIRCIoT()

 datumset_text  = '[{"bigval":"long-long-value-xxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxsensorxxxxxxxxnxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxx","ot":"request","dst":"PLAYER@Kidsroom",'
 datumset_text += '"t":"2018-08-23 14:48:07.115959","src":"myengine",'
 datumset_text += '"addonvar1":"value1","addonvar2":"val2","addonvar3":"val3",'
 datumset_text += '"x1":45,"x2":46,"x3":47,"x4":551,"x5l":0.000000001,"uu":"o",'
 datumset_text += '"middlevar":"text-text-text-text-text-text-text-text-text",'
 datumset_text += '"visionon1":"000001","vixicron2":"abcd","uptime645":"ffff",'
 datumset_text += '"garbagevar":"ejkqdfwjefkljwklefjklwejfklwejfkljwkljfeklw",'
 datumset_text += '"cnd":{"uri":"?"}},'
 datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:07.116012",'
 datumset_text += '"src":"myengine","cnd":{"temperature":"?"},"ot":"request"},'
 datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:08.157125",'
 datumset_text += '"src":"myengine","cnd":{"humidity":"?"},"ot":"request"}]'
  
 print ("input datumset: @\033[1;33;44m{}\033[0m@\n".format(datumset_text))
 json_text, skip_param, part_param \
  = irciot.irciot_encap_(datumset_text, 0, 0)
 if (not irciot.is_irciot_(json_text)):
   print ("*** Not an IRC-IoT message")
 else:
   print("output IRC-IoT: @{}@len={}@\n".format(json_text, len(json_text)))
   msg_text = irciot.irciot_deinencap_(json_text)
   if (msg_text != ""):
     print("output datumset: @\033[1;36;44m{}\033[0m@\n".format(msg_text))
   print("input it to self\n")
   while ((skip_param > 0) or (part_param > 0)):
     json_text, skip_param, part_param \
      = irciot.irciot_encap_(datumset_text, skip_param, part_param)
     print("output IRC-IoT: @{}@len={}@\n".format(json_text, len(json_text)))
     msg_text = irciot.irciot_deinencap_(json_text)
     print("input it to self\n")
     if (msg_text != ""):
       print("output datumset: @\033[1;36;44m{}\033[0m@\n".format(msg_text))
   
if __name__ == '__main__':
  main()

