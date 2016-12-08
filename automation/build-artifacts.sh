#!/bin/bash -xe
[[ -d exported-artifacts ]] \
|| mkdir -p exported-artifacts

[[ -d tmp.repos ]] \
|| mkdir -p tmp.repos

SUFFIX=".$(date -u +%Y%m%d%H%M%S).git$(git rev-parse --short HEAD)"

./autogen.sh
./configure \
    --with-dist
make dist

# We build the depdendencies for windows only on latest fedora.
# Do not check %dist but just try to get them. Exit cleanly if missing.
if yum-builddep -y ovirt-guest-agent-windows.spec; then
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        -D "release_suffix ${SUFFIX}" \
        -ba ovirt-guest-agent-windows.spec
fi

if rpm --eval "%dist" | grep -qFi 'el6'; then
    yum-builddep -y ovirt-guest-agent.rhel6.spec
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        -D "release_suffix ${SUFFIX}" \
        -ba ovirt-guest-agent.rhel6.spec
else
    yum-builddep -y ovirt-guest-agent.spec
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        -D "release_suffix ${SUFFIX}" \
        -ba ovirt-guest-agent.spec
fi

mv *.tar.bz2 exported-artifacts
find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} exported-artifacts/ \;
