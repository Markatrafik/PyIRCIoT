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
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.189'
  #
  # IRC-IoT Embedded Languages tags:
  #
  lang_ANSYML = 'yml' # Ansible YAML
  lang_BASH   = 'sh'  # Bash Script
  lang_BASIC  = 'bas' # BASIC
  lang_CS     = 'cs'  # C Sharp
  lang_CSP    = 'csp' # Cache Server Pages
  lang_GO     = 'go'  # Google Golang
  lang_JRE    = 'jre' # Java (Runtime Enivronment)
  lang_JS     = 'js'  # JavaScript
  lang_LUA    = 'lua' # Lua Script
  lang_QML    = 'qml' # Qt Meta Language
  lang_PERL   = 'pl'  # Perl
  lang_PHP    = 'php' # PHP
  lang_PYTHON = 'py'  # Python
  lang_R      = 'r'   # GNU R
  lang_RUBY   = 'rb'  # Ruby
  lang_SWIFT  = 'swt' # Apple Swift
  #
  lang_ALL = [
   lang_ANSYML, lang_BASH, lang_BASIC,  lang_CS,   lang_CSP,
   lang_GO,     lang_JRE,  lang_JS,     lang_LUA,  lang_QML,
   lang_PERL,   lang_PHP,  lang_PYTHON, lang_RUBY, lang_R,
   lang_SWIFT
  ]
  #
  err_UNKNOWN_LANGUAGE = 1001
  err_UNSUPPORTED_YET  = 1002
  err_LANGUAGE_SYNTAX  = 1007
  #
  err_DESCRIPTIONS = {
   err_UNKNOWN_LANGUAGE   : "Unknown programming langauge"
   err_UNSUPPORTED_YET    : "This language is not yet supported"
   err_LANGUAGE_SYNTAX    : "Incorrect syntax for this language"
  }
  #
  mod_JRE = 'py4j.java_gateway'
  mod_LUA = 'lupa'
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

 def irciot_EL_check_lang_(self, in_lang):
  if not isinstance(in_lang, str):
    return False
  if in_lang not in self.CONST_EL_.lang_ALL:
    return False
  return True

 # incomplete
 def irciot_EL_run_code_(self, in_lang, in_code, in_environment):
  if not self.irciot_EL_check_lang_(in_lang):
    return None
  return None

 def irciot_EL_import_(self, in_pointer, in_module_name):
  if in_pointer == None:
    import importlib
    try:
      my_pointer = importlib.import_module(in_module_name)
    except ImportError:
      my_pointer = None
    return my_pointer
  else:
    return in_pointer
  #
  # End of irciot_EL_import_()

 # incomplete
 def irciot_EL_init_language_(self, in_lang):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  if in_lang == lang_ANSYML:
    pass
  elif in_lang == lang_BASH:
    pass
  elif in_lang == lang_BASIC:
    pass
  elif in_lang == lang_CS:
    pass
  elif in_lang == lang_CSP:
    pass
  elif in_lang == lang_GO:
    pass
  elif in_lang == lang_JRE:
    self.my_JRE = self.irciot_EL_import_(self.CONST.mod_JRE)
    if self.my_JRE == None:
      return False
  elif in_lang == lang_JS:
    pass
  elif in_lang == lang_LUA:
    self.my_LUA = self.irciot_EL_import_(self.CONST.mod_LUA):
    if self.my_LUA == None:
      return False
  elif in_lang == lang_QML:
    pass
  elif in_lang == lang_PERL:
    pass
  elif in_lang == lang_PHP:
    pass
  elif in_lang == lang_R:
    pass
  elif in_lang == lang_PYTHON:
    pass
  elif in_lang == lang_RUBY:
    pass
  elif in_lang == lang_SWIFT:
    pass
  return False

