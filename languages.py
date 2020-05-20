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

# ATTENTION!!! THIS CLASS WAS TESTED ONLY ON LINUX, WHILE ON THE
# OTHER OS'ES IT DOES NOT WORK YET. ALSO, USING THIS CLASS IS
# DANGEROUS, BECAUSE A POTENTIAL ATTACKER CAN GAIN REMOTE CONTROL
# ON YOUR SYSTEM. USE IT IF YOU KNOW WHAT ARE YOU DOING!

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
import tracemalloc
import contextlib
import signal

class PyLayerIRCIoT_EL_(object):

 class CONST_EL_(object):
  #
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.201'
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
  lang_PERL   = 'pl'  # Perl
  lang_PHP    = 'php' # PHP
  lang_PYTHON = 'py'  # Python
  lang_R      = 'r'   # GNU R
  lang_RUBY   = 'rb'  # Ruby
  lang_SMTLK  = 'st'  # GNU SmallTalk
  lang_SWIFT  = 'swt' # Apple Swift
  lang_TCL    = 'tcl' # TCL Script
  #
  if not CAN_debug_library:
    lang_ALL = [ lang_PYTHON ] # More safer but still dangerous
  else:
    lang_ALL = [
     lang_ANSYML, lang_BASH,   lang_BASIC, lang_CS,  lang_CSP,
     lang_GO,     lang_JRE,    lang_JS,    lang_LUA, lang_PERL,
     lang_PHP,    lang_PYTHON, lang_RUBY,  lang_R,   lang_SWIFT,
     lang_TCL
    ]
  #
  err_UNKNOWN_LANGUAGE = 1001
  err_UNSUPPORTED_YET  = 1002
  err_BAD_ENVIRONMENT  = 1003
  err_COMMON_FILTER    = 1004
  err_LANGUAGE_FILTER  = 1005
  err_LANGUAGE_SYNTAX  = 1007
  err_CODE_SIZE_LIMIT  = 1008
  err_LOADING_MODULES  = 1009
  err_CODE_EXECUTION   = 1010
  #
  err_DESCRIPTIONS = {
   err_UNKNOWN_LANGUAGE : "Unknown programming langauge",
   err_UNSUPPORTED_YET  : "This language is not yet supported",
   err_LANGUAGE_SYNTAX  : "Incorrect syntax for this language",
   err_LOADING_MODULES  : "Unable to load required modules",
   err_BAD_ENVIRONMENT  : "Invalid language environment",
   err_COMMON_FILTER    : "Code declined by common filter",
   err_LANGUAGE_FILTER  : "Code declined by language filter",
   err_CODE_SIZE_LIMIT  : "Code size limit exceeded",
   err_CODE_EXECUTION   : "Problem while executing the code"
  }
  #
  mod_ANSVAR = 'ansible.vars.manager'
  mod_ANSINV = 'ansible.inventory.manager'
  mod_ANSYML = 'ansible.executor'
  mod_JRE = 'py4j.java_gateway'
  mod_JS  = 'js2py'
  mod_LUA = 'lupa'
  mod_TCL = 'tkinter'
  #
  common_filter_regexps = [
   '.*\\\\\\.*', '.*\\\\\'.*', '.*\\\\\".*', # Disable some escaping
   '.*\_\_\s*\.\s*\_\_.*'
  ]
  #
  lang_filter_BASIC_regexps  = []
  lang_filter_PYTHON_regexps = []
  lang_filter_PYTHON_types = {  'Add', 'And', 'Assign', 'Attribute',
   'BinOp', 'BitAnd', 'BitOr', 'BitXor', 'BoolOp', 'Dict', 'Div', 'Else',
   'Expr', 'For', 'If', 'Index', 'keyword', 'List', 'Load', 'Mod', 'Module',
   'Mult', 'NameConstant', 'Not', 'Num', 'Or', 'Set', 'Store', 'Str', 'Sub',
   'Subscript', 'Tuple',  'UAdd', 'UnaryOp', 'USub', 'While', 'Compare', 'Eq' }
  lang_filter_PYTHON_funcs = { 'abs', 'max', 'min', 'int', 'float', 'range',
   'set', 'print' }
  lang_filter_PYTHON_names = { 'True', 'False', 'None' }
  lang_filter_PYTHON_names = { *lang_filter_PYTHON_names, *lang_filter_PYTHON_funcs }
  lang_filter_RUBY_regexps = []
  lang_filter_LUA_regexps  = []
  lang_filter_TCL_regexps  = [ '.*package\s*require.*', '.*vwait.*' ]
  lang_filter_JAVA_regexps = []
  lang_filter_JS_regexps   = []
  #
  environment_first_chars  = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
  environment_second_chars = environment_first_chars + "0123456789_"
  #
  default_execution_timeout = 3 # in seconds
  default_maximal_code_size = 4096 # bytes
  default_maximal_mem_usage = 1048576 # bytes
  default_maximal_cpu_usage = 5 # percent of one core
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
  self.__execution_timeout = self.CONST.default_execution_timeout
  self.__maximal_code_size = self.CONST.default_maximal_code_size
  self.__maximal_mem_usage = self.CONST.default_maximal_mem_usage
  self.__maximal_cpu_usage = self.CONST.default_maximal_cpu_usage
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

 def irciot_EL_set_timeout_(in_timeout):
  if not isinstance(in_timeout, int):
    return
  self.__execution_timeout = in_timeout

 def irciot_EL_set_code_size_(in_size):
  if not isinstance(in_size, int):
    return
  self.__maximal_code_size = in_size

 # incomplete
 def irciot_EL_check_environment_(self, in_lang, in_environment):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  if not isinstance(in_environment, dict):
    return False
  for my_key in in_environment.keys():
    if not isinstance(my_key, str):
      return False
    if my_key == "":
      return False
    if my_key[0] not in self.CONST.environment_first_chars:
      return False
    for my_char in my_key:
      if my_char not in self.CONST.environment_second_chars:
        return False
    my_item = in_environment[my_key]
    if not isinstance(my_item, str):
      return False

  return True

 def irciot_EL_check_matchers_(self, in_code, in_matchers):
  if not isinstance(in_matchers, list):
    return True
  for my_re in in_matchers:
    if my_re.match(in_code):
      self.irciot_EL_error_(self.CONST.err_LANGUAGE_FILTER, None)
      return False
  return True

 # incomplete
 def irciot_EL_check_Ansible_code_(self, in_code):
  return True

 # incomplete
 def irciot_EL_check_BASIC_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__BASIC_filter_matchers):
    return False
  return True

 # incomplete
 def irciot_EL_check_Java_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__JAVA_filter_matchers):
    return False
  return True

 # incomplete
 def irciot_EL_check_JS_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__JS_filter_matchers):
    return False
  return True

 # incomplete
 def irciot_EL_check_LUA_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__LUA_filter_matchers):
    return False
  return True

 # incomplete
 def irciot_EL_check_TCL_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__TCL_filter_matchers):
    return False
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
    my_line = in_code.replace(r'[\r\n]', ';')
    my_check.check(my_line)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_LANGUAGE_SYNTAX, str(my_ex))
    return False
  return True
  #
  # End of irciot_EL_check_Python_code_()

 # incomplete
 def irciot_EL_check_Ruby_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__RUBY_filter_matchers):
    return False
  return True

 # incomplete
 def irciot_EL_check_code_(self, in_lang, in_code):
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  if not isinstance(in_code, str):
    return False
  if len(in_code) > self.__maximal_code_size:
    self.irciot_EL_error_(self.CONST.err_CODE_SIZE_LIMIT, \
      '+%d bytes' % int(len(in_code) - self.__maximal_code_size))
  # Common filters:
  for my_re in self.__common_filter_matchers:
    if my_re.match(in_code):
      self.irciot_EL_error_(self.CONST.err_COMMON_FILTER, None)
      return False
  # Language-specific filters:
  if in_lang == self.CONST.lang_ANSYML:
    return self.irciot_EL_check_Ansible_code_(in_code)
  elif in_lang == self.CONST.lang_BASIC:
    return self.irciot_EL_check_BASIC_code_(in_code)
  elif in_lang == self.CONST.lang_JRE:
    return self.irciot_EL_check_Java_code_(in_code)
  elif in_lang == self.CONST.lang_JS:
    return self.irciot_EL_check_JS_code_(in_code)
  elif in_lang == self.CONST.lang_LUA:
    return self.irciot_EL_check_LUA_code_(in_code)
  elif in_lang == self.CONST.lang_PYTHON:
    return self.irciot_EL_check_Python_code_(in_code)
  elif in_lang == self.CONST.lang_RUBY:
    return self.irciot_EL_check_Ruby_code_(in_code)
  elif in_lang == self.CONST.lang_TCL:
    return self.irciot_EL_check_TCL_code_(in_code)

  return True

 @contextlib.contextmanager
 def python_stdout_(self, in_stdout = None):
   import sys
   def restore_io_(in_out, in_err):
     sys.stdout = in_out
     sys.stderr = in_err
   old_stdout = sys.stdout
   old_stderr = sys.stderr
   if in_stdout == None:
     in_stdout = StringIO()
   sys.stdout = in_stdout
   sys.stderr = None
   try:
     yield in_stdout
   except Exception as my_ex:
     restore_io_(old_stdout, old_stderr)
     raise Exception(my_ex)
   restore_io_(old_stdout, old_stderr)
 #
 # End of python_stdout_()

 def timeout_termination_(self):
   raise Exception('Execution timed out: %s sec.' \
     % self.__execution_timeout)

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
  my_context = self.__JS.EvalJs()
  my_code = 'var output;document={write:function(value){output=value;}};'
  my_code += in_code
  try:
    my_context.execute(my_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  my_out = None
  try:
    if my_context.output != None:
      my_out = str(my_context.output)
  except:
    pass
  del my_context
  return my_out

 # incomplete
 def __irciot_EL_run_LUA_code_(self, in_code, in_environment):
  my_lua = self.__LUA.LuaRuntime()
  for my_key in in_environment.keys():
    my_value = in_environment[ my_key ]
    if isinstance(my_value, str):
      my_lua.globals()[ my_key ] = my_value
  my_out = None
  try:
    my_out = my_lua.eval(in_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  del my_lua
  return my_out

 # incomplete
 def __irciot_EL_run_TCL_code_(self, in_code, in_environment):
  my_tcl = self.__TCL.Tcl();
  my_tcl.after(self.__execution_timeout * 1000, self.timeout_termination_)
  my_out = None
  for my_key in in_environment.keys():
    my_str = in_environment[ my_key ].replace('"', '\\"')
    my_tcl.eval('set %s "%s"' % (my_key, my_str))
  try:
    my_out = my_tcl.eval(in_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  del my_tcl
  return my_out

 # incomplete
 def __irciot_EL_run_Python_code_(self, in_code, in_environment):
  my_dict = {}
  for my_name in self.CONST.lang_filter_PYTHON_funcs:
    my_dict[ my_name ] = eval(compile(my_name, '<str>', 'eval'))
  for my_key in in_environment.keys():
    my_value = in_environment[ my_key ]
    if isinstance(my_value, str):
      my_dict[ my_key ] = my_value
  with self.python_stdout_() as my_out:
    exec(in_code, { '__builtins__': None }, my_dict)
  return my_out.getvalue()
  #
  # End of __irciot_EL_run_Python_code_()

 # incomplete
 def __irciot_EL_run_Ruby_code_(self, in_code, in_environment):
  my_out = ""

  return my_out
  #
  # End of __irciot_EL_run_Ruby_code_()

 # incomplete
 def irciot_EL_run_code_(self, in_lang, in_code, in_environment = {}):
  def timeout_signal_(in_signal, in_frame):
    self.timeout_termination_()
  if not self.irciot_EL_check_code_(in_lang, in_code):
    return None
  if not self.irciot_EL_check_environment_(in_lang, in_environment):
    self.irciot_EL_error_(self.CONST.err_BAD_ENVIRONMENT, None)
    return None
  my_out = None
  signal.signal(signal.SIGALRM, timeout_signal_)
  signal.alarm(self.__execution_timeout)
  try:
    if in_lang == self.CONST.lang_ANSYML:
      my_out = self.__irciot_EL_run_ANSYML_code_(in_code, in_environment)
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
      my_out = self.__irciot_EL_run_JAVA_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_JS:
      my_out = self.__irciot_EL_run_JS_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_LUA:
      my_out = self.__irciot_EL_run_LUA_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_PERL:
      pass
    elif in_lang == self.CONST.lang_PHP:
      pass
    elif in_lang == self.CONST.lang_R:
      pass
    elif in_lang == self.CONST.lang_PYTHON:
      my_out = self.__irciot_EL_run_Python_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_RUBY:
      my_out = self.__irciot_EL_run_Ruby_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_SWIFT:
      pass
    elif in_lang == self.CONST.lang_TCL:
      my_out = self.__irciot_EL_run_TCL_code_(in_code, in_environment)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  signal.alarm(0)
  if my_out == None:
    my_out = ""
  elif not isinstance(my_out, str):
    my_out = str(my_out)
  return my_out
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
  if in_lang in self.__allowed_EL:
    return True
  else:
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

 def __irciot_EL_matchers_(self, in_regexps):
  my_matchers = []
  for my_regexp in in_regexps:
    my_matchers += [ re.compile(my_regexp) ]
  return my_matchers

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
    self.__BASIC_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_BASIC_regexps)
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_CS:
    pass
  elif in_lang == self.CONST.lang_CSP:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_GO:
    pass
  elif in_lang == self.CONST.lang_JRE:
    self.__JAVA_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_JAVA_regexps)
    self.__JRE = self.irciot_EL_import_(self.CONST.mod_JRE)
    if self.__JRE != None:
      return True
  elif in_lang == self.CONST.lang_JS:
    self.__JS_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_JS_regexps)
    self.__JS  = self.irciot_EL_import_(self.CONST.mod_JS)
    if self.__JS  != None:
      return True
  elif in_lang == self.CONST.lang_LUA:
    self.__LUA_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_LUA_regexps)
    self.__LUA = self.irciot_EL_import_(self.CONST.mod_LUA)
    if self.__LUA != None:
      return True
  elif in_lang == self.CONST.lang_PERL:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_PHP:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_R:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_PYTHON:
    self.__PYTHON_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_PYTHON_regexps)
    return True
  elif in_lang == self.CONST.lang_RUBY:
    self.__RUBY_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_RUBY_regexps)
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_SWIFT:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_TCL:
    self.__TCL_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_TCL_regexps)
    self.__TCL = self.irciot_EL_import_(self.CONST.mod_TCL)
    if self.__TCL != None:
      return True
  self.irciot_EL_finish_language_(in_lang)
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
      del self.__BASIC_filter_matchers
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
      del self.__JAVA_filter_matchers
    elif in_lang == self.CONST.lang_JS:
      del self.__JS
      del self.__JS_filter_matchers
    elif in_lang == self.CONST.lang_LUA:
      del self.__LUA
      del self.__LUA_filter_matchers
    elif in_lang == self.CONST.lang_PERL:
      pass
    elif in_lang == self.CONST.lang_PHP:
      pass
    elif in_lang == self.CONST.lang_R:
      pass
    elif in_lang == self.CONST.lang_PYTHON:
      del self.__PYTHON_filter_matchers
    elif in_lang == self.CONST.lang_RUBY:
      del self.__RUBY_filter_matchers
    elif in_lang == self.CONST.lang_SWIFT:
      pass
    elif in_lang == self.CONST.lang_TCL:
      del self.__TCL
      del self.__TCL_filter_matchers
  except:
    return False
  return True
  #
  # End of irciot_EL_finish_language_()

