#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE="~/Development/openerp"
fi

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
        
        echo "parent_location = lp:~clearcorp/$1/$3" > $DES_DIR/.bzr/branch/branch.conf
    fi
    echo ""
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
