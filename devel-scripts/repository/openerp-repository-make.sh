#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE=~/Development/openerp
fi

OPENERP_REPO_BASE=$(readlink -m $OPENERP_REPO_BASE)

function branch_project {
    # $1: Project name
    # $2: Type (original, ccorp)
    # $3,4,5,...: Original branches
    echo ""
    echo ""
    echo "Project: $1"
    echo "--------------------------------------------------------------"
    echo ""
    
    REPO_DIR=$OPENERP_REPO_BASE/$1
    
    echo "Create $2 repository $REPO_DIR"
    if [ -d $REPO_DIR ]; then
        echo "repository already exists, delete before running the script to recreate"
        echo "$REPO_DIR"
    else
        echo "bzr init-repo --no-tree $REPO_DIR"
        bzr init-repo --no-tree $REPO_DIR
    fi
    echo ""
    
    echo "Subdirectories creation"
    if [ -d $REPO_DIR/main ]; then
        echo "main already exists, delete before running the script to recreate"
        echo "$REPO_DIR/main"
    else
        echo "mkdir $REPO_DIR/main"
        mkdir $REPO_DIR/main
    fi
    if [ -d $REPO_DIR/features ]; then
        echo "features already exists, delete before running the script to recreate"
        echo "$REPO_DIR/features"
    else
        echo "mkdir $REPO_DIR/features"
        mkdir $REPO_DIR/features
    fi
    echo ""
    
    echo "Main branches creation"
    echo ""
    args=("$@")
    start=2
    let "stop=$#-1"
    for i in `seq $start $stop`; do
        branch=${args[$i]}
        LP_OERP="http://bazaar.launchpad.net/$1/$branch"
        LP_CCORP="http://bazaar.launchpad.net/~clearcorp/$1/${branch}-ccorp"
        echo "Branch creation: $1/$branch"
        
        echo "Branch $LP_OERP"
        if [ -d $REPO_DIR/main/$branch/.bzr ]; then
            echo "$REPO_DIR/main/$branch already exists, delete before running the script to recreate"
        else
            echo "bzr branch $LP_OERP $REPO_DIR/main/$branch"
            bzr branch $LP_OERP $REPO_DIR/main/$branch
        fi
        
        if [[ $2 =~ ^ccorp$ ]]; then
            echo "Branch $LP_CCORP"
            if [ -d $REPO_DIR/main/${branch}-ccorp/.bzr ]; then
                echo "$REPO_DIR/main/${branch}-ccorp already exists, delete before running the script to recreate"
            else
                echo "bzr branch $LP_CCORP $REPO_DIR/main/${branch}-ccorp"
                bzr branch $LP_CCORP $REPO_DIR/main/${branch}-ccorp
            fi
        fi

        echo "Updating parent locations"
        echo "parent_location = $LP_OERP" > $REPO_DIR/main/$branch/.bzr/branch/branch.conf
        if [[ $2 =~ ^ccorp$ ]]; then
            echo "parent_location = $LP_OERP" > $REPO_DIR/main/${branch}-ccorp/.bzr/branch/branch.conf
            echo "push_location = $LP_CCORP" >> $REPO_DIR/main/${branch}-ccorp/.bzr/branch/branch.conf
        fi
        
        echo ""
    done
    
    echo ""
    echo ""
}

branch_project  original    openobject-server       5.0 6.0 6.1 trunk
branch_project  original    openobject-addons       5.0 6.0 6.1 trunk extra-5.0 extra-6.0 extra-trunk
branch_project  original    openobject-client       5.0 6.0 6.1 trunk
branch_project  original    openobject-client-web   5.0 6.0 trunk
branch_project  original    openerp-web             6.1 trunk
branch_project  original    openobject-doc          5.0 6.0 6.1

branch_project  ccorp       openerp-ccorp-addons    5.0 6.0 6.1 trunk
branch_project  ccorp       openerp-costa-rica      6.0 6.1 trunk
branch_project  ccorp       openerp-ccorp-scripts   stable trunk
