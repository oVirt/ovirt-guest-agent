SUBDIRS =    \
    wrappers \
    $(NULL)

EXTRA_DIST=                    \
    sudoers.ovirt-guest-agent  \
    $(NULL)

if INSTALL_SUDO_SCRIPTS
install-data-hook:
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/sudoers.d
	$(INSTALL) -m 440 sudoers.ovirt-guest-agent $(DESTDIR)/$(sysconfdir)/sudoers.d/50_ovirt-guest-agent
endif
