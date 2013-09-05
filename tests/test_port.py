#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8


class TestPort(object):
    def __init__(self, vport_name, *args, **kwargs):
        self._vport_name = vport_name

    def write(buffer):
        return len(buffer)

    def read(size):
        return ""


_registered_ports = {}


def get_test_port(vport_name):
    return _registered_ports.get(vport_name, TestPort(vport_name))


def add_test_port(vport_name, port):
    assert(isinstance(port, TestPort))
    _registered_ports[vport_name] = port
