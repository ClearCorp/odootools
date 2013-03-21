#!/bin/bash

touch /var/log/openerp/cp-db.log
chown openerp:openerp /var/log/openerp/cp-db.log

export OPENERP_CCORP_DIR="/usr/local/share/oerptools/bash"

cd / #Avoids the could not change directory to "/root" error

echo date >> /var/log/openerp/cp-db.log
/usr/local/sbin/ccorp-openerp-cp-db [DB1] [DB2] [TEST_SERVER] >> /var/log/openerp/cp-db.log
