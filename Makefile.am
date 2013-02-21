ACLOCAL_AMFLAGS=-I m4

SUBDIRS =                \
    ovirt-guest-agent

if BUILD_SSO_MODULES
SUBDIRS += \
	pam-ovirt-cred       \
    gdm-plugin           \
    gdm2-plugin          \
    kdm-plugin
endif

CLEANFILES = \
    *~

MAINTAINERCLEANFILES = \
    config.h.in \
    Makefile.in

# When fixing a file to conform with pep8 add it to the WL here so it will be
# checkd from now on
PEP8_WHITELIST = \
	ovirt-guest-agent/CredServer.py \
	ovirt-guest-agent/GuestAgentLinux2.py \
	ovirt-guest-agent/GuestAgentWin32.py \
	ovirt-guest-agent/LockActiveSession.py \
	ovirt-guest-agent/OVirtAgentLogic.py \
	ovirt-guest-agent/OVirtGuestService.py \
	ovirt-guest-agent/VirtIoChannel.py \
	ovirt-guest-agent/WinFile.py \
	ovirt-guest-agent/ovirt-guest-agent.py \
	ovirt-guest-agent/version.py

PEP8_BLACKLIST = ovirt-guest-agent/setup.py

check-local:
	$(PEP8) --exclude="$(PEP8_BLACKLIST)" --filename '*.py,*.py.in' \
		$(PEP8_WHITELIST)
	@if test -f .gitignore; then \
	  for i in `git ls-files \*.in`; do \
	    if ! grep -q -x $${i%%.in} .gitignore; then \
	      echo "Missing $${i%%.in} in .gitignore"; exit 1; fi; \
	  done; \
	fi;


install-exec-hook:
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/lock/subsys/ovirt-guest-agent
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/log/ovirt-guest-agent
