#!/usr/bin/python
#
# Copyright 2010 Red Hat, Inc. and/or its affiliates.
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  See the files README and
# LICENSE_GPL_v2 which accompany this distribution.
#

import logging, logging.config, os, time, signal, sys
import ConfigParser
from GuestAgentLinux2 import LinuxVdsAgent

AGENT_CONFIG = '/etc/ovirt-guest-agent.conf'
AGENT_PIDFILE = '/run/ovirt-guest-agent.pid'

class OVirtAgentDaemon:

    def __init__(self):
        logging.config.fileConfig(AGENT_CONFIG)

    def run(self):
        logging.info("Starting oVirt guest agent")

        config = ConfigParser.ConfigParser()
        config.read(AGENT_CONFIG)

        self.agent = LinuxVdsAgent(config)

        with file(AGENT_PIDFILE, "w") as f:
            f.write("%s\n" % (os.getpid()))
        os.chmod(AGENT_PIDFILE, 0x1b4) # rw-rw-r-- (664)
        
        self.register_signal_handler()
        self.agent.run()

        logging.info("oVirt guest agent is down.")

    def register_signal_handler(self):
        
        def sigterm_handler(signum, frame):
            logging.debug("Handling signal %d" % (signum))
            if signum == signal.SIGTERM:
                logging.info("Stopping oVirt guest agent")
                self.agent.stop()
 
        signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    try:
        try:
            agent = OVirtAgentDaemon()
            agent.run()
        except:
            logging.exception("Unhandled exception in oVirt guest agent!")
            sys.exit(1)
    finally:
        try:
            os.unlink(AGENT_PIDFILE)
        except:
            pass
