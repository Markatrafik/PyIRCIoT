'''
'' PyIRCIoT_EL_ (IRC-IoT Embedded Languages class)
''
'' Copyright (c) 2019-2021 Alexey Y. Woronov
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
try:
 import signal
except: pass
try: # insecure, but for development
 from irciot_shared import *
except:
 from PyIRCIoT.irciot_shared import *

class PyLayerIRCIoT_EL_( irciot_shared_ ):

 class CONST_EL_( irciot_shared_.CONST ):
  #
  irciot_protocol_version = '0.3.33'
  #
  irciot_library_version  = '0.0.235'
  #
  # IRC-IoT Embedded Languages tags:
  #
  lang_ANSYML = 'yml' # Ansible YAML
  lang_BASH   = 'sh'  # Bash Script
  lang_BASIC  = 'bas' # BASIC
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
  lang_SMTLK  = 'gst' # GNU SmallTalk
  lang_SWIFT  = 'swt' # Apple Swift
  lang_TCL    = 'tcl' # TCL Script
  #
  if not CAN_debug_library:
    lang_ALL = [ lang_PYTHON ] # More safer but still dangerous
  else:
    lang_ALL = [
     lang_ANSYML, lang_BASH, lang_BASIC, lang_CSP,   lang_GO,
     lang_JRE,    lang_JS,   lang_LUA,   lang_PERL,  lang_PHP,
     lang_PYTHON, lang_RUBY, lang_R,     lang_SWIFT, lang_TCL
    ]
  #
  err_EL_ERROR         = 1000
  err_UNKNOWN_LANGUAGE = 1001
  err_UNSUPPORTED_YET  = 1002
  err_BAD_ENVIRONMENT  = 1003
  err_COMMON_FILTER    = 1004
  err_LANGUAGE_FILTER  = 1005
  err_LANGUAGE_SYNTAX  = 1007
  err_CODE_SIZE_LIMIT  = 1008
  err_LOADING_MODULES  = 1009
  err_CODE_EXECUTION   = 1010
  err_TIME_EXECUTION   = 1024
  err_LEXICAL_ANALISIS = 1025
  err_ILLEGAL_TYPE     = 1100
  err_ILLEGAL_SUBST    = 1101
  err_ILLEGAL_FUNCT    = 1103
  err_ILLEGAL_IMPORT   = 1121
  err_ILLEGAL_IMPORTF  = 1122
  err_RESERVED_NAME    = 1131
  err_UNRECOG_INPUT    = 1151
  #
  err_DESCRIPTIONS = irciot_shared_.CONST.err_DESCRIPTIONS
  err_DESCRIPTIONS.update({
   err_EL_ERROR         : "EL error ({}):",
   err_UNKNOWN_LANGUAGE : "Unknown programming langauge",
   err_UNSUPPORTED_YET  : "This language is not yet supported",
   err_LANGUAGE_SYNTAX  : "Incorrect syntax for this language",
   err_LOADING_MODULES  : "Unable to load required modules",
   err_BAD_ENVIRONMENT  : "Invalid language environment",
   err_COMMON_FILTER    : "Code declined by common filter",
   err_LANGUAGE_FILTER  : "Code declined by language filter",
   err_CODE_SIZE_LIMIT  : "Code size limit exceeded",
   err_CODE_EXECUTION   : "Problem while executing the code",
   err_TIME_EXECUTION   : "Execution timed out",
   err_LEXICAL_ANALISIS : "lexical analysis failed",
   err_ILLEGAL_TYPE     : "The type '{}' is not allowed",
   err_ILLEGAL_FUNCT    : "The function '{}' is not allowed",
   err_ILLEGAL_SUBST    : "command substitution is not allowed",
   err_ILLEGAL_IMPORT   : "'import' statement is not allowed",
   err_ILLEGAL_IMPORTF  : "'import' 'from' statement is not allowed",
   err_RESERVED_NAME    : "The name '{}' is reserved",
   err_UNRECOG_INPUT    : "Unrecognised input: '{}'"
  })
  #
  mod_ANSLDR = 'ansible.parsing.dataloader'
  mod_ANSVAR = 'ansible.vars.manager'
  mod_ANSINV = 'ansible.inventory.manager'
  mod_ANSPLY = 'ansible.playbook.play'
  mod_ANSTQM = 'ansible.executor.task_queue_manager'
  mod_ANSCBP = 'ansible.plugins.callback'
  mod_CSPSYS = 'intersys.pythonbind'
  mod_BASTOK = 'PyBasic.basictoken'
  mod_BASLEX = 'PyBasic.lexer'
  mod_BASPRG = 'PyBasic.program'
  mod_BSHLEX = 'bashlex'
  mod_PHPLEX = 'phply.phplex'
  mod_PHPPAR = 'phply.phpparse'
  mod_R_ROBJ = 'rpy2.robjects'
  mod_R_INTF = 'rpy2.rinterface'
  mod_MATH = 'math'
  mod_JRE = 'py4j.java_gateway'
  mod_JS  = 'js2py'
  mod_LUA = 'lupa'
  mod_TCL = 'tkinter'
  #
  common_filter_regexps = [
   '.*\\\\\\.*', '.*\\\\\'.*', '.*\\\\\".*', # Disable some escaping
   '.*__\s*\.\s*__.*'
  ]
  #
  lang_filter_BASH_regexps = [ '^\/sbin.*', '.*>.*' ]
  lang_filter_BASH_funcs   = { 'printf', 'echo' }
  lang_filter_BASIC_regexps = []
  lang_filter_PYTHON_regexps = [ '.*__[a-z]*__.*' ]
  lang_filter_PYTHON_types = { 'Add', 'And', 'Assign', 'Attribute', 'Slice',
   'BinOp', 'BitAnd', 'BitOr', 'BitXor', 'BoolOp', 'Dict', 'Div', 'Else', 'Eq',
   'Expr', 'For', 'If', 'Index', 'keyword', 'List', 'Load', 'Mod', 'Module',
   'Mult', 'NameConstant', 'Not', 'Num', 'Or', 'Pass', 'Set', 'Store', 'Str',
   'Sub', 'Subscript', 'Tuple', 'UAdd', 'UnaryOp', 'USub', 'While', 'Compare',
   'Constant' }
  lang_filter_PYTHON_maths = { 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
   'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
   'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh',
   'sqrt', 'tan', 'tanh' }
  lang_filter_PYTHON_funcs = { 'abs', 'max', 'min', 'bool', 'int', 'float', 'range',
   'set', 'print', 'len', 'str', 'type', 'isinstance' }
  lang_filter_PYTHON_funcs = { *lang_filter_PYTHON_funcs, *lang_filter_PYTHON_maths }
  lang_filter_PYTHON_names = { 'True', 'False', 'None' }
  lang_filter_PYTHON_names = { *lang_filter_PYTHON_names, *lang_filter_PYTHON_funcs }
  lang_filter_PHP_tokens   = { 'VARIABLE', 'STRING', 'EQUALS', 'LNUMBER', 'SEMI',
   'PRINT', 'LPAREN', 'RPAREN', 'PLUS', 'MINUS', 'MUL', 'DIV', 'IF', 'COLON', 'ELSE',
   'IS_GREATER', 'IS_SMALLER', 'LBRACE', 'RBRACE', 'NOT', 'XOR', 'FOR', 'WHILE',
   'QUOTE', 'ENCAPSED_AND_WHITESPACE', 'CONSTANT_ENCAPSED_STRING', 'IS_NOT_EQUAL' }
  lang_filter_PHP_regexps  = []
  lang_filter_R_regexps    = []
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
  default_maximal_code_size = 2048 # bytes
  default_maximal_mem_usage = 1048576 # bytes
  default_maximal_cpu_usage = 5 # percent of one core
  #
  def __setattr__(self, *_):
    pass

 def __init__(self):
  #
  self.CONST = self.CONST_EL_()
  #
  super(PyLayerIRCIoT_EL_, self).__init__()
  #
  self.__allowed_EL = []
  self.__common_filter_matchers = []
  for my_regexp in self.CONST.common_filter_regexps:
    self.__common_filter_matchers += [ re.compile(my_regexp) ]
  self.__execution_timeout = self.CONST.default_execution_timeout
  self.__maximal_code_size = self.CONST.default_maximal_code_size
  self.__maximal_mem_usage = self.CONST.default_maximal_mem_usage
  self.__maximal_cpu_usage = self.CONST.default_maximal_cpu_usage
  self.__os_name = self.get_os_name_()
  #
  self.__ansible_vault_password = None
  #
  self.errors = self.CONST.err_DESCRIPTIONS
  #
  self.irciot_set_locale_(self.lang)
  #
  self._silence = not CAN_debug_library
  #
  # End of PyLayerIRCIoT_EL_.__init__()

 def __del__(self):
  self.__ansibe_vault_password \
   = self.wipe_string_(self.__ansible_vault_password)

 def irciot_set_locale_(self, in_lang):
  if not isinstance(in_lang, str):
    return
  self.lang = in_lang
  my_desc = {}
  try:
    from PyIRCIoT.irciot_errors \
    import irciot_get_common_error_descriptions_
    my_desc.update(irciot_get_common_error_descriptions_(in_lang))
    my_desc = self.validate_descriptions_(my_desc)
    if my_desc != {}:
      self.errors.update(my_desc)
  except:
    pass
  my_desc = {}
  try:
    from PyIRCIoT.irciot_errors \
    import irciot_get_EL_error_descriptions_
    my_desc.update(irciot_get_EL_error_descriptions_(in_lang))
    my_desc = self.validate_descriptions_(my_desc)
    if my_desc != {}:
      self.errors.update(my_desc)
  except:
    pass

 def irciot_EL_error_(self, in_error_code, in_addon):
  if in_error_code in self.errors.keys():
    my_descr = self.errors[in_error_code]
    if isinstance(in_addon, str):
      my_descr += " ({})".format(in_addon)
  else:
    return
  if not self._silence:
    print(self.errors[self.CONST.err_EL_ERROR].format(in_error_code), my_descr)
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
  if not isinstance(in_timeout, int): return
  self.__execution_timeout = in_timeout

 def irciot_EL_set_code_size_(in_size):
  if not isinstance(in_size, int): return
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
 def irciot_EL_check_BASH_code_(self, in_code):
  class bash_checker_(self.__BSHLEX.ast.nodevisitor):
    def check(self, in_code):
      my_trees = self.bashlex.parse(in_code)
      for my_tree in my_trees:
        self.visit(my_tree)
    def visit(self, in_node):
      # print(in_node)
      super(bash_checker_, self).visit(in_node)
    def visitcommandsubstitution(self, in_node, in_command):
      raise SyntaxError(self.errors[self.CONST.err_ILLEGAL_SUBST])
  if not self.irciot_EL_check_matchers_(in_code, self.__BASH_filter_matchers):
    return False
  my_line = in_code.replace(r'[\r\n]', ';')
  my_check = bash_checker_()
  my_check.CONST = self.CONST
  my_check.errors = self.errors
  my_check.bashlex = self.__BSHLEX
  try:
    my_check.check(my_line)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_LANGUAGE_SYNTAX, str(my_ex))
    return False
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
 def irciot_EL_check_PHP_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__PHP_filter_matchers):
    return False
  # Warning: This code is only for testing of phply library... will be removed
  my_lexer = self.__PHPLEX.lexer.clone()
  my_lexer.input("<?php " + in_code + "?>")
  my_error = None
  while True:
    try:
      my_tok = my_lexer.token()
      if not my_tok:
        break
    except:
      my_error = self.errors[self.CONST.LEXICAL_ANALISIS]
      break
    if my_tok.type not in self.CONST.lang_filter_PHP_tokens:
      my_error = "ivalid " + str(my_tok)
      break
  if my_error != None:
    self.irciot_EL_error_(self.CONST.err_LANGUAGE_SYNTAX, my_error)
    # It's not a syntax it's lexic, but we could say so ...
    return False

  return True

 # incomplete
 def irciot_EL_check_TCL_code_(self, in_code):
  class TCL_checker_(ast.NodeVisitor):
    def check(self, in_code):
      pass
    def visit(self, in_node):
      pass
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
        raise SyntaxError(self.errors[self.CONST.err_ILLEGAL_FUNCT].format( \
         in_node.func.id))
    def visit_Name(self, in_node):
      try:
        eval(in_node.id)
      except NameError:
        ast.NodeVisitor.generic_visit(self, in_node)
      else:
        if in_node.id in self.CONST.lang_filter_PYTHON_names:
          ast.NodeVisitor.generic_visit(self, in_node)
        else:
          raise SyntaxError(self.errors[self.CONST.err_RESERVED_NAME].format( \
           in_node.id))
    def visit_Import(self, in_node):
      raise SyntaxError(self.errors[self.CONST.err_ILLEGAL_IMPORT])
    def visit_ImportFrom(self, in_node):
      raise SyntaxError(self.errors[self.CONST.err_ILLEGAL_IMPORTF])
    def generic_visit(self, in_node):
      if type(in_node).__name__ in self.CONST.lang_filter_PYTHON_types:
        ast.NodeVisitor.generic_visit(self, in_node)
      else:
        raise SyntaxError(self.errors[self.CONST.err_ILLEGAL_TYPE].format( \
         type(in_node).__name__))
  if not self.irciot_EL_check_matchers_(in_code, self.__PYTHON_filter_matchers):
    return False
  my_check = Python_checker_();
  my_check.CONST = self.CONST
  my_check.errors = self.errors
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
 def irciot_EL_check_R_code_(self, in_code):
  if not self.irciot_EL_check_matchers_(in_code, self.__R_filter_matchers):
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
     '+{}{}'.format(len(in_code) - self.__maximal_code_size, \
      errors[self.CONST.err_BYTES]))
  # Common filters:
  for my_re in self.__common_filter_matchers:
    if my_re.match(in_code):
      self.irciot_EL_error_(self.CONST.err_COMMON_FILTER, None)
      return False
  # Language-specific filters:
  if in_lang == self.CONST.lang_ANSYML:
    return self.irciot_EL_check_Ansible_code_(in_code)
  elif in_lang == self.CONST.lang_BASH:
    return self.irciot_EL_check_BASH_code_(in_code)
  elif in_lang == self.CONST.lang_BASIC:
    return self.irciot_EL_check_BASIC_code_(in_code)
  elif in_lang == self.CONST.lang_JRE:
    return self.irciot_EL_check_Java_code_(in_code)
  elif in_lang == self.CONST.lang_JS:
    return self.irciot_EL_check_JS_code_(in_code)
  elif in_lang == self.CONST.lang_LUA:
    return self.irciot_EL_check_LUA_code_(in_code)
  elif in_lang == self.CONST.lang_PHP:
    return self.irciot_EL_check_PHP_code_(in_code)
  elif in_lang == self.CONST.lang_PYTHON:
    return self.irciot_EL_check_Python_code_(in_code)
  elif in_lang == self.CONST.lang_R:
    return self.irciot_EL_check_R_code_(in_code)
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

 def __timeout_termination_(self):
  raise Exception('{}: {}'.format( \
   self.errors[self.CONST.err_TIME_EXECUTION], \
   self.__execution_timeout) \
   + self.errors[self.CONST.err_SEC])

 def irciot_EL_set_Ansible_Vault_(in_password):
  if not isinstance(in_password, str):
    return False
  if in_password == "": return False
  self.__ansible_vault_passwod = self.copy_string_(in_password)
  in_password = self.wipe_string_(in_password)
  return True

 # incomplete
 def __irciot_EL_run_ANSYML_code_(self, in_code, in_environment = {}):
  import yaml
  class my_loader_class_(self.__ANSLDR.DataLoader):
    def __init__(self, *args, **kwargs):
      super(my_loader_class_, self).__init__(*args, **kwargs)
    def get_basedir(self):
      return ""
  class my_callback_class_(self.__ANSCBP.CallbackBase):
    result = None
    def __init__(self, *args, **kwargs):
      super(my_callback_class_, self).__init__(*args, **kwargs)
    def v2_runner_on_ok(self, result, **kwargs):
      self.result = json.dumps(result._result)
    def v2_runner_on_failed(self, result, *args, **kwargs):
      self.result = json.dumps(result._result)
  my_passwords = { 'vault_pass': self.__ansible_vault_password }
  my_loader = my_loader_class_()
  my_inv = self.__ANSINV.InventoryManager(loader = my_loader, \
    sources = 'localhost,')
  my_var = self.__ANSVAR.VariableManager(loader = my_loader, \
    inventory = my_inv)
  my_var._extra_vars = in_environment
  my_tasks = []
  my_load = yaml.load_all(in_code)
  for my_item in my_load:
    for my_subitem in my_item:
      my_dict = {}
      for my_subkey in my_subitem.keys():
        my_dict.update({ 'module': my_subkey,
         'args': my_subitem[ my_subkey ] })
        break
      my_tasks.append({ 'action': my_dict })
  my_source = {
    'name': 'IRC-IoT', 'hosts': [ 'localhost' ],
    'gather_facts': 'no', 'tasks': my_tasks }
  my_play = self.__ANSPLY.Play().load(my_source)
  my_callback = my_callback_class_()
  my_tqm  = self.__ANSTQM.TaskQueueManager(loader = my_loader, \
    inventory = my_inv, variable_manager = my_var, \
    passwords = my_passwords, stdout_callback = my_callback )
  try:
    my_ret = my_tqm.run(my_play)
  except Exception as my_ex:
    my_ret = -1
  if my_tqm is not None:
    my_tqm.cleanup()
  del my_tqm
  del my_play
  del my_var
  del my_inv
  del my_loader
  my_out = my_callback.result
  del my_callback
  if my_ret == -1:
    my_passwords['vault_pass'] \
     = self.wipe_string_(my_passwords['vault_pass'])
    raise Exception(str(my_ex))
  my_passwords['vault_pass'] \
   = self.wipe_string_(my_passwords['vault_pass'])
  return my_out
  #
  # End of __irciot_EL_run_ANSYML_code_()

 # incomplete
 def __irciot_EL_run_BASH_code_(self, in_code, in_environment = {}):

  return ""

 # incomplete
 def __irciot_EL_run_BASIC_code_(self, in_code, in_envronment = {}):
  my_lexer = self.__BASLEX.Lexer()
  my_prog  = self.__BASPRG.Program()
  my_token = self.__BASTOK.BASICToken
  my_code  = in_code
  if my_code[-1] != '\n':
    my_code += "\n"
  if "\nRUN\n" not in my_code:
    my_code += "RUN\n"
  if "\nEXIT\n" not in my_code:
    my_code += "EXIT\n"
  with self.python_stdout_() as my_out:
    for my_line in my_code.split('\n'):
      my_tokens = my_lexer.tokenize(my_line)
      if my_tokens[0].category == my_token.EXIT:
        break
      elif my_tokens[0].category == my_token.UNSIGNEDINT \
       and len(my_tokens) > 1:
        my_prog.add_stmt(my_tokens)
      elif my_tokens[0].category == my_token.UNSIGNEDINT \
       and len(my_tokens) == 1:
        my_prog.delete_statement(int(my_tokens[0].lexeme))
      elif my_tokens[0].category == my_token.RUN:
        my_prog.execute()
      elif my_tokens[0].category == my_token.LIST:
        my_prog.list()
      else:
        raise(self.errors[self.CONST.err_UNRECOG_INPUT].format( \
          my_tokens[0].lexeme()))
  del my_prog
  del my_lexer
  return my_out.getvalue()
  #
  # Endof of __irciot_EL_run_BASIC_code_()

 # incomplete
 def __irciot_EL_run_JAVA_code_(self, in_code, in_environment = {}):

  return None

 # incomplete
 def __irciot_EL_run_JS_code_(self, in_code, in_environment = {}):
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
 def __irciot_EL_run_PHP_code_(self, in_code, in_environment):

  return None

 # incomplete
 def __irciot_EL_run_TCL_code_(self, in_code, in_environment):
  my_tcl = self.__TCL.Tcl();
  my_tcl.after(self.__execution_timeout * 1000, \
    self.__timeout_termination_ )
  my_out = None
  for my_key in in_environment.keys():
    my_str = in_environment[ my_key ].replace('"', '\\"')
    my_tcl.eval('set {} "{}"'.format(my_key, my_str))
  try:
    my_out = my_tcl.eval(in_code)
  except Exception as my_ex:
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, str(my_ex))
  del my_tcl
  return my_out

 # incomplete
 def __irciot_EL_run_Python_code_(self, in_code, in_environment):
  my_dict = {}
  my_MATH = self.irciot_EL_import_(self.CONST.mod_MATH)
  for my_name in self.CONST.lang_filter_PYTHON_maths:
    my_dict[ my_name ] = getattr(my_MATH, my_name)
  for my_name in self.CONST.lang_filter_PYTHON_funcs:
    if my_name not in self.CONST.lang_filter_PYTHON_maths:
      my_dict[ my_name ] = eval(compile(my_name, '<str>', 'eval'))
  for my_key in in_environment.keys():
    my_value = in_environment[ my_key ]
    if isinstance(my_value, str):
      my_dict[ my_key ] = my_value
  with self.python_stdout_() as my_out:
    exec(in_code, { '__builtins__': None }, my_dict)
  del my_MATH
  return my_out.getvalue()
  #
  # End of __irciot_EL_run_Python_code_()

 # incomplete
 def __irciot_EL_run_Ruby_code_(self, in_code, in_environment = {}):

  return None
  #
  # End of __irciot_EL_run_Ruby_code_()

 # incomplete
 def __irciot_EL_run_R_code_(self, in_code, in_environment = {}):
  my_error = None
  with self.python_stdout_() as my_out:
    try:
      self.__R_ROBJ.r(in_code)
    except self.__R_INTF.RRuntimeError as my_ex:
      my_split = str(my_ex).replace("\n", " ").split(':')
      del my_split[0]
      my_error = ""
      for my_idx in range(len(my_split)):
        my_error += " " + my_split[my_idx]
      while "  " in my_error:
        my_error = my_error.replace("  ", " ")
    except Exception as my_ex:
      my_error = self.errors[self.CONST.err_UNKNOWN] \
       + ": {}".format(my_ex)
  if isinstance(my_error, str):
    self.irciot_EL_error_(self.CONST.err_CODE_EXECUTION, \
     my_error.lstrip().rstrip())
    return None
  my_out = my_out.getvalue()
  for my_rep in [ ( '\n\n\n[1]\n ', '\n' ),
   ( '[1]\n ', '' ), ( '[1] ', '' ), ( '\n', '' ) ]:
    my_out = my_out.replace(my_rep[0], my_rep[1])
  return my_out
  #
  # End of __irciot_EL_run_R_code_()

 # incomplete
 def irciot_EL_run_code_(self, in_lang, in_code, in_environment = {}):
  def __timeout_signal_(in_signal, in_frame):
    self.__timeout_termination_()
  if not self.irciot_EL_check_code_(in_lang, in_code):
    return ""
  if not self.irciot_EL_check_environment_(in_lang, in_environment):
    self.irciot_EL_error_(self.CONST.err_BAD_ENVIRONMENT, None)
    return ""
  if CAN_debug_library:
    self.irciot_EL_error_(self.CONST.err_DEVEL, "EL")
  my_out = None
  if self.__os_name == self.CONST.os_windows:
    pass # Need a method to stop the script by timeout in the Windows
  else:
    try:
      signal.signal(signal.SIGALRM, __timeout_signal_)
      signal.alarm(self.__execution_timeout)
    except:
      pass
  try:
    if in_lang == self.CONST.lang_ANSYML:
      my_out = self.__irciot_EL_run_ANSYML_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_BASH:
      my_out = self.__irciot_EL_run_BASH_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_BASIC:
      my_out = self.__irciot_EL_run_BASIC_code_(in_code, in_environment)
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
      my_out = self.__irciot_EL_run_PHP_code_(in_code, in_environment)
    elif in_lang == self.CONST.lang_R:
      my_out = self.__irciot_EL_run_R_code_(in_code, in_environment)
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
  if self.__os_name != self.CONST.os_windows:
    try:
      signal.alarm(0)
    except: pass
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
  elif self.irciot_EL_check_lang_(in_lang):
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
  ''' This method initializes all the necessary components for the
      required Embedded Language, loads the necessary modules,
      allocates memory and starts the necessary child processes
      in: in_lang -- Embedded Language ID of 'str' type
      out: value with type 'bool', True when seccessfuly initialized
  '''
  if in_lang not in self.__allowed_EL:
    return False
  if in_lang == self.CONST.lang_ANSYML:
    self.__ANSTQM = self.irciot_EL_import_(self.CONST.mod_ANSTQM)
    self.__ANSPLY = self.irciot_EL_import_(self.CONST.mod_ANSPLY)
    self.__ANSINV = self.irciot_EL_import_(self.CONST.mod_ANSINV)
    self.__ANSVAR = self.irciot_EL_import_(self.CONST.mod_ANSVAR)
    self.__ANSLDR = self.irciot_EL_import_(self.CONST.mod_ANSLDR)
    self.__ANSCBP = self.irciot_EL_import_(self.CONST.mod_ANSCBP)
    for my_item in [ self.__ANSTQM, self.__ANSPLY, self.__ANSLDR, \
     self.__ANSINV, self.__ANSVAR, self.__ANSCBP ]:
      if my_item == None: return False
    return True
  elif in_lang == self.CONST.lang_BASH:
    self.__BASH_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_BASH_regexps)
    self.__BSHLEX = self.irciot_EL_import_(self.CONST.mod_BSHLEX)
    if self.__BSHLEX == None: return False
    return True
  elif in_lang == self.CONST.lang_BASIC:
    self.__BASIC_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_BASIC_regexps)
    self.__BASTOK = self.irciot_EL_import_(self.CONST.mod_BASTOK)
    self.__BASLEX = self.irciot_EL_import_(self.CONST.mod_BASLEX)
    self.__BASPRG = self.irciot_EL_import_(self.CONST.mod_BASPRG)
    for my_item in [ self.__BASTOK, self.__BASLEX, self.__BASPRG ]:
      if my_item == None: return False
    return True
  elif in_lang == self.CONST.lang_CSP:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_GO:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_JRE:
    self.__JAVA_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_JAVA_regexps)
    self.__JRE = self.irciot_EL_import_(self.CONST.mod_JRE)
    if self.__JRE != None: return True
  elif in_lang == self.CONST.lang_JS:
    self.__JS_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_JS_regexps)
    self.__JS  = self.irciot_EL_import_(self.CONST.mod_JS)
    if self.__JS  != None: return True
  elif in_lang == self.CONST.lang_LUA:
    self.__LUA_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_LUA_regexps)
    self.__LUA = self.irciot_EL_import_(self.CONST.mod_LUA)
    if self.__LUA != None: return True
  elif in_lang == self.CONST.lang_PERL:
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_PHP:
    self.__PHP_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_PHP_regexps)
    self.__PHPLEX = self.irciot_EL_import_(self.CONST.mod_PHPLEX)
    if self.__PHPLEX != None:

      return True
    self.irciot_EL_error_(self.CONST.err_UNSUPPORTED_YET, None)
  elif in_lang == self.CONST.lang_R:
    self.__R_filter_matchers = \
     self.__irciot_EL_matchers_(self.CONST.lang_filter_R_regexps)
    self.__R_ROBJ = self.irciot_EL_import_(self.CONST.mod_R_ROBJ)
    self.__R_INTF = self.irciot_EL_import_(self.CONST.mod_R_INTF)
    if self.__R_ROBJ == None or self.__R_INTF == None:
      return False
    return True
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
  #
  # End of irciot_EL_init_language_()

 def irciot_EL_finish_language_(self, in_lang):
  ''' This method terminates the processes necessary for the
      given Embedded Language to work and frees memory
      in: in_lang -- Embedded Language ID of 'str' type
      out: value with type 'bool', True when successfuly finished
  '''
  if not self.irciot_EL_check_lang_(in_lang):
    return False
  try:
    if in_lang == self.CONST.lang_ANSYML:
      del self.__ANSVAR
      del self.__ANSINV
      del self.__ANSTQM
      del self.__ANSPLY
      del self.__ANSLDR
      del self.__ANSCBP
      self.__ansible_vault_password \
       = self.wipe_string_(self.__ansible_vault_password)
      self.__ansible_vault_password = None
    elif in_lang == self.CONST.lang_BASH:
      del self.__BSHLEX
      del self.__BASH_filter_matchers
    elif in_lang == self.CONST.lang_BASIC:
      del self.__BASTOK
      del self.__BASLEX
      del self.__BASPRG
      del self.__BASIC_filter_matchers
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
      del self.__PHPLEX
      del self.__PHP_filter_matchers
    elif in_lang == self.CONST.lang_R:
      del self.__R_ROBJ
      del self.__R_INTF
      del self.__R_filter_matchers
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

