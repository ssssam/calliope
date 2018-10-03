#!/bin/sh

set -e

dnf remove -y autoconf automake cracklib-dicts dbus-devel gcc gtk2 gtk-doc libseccomp-devel libvorbis-devel libxml2-devel NetworkManager-libnm-devel python3-devel redhat-rpm-config
dnf clean all

rm -R /root/*
