#!/bin/sh

cp /usr/share/libtool/config/ltmain.sh  .

for f in config.guess config.sub depcomp missing install-sh
do
	cp /usr/share/automake-1.11/$f .
done

aclocal
autoconf
autoheader
automake 

