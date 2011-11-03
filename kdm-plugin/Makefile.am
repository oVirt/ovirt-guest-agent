
PAM_SERVICE_NAME = kdm-rhevcred

dist_noinst_DATA =	    	    \
    src/CMakeLists.txt          \
    src/kgreet_rhevcred.h       \
    src/kgreet_rhevcred.cpp     \
    src/RhevCred.h              \
    src/RhevCred.cpp

kgreet_rhevcreddir = $(KDM_GREETER_PLUGINS_DIR)
kgreet_rhevcred_DATA = kgreet_rhevcred.so

kgreet_rhevcred.so:
	cmake -DCMAKE_INSTALL_PREFIX=/usr src/CMakeLists.txt
	make -C src
	(	TMPDIR=`mktemp -d`; \
		DESTDIR=$$TMPDIR make -C src install; \
		install -s $$TMPDIR/$(KDM_GREETER_PLUGINS_DIR)/kgreet_rhevcred.so .; \
		rm -rf $$TMPDIR )

$(PAM_SERVICE_NAME): $(PAM_SERVICE_NAME).pam
	cp $(PAM_SERVICE_NAME).pam $(PAM_SERVICE_NAME)

pamdir = $(PAM_PREFIX)/pam.d
pam_DATA = $(PAM_SERVICE_NAME)

EXTRA_DIST = $(PAM_SERVICE_NAME).pam

CLEANFILES =            \
    *~                  \
    kgreet_rhevcred.so  \
    $(PAM_SERVICE_NAME)
