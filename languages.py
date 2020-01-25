'''
'' PyIRCIoT_EL_ (IRC-IoT Embedded Languages class)
''
'' Copyright (c) 2019-2020 Alexey Y. Woronov
''
'' By using this file, you agree to the terms and conditions set
'' forth in the LICENSE file which can be found at the top level
'' of this package
''
'' Authors:
''  Alexey Y. Woronov <alexey@woronov.ru>
'''

class PyLayerIRCIoT_EL_(object):

 class CONST_EL_(object):
  #
  irciot_protocol_version = '0.3.31'
  #
  irciot_library_version  = '0.0.170'
  #
  # IRC-IoT Embedded Languages tags:
  #
  lang_BASH   = 'sh'  # Bash Script
  lang_CS     = 'cs'  # C Sharp
  lang_CSP    = 'csp' # Caché Server Pages
  lang_GO     = 'go'  # Golang
  lang_JRE    = 'jre' # Java (Runtime Enivronment)
  lang_JS     = 'js'  # JavaScript
  lang_PHP    = 'php' # PHP
  lang_PYTHON = 'py'  # Python
  lang_RUBY   = 'rb'  # Ruby
  #
  lang_ALL = [
   lang_BASH, lang_JRE, lang_JS,
   lang_PHP, lang_PYTHON, lang_RUBY
  ]
  #
  err_UNKNOWN_LANGUAGE = 1001
  err_LANGUAGE_SYNTAX  = 1007
  #
  err_DESCRIPTIONS = {
   err_UNKNOWN_LANGUAGE   : "This language is not supported"
   err_LANGUAGE_SYNTAX    : "Incorrect syntax for this language"
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

