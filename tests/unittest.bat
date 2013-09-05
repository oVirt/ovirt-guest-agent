@echo off
REM Run unittests for Windows

set PYTHONPATH=%PYTHONPATH%;../ovirt-guest-agent;.;
python testrunner.py guest_agent_test.py encoding_test.py
