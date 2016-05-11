flush_caches_scriptdir = $(pkgdatadir)/scripts/hooks/defaults
flush_caches_script_SCRIPTS= \
    flush-caches             \
    $(NULL)

EXTRA_DIST=                       \
    flush-caches                  \
    55-flush-caches.consolehelper \
    55-flush-caches.sudo          \
    $(NULL)

flushcachesinvocatordir = $(pkgdatadir)/scripts/hooks/defaults
if INSTALL_SUDO_SCRIPTS
FLUSH_CACHES_INVOCATOR=55-flush-caches.sudo
else
if INSTALL_USERMODE_SCRIPTS
FLUSH_CACHES_INVOCATOR=55-flush-caches.consolehelper
endif
endif

flushcachesinvocator_SCRIPTS= \
    $(FLUSH_CACHES_INVOCATOR) \
    $(NULL)

install-exec-hook:
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/defaults
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/before_migration
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/after_migration
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/before_hibernation
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/after_hibernation
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/before_migration
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/after_migration
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/before_hibernation
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/after_hibernation
	$(LN_S) -f $(pkgdatadir)/scripts/hooks/defaults/55-flush-caches $(DESTDIR)/$(pkgdatadir)/scripts/hooks/before_migration/55_flush-caches
	$(LN_S) -f $(pkgdatadir)/scripts/hooks/defaults/55-flush-caches $(DESTDIR)/$(pkgdatadir)/scripts/hooks/before_hibernation/55_flush-caches
	$(LN_S) -f $(pkgdatadir)/scripts/hooks/before_migration/55_flush-caches $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/before_migration/55_flush-caches
	$(LN_S) -f $(pkgdatadir)/scripts/hooks/before_hibernation/55_flush-caches $(DESTDIR)/$(sysconfdir)/ovirt-guest-agent/hooks.d/before_hibernation/55_flush-caches
	$(LN_S) -f $(pkgdatadir)/scripts/hooks/defaults/$(FLUSH_CACHES_INVOCATOR) $(DESTDIR)/$(pkgdatadir)/scripts/hooks/defaults/55-flush-caches
