ACLOCAL_AMFLAGS=-I m4

SUBDIRS =                \
    ovirt-guest-agent    \
    GinaSSO              \
    tests                \
    windows-credprov     \
    $(NULL)

if BUILD_SSO_MODULES
SUBDIRS +=               \
    pam-ovirt-cred
endif

if BUILD_GDM_MODULE
SUBDIRS +=               \
    gdm-plugin           \
    gdm2-plugin
endif

if BUILD_KDM_MODULE
SUBDIRS +=               \
    kdm-plugin
endif

DIST_SUBDIRS=$(SUBDIRS)

CLEANFILES = \
    *~

MAINTAINERCLEANFILES = \
    config.h.in \
    Makefile.in

EXTRA_DIST=                     \
    AUTHORS                     \
    README_Fedora.txt           \
    ovirt-guest-agent.spec      \
    ovirt-guest-agent.rhel6.spec\
    m4/fhs.m4                   \
    debian                      \
    $(NULL)

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
    ovirt-guest-agent/version.py \
    tests/*.py

PEP8_BLACKLIST = ovirt-guest-agent/setup.py

check-local:
	$(PEP8) --exclude="$(PEP8_BLACKLIST)" --filename '*.py,*.py.in' \
		$(PEP8_WHITELIST)
	@if test -f .gitignore; then \
		for i in `git ls-files \*.in`; do \
			if ! grep -q -x $${i%%.in} .gitignore; then \
				echo "Missing $${i%%.in} in .gitignore"; exit 1; \
			fi; \
		done; \
	fi;


install-exec-hook:
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/log/ovirt-guest-agent
