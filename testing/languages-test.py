#!/usr/bin/python3

import sys
import os
import json
import warnings
import unittest
from pprint import pprint
from languages import PyLayerIRCIoT_EL_

EL = PyLayerIRCIoT_EL_()

# UNITTEST:

class PyLayerIRCIoT_EL_Test(unittest.TestCase):

  _testMethodName = ''

  def __init__(self, in_name):
   global _log_mode
   _log_mode = 1
   EL._silence = True
   super(PyLayerIRCIoT_EL_Test, self).__init__(in_name)
   #
   # End of PyLayerIRCIoT_EL_Test.__init__()

  def test000_default_(self):
    self.assertEqual(EL_test_default_(), True)

  def test001_test_simple_LUA_(self):
    self.assertEqual(EL_test_simple_LUA_(), True)

  def test101_test_simple_Python_(self):
    self.assertEqual(EL_test_simple_Python_(), True)

  def test102_test_simple_JS_(self):
    self.assertEqual(EL_test_simple_JavaScript_(), True)

  def test103_test_simple_R_(self):
    self.assertEqual(EL_test_simple_R_(), True)

  def test121_test_Python_for_range_(self):
    self.assertEqual(EL_test_Python_for_range_(), True)

  def test123_test_Python_cosinus_(self):
    self.assertEqual(EL_test_Python_cosinus_(), True)

  def test152_test_JS_arithmetics_(self):
    self.assertEqual(EL_test_JS_arithmetics_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def EL_test_default_():
  to_log_("TEST_IS_OK")
  return True

def EL_test_(in_code, in_check, in_lang):
  to_log_('{} code: "{}"'.format(in_lang, in_code))
  if not EL.irciot_EL_admit_language_(in_lang):
    to_log_('Cannot admit language: {}'.format(in_lang))
    return False
  if not EL.irciot_EL_init_language_(in_lang):
    to_log_('Cannot init language: {}'.format(in_lang))
    return False
  my_out = EL.irciot_EL_run_code_(in_lang, in_code)
  to_log_("{} out: '{}'".format(in_lang, my_out))
  if my_out.replace('\n', '@') == in_check:
    to_log_('TEST_IS_OK')
    return True
  return False
  # End of EL_test_()

def EL_LUA_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_LUA)

def EL_JS_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_JS)

def EL_R_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_R)

def EL_python_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_PYTHON)

def EL_BASIC_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_BASIC)

def EL_TCL_(in_code, in_check):
  return EL_test_(in_code, in_check, EL.CONST.lang_TCL)

def EL_test_simple_LUA_():
  return EL_LUA_("assert(os.setlocale('C'))", "C")

def EL_test_simple_JavaScript_():
  return EL_JS_("document.write('hello')", "hello")

def EL_test_simple_R_():
  return EL_R_("print(pi)", "3.141593")

def EL_test_simple_TCL_():
  return EL_TCL_("set aaa hello;return $aaa", "hello")

def EL_test_JS_arithmetics_():
  my_script = "var a=12345+54321/333;var b=a-2509;b++;document.write(b*3|0)"
  return EL_JS_(my_script, "30000")

def EL_test_simple_BASIC_():
  return EL_BASIC_("10 PRINT 123", "123@")

def EL_test_simple_Python_():
  return EL_python_("print('hello',end='')", "hello")

def EL_test_Python_for_range_():
  return EL_python_("for i in range(3): print(i); print('a')", "0@a@1@a@2@a@")

def EL_test_Python_cosinus_():
  return EL_python_("s=str(cos(pi*2-pi/3));print(s[0:7],end='')", "0.50000")

my_command = ""
my_params  = []

def main():

 global my_command
 global my_params

 my_params = []
 if (len(sys.argv) > 1):
   my_command = sys.argv[1]
 for my_idx in range(2, 6):
   if len(sys.argv) > my_idx:
     my_params += [ sys.argv[my_idx] ]
 if (my_command == ""):
   my_command = 'default'

 if 'locale' in my_params:
   EL.irciot_set_locale_('ru')

 to_log_("TEST NAME: '{}'".format(my_command))

 if my_command == 'default':
   EL_test_default_()

 if my_command == 'lua':
   EL_test_simple_LUA_()
 if my_command == 'js':
   EL_test_simple_JavaScript_()
 if my_command == 'python':
   EL_test_simple_Python_()
 if my_command == 'basic':
   EL_test_simple_BASIC_()
 if my_command == 'r':
   EL_test_simple_R_()
 if my_command == 'tcl':
   EL_test_simple_TCL_()
 if my_command == 'pyrangefor':
   EL_test_Python_for_range_()
 if my_command == 'pycosinus':
   EL_test_Python_cosinus_()
 if my_command == 'jsarith':
   EL_test_JS_arithmetics_()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()

