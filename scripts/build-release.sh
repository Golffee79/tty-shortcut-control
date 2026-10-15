#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
version=${1:-0.2.0}
: "${GNUPGHOME:?Set GNUPGHOME to the private release signing key directory}"
root=$(pwd)
build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT HUP INT TERM
pkg="$build/pkg"
mkdir -p "$pkg/DEBIAN" "$pkg/usr/bin" "$pkg/usr/share/tty-shortcut-control" "$pkg/usr/share/applications" "$pkg/usr/share/icons/hicolor/scalable/apps" "$pkg/usr/share/doc/tty-shortcut-control"
cat > "$pkg/DEBIAN/control" <<CONTROL
Package: tty-shortcut-control
Version: $version
Section: utils
Priority: optional
Architecture: all
Maintainer: Golffee79 <126460491+Golffee79@users.noreply.github.com>
Depends: python3, python3-gi, gir1.2-gtk-3.0, x11-xserver-utils
Homepage: https://github.com/Golffee79/tty-shortcut-control
Description: One-switch Ctrl+Alt+F1 control for X11
 Compact GTK utility with English and Thai labels, automatic saving,
 and a per-user backup of the original F1 mapping. Requires X11.
CONTROL
printf '#!/bin/sh\nexec /usr/bin/python3 /usr/share/tty-shortcut-control/tty-shortcut-control.py "$@"\n' > "$pkg/usr/bin/tty-shortcut-control"
chmod 755 "$pkg/usr/bin/tty-shortcut-control"
install -m 644 tty-shortcut-control.py "$pkg/usr/share/tty-shortcut-control/"
install -m 644 packaging/tty-shortcut-control.desktop "$pkg/usr/share/applications/"
install -m 644 packaging/tty-shortcut-control.svg "$pkg/usr/share/icons/hicolor/scalable/apps/"
install -m 644 README.md "$pkg/usr/share/doc/tty-shortcut-control/"
mkdir -p apt
# Keep old packages downloadable for clients that still have an older index.
dpkg-deb --root-owner-group --build "$pkg" "apt/tty-shortcut-control_${version}_all.deb"
cd apt
dpkg-scanpackages --multiversion . /dev/null > Packages
gzip -n -9 -c Packages > Packages.gz
# Avoid including old metadata/signatures in the next Release file.
rm -f Release InRelease Release.gpg
apt-ftparchive -o APT::FTPArchive::Release::Origin=Golffee79 -o APT::FTPArchive::Release::Label=TTY-Shortcut-Control release . > Release
gpg --batch --yes --export > keyring.gpg
gpg --batch --yes --clearsign --output InRelease Release
gpg --batch --yes --armor --detach-sign --output Release.gpg Release
printf '\nBuilt signed APT repository in %s/apt\n' "$root"
