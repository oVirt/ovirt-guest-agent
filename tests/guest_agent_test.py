#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8


from ConfigParser import ConfigParser
import platform

from message_validator import MessageValidator
from testrunner import GuestAgentTestCase

import test_port


def _linux_setup_test(conf):
    port_name = 'linux-functional-test-port'
    conf.set('general', 'applications_list',
             'kernel ovirt-guest-agent xorg-x11-drv-qxl '
             'linux-image xserver-xorg-video-qxl')
    conf.set('general', 'ignored_fs',
             'rootfs tmpfs autofs cgroup selinuxfs udev mqueue '
             'nfds proc sysfs devtmpfs hugetlbfs rpc_pipefs devpts '
             'securityfs debugfs binfmt_misc fuse.gvfsd-fuse '
             'fuse.gvfs-fuse-daemon fusectl usbfs')
    from GuestAgentLinux2 import LinuxVdsAgent
    return port_name, LinuxVdsAgent


def _win32_setup_test(conf):
    port_name = "windows-functional-test-port"
    from GuestAgentWin32 import WinVdsAgent
    return port_name, WinVdsAgent


class FunctionalTest(GuestAgentTestCase):
    def setUp(self):
        self._config = ConfigParser()
        self._config.add_section('general')
        self._config.add_section('virtio')

        agent_class = None
        if platform.system() in ['Windows', 'Microsoft']:
            self._vport_name, agent_class = _win32_setup_test(self._config)
        else:
            self._vport_name, agent_class = _linux_setup_test(self._config)

        self._validator = MessageValidator(self._vport_name)
        self._vport = self._validator.port()
        test_port.add_test_port(self._vport_name, self._vport)

        self._config.set('general', 'heart_beat_rate', '5')
        self._config.set('general', 'report_user_rate', '10')
        self._config.set('general', 'report_application_rate', '120')
        self._config.set('general', 'report_disk_usage', '300')
        self._config.set('virtio', 'device', self._vport_name)

        self.vdsAgent = agent_class(self._config)

    def testSendInfo(self):
        self._validator.verifySendInfo(self.vdsAgent)

    def testSendAppList(self):
        self._validator.verifySendAppList(self.vdsAgent)

    def testSendDisksUsages(self):
        self._validator.verifySendDisksUsages(self.vdsAgent)

    def testSendMemoryStats(self):
        self._validator.verifySendMemoryStats(self.vdsAgent)

    def testSendFQDN(self):
        self._validator.verifySendFQDN(self.vdsAgent)

    def testSendUserInfo(self):
        self._validator.verifySendUserInfo(self.vdsAgent)

    def testSessionLogon(self):
        self._validator.verifySessionLogon(self.vdsAgent)

    def testSessionLogoff(self):
        self._validator.verifySessionLogon(self.vdsAgent)

    def testSessionLock(self):
        self._validator.verifySessionLock(self.vdsAgent)

    def testSessionUnlock(self):
        self._validator.verifySessionUnlock(self.vdsAgent)

    def testSessionStartup(self):
        self._validator.verifySessionStartup(self.vdsAgent)

    def testSessionShutdown(self):
        self._validator.verifySessionShutdown(self.vdsAgent)
