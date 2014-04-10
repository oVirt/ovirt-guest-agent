AC_DEFUN([DEFINE_FHS_REDHAT],[
        AC_SUBST([exec_prefix],    ['${prefix}'])
        AC_SUBST([bindir],         ['${exec_prefix}/bin'])
        AC_SUBST([sbindir],        ['${exec_prefix}/sbin'])
        AC_SUBST([libexecdir],     ['${exec_prefix}/libexec'])
        AC_SUBST([datarootdir],    ['${prefix}/share'])
        AC_SUBST([datadir],        ['${datarootdir}'])
        AC_SUBST([sysconfdir],     ['/etc'])
        AC_SUBST([localstatedir],  ['/var'])
        AC_SUBST([sharedstatedir], ['/var/lib'])
        AC_SUBST([includedir],     ['${prefix}/include'])
        AC_SUBST([oldincludedir],  ['/usr/include'])
        AC_SUBST([libdir],         ['${exec_prefix}/lib'])
        AC_SUBST([localedir],      ['${datarootdir}/locale'])
        AC_SUBST([mandir],         ['/usr/share/man'])
        AC_SUBST([infodir],        ['/usr/share/info'])
        AC_SUBST([rundir],         ['${sharedstatedir}/run'])
        AC_SUBST([udevdir],        ['${sysconfdir}/udev'])
])

AC_DEFUN([DEFINE_FHS_SUSE],[
        AC_SUBST([exec_prefix],    ['${prefix}'])
        AC_SUBST([bindir],         ['${exec_prefix}/bin'])
        AC_SUBST([sbindir],        ['${exec_prefix}/sbin'])
        AC_SUBST([libexecdir],     ['${exec_prefix}/libexec'])
        AC_SUBST([datarootdir],    ['${prefix}/share'])
        AC_SUBST([datadir],        ['${datarootdir}'])
        AC_SUBST([sysconfdir],     ['/etc'])
        AC_SUBST([localstatedir],  ['/var'])
        AC_SUBST([sharedstatedir], ['/var/lib'])
        AC_SUBST([includedir],     ['${prefix}/include'])
        AC_SUBST([oldincludedir],  ['/usr/include'])
        AC_SUBST([libdir],         ['${exec_prefix}/lib'])
        AC_SUBST([localedir],      ['${datarootdir}/locale'])
        AC_SUBST([mandir],         ['/usr/share/man'])
        AC_SUBST([infodir],        ['/usr/share/info'])
        AC_SUBST([rundir],         ['${sharedstatedir}/run'])
        AC_SUBST([udevdir],        ['/lib/udev'])
])

AC_DEFUN([DEFINE_FHS_DEBIAN],[
        AC_SUBST([exec_prefix],    ['${prefix}'])
        AC_SUBST([bindir],         ['${exec_prefix}/bin'])
        AC_SUBST([sbindir],        ['${exec_prefix}/sbin'])
        AC_SUBST([libexecdir],     ['${exec_prefix}/libexec'])
        AC_SUBST([datarootdir],    ['${prefix}/share'])
        AC_SUBST([datadir],        ['${datarootdir}'])
        AC_SUBST([sysconfdir],     ['/etc'])
        AC_SUBST([localstatedir],  ['/var'])
        AC_SUBST([sharedstatedir], ['/var/lib'])
        AC_SUBST([includedir],     ['${prefix}/include'])
        AC_SUBST([oldincludedir],  ['/usr/include'])
        AC_SUBST([libdir],         ['${exec_prefix}/lib'])
        AC_SUBST([localedir],      ['${datarootdir}/locale'])
        AC_SUBST([mandir],         ['/usr/share/man'])
        AC_SUBST([infodir],        ['/usr/share/info'])
        AC_SUBST([rundir],         ['${sharedstatedir}/run'])
        AC_SUBST([udevdir],        ['/lib/udev'])
])


AC_DEFUN([DEFINE_FHS],[
    if test -f /etc/redhat-release; then
        DEFINE_FHS_REDHAT
    elif test -f /etc/SuSE-release; then
        DEFINE_FHS_SUSE
    elif test -f /etc/debian_version; then
        DEFINE_FHS_DEBIAN
    fi

    AC_SUBST([pkgdocdir], [m4_ifset([AC_PACKAGE_TARNAME],
                                    ['${docdir}/${PACKAGE_TARNAME}'],
                                     ['${docdir}/${PACKAGE}'])])

    if test "x${udevdir}" == "x"; then
        AC_SUBST([udevdir], ['${sysconfdir}/udev'])
    fi
    AC_SUBST([udevrulesdir], ['${udevdir}/rules.d'])
    AC_SUBST([pkgdatadir], ['${datadir}/${PACKAGE}'])
    AC_SUBST([pkgdaemonpidpath], ['${rundir}/${PACKAGE}.pid'])

    AC_SUBST([lib64dir],       ['${exec_prefix}/lib64'])

    if test -d /usr/lib64; then
        AC_SUBST([libarchdir], ['${lib64dir}'])
    else
        AC_SUBST([libarchdir], ['${libdir}'])
    fi

    if test -d /var/lock/subsys; then
        AC_SUBST([lock_dir],   ['/var/lock/subsys'])
    else
        AC_SUBST([lock_dir],   ['/var/lock'])
    fi
])

AC_DEFUN([PRINT_VARS],[
    echo "prefix:           $prefix"
    echo "exec_prefix:      $exec_prefix"
    echo "bindir:           $bindir"
    echo "sbindir:          $sbindir"
    echo "libexecdir:       $libexecdir"
    echo "datarootdir:      $datarootdir"
    echo "datadir:          $datadir"
    echo "sysconfdir:       $sysconfdir"
    echo "sharedstatedir:   $sharedstatedir"
    echo "localstatedir:    $localstatedir"
    echo "includedir:       $includedir"
    echo "oldincludedir:    $oldincludedir"
    echo "docdir:           $docdir"
    echo "infodir:          $infodir"
    echo "htmldir:          $htmldir"
    echo "dvidir:           $dvidir"
    echo "pdfdir:           $pdfdir"
    echo "psdir:            $psdir"
    echo "libdir:           $libdir"
    echo "lib64dir:         $lib64dir"
    echo "libarchdir:       $libarchdir"
    echo "localedir:        $localedir"
    echo "mandir:           $mandir"
    echo "pkgdocdir:        $pkgdocdir"
    echo "pkgdatadir:       $pkgdatadir"
    echo "pkgdaemonpidpath: $pkgdaemonpidpath"
])

