#!/bin/bash

CONF_FILE=$1

# Backup config file
cp -a $CONF_FILE $CONF_FILE.bak~


# Change addons in file
odoo_list=$(for repo in `ls -1d /opt/odoo/8.0/odoo/*`; do echo -n "             "; echo $repo","; done; echo "\n")
clearcorp_list=$(for repo in `ls -1d /opt/odoo/8.0/clearcorp/*`; do echo -n "           "; echo $repo","; done; echo "\n")
custom_list=$(for repo in `ls -1d /opt/odoo/8.0/custom/*`; do echo -n "         "; echo $repo","; done; echo "\n")
oca_list=$(for repo in `ls -1d /opt/odoo/8.0/oca/*`; do echo -n "               "; echo $repo","; done; echo "\n")
other_list=$(for repo in `ls -1d /opt/odoo/8.0/other/*`; do echo -n "           "; echo $repo","; done; echo "\n")

addons="# Addons start - DO NOT REMOVE THIS LINE\n\
$odoo_list\
$clearcorp_list\
$custom_list\
$oca_list\
$other_list\
                # Addons end - DO NOT REMOVE THIS LINE"

perl -i -0pe 's|# Addons start.*# Addons end - DO NOT REMOVE THIS LINE|'"$addons"'|s' $CONF_FILE

exit 0

