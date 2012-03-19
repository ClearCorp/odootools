#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE=~/Development/openerp
fi

OPENERP_REPO_BASE=$(readlink -m $OPENERP_REPO_BASE)

#WARNING: do not activate push unless you know exactly what you are doing.
if [[ $OPENERP_REPO_PUSH != 1 ]]; then
    OPENERP_REPO_PUSH=0
fi

function bzr_pull {
    echo ""
	cd $1
	echo "+++ bzr pull $1"
    echo "$(pwd)/$1"
	bzr pull
	cd ..
}

function bzr_push {
    if [ $OPENERP_REPO_PUSH ]; then
        echo ""
        cd $1
        echo "+++ bzr pull $1"
        echo "$(pwd)/$1"
        bzr pull
        echo "+++ bzr push $1"
        echo "$(pwd)/$1"
        bzr push
        cd ..
    fi
}

function update_oerp_project {
    # $1: Project name
    # $2: Type (original, ccorp)
    # $3,4,5,...: Original branches
    echo ""
    echo ""
    echo "Project: $1"
    echo "--------------------------------------------------------------"
    echo ""
    
    REPO_DIR=$OPENERP_REPO_BASE/$1
    
    echo "Check $2 repository $REPO_DIR"
    if [ ! -d $REPO_DIR ]; then
        echo "repository doesn't exists, skipping"
        echo "$REPO_DIR"
        return 1
    fi
    echo ""
    
    echo "Main branches update"
    echo ""
    args=("$@")
    start=2
    let "stop=$#-1"
    for i in `seq $start $stop`; do
        branch=${args[$i]}
        
        echo "Check branch $REPO_DIR/main/$branch"
        if [ ! -d $REPO_DIR/main/$branch ]; then
            echo "branch doesn't exists, skipping"
            echo "$REPO_DIR/main/$branch"
            echo ""
        else
            echo "Branch pull: $REPO_DIR/main/$branch"
            
            echo "cd $REPO_DIR/main/$branch"
            cd $REPO_DIR/main/$branch
            echo "bzr pull"
            bzr pull
            echo ""
        fi
        
        if [[ $2 =~ ^ccorp$ ]]; then
            echo "Check branch $REPO_DIR/main/${branch}-ccorp"
            if [ ! -d $REPO_DIR/main/${branch}-ccorp ]; then
                echo "branch doesn't exists, skipping"
                echo "$REPO_DIR/main/${branch}-ccorp"
                echo ""
            else
                echo "Branch pull: $REPO_DIR/main/${branch}-ccorp"
                
                echo "cd $REPO_DIR/main/${branch}-ccorp"
                cd $REPO_DIR/main/${branch}-ccorp
                echo "bzr pull"
                bzr pull
                echo ""
                
                if [ $OPENERP_REPO_PUSH ]; then
                    echo "Branch push: $REPO_DIR/main/${branch}-ccorp"
                    
                    echo "cd $REPO_DIR/main/${branch}-ccorp"
                    cd $REPO_DIR/main/${branch}-ccorp
                    echo "bzr push"
                    bzr push
                    echo ""
                fi
            fi
        fi
        
        echo ""
    done
    
    echo ""
    echo ""
}

update_oerp_project original    openobject-server       5.0 6.0 6.1 trunk
update_oerp_project original    openobject-addons       5.0 6.0 6.1 trunk extra-5.0 extra-6.0 extra-trunk
update_oerp_project original    openobject-client       5.0 6.0 6.1 trunk
update_oerp_project original    openobject-client-web   5.0 6.0 trunk
update_oerp_project original    openerp-web             6.1 trunk
update_oerp_project original    openobject-doc          5.0 6.0 6.1

update_oerp_project ccorp       openerp-ccorp-addons    5.0 6.0 6.1 trunk
update_oerp_project ccorp       openerp-costa rica      6.0 6.1 trunk
update_oerp_project ccorp       openerp-ccorp-scripts   stable trunk
