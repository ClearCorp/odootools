#!/bin/bash

CONF_FILE=$1
VERSION=$2

# Backup config file
cp -a $CONF_FILE $CONF_FILE.bak


# Change addons in file
odoo_list=$(echo "		/opt/odoo/$VERSION/odoo/odoo-private/addons,"; for repo in `ls -1d /opt/odoo/$VERSION/odoo/* | grep -v odoo-private`; do echo -n "            "; echo $repo","; done; echo "\n")
clearcorp_list=$(for repo in `ls -1d /opt/odoo/$VERSION/clearcorp/*`; do echo -n "		"; echo $repo","; done; echo "\n")
custom_list=$(for repo in `ls -1d /opt/odoo/$VERSION/custom/*`; do echo -n "		"; echo $repo","; done; echo "\n")
oca_list=$(for repo in `ls -1d /opt/odoo/$VERSION/oca/*`; do echo -n "		"; echo $repo","; done; echo "\n")
other_list=$(for repo in `ls -1d /opt/odoo/$VERSION/other/*`; do echo -n "		"; echo $repo","; done; echo "\n")

addons="# Addons start - DO NOT REMOVE THIS LINE,\n\
$odoo_list\
$clearcorp_list\
$custom_list\
$oca_list\
$other_list\
		# Addons end - DO NOT REMOVE THIS LINE"

perl -i -0pe 's|# Addons start.*# Addons end - DO NOT REMOVE THIS LINE|'"$addons"'|s' $CONF_FILE

exit 0
