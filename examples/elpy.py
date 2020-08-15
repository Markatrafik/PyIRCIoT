#!/usr/bin/python3

import sys

try: # need for development
  from languages import PyLayerIRCIoT_EL_
except:
  from PyIRCIoT.languages import PyLayerIRCIoT_EL_

def main():

  if len(sys.argv) == 1:
    my_python_code = "for i in range(3): print('hello ',end='')"
  else:
    my_python_code = sys.argv[1]
  print('Python code: "{}"'.format(my_python_code))

  ii_lang = PyLayerIRCIoT_EL_()
  # ii_lang.irciot_set_locale_("de")
  ii_python = ii_lang.CONST.lang_PYTHON

  if not ii_lang.irciot_EL_admit_language_(ii_python):
    print('Cannot admit language: Python')
    return

  if not ii_lang.irciot_EL_init_language_(ii_python):
    print('Cannot init language: Python')
    return

  my_out = ii_lang.irciot_EL_run_code_(ii_python, my_python_code)

  print("Python out: '{}'".format(my_out))

  sys.exit()

if __name__ == '__main__':
  main()

