
EXTRA_DIST =                         \
    ovirt-container-list-wrapper.sh  \
    ovirt-hibernate-wrapper.sh       \
    ovirt-logout-wrapper.sh          \
    ovirt-locksession-wrapper.sh     \
    ovirt-shutdown-wrapper.sh        \
    ovirt-flush-caches-wrapper.sh    \
    ovirt-sudo-wrapper.sh            \
    $(NULL)

CLEANFILES = \
    *~

if INSTALL_SUDO_SCRIPTS
sudoscriptsdir = $(pkgdatadir)
sudoscripts_SCRIPTS=                \
    ovirt-sudo-wrapper.sh           \
    ovirt-container-list-wrapper.sh  \
    ovirt-hibernate-wrapper.sh      \
    ovirt-logout-wrapper.sh         \
    ovirt-shutdown-wrapper.sh       \
    ovirt-locksession-wrapper.sh    \
    ovirt-flush-caches-wrapper.sh   \
    $(NULL)

install-exec-hook:
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-container-list
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-logout
	$(LN_S) -f $(pkgdatadir)/ovirt-sudo-wrapper.sh $(DESTDIR)/$(pkgdatadir)/ovirt-flush-caches
endif

if INSTALL_USERMODE_SCRIPTS
install-exec-hook:
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-container-list
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-logout
	$(LN_S) -f $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-flush-caches
endif
