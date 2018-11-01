#!/bin/sh

set -e

dnf update -y

dnf install -y dbus-x11 dconf meson python3-pytest python3-pytest-benchmark

# We can't use Tracker from Fedora repos right now as we need features that are
# not yet in any stable release. Once Tracker 2.2 is released we can go back to
# installing frm DNF.
dnf install -y 'dnf-command(builddep)' dbus-devel gcc git libseccomp-devel libvorbis-devel redhat-rpm-config
dnf builddep -y tracker
git clone https://gitlab.gnome.org/GNOME/tracker-miners.git
mkdir tracker-miners/subprojects && cd tracker-miners/subprojects && git clone https://gitlab.gnome.org/GNOME/tracker.git
mkdir tracker-miners/build && cd tracker-miners/build; meson .. -Dprefix=/usr -Ddocs=false -Dminer_rss=false -Dtracker_core=subproject -Dfunctional_tests=false -Dtracker:functional_tests=false -Dtracker:docs=false && ninja && ninja install
glib-compile-schemas /usr/share/glib-2.0/schemas
# This will be auto-removed if we don't mark it installed.
dnf mark install NetworkManager-libnm

# Needed to build Python packages containing C code.
dnf install -y python3-devel

pip3 install click pyxdg yoyo-migrations
pip3 install mutagen
pip3 install jinja2 lightfm musicbrainzngs spotipy
dnf install -y gstreamer1-plugins-good

# lightfm requires libgomp, this prevents it being removed when we uninstall GCC
dnf mark install libgomp

# jinja2 requires python3-markupsafe, this prevents it being removed during cleanup.
dnf mark install python3-markupsafe

# dbus-launch warns if there's no /etc/machine-idwarns if there's no /etc/machine-id..
systemd-machine-id-setup
