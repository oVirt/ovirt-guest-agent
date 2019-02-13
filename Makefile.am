ACLOCAL_AMFLAGS=-I m4

SUBDIRS =                \
    configurations       \
    ovirt-guest-agent    \
    GinaSSO              \
    tests                \
    windows-credprov     \
    scripts              \
    hooks                \
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
    ovirt-guest-agent/hooks.py \
    tests/*.py

PEP8_BLACKLIST = ovirt-guest-agent/setup.py

# Only execute the PEP8 checks if it was found
# If pep8 couldn't be located don't execute this
# Switch to pycodestyle revealed lots `bare except` issues.
# Excluding those from test for now.
if HAVE_PEP8
check-local:
	$(PEP8) --exclude="$(PEP8_BLACKLIST)" --filename '*.py,*.py.in' \
		--ignore=E722 $(PEP8_WHITELIST)
	@if test -f .gitignore; then \
		for i in `git ls-files \*.in`; do \
			if ! grep -q -x $${i%%.in} .gitignore; then \
				echo "Missing $${i%%.in} in .gitignore"; exit 1; \
			fi; \
		done; \
	fi;
endif

install-exec-hook:
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/log/ovirt-guest-agent
