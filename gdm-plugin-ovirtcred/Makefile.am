
SUBDIRS = icons

PAM_SERVICE_NAME = gdm-rhevcred

extensiondir = $(extensionsdatadir)/rhevcred
extension_DATA = page.ui

AM_CPPFLAGS =                                               \
	-I$(GDM_SRC_DIR)/common                                 \
	-I$(GDM_SRC_DIR)/gui/simple-greeter/libgdmsimplegreeter \
	-DPLUGINDATADIR=\""$(extensiondir)"\"                   \
	-DPAMSERVICENAME=\""$(PAM_SERVICE_NAME)"\"              \
    $(DISABLE_DEPRECATED_CFLAGS)			                \
	$(GDM_PLUGIN_CFLAGS)			                        \
	$(NULL)

plugindir = $(GDM_SIMPLE_GREETER_PLUGINS_DIR)
plugin_LTLIBRARIES = rhevcred.la

rhevcred_la_CFLAGS =    \
	$(GDM_PLUGIN_CFLAGS)    \
	$(NULL)

rhevcred_la_LDFLAGS = -module -avoid-version -export-dynamic
rhevcred_la_LIBADD  = $(GDM_SRC_DIR)/gui/simple-greeter/libgdmsimplegreeter/libgdmsimplegreeter.la
rhevcred_la_SOURCES =					\
			gdm-rhevcred-extension.h	\
			gdm-rhevcred-extension.c	\
			plugin.c

$(PAM_SERVICE_NAME): $(PAM_SERVICE_NAME).pam
	cp $(PAM_SERVICE_NAME).pam $(PAM_SERVICE_NAME)

pamdir = $(PAM_PREFIX)/pam.d
pam_DATA = $(PAM_SERVICE_NAME)

EXTRA_DIST = $(extension_DATA) $(PAM_SERVICE_NAME).pam
CLEANFILES = $(PAM_SERVICE_NAME)

MAINTAINERCLEANFILES =                  \
        *~                              \
        $(PAM_SERVICE_NAME)             \
        Makefile.in
