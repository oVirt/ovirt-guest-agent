
EXTRA_DIST =                         \
    ovirt-hibernate-wrapper.sh       \
    ovirt-locksession-wrapper.sh     \
    ovirt-shutdown-wrapper.sh        \
    ovirt-sudo-wrapper.sh            \
    $(NULL)

CLEANFILES = \
    *~

if INSTALL_SUDO_SCRIPTS
sudoscriptsdir = $(pkgdatadir)
sudoscripts_SCRIPTS=                \
    ovirt-sudo-wrapper.sh           \
    ovirt-hibernate-wrapper.sh      \
    ovirt-shutdown-wrapper.sh       \
    ovirt-locksession-wrapper.sh    \
    $(NULL)

install-exec-hook:
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
endif

if INSTALL_USERMODE_SCRIPTS
install-exec-hook:
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
endif
