#! /usr/bin/python2
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from testrunner import GuestAgentTestCase as TestCaseBase
from VirtIoChannel import _filter_object


class EncodingTest(TestCaseBase):

    def testNonUnicodeKeyInput(self):
        non_unicode_key = {'non-unicode-key': u'unicode value'}
        self.assertEquals({u'non-unicode-key': u'unicode value'},
                          _filter_object(non_unicode_key))

    def testNonUnicodeValueInput(self):
        non_unicode_value = {u'unicode-key': 'non-unicode value'}
        self.assertEquals({u'unicode-key': u'non-unicode value'},
                          _filter_object(non_unicode_value))

    def testWindowsFailureOnValidValue(self):
        VALID = u'\u0F65'
        self.assertEquals(VALID, _filter_object(VALID))

    def testNullChar(self):
        non_unicode_value = {u'unicode-key': '\x00'}
        self.assertEquals({u'unicode-key': u'\ufffd'},
                          _filter_object(non_unicode_value))

    def testIllegalUnicodeInput(self):
        ILLEGAL_DATA = {u'foo': u'\x00data\x00test\uffff\ufffe\udc79\ud800'}
        EXPECTED = {u'foo': u'\ufffddata\ufffdtest\ufffd\ufffd\ufffd\ufffd'}
        self.assertEqual(EXPECTED, _filter_object(ILLEGAL_DATA))

    def testIllegalUnicodeCharacters(self):
        INVALID = (u'\u0000', u'\ufffe', u'\uffff', u'\ud800', u'\udc79',
                   u'\U00000000', '\x00', '\x01', '\x02', '\x03', '\x04',
                   '\x05')
        for invchar in INVALID:
            self.assertEqual(u'\ufffd', _filter_object(invchar))

    def testLegalUnicodeCharacters(self):
        LEGAL = (u'\u2122', u'Hello World')
        for legalchar in LEGAL:
            self.assertEqual(legalchar, _filter_object(legalchar))
