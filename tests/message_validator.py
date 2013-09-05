#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import test_port
import json
import logging


class TestPortWriteBuffer(test_port.TestPort):
    def __init__(self, vport_name, *args, **kwargs):
        test_port.TestPort.__init__(self, vport_name, *args, **kwargs)
        self._buffer = ''

    def write(self, buffer):
        self._buffer = self._buffer + buffer
        return len(buffer)

    def read(self, size):
        return ''

    def clear(self):
        self._buffer = ''


def _ensure_messages(*messages):
    def wrapped(f):
        def fun(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            names = []
            parsed = self._get_messages()
            assert(len(parsed) == len(messages))
            for m in parsed:
                assert('__name__' in m)
                names.append(m['__name__'])
                self._check(m)
            for m in messages:
                assert(m in names)
            return result
        return fun
    return wrapped


def _name_only(n):
    def wrapped(o):
        assert(len(o) == 1)
        assert(o['__name__'] == n)
    return wrapped


def assert_string_param(o, n):
    assert(n in o)
    assert(isinstance(o[n], basestring))


def assert_integral_param(o, n):
    assert(n in o)
    integral = isinstance(o[n], (int, long))
    if not integral and isinstance(o[n], basestring):
        var = long(o[n])
        integral = True
    assert(integral)


def _name_and_one_str_param(msg_name, param_name):
    def wrapped(o):
        assert(o['__name__'] == msg_name)
        assert_string_param(o, param_name)
    return wrapped


def assert_is_string_list(o):
    assert(isinstance(o, list))
    for s in o:
        assert(isinstance(s, basestring))


def _name_and_one_string_list_param(msg_name, param_name):
    def wrapped(o):
        assert(o['__name__'] == msg_name)
        assert(param_name in o)
        assert_is_string_list(o[param_name])
    return wrapped


def validate_network_interfaces(msg):
    assert(msg['__name__'] == 'network-interfaces')
    assert('interfaces' in msg)
    assert(isinstance(msg['interfaces'], list))
    for obj in msg['interfaces']:
        assert_string_param(obj, 'hw')
        assert_string_param(obj, 'name')
        assert('inet' in obj)
        assert_is_string_list(obj['inet'])
        assert('inet6' in obj)
        assert_is_string_list(obj['inet6'])


def validate_disks_usage(msg):
    for disk in msg['disks']:
        assert_string_param(disk, 'fs')
        assert_string_param(disk, 'path')
        assert('total' in disk)
        assert_integral_param(disk, 'total')
        assert('used' in disk)
        assert_integral_param(disk, 'used')


def validate_memory_stats(msg):
    assert('memory' in msg)
    mem = msg['memory']
    assert_integral_param(mem, 'majflt')
    assert_integral_param(mem, 'mem_free')
    assert_integral_param(mem, 'mem_total')
    assert_integral_param(mem, 'mem_unused')
    assert_integral_param(mem, 'pageflt')
    assert_integral_param(mem, 'swap_in')
    assert_integral_param(mem, 'swap_out')


_MSG_VALIDATORS = {
    'active-user': _name_and_one_str_param('active-user', 'name'),
    'applications': _name_and_one_string_list_param('applications',
                                                    'applications'),
    'disks-usage': validate_disks_usage,
    'fqdn': _name_and_one_str_param('fqdn', 'fqdn'),
    'host-name': _name_and_one_str_param('host-name', 'name'),
    'memory-stats': validate_memory_stats,
    'network-interfaces': validate_network_interfaces,
    'os-version': _name_and_one_str_param('os-version', 'version'),
    'session-lock': _name_only('session-lock'),
    'session-logoff': _name_only('session-logoff'),
    'session-logon': _name_only('session-logon'),
    'session-shutdown': _name_only('session-shutdown'),
    'session-startup': _name_only('session-startup'),
    'session-unlock': _name_only('session-unlock'),
}


def _check_fun(msg):
    logging.debug("Message: %s", str(msg))
    assert(msg['__name__'] in _MSG_VALIDATORS)
    _MSG_VALIDATORS[msg['__name__']](msg)


class MessageValidator(object):
    def __init__(self, vport_name):
        self._port = TestPortWriteBuffer(vport_name)

    def port(self):
        return self._port

    def _get_messages(self):
        result = []
        for line in self._port._buffer.split('\n'):
            line = line.strip()
            if line:
                result.append(json.loads(line))
        return result

    def _check(self, msg):
        _check_fun(msg)

    @_ensure_messages('host-name', 'os-version', 'network-interfaces')
    def verifySendInfo(self, agent):
        agent.sendInfo()

    @_ensure_messages('applications')
    def verifySendAppList(self, agent):
        agent.sendAppList()

    @_ensure_messages('disks-usage')
    def verifySendDisksUsages(self, agent):
        agent.sendDisksUsages()

    @_ensure_messages('memory-stats')
    def verifySendMemoryStats(self, agent):
        agent.sendMemoryStats()

    @_ensure_messages('active-user')
    def verifySendUserInfo(self, agent):
        agent.sendUserInfo()

    @_ensure_messages('fqdn')
    def verifySendFQDN(self, agent):
        agent.sendFQDN()

    @_ensure_messages('active-user', 'session-logon')
    def verifySessionLogon(self, agent):
        agent.sessionLogon()

    @_ensure_messages('active-user', 'session-logoff')
    def verifySessionLogoff(self, agent):
        agent.sessionLogoff()

    @_ensure_messages('session-lock')
    def verifySessionLock(self, agent):
        agent.sessionLock()

    @_ensure_messages('session-unlock')
    def verifySessionUnlock(self, agent):
        agent.sessionUnlock()

    @_ensure_messages('session-startup')
    def verifySessionStartup(self, agent):
        agent.sessionStartup()

    @_ensure_messages('session-shutdown')
    def verifySessionShutdown(self, agent):
        agent.sessionShutdown()
