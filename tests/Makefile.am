AM_TESTS_ENVIRONMENT=PYTHONPATH=$(PYTHONPATH):$(top_srcdir)/ovirt-guest-agent:$(top_srcdir)/tests; export PYTHONPATH;
LOG_COMPILER=$(PYTHON)
AM_LOG_FLAGS=$(top_srcdir)/tests/testrunner.py

TESTS=\
    encoding_test.py \
    guest_agent_test.py \
    $(NULL)

EXTRA_DIST=                 \
    encoding_test.py        \
    guest_agent_test.py     \
    message_validator.py    \
    test_port.py            \
    testrunner.py           \
    unittest.bat            \
    $(NULL)

