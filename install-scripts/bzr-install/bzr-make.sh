#!/bin/bash
# bzr-make.sh

# Description:	This script must be located at /var/www/
#				Its function is to prepare a tar archive with the latest
#				version of bzr-setup and all needed files in it.

bzr update $LIBBASH_CCORP_DIR

cd /var/www
rm bzr-install.tar.gz

mkdir -p bzr-install/main-lib
cp $LIBBASH_CCORP_DIR/main-lib/checkRoot.sh bzr-install/main-lib/checkRoot.sh
cp $LIBBASH_CCORP_DIR/main-lib/getDist.sh bzr-install/main-lib/getDist.sh
cp $LIBBASH_CCORP_DIR/main-lib/setSources.sh bzr-install/main-lib/setSources.sh

mkdir -p bzr-install/install-scripts/bzr-install
cp $LIBBASH_CCORP_DIR/install-scripts/bzr-install/bzr-setup.sh bzr-install/install-scripts/bzr-install/bzr-setup.sh

cat > bzr-install/install.sh << EOF
#!/bin/bash
#install.sh

cd install-scripts/bzr-install
./bzr-setup.sh
EOF

chmod +x bzr-install/install.sh

tar cvzf bzr-install.tar.gz bzr-install
rm -r bzr-install
