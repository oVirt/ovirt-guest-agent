
AC_PREREQ([2.63])

AC_INIT([ovirt-guest-agent],
	[1.0.8],
	[http://bugzilla.redhat.com])

AM_INIT_AUTOMAKE([1.9 no-dist-gzip dist-bzip2 -Wall])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_CONFIG_HEADER(config.h)
AC_CONFIG_MACRO_DIR([m4])
DEFINE_FHS
AC_PROG_CC
AC_PROG_CXX
AM_PROG_AR
AC_PROG_LIBTOOL
AC_PROG_INSTALL
AC_PROG_MKDIR_P
AC_PROG_LN_S
AM_PATH_PYTHON

AC_ARG_WITH(sso,
            AS_HELP_STRING([--with-sso],
                           [If single sign on modules should be built, default=yes]),
            sso=${withval}, sso=yes)
AC_SUBST(sso)
AC_ARG_WITH(dist,
            AS_HELP_STRING([--with-dist],
                           [This configuration is for distribution creation only, default=no]),
            dist=${withval}, dist=no)
AC_SUBST(dist)
AC_ARG_WITH(gdm,
            AS_HELP_STRING([--with-gdm],
                           [Whether or not to build the single sign on GDM extension, default=yes]),
            gdm=${withval}, gdm=$sso)
AC_SUBST(gdm)
AC_ARG_WITH(kdm,
            AS_HELP_STRING([--with-kdm],
                           [Whether or not to build the single sign on KDM extension, default=yes]),
            kdm=${withval}, kdm=$sso)
AC_SUBST(kdm)
AM_CONDITIONAL(BUILD_GDM_MODULE, [test -n "$gdm" -a "x$gdm" != xno ])
AM_CONDITIONAL(BUILD_KDM_MODULE, [test -n "$kdm" -a "x$kdm" != xno ])
AM_CONDITIONAL(BUILD_SSO_MODULES, [test -n "$sso" -a "x$sso" != xno ])

dnl ---------------------------------------------------------------------------
dnl needed for systemd detection
dnl ---------------------------------------------------------------------------
PKG_PROG_PKG_CONFIG

if test "x$sso" == "xyes"; then
    if test "x$dist" == "xno"; then
        AC_CHECK_HEADERS([arpa/inet.h fcntl.h stdlib.h string.h sys/socket.h unistd.h])

        AC_CHECK_FUNCS([memset select socket strchr strerror strndup])

        AC_CHECK_LIB([pam], [pam_get_user])
    fi
fi

AC_TYPE_SIZE_T
AC_TYPE_PID_T

dnl ---------------------------------------------------------------------------
dnl Check if we have systemd so we know if we have to install the systemd
dnl service
dnl ---------------------------------------------------------------------------
AC_ARG_WITH([systemdsystemunitdir],
    AS_HELP_STRING([--with-systemdsystemunitdir=DIR],[Directory for systemd service files]),
    [], [with_systemdsystemunitdir=$($PKG_CONFIG --variable=systemdsystemunitdir systemd)])
if test "x$with_systemdsystemunitdir" != xno; then
    AC_SUBST([systemdsystemunitdir], [$with_systemdsystemunitdir])
fi
AM_CONDITIONAL(HAVE_SYSTEMD, [test -n "$with_systemdsystemunitdir" -a "x$with_systemdsystemunitdir" != xno ])

dnl ---------------------------------------------------------------------------
dnl Checking for pep8
dnl ---------------------------------------------------------------------------
AC_PATH_PROG([PEP8], [pep8])
if test "x$PEP8" = "x"; then
  AC_MSG_WARN([python-pep8 not found])
fi


dnl ---------------------------------------------------------------------------
dnl - Dependencies
dnl ---------------------------------------------------------------------------

if test "x$sso" == "xyes"; then
    if test "x$gdm" == "xyes"; then
        DBUS_GLIB_REQUIRED_VERSION=0.74
        GDM_SIMPLE_GREETER_REQUIRED_VERSION=3.2.1.1
        GLIB_REQUIRED_VERSION=2.22.0
        GTK_REQUIRED_VERSION=2.18.0

        # A hack to ignore gdm-devel package when building gdm-2.
        if ! test -z "$with_gdm_src_dir"; then
           GDM_SIMPLE_GREETER_REQUIRED=""
        else
           GDM_SIMPLE_GREETER_REQUIRED="gdmsimplegreeter >= $GDM_SIMPLE_GREETER_REQUIRED_VERSION"
        fi

        if test "x$dist" == "xno"; then
        PKG_CHECK_MODULES(GDM_PLUGIN,
                dbus-glib-1 >= $DBUS_GLIB_REQUIRED_VERSION
                $GDM_SIMPLE_GREETER_REQUIRED
                gobject-2.0 >= $GLIB_REQUIRED_VERSION
                gtk+-2.0 >= $GTK_REQUIRED_VERSION
        )
        fi
        GDM_PLUGIN_LIBS="$GDM_PLUGIN_LIBS -lm"
        AC_SUBST(GDM_PLUGIN_CFLAGS)
        AC_SUBST(GDM_PLUGIN_LIBS)
    fi

    if test "x$kdm" == "xyes"; then
        QT_REQUIRED_VERSION=4.6.2

        if test "x$dist" == "xno"; then
        PKG_CHECK_MODULES(KDM_PLUGIN,
                QtCore >= $QT_REQUIRED_VERSION
                QtDBus >= $QT_REQUIRED_VERSION
                QtGui >= $QT_REQUIRED_VERSION
        )
        fi
        KDM_PLUGIN_LIBS="$KDM_PLUGIN_LIBS -lm"
        AC_SUBST(KDM_PLUGIN_CFLAGS)
        AC_SUBST(KDM_PLUGIN_LIBS)
    fi
    dnl ---------------------------------------------------------------------------
    dnl - Directory for GDM source package files
    dnl ---------------------------------------------------------------------------
    if test "x$gdm" == "xyes"; then
        AC_ARG_WITH(gdm-src-dir,
                    AS_HELP_STRING([--with-gdm-src-dir=<dir>],
                                   [GDM package source files directory]))

        if ! test -z "$with_gdm_src_dir"; then
           GDM_SRC_DIR=$with_gdm_src_dir
        else
           GDM_SRC_DIR=
        fi

        AC_SUBST(GDM_SRC_DIR)
    fi
fi # if sso enabled

dnl ---------------------------------------------------------------------------
dnl - Directory for PAM configuration files
dnl ---------------------------------------------------------------------------

withval=""
AC_ARG_WITH(pam-prefix,
            AS_HELP_STRING([--with-pam-prefix=<prefix>],
                           [specify where pam files go]),
            [if test x$withval != x; then
               AC_MSG_RESULT("PAM files will be installed in prefix ${withval}.")
             fi])

if test x$withval != x; then
	PAM_PREFIX="$withval"
else
	PAM_PREFIX='${sysconfdir}'
fi
AC_SUBST(PAM_PREFIX)

dnl ---------------------------------------------------------------------------
dnl - Directory for PAM modules files
dnl ---------------------------------------------------------------------------
AC_ARG_ENABLE(securedir,
	AS_HELP_STRING([--enable-securedir=DIR],[path to location of PAMs @<:@default=$libarchdir/security@:>@]),
	SECUREDIR=$enableval, SECUREDIR=$libarchdir/security)
AC_SUBST(SECUREDIR)

dnl ---------------------------------------------------------------------------
dnl - Directory for GDM simple greeter plugins
dnl ---------------------------------------------------------------------------
AC_ARG_WITH(simple-greeter-plugins-dir,
            AS_HELP_STRING([--with-simple-greeter-plugins-dir=<dir>],
                           [simple greeter plugins directory]))

if ! test -z "$with_simple_greeter_plugins_dir"; then
   GDM_SIMPLE_GREETER_PLUGINS_DIR=$with_simple_greeter_plugins_dir
else
   GDM_SIMPLE_GREETER_PLUGINS_DIR=$libarchdir/gdm/simple-greeter/extensions
fi
AC_SUBST(GDM_SIMPLE_GREETER_PLUGINS_DIR)

dnl ---------------------------------------------------------------------------
dnl - Directory for KDM greeter plugins
dnl ---------------------------------------------------------------------------

KDM_GREETER_PLUGINS_DIR=$libarchdir/kde4
AC_SUBST(KDM_GREETER_PLUGINS_DIR)

dnl ---------------------------------------------------------------------------
dnl - Configuration file stuff
dnl ---------------------------------------------------------------------------
AC_ARG_WITH(extensionsdatadir,
            AS_HELP_STRING([--with-extensions-datadir],
                           [directory where extensions store data, default=DATADIR/gdm/simple-greeter/extensions]),
            extensionsdatadir=${withval}, extensionsdatadir=${datadir}/gdm/simple-greeter/extensions)
AC_SUBST(extensionsdatadir)

AC_CONFIG_FILES([
    Makefile
    GinaSSO/Makefile
    ovirt-guest-agent/Makefile
    ovirt-guest-agent/ovirt-guest-agent
    ovirt-guest-agent/consoleapps/Makefile
    ovirt-guest-agent/pam/Makefile
    tests/Makefile
    windows-credprov/Makefile
])
if test "x$sso" == "xyes"; then
    AC_CONFIG_FILES([
        pam-ovirt-cred/Makefile
    ])
    if test "x$gdm" == "xyes"; then
        AC_CONFIG_FILES([
            gdm-plugin/Makefile
            gdm-plugin/icons/Makefile
            gdm-plugin/icons/16x16/Makefile
            gdm-plugin/icons/48x48/Makefile
            gdm2-plugin/Makefile
        ])
    fi
    if test "x$kdm" == "xyes"; then
        AC_CONFIG_FILES([
            kdm-plugin/Makefile
        ])
    fi
fi

AC_OUTPUT
