#!/bin/sh

INSTALL_PATH="/usr/share/python"
export DH_VIRTUALENV_INSTALL_ROOT=${INSTALL_PATH}

make-deb --install-path=${INSTALL_PATH}
dpkg-buildpackage -us -uc
