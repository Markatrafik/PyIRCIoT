#!/usr/bin/python3

import sys
import os
import unittest
from pprint import pprint
from rfc1459 import PyLayerIRC

# FOR TESTING:

my_command = ""
my_params  = []

my_irc = PyLayerIRC()

# UNITTEST:

class PyLayerIRCTest(unittest.TestCase):

  _testMethodName = ''

  def __init__(self, in_name):
    global _log_mode
    _log_mode = 1
    super(PyLayerIRCTest, self).__init__(in_name)
    #
    # End of PyLayerIRC.__init__()

  def test001_default_(self):
    self.assertEqual(irc_test_default_(), True)

  def test003_unary_isitip_(self):
    self.assertEqual(irc_unary_isitip_(), True)

  def test005_unary_nicks_(self):
    self.assertEqual(irc_unary_nicks_(), True)

  def test006_unary_masks_(self):
    self.assertEqual(irc_unary_masks_(), True)

_log_mode = 0

def to_log_(in_text):
 if _log_mode == 0:
   print(in_text)

# FOR TESTING:

def irc_test_default_():
  to_log_("TEST_IS_OK")
  return True

def irc_unary_isitip_():
  if my_irc.is_ip_address_('::1') \
   and my_irc.is_ipv4_address_("127.0.0.1") \
   and not my_irc.is_ipv4_address_("235.345.63.1") \
   and my_irc.is_ipv6_address_("2a00:1450:4010:c06::8b") \
   and my_irc.is_ipv6_address_("1234:5678:90ab:cde::8b") \
   and my_irc.is_ipv6_address_("ABCD:EFab:cdef:cde::81") \
   and not my_irc.is_ipv6_address_("2a00:1450:4010:c06::8z"):
     to_log_("TEST_IS_OK")
     return True
  return False

def irc_unary_nicks_():
  my_test = True
  for my_idx in range(1000):
    my_irc.irc_random_nick_("Test", True)
    to_log_("%d. PyLayerIRC." % my_idx \
      + "irc_random_nick_('Test', True) -> ")
    to_log_("PyLayerIRC.is_irc_nick_('%s') -> " \
      % my_irc.irc_nick_try)
    if not my_irc.is_irc_nick_(my_irc.irc_nick_try):
      my_test = False
      to_log_("False")
      break;
    to_log_("True")
  if my_test:
    to_log_("TEST_IS_OK")
    return True
  return False

def irc_unary_masks_():
  my_couple_set = [
    ( 'noobot!~noobot@odroid.supertux.com', 'noo*!*noobot@odroid.supertux.com', True ),
    ( '_\\.*3kl3kdf;l2fk 4kfk4f3 f34f!!!@', '\\\\\\!@@#023', False ),
    ( 'aaaa!aaaa@b.com', 'aaaa!aaaa@b.com', True ),
    ( 'super_duper!superuser@invider-inovation.org', '*!*@invider-*.org', True ),
    ( 'aaaa!bbbb@cccc.ddd', '*!*@*', True ), ( 'a!b@c', 'a!b@*', True ),
    ( 'aaaaaaaaaaaaaaaaaaaaaa!x@yyyyyyyyyyyyyyyyyyyyy', '*a*a*a*!x@*y*y*y*', True ),
    ( 'abcdef@super-system.co.uk', 'NICKNAME!abcdef@super-system.co.uk', False )
  ]
  my_ok = True
  for my_couple in my_couple_set:
    ( my_from, my_mask, my_need ) = my_couple
    to_log_("Comparing [ '%s' with '%s' ] must be %s ..." % (my_from, my_mask, my_need))
    my_result = my_irc.irc_check_mask_(my_from, my_mask)
    to_log_("out = '%s'." % my_result)
    if my_result == None:
      my_test = False
    elif my_result:
      my_test = True
    else:
      my_test = False
    if my_test != my_need:
      my_ok = False
      to_log_('Checking stopped ...')
      to_log_('TEST_FAILED')
      break
  if my_ok:
    to_log_('TEST_IS_OK')
    return True
  return False

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

 print ("TEST NAME: '%s'" % my_command)

 if (my_command == 'default'):
   irc_test_default_()

 if (my_command == 'nicks'):
   irc_unary_nicks_()

 if (my_command == 'masks'):
   irc_unary_masks_()

 if (my_command == 'isitip'):
   irc_unary_isitip_()

if __name__ == '__main__':
  if len(sys.argv) == 1:
    unittest.main(verbosity=2)
    sys.exit(0)
  main()
