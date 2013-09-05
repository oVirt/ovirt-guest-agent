#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import unittest

from nose import config
from nose import core
from nose import result

from VirtIoChannel import VirtIoStream


class GuestAgentTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

    def assertRaises(self, exceptions, callable, *args, **kwargs):
            passed = False
            try:
                callable(*args, **kwargs)
            except exceptions:
                passed = True
            self.assertTrue(passed)


class GuestAgentTestRunner(core.TextTestRunner):
    def __init__(self, *args, **kwargs):
        core.TextTestRunner.__init__(self, *args, **kwargs)

    def _makeResult(self):
        return result.TextTestResult(self.stream,
                                     self.descriptions,
                                     self.verbosity,
                                     self.config)

    def run(self, test):
        result_ = core.TextTestRunner.run(self, test)
        return result_


def run():
    argv = sys.argv
    stream = sys.stdout
    verbosity = 3
    testdir = os.path.dirname(os.path.abspath(__file__))

    conf = config.Config(stream=stream,
                         env=os.environ,
                         verbosity=verbosity,
                         workingDir=testdir,
                         plugins=core.DefaultPluginManager())

    runner = GuestAgentTestRunner(stream=conf.stream,
                                  verbosity=conf.verbosity,
                                  config=conf)

    sys.exit(not core.run(config=conf, testRunner=runner, argv=argv))


if __name__ == '__main__':
    # We're ensuring VirtIoStream is monkey patched to unit test output mode
    # which requires no VirtIO Channel to be present
    VirtIoStream.is_test = True
    run()
