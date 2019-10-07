'''
'' PyIRCIoT_EL_ (IRC-IoT Embedded Languages class)
''
'' Copyright (c) 2019 Alexey Y. Woronov
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

class PyLayerIRCIoT_EL_(object):

 class CONST_EL_(object):
  #
  irciot_protocol_version = '0.3.29'
  #
  irciot_library_version  = '0.0.141'
  #
  # IRC-IoT Embedded Languages tags:
  #
  lang_BASH   = 'sh'  # Bash Script
  lang_JRE    = 'jre' # Java (Runtime Enivronment)
  lang_JS     = 'js'  # JavaScript
  lang_PHP    = 'php' # PHP
  lang_PYHON  = 'py'  # Python
  lang_RUBY   = 'rb'  # Ruby
  #
  err_DESCRIPTIONS = {
   err_UNKNOWN_LANGUAGE   : "This language is not supported"
  }
  #
  def __setattr__(self, *_):
      pass

 def __init__(self):
  #
  self.CONST = self.CONST_EL_()
  #
  # End of PyLayerIRCIoT_EL_.__init__()

 def irciot_EL_error_(self, in_error_code, in_addon):
  my_message = ""
  if in_error_code in self.CONST.err_DESCRIPTIONS.keys():
    my_descr = self.CONST.err_DESCRIPTIONS[in_error_code]
    if isinstance(in_addon, str):
      my_descr += " (%s)" % in_addon
  else:
    return None
  return my_descr
  #
  # End of irciot_EL_error_()

 def irciot_EL_protocol_version_(self):
  return self.CONST.irciot_protocol_version

 def irciot_EL_library_version_(self):
  return self.CONST.irciot_library_version

 def irciot_EL_compatibility_(self):
  return ( \
    self.CONST.irciot_protocol_version, \
    self.CONST.irciot_library_version)

