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

# Those Global options override default behavior and memory usage
#
CAN_debug_library  = True

import re
import ast
try:
 import json
except:
 import simplejson as json
from io import StringIO
import contextlib

class PyLayerIRCIoT_EL_(object):

 class CONST_EL_(object):
  #
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.197'
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
  lang_SMTLK  = 'st'  # SmallTalk
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
  err_BAD_ENVIRONMENT  = 1003
  err_COMMON_FILTER    = 1004
  err_LANGUAGE_FILTER  = 1005
  err_LANGUAGE_SYNTAX  = 1007
  err_LOADING_MODULES  = 1009
  err_CODE_EXECUTION   = 1010
  #
  err_DESCRIPTIONS = {
   err_UNKNOWN_LANGUAGE : "Unknown programming langauge",
   err_UNSUPPORTED_YET  : "This language is not yet supported",
   err_LANGUAGE_SYNTAX  : "Incorrect syntax for this language",
   err_LOADING_MODULES  : "Unable to load required modules",
   err_BAD_ENVIRONMENT  : "Invalid language environment",
   err_COMMON_FILTER    : "Code denied by common filter",
   err_LANGUAGE_FILTER  : "Code denied by language filter",
   err_CODE_EXECUTION   : "Problems while executing the code"
  }
  #
  mod_ANSVAR = 'ansible.vars.manager'
  mod_ANSINV = 'ansible.inventory.manager'
  mod_ANSYML = 'ansible.executor'
  mod_JRE = 'py4j.java_gateway'
  mod_JS  = 'js2py'
  mod_LUA = 'lupa'
  #
  common_filter_regexps = [
   '.*\\\\\\.*', '.*\\\\\'.*', '.*\\\\\".*' # Disable some escaping
  ]
  #
  lang_filter_PYTHON_types = set([ 'Assign', 'Module', 'Expr', 'Store', 'For', 'If', \
   'Else', 'Tuple', 'List', 'Load', 'Str', 'Num', 'BinOp', 'Mult' ])
  lang_filter_PYTHON_funcs = set([ 'abs', 'max', 'min', 'range', 'xrange', 'print' ])
  lang_filter_PYTHON_names = set([ 'True', 'False', 'None', 'print' ])
  #
  def __setattr__(self, *_):
    pass

 def __init__(self):
  #
  self.CONST = self.CONST_EL_()
  #
  self.__allowed_EL = []
  self.__common_filter_matchers = []
  for my_regexp in self.CONST.common_filter_regexps:
    self.__common_filter_matchers += [ re.compile(my_regexp) ]
  #
  # End of PyLayerIRCIoT_EL_.__init__()

 def irciot_EL_error_(self, in_error_code, in_addon):
  if in_error_code in self.CONST.err_DESCRIPTIONS.keys():
    my_descr = self.CONST.err_DESCRIPTIONS[in_error_code]
    if isinstance(in_addon, str):
      my_descr += " (%s)" % in_addon
  else:
    return
  if CAN_debug_library:
    print("EL error (%d):" % in_error_code, my_descr)
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
 def irciot_EL_check_environment_(self, in_lang, in_environment):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  if not isinstance(in_environment, dict):
    return False
  for my_key in in_environment.keys():
    if not isinstance(in_environment[my_key], str):
      return False

  return True

 # incomplete
 def irciot_LE_check_Java_code_(self, in_code):

  return True

 # incomplete
 def irciot_EL_check_LUA_code_(self, in_code):

  return True

 # incomplete
 def irciot_EL_check_Python_code_(self, in_code):
  class Python_checker_(ast.NodeVisitor):
    def check(self, in_code):
      self.visit(ast.parse(in_code))
    def visit_Call(self, in_node):
      if in_node.func.id in self.CONST.lang_filter_PYTHON_funcs:
        ast.NodeVisitor.generic_visit(self, in_node)
      else:
        raise SyntaxError("function '%s' is not allowed" % in_node.func.id)
    def visit_Name(self, in_node):
      try:
        eval(in_node.id)
      except NameError:
        ast.NodeVisitor.generic_visit(self, in_node)
      else:
        if in_node.id in self.CONST.lang_filter_PYTHON_names:
          ast.NodeVisitor.generic_visit(self, in_node)
        else:
          raise SyntaxError("name '%s' is reserved" % in_node.id)
    def visit_Import(self, in_node):
      SyntaxError("import statement is not allowed")
    def visit_ImportFrom(self, in_node):
      SyntaxError("import from statement is not allowed")
    def generic_visit(self, in_node):
      if type(in_node).__name__ in self.CONST.lang_filter_PYTHON_types:
        ast.NodeVisitor.generic_visit(self, in_node)
      else:
        raise SyntaxError("type '%s' is not allowed" % type(in_node).__name__)
  my_check = Python_checker_();
  my_check.CONST = self.CONST
  try:
    for my_line in re.split(r'[\r\n#;]', in_code):
      my_check.check(my_line)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_LANGUAGE_SYNTAX, str(my_ex))
    return False
  return True
  #
  # End of irciot_EL_check_Python_code_()

 # incomplete
 def irciot_EL_check_code_(self, in_lang, in_code):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  if not isinstance(in_code, str):
    return False
  # Common filters:
  for my_re in self.__common_filter_matchers:
    if my_re.match(in_code):
      self.irciot_EL_error_(self.CONST.err_COMMON_FILTER, '%s' % my_re)
      return False
  # Language-specific filters:
  if in_lang == self.CONST.lang_JRE:
    return self.irciot_EL_check_Java_code_(in_code)
  elif in_lang == self.CONST.lang_LUA:
    return self.irciot_EL_check_LUA_code_(in_code)
  elif in_lang == self.CONST.lang_PYTHON:
    return self.irciot_EL_check_Python_code_(in_code)

  return True

 # incomplete
 def __irciot_EL_run_ANSYML_code_(self, in_code, in_environment):
  my_inventory = self.__ANSINV.manager.InventoryManager()
  my_vars = self.__ANSVAR.VariableManager()
  my_vars.extra_vars = in_environment

  del my_vars
  return None

 # incomplete
 def __irciot_EL_run_JAVA_code_(self, in_code, in_environment):

  return None

 # incomplete
 def __irciot_EL_run_JS_code_(self, in_code, in_environment):

  return None

 # incomplete
 def __irciot_EL_run_LUA_code_(self, in_code, in_environment):
  my_lua = self.__LUA.LuaRuntime()
  for in_key in in_environment.keys():
    my_value = in_environment[ in_key ]
    if isinstance(my_value, str):
      my_lua.globals()[ in_key ] = my_value
  try:
    my_out = my_lua.eval(in_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  del my_lua
  return my_out

 # incomplete
 def __irciot_EL_run_Python_code_(self, in_code, in_environment):
  @contextlib.contextmanager
  def Python_stdout_(in_stdout = None):
    import sys
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    if in_stdout == None:
      in_stdout = StringIO()
    sys.stdout = in_stdout
    sys.stderr = None
    yield in_stdout
    sys.stdout = old_stdout
    sys.stderr = old_stderr
  try:
    with Python_stdout_() as my_out:
      exec(in_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
    return ""
  return my_out.getvalue()

 # incomplete
 def irciot_EL_run_code_(self, in_lang, in_code, in_environment = {}):
  if not self.irciot_EL_check_code_(in_lang, in_code):
    return None
  if not self.irciot_EL_check_environment_(in_lang, in_environment):
    return None
  try:
    if in_lang == self.CONST.lang_ANSYML:
      return self.__irciot_EL_run_ANSYML_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_BASH:
      pass
    elif in_lang == self.CONST.lang_BASIC:
      pass
    elif in_lang == self.CONST.lang_CS:
      pass
    elif in_lang == self.CONST.lang_CSP:
      pass
    elif in_lang == self.CONST.lang_GO:
      pass
    elif in_lang == self.CONST.lang_JRE:
      return self.__irciot_EL_run_JAVA_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_JS:
      return self.__irciot_EL_run_JS_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_LUA:
      return self.__irciot_EL_run_LUA_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_QML:
      pass
    elif in_lang == self.CONST.lang_PERL:
      pass
    elif in_lang == self.CONST.lang_PHP:
      pass
    elif in_lang == self.CONST.lang_R:
      pass
    elif in_lang == self.CONST.lang_PYTHON:
      return self.__irciot_EL_run_Python_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_RUBY:
      pass
    elif in_lang == self.CONST.lang_SWIFT:
      pass
  except:
    pass
  return None
  #
  # End of irciot_EL_run_code_()

 def irciot_EL_import_(self, in_module_name):
  import importlib
  try:
    return importlib.import_module(in_module_name)
  except ImportError:
    self.irciot_EL_error_(self.CONST.err_LOADING_MODULES, None)
    return None
  #
  # End of irciot_EL_import_()

 def irciot_EL_admit_language_(self, in_lang):
  if in_lang not in self.__allowed_EL:
    if self.irciot_EL_check_lang_(in_lang):
      self.__allowed_EL += [ in_lang ]
      return True
  return False

 def irciot_EL_revoke_language_(self, in_lang):
  if in_lang in self.__allowed_EL:
    self.irciot_EL_finish_language_(in_lang)
    self.__allowed_EL.remove(in_lang)

 def irciot_EL_allowed_languages_(self):
  return self.__allowed_EL

 # incomplete
 def irciot_EL_init_language_(self, in_lang):
  if in_lang not in self.__allowed_EL:
    return False
  if in_lang == self.CONST.lang_ANSYML:
    self.__ANSYML = self.irciot_EL_import_(self.CONST.mod_ANSYML)
    if self.__ANSYML != None:
      self.__ANSINV = self.irciot_EL_import_(self.CONST.mod_ANSINV)
      if self.__ANSINV is None:
        del self.__ANSYML
      else:
        self.__ANSVAR = self.irciot_EL_import_(self.CONST.mod_ANSVAR)
        if self.__ANSVAR is None:
          del self.__ANSYML
          del self.__ANSINV
        else:
          return True
  elif in_lang == self.CONST.lang_BASH:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_BASIC:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_CS:
    pass
  elif in_lang == self.CONST.lang_CSP:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_GO:
    pass
  elif in_lang == self.CONST.lang_JRE:
    self.__JRE = self.irciot_EL_import_(self.CONST.mod_JRE)
    if self.__JRE != None:
      return True
  elif in_lang == self.CONST.lang_JS:
    self.__JS  = self.irciot_EL_import_(self.CONST.mod_JS)
    if self.__JS  != None:
      return True
  elif in_lang == self.CONST.lang_LUA:
    self.__LUA = self.irciot_EL_import_(self.CONST.mod_LUA)
    if self.__LUA != None:
      return True
  elif in_lang == self.CONST.lang_QML:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_PERL:
    pass
  elif in_lang == self.CONST.lang_PHP:
    pass
  elif in_lang == self.CONST.lang_R:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_PYTHON:
    return True
  elif in_lang == self.CONST.lang_RUBY:
    pass
  elif in_lang == self.CONST.lang_SWIFT:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  return False
  # End of irciot_EL_init_language_()

 def irciot_EL_finish_language_(self, in_lang):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  try:
    if in_lang == self.CONST.lang_ANSYML:
      del self.__ANSVAR
      del self.__ANSINV
      del self.__ANSYML
    elif in_lang == self.CONST.lang_BASH:
      pass
    elif in_lang == self.CONST.lang_BASIC:
      pass
    elif in_lang == self.CONST.lang_CS:
      pass
    elif in_lang == self.CONST.lang_CSP:
      pass
    elif in_lang == self.CONST.lang_GO:
      pass
    elif in_lang == self.CONST.lang_JRE:
      del self.__JRE
    elif in_lang == self.CONST.lang_JS:
      del self.__JS
    elif in_lang == self.CONST.lang_LUA:
      del self.__LUA
    elif in_lang == self.CONST.lang_QML:
      pass
    elif in_lang == self.CONST.lang_PERL:
      pass
    elif in_lang == self.CONST.lang_PHP:
      pass
    elif in_lang == self.CONST.lang_R:
      pass
    elif in_lang == self.CONST.lang_PYTHON:
      pass
    elif in_lang == self.CONST.lang_RUBY:
      pass
    elif in_lang == self.CONST.lang_SWIFT:
      pass
  except:
    return False
  return True
  #
  # End of irciot_EL_finish_language_()

