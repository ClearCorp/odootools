#!/bin/bash
# bzr-make.sh

# Description:	This script must be located at /var/www/
#				Its function is to prepare a tar archive with the latest
#				version of bzr-setup and all needed files in it.

ccorp-bzr-update
ccorp-bzr-update

#Gets the dir source
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
DIR=$(readlink -m $DIR/../..)

rm -r bin
mkdir bin

mkdir -p bin/main-lib
cp $DIR/main-lib/checkRoot.sh bin/main-lib/checkRoot.sh
cp $DIR/main-lib/getDist.sh bin/main-lib/getDist.sh
cp $DIR/main-lib/setSources.sh bin/main-lib/setSources.sh

mkdir -p bin/install-scripts/bzr-install
cp $DIR/install-scripts/bzr-install/bzr-setup.sh bin/install-scripts/bzr-install/bzr-setup.sh
cp $DIR/install-scripts/bzr-install/bzr-update.sh bin/install-scripts/bzr-install/bzr-update.sh

cp $DIR/install-scripts/bzr-install/setup.sh bin/setup.sh
chmod +x bin/setup.sh

cp -a bin openerp-ccorp-scripts
tar cvzf openerp-ccorp-scripts.tgz openerp-ccorp-scripts
rm -r openerp-ccorp-scripts
