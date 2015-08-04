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

#Build windows agent on fedora only, the rpm will be distro-agnostic
if rpm --eval "%dist" | grep -qFi 'fc'; then
    yum-builddep -y ovirt-guest-agent-windows.spec
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
elif rpm --eval "%dist" | grep -qFi 'el7'; then
    echo "TODO"
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
