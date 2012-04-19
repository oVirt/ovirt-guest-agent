
AC_PREREQ([2.63])

AC_INIT([ovirt-guest-agent],
	[1.0.4],
	[http://bugzilla.redhat.com])

AM_INIT_AUTOMAKE([1.9 no-dist-gzip dist-bzip2 -Wall])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_CONFIG_HEADER(config.h)
AC_CONFIG_MACRO_DIR([m4])

AC_PROG_CC
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_PROG_INSTALL

AC_CHECK_HEADERS([arpa/inet.h fcntl.h stdlib.h string.h sys/socket.h unistd.h])
AC_CHECK_HEADERS([security/pam_ext.h security/pam_modules.h])

AC_CHECK_FUNCS([memset select socket strchr strerror strndup])

AC_CHECK_LIB([pam], [pam_get_user])

AC_TYPE_SIZE_T
AC_TYPE_PID_T

dnl ---------------------------------------------------------------------------
dnl - Dependencies
dnl ---------------------------------------------------------------------------

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

PKG_CHECK_MODULES(GDM_PLUGIN,
        dbus-glib-1 >= $DBUS_GLIB_REQUIRED_VERSION
        $GDM_SIMPLE_GREETER_REQUIRED
        gobject-2.0 >= $GLIB_REQUIRED_VERSION
        gtk+-2.0 >= $GTK_REQUIRED_VERSION
)
GDM_PLUGIN_LIBS="$GDM_PLUGIN_LIBS -lm"
AC_SUBST(GDM_PLUGIN_CFLAGS)
AC_SUBST(GDM_PLUGIN_LIBS)

QT_REQUIRED_VERSION=4.6.2

PKG_CHECK_MODULES(KDM_PLUGIN,
        QtCore >= $QT_REQUIRED_VERSION
        QtDBus >= $QT_REQUIRED_VERSION
        QtGui >= $QT_REQUIRED_VERSION
)
KDM_PLUGIN_LIBS="$KDM_PLUGIN_LIBS -lm"
AC_SUBST(KDM_PLUGIN_CFLAGS)
AC_SUBST(KDM_PLUGIN_LIBS)

dnl ---------------------------------------------------------------------------
dnl - Directory for GDM source package files
dnl ---------------------------------------------------------------------------

AC_ARG_WITH(gdm-src-dir,
            AS_HELP_STRING([--with-gdm-src-dir=<dir>],
                           [GDM package source files directory]))

if ! test -z "$with_gdm_src_dir"; then
   GDM_SRC_DIR=$with_gdm_src_dir
else
   GDM_SRC_DIR=
fi

AC_SUBST(GDM_SRC_DIR)

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

if test ${libdir} = '${exec_prefix}/lib'
then
    case "`uname -m`" in
        x86_64)
        libdir="/lib64" ;;
        *)
        libdir="/lib" ;;
    esac
fi

AC_ARG_ENABLE(securedir,
	AS_HELP_STRING([--enable-securedir=DIR],[path to location of PAMs @<:@default=$libdir/security@:>@]),
	SECUREDIR=$enableval, SECUREDIR=$libdir/security)
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
   GDM_SIMPLE_GREETER_PLUGINS_DIR=${libdir}/gdm/simple-greeter/extensions
fi

AC_SUBST(GDM_SIMPLE_GREETER_PLUGINS_DIR)

dnl ---------------------------------------------------------------------------
dnl - Directory for KDM greeter plugins
dnl ---------------------------------------------------------------------------

KDM_GREETER_PLUGINS_DIR=${libdir}/kde4
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
    ovirt-guest-agent/Makefile
    ovirt-guest-agent/consoleapps/Makefile
    ovirt-guest-agent/pam/Makefile
    pam-ovirt-cred/Makefile
    gdm-plugin/Makefile
    gdm-plugin/icons/Makefile
    gdm-plugin/icons/16x16/Makefile
    gdm-plugin/icons/48x48/Makefile
    gdm2-plugin/Makefile
    kdm-plugin/Makefile
])

AC_OUTPUT
