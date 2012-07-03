#!/bin/bash

if [[ $OPENERP_REPO_BASE == "" ]]; then
    OPENERP_REPO_BASE=~/Development/openerp
fi

OPENERP_REPO_BASE=$(readlink -m $OPENERP_REPO_BASE)

#WARNING: do not activate push unless you know exactly what you are doing.
if [[ $OPENERP_REPO_PUSH != 1 ]]; then
    OPENERP_REPO_PUSH=0
fi

LOG=""

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
            LOG="${LOG}WARNING: $REPO_DIR/main/$branch"
            LOG="${LOG}\nbranch doesn't exists, skipping\n\n"
        else
            echo "Branch pull: $REPO_DIR/main/$branch"
            
            echo "cd $REPO_DIR/main/$branch"
            cd $REPO_DIR/main/$branch
            echo "bzr pull"
            bzr pull
            if [[ $? == 0 ]]; then
                LOG="${LOG}INFO: $REPO_DIR/main/$branch"
                LOG="${LOG}\nbzr pull OK\n\n"
            else
                LOG="${LOG}ERROR: $REPO_DIR/main/$branch"
                LOG="${LOG}\nbzr pull FAIL\n\n"
            fi
            echo ""
        fi
        
        if [[ $2 =~ ^original$ ]]; then
            echo "Check branch $REPO_DIR/main/${branch}-ccorp"
            if [ ! -d $REPO_DIR/main/${branch}-ccorp ]; then
                echo "branch doesn't exists, skipping"
                echo "$REPO_DIR/main/${branch}-ccorp"
                echo ""
                LOG="${LOG}WARNING: $REPO_DIR/main/$branch-ccorp"
                LOG="${LOG}\nbranch doesn't exists, skipping\n\n"
            else
                echo "Branch pull: $REPO_DIR/main/${branch}-ccorp"
                
                echo "cd $REPO_DIR/main/${branch}-ccorp"
                cd $REPO_DIR/main/${branch}-ccorp
                echo "bzr pull"
                bzr pull
	            if [[ $? == 0 ]]; then
	                LOG="${LOG}INFO: $REPO_DIR/main/$branch-ccorp"
	                LOG="${LOG}\nbzr pull OK\n\n"
	            else
	                LOG="${LOG}ERROR: $REPO_DIR/main/$branch-ccorp"
	                LOG="${LOG}\nbzr pull FAIL\n\n"
	            fi
                echo "bzr pull :push"
                bzr pull :push
	            if [[ $? == 0 ]]; then
	                LOG="${LOG}INFO: $REPO_DIR/main/$branch-ccorp"
	                LOG="${LOG}\nbzr pull OK\n\n"
	            else
	                LOG="${LOG}ERROR: $REPO_DIR/main/$branch-ccorp"
	                LOG="${LOG}\nbzr pull FAIL\n\n"
	            fi
                echo ""
                
                if [ $OPENERP_REPO_PUSH ]; then
                    echo "Branch push: $REPO_DIR/main/${branch}-ccorp"
                    
                    echo "cd $REPO_DIR/main/${branch}-ccorp"
                    cd $REPO_DIR/main/${branch}-ccorp
                    echo "bzr push"
                    bzr push
		            if [[ $? == 0 ]]; then
		                LOG="${LOG}INFO: $REPO_DIR/main/$branch-ccorp"
		                LOG="${LOG}\nbzr push OK\n\n"
		            else
		                LOG="${LOG}ERROR: $REPO_DIR/main/$branch-ccorp"
		                LOG="${LOG}\nbzr push FAIL\n\n"
		            fi
                    echo ""
                fi
            fi
        elif [[ $2 =~ ^ccorp$ ]]; then
            if [ $OPENERP_REPO_PUSH ]; then
                echo "Branch push: $REPO_DIR/main/${branch}"
                
                echo "cd $REPO_DIR/main/${branch}"
                cd $REPO_DIR/main/${branch}
                echo "bzr push"
                bzr push
	            if [[ $? == 0 ]]; then
	                LOG="${LOG}INFO: $REPO_DIR/main/$branch"
	                LOG="${LOG}\nbzr push OK\n\n"
	            else
	                LOG="${LOG}ERROR: $REPO_DIR/main/$branch"
	                LOG="${LOG}\nbzr push FAIL\n\n"
	            fi
                echo ""
            fi
        fi
        
        echo ""
    done
    
    echo ""
    echo ""
}

update_oerp_project openobject-server       original    5.0 6.0 6.1 trunk
update_oerp_project openobject-addons       original    5.0 6.0 6.1 trunk extra-5.0 extra-6.0 extra-trunk
update_oerp_project openobject-client       original    5.0 6.0 6.1 trunk
update_oerp_project openobject-client-web   original    5.0 6.0 trunk
update_oerp_project openerp-web             original    6.1 trunk
update_oerp_project openobject-doc          original    5.0 6.0 6.1

update_oerp_project openerp-ccorp-addons    ccorp   5.0 6.0 6.1 trunk
update_oerp_project openerp-costa-rica      ccorp   6.0 6.1 trunk
update_oerp_project openerp-ccorp-scripts   ccorp   stable trunk

update_oerp_project banking-addons          original    5.0 6.0 6.1 trunk



echo "OpenERP repository update log:"
echo ""
echo -e $LOG
