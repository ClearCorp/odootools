#!/bin/bash
# bzr-make.sh

# Description:	This script must be located at /var/www/
#				Its function is to prepare a tar archive with the latest
#				version of bzr-setup and all needed files in it.

libbash_ccorp_path="/usr/local/share/libbash-ccorp"

bzr update $libbash_ccorp_path

rm bzr-install.tar.gz

mkdir -p bzr-install/main-lib
cp $libbash_ccorp_path/main-lib/checkRoot.sh bzr-install/main-lib/checkRoot.sh
cp $libbash_ccorp_path/main-lib/checkRoot.sh bzr-install/main-lib/getDist.sh
cp $libbash_ccorp_path/main-lib/checkRoot.sh bzr-install/main-lib/setSources.sh
cp $libbash_ccorp_path/main-lib/checkRoot.sh bzr-install/main-lib/addKey.sh

mkdir -p bzr-install/install-scripts/bzr-install
cp $libbash_ccorp_path/install-scripts/bzr-install/bzr-setup.sh bzr-install/install-scripts/bzr-install/bzr-setup.sh

cat > bzr-install/install.sh << EOF
#!/bin/bash
#install.sh

cd install-scripts/bzr-install
./bzr-setup.sh
EOF

tar cvzf bzr-install.tar.gz bzr-install
rm -r bzr-install
