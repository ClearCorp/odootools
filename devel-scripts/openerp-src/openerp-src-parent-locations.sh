#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE=~/Development/openerp
fi

OPENERP_REPO_BASE=$(readlink -m $OPENERP_REPO_BASE)

REPO_DIR=$OPENERP_REPO_BASE/openerp-src/src

echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/5.0-ccorp" > $REPO_DIR/5.0/openobject-server/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/6.0-ccorp" > $REPO_DIR/6.0/openobject-server/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/6.1-ccorp" > $REPO_DIR/6.1/openobject-server/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/trunk-ccorp" > $REPO_DIR/trunk/openobject-server/.bzr/branch/branch.conf

echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/5.0-ccorp" > $REPO_DIR/5.0/openobject-addons/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/6.0-ccorp" > $REPO_DIR/6.0/openobject-addons/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/6.1-ccorp" > $REPO_DIR/6.1/openobject-addons/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/trunk-ccorp" > $REPO_DIR/trunk/openobject-addons/.bzr/branch/branch.conf

echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/extra-5.0-ccorp" > $REPO_DIR/5.0/openobject-addons-extra/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/extra-6.0-ccorp" > $REPO_DIR/6.0/openobject-addons-extra/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/extra-trunk-ccorp" > $REPO_DIR/trunk/openobject-addons-extra/.bzr/branch/branch.conf

echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client/5.0-ccorp" > $REPO_DIR/5.0/openobject-client/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client/6.0-ccorp" > $REPO_DIR/6.0/openobject-client/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client/6.1-ccorp" > $REPO_DIR/6.1/openobject-client/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client/trunk-ccorp" > $REPO_DIR/trunk/openobject-client/.bzr/branch/branch.conf

echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client-web/5.0-ccorp" > $REPO_DIR/5.0/openobject-client-web/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-client-web/6.0-ccorp" > $REPO_DIR/6.0/openobject-client-web/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openerp-web/6.1-ccorp" > $REPO_DIR/6.1/openerp-web/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openerp-web/trunk-ccorp" > $REPO_DIR/trunk/openerp-web/.bzr/branch/branch.conf


echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/trunk-ccorp" > $REPO_DIR/openerp/trunk/openobject-server/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openerp-web/trunk-ccorp" > $REPO_DIR/openerp/trunk/openerp-web/.bzr/branch/branch.conf
echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/trunk-ccorp" > $REPO_DIR/openerp/trunk/openobject-addons/.bzr/branch/branch.conf
