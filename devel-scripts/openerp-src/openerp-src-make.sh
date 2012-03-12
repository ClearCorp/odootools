#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE=~/Development/openerp
fi

OPENERP_REPO_BASE=$(readlink -m $OPENERP_REPO_BASE)

function branch_project {
	# $1: Project name
	# $2: Version
	# $3: Original branch
	# $4: Destination branch
    echo ""
    echo ""
	echo "BRANCH $1 ($4) v$2"
    echo "--------------------------------------------------------------"
    echo ""
	
	ORI_DIR=$OPENERP_REPO_BASE/$1/main/$3
	DES_DIR=$OPENERP_REPO_BASE/openerp-src/src/$2/$4
    
    echo "Checking branch"
    if [ -d $DES_DIR ]; then
        echo "branch already exists, delete before running the script to recreate"
        echo $ORI_DIR
    else
        echo "bzr branch --no-tree $ORI_DIR $DES_DIR"
        bzr branch --no-tree $ORI_DIR $DES_DIR
        
        echo "parent_location = http://bazaar.launchpad.net/~clearcorp/$1/$3" > $DES_DIR/.bzr/branch/branch.conf
    fi
    echo ""
}

function mkrepo {
    
    REPO_DIR=$OPENERP_REPO_BASE/openerp-src/src/openerp
    
    if [ -d $REPO_DIR ]; then
        echo "repository already exists, delete before running the script to recreate"
        echo $REPO_DIR
    else
        echo "bzr init-repo $REPO_DIR"
        bzr init-repo $REPO_DIR
        
        mkdir $REPO_DIR/trunk
        bzr branch $OPENERP_REPO_BASE/openobject-server/main/trunk-ccorp $REPO_DIR/trunk/openobject-server
        echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-server/trunk-ccorp" > $REPO_DIR/trunk/openobject-server/.bzr/branch/branch.conf
        bzr branch $OPENERP_REPO_BASE/openerp-web/main/ccorp-trunk $REPO_DIR/trunk/openerp-web
        echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openerp-web/trunk-ccorp" > $REPO_DIR/trunk/openerp-web/.bzr/branch/branch.conf
        bzr branch $OPENERP_REPO_BASE/openobject-addons/main/ccorp-trunk $REPO_DIR/trunk/openobject-addons
        echo "parent_location = http://bazaar.launchpad.net/~clearcorp/openobject-addons/trunk-ccorp" > $REPO_DIR/trunk/openobject-addons/.bzr/branch/branch.conf
    fi
}

branch_project	openobject-server	5.0		5.0-ccorp	openobject-server
branch_project	openobject-server	6.0		6.0-ccorp	openobject-server
branch_project	openobject-server	6.1		6.1-ccorp	openobject-server
branch_project	openobject-server	trunk	trunk-ccorp	openobject-server

branch_project	openobject-addons	5.0		5.0-ccorp	openobject-addons
branch_project	openobject-addons	6.0		6.0-ccorp	openobject-addons
branch_project	openobject-addons	6.1 	6.1-ccorp	openobject-addons
branch_project	openobject-addons	trunk	trunk-ccorp	openobject-addons

branch_project	openobject-addons	5.0		extra-5.0-ccorp		openobject-addons-extra
branch_project	openobject-addons	6.0		extra-6.0-ccorp		openobject-addons-extra
branch_project	openobject-addons	trunk	extra-trunk-ccorp	openobject-addons-extra

branch_project	openobject-client	5.0		5.0-ccorp	openobject-client
branch_project	openobject-client	6.0		6.0-ccorp	openobject-client
branch_project	openobject-client	6.1		6.1-ccorp	openobject-client
branch_project	openobject-client	trunk	trunk-ccorp	openobject-client

branch_project	openobject-client-web	5.0		5.0-ccorp	openobject-client-web
branch_project	openobject-client-web	6.0		6.0-ccorp	openobject-client-web
branch_project	openerp-web				6.1		6.1-ccorp	openerp-web
branch_project	openerp-web				trunk	trunk-ccorp	openerp-web

mkrepo
