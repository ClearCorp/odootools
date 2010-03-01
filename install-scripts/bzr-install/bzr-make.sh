#!/bin/bash
# bzr-make.sh

# Description:	This script must be located at /var/www/
#				Its function is to prepare a tar archive with the latest
#				version of bzr-setup and all needed files in it.

mkdir bzr-temp
bzr checkout --lightweight /bzr/libbash-ccorp/trunk bzr-temp

mkdir bzr-install

mkdir bzr-install/main-lib
cp bzr-temp/main-lib/checkRoot.sh bzr-install/checkRoot.sh
cp bzr-temp/main-lib/checkRoot.sh bzr-install/getDist.sh
cp bzr-temp/main-lib/checkRoot.sh bzr-install/setSources.sh
cp bzr-temp/main-lib/checkRoot.sh bzr-install/addKey.sh

mkdir bzr-install/install-scripts
mkdir bzr-install/install-scripts/bzr-install
cp bzr-temp/install-scripts/bzr-install/bzr-setup.sh bzr-install/install-scripts/bzr-install/bzr-setup.sh

cat > bzr-temp/install.sh << EOF
#!/bin/bash
#install.sh

cd install-scripts/bzr-install
./bzr-setup.sh
EOF

tar cvzf bzr-install.tar.gz bzr-install
rm -r bzr-install
rm -r bzr-temp
