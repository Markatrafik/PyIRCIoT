#!/usr/bin/python3.5

from irciot import PyIRCIoT

def main():

 irciot = PyIRCIoT()

 datumset_text  = '[{"bigval":"long-long-value-xxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 datumset_text += 'xxxxxxxxxxxxxxxxxxx","ot":"request","dst":"PLAYER@Kidsroom",'
 datumset_text += '"t":"2018-08-23 14:48:07.115959","src":"myengine",'
 datumset_text += '"cnd":{"uri":"?"}},'
 datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:07.116012",'
 datumset_text += '"src":"myengine","cnd":{"temperature":"?"},"ot":"request"},'
 datumset_text += '{"dst":"THERMO@Kidsroom","t":"2018-08-23 14:48:08.157125",'
 datumset_text += '"src":"myengine","cnd":{"humidity":"?"},"ot":"request"}]'
  
 print ("input datumset: @%s@\n" % datumset_text)
 json_text, skip_param, part_param \
  = irciot.irciot_encap_(datumset_text, 0, 0)
 if (not irciot.is_irciot_(json_text)):
   print ("*** Not an IRC-IoT message")
 else:
   print("output IRC-IoT: @%s@len=%d@\n" % (json_text, len(json_text)))
   msg_text = irciot.irciot_deinencap_(json_text)
   if (msg_text != ""):
     print("output datumset: @%s@\n" % msg_text)
   print("input it to self\n")
   while ((skip_param > 0) or (part_param > 0)):
     json_text, skip_param, part_param \
      = irciot.irciot_encap_(datumset_text, skip_param, part_param)
     print("output IRC-IoT: @%s@len=%d@\n" % (json_text, len(json_text)))
     msg_text = irciot.irciot_deinencap_(json_text)
     print("input it to self\n")
     if (msg_text != ""):
       print("output datumset: @%s@\n" % msg_text)
   
main()

