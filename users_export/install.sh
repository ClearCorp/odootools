#!/bin/bash

# Users export install script

# Make sure only root can run our script
if [[ $EUID -ne 0 ]];
  then
    echo "This script must be run as root" 1>&2
    exit 1
fi

apt-get install -y gcc

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed gcc"
  else
    echo "Unable to install gcc please verify."
    exit 1
fi

apt-get install -y virtualenv python3-virtualenv

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed python3-virtualenv"
  else
    echo "Unable to install python3-virtualenv please verify."
    exit 1
fi

apt-get install -y python3-dev

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed python3-dev"
  else
    echo "Unable to install python3-dev please verify."
    exit 1
fi

apt-get install -y libffi-dev

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed libffi-dev"
  else
    echo "Unable to install libffi-dev please verify."
    exit 1
fi

apt-get install -y libpq-dev

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed libpq-dev"
  else
    echo "Unable to install libpq-dev please verify."
    exit 1
fi

echo "Creating dir users_export in /opt"
mkdir -p /opt/users_export
echo "Copying files to /opt/users_export"
cp -a users_export/ /opt/users_export/
cp -a requirements.txt /opt/users_export/

echo "Creating environment"
cd /opt/users_export
virtualenv --python=/usr/bin/python3 env

echo "Installing requiremets"
/opt/users_export/env/bin/pip install -r /opt/users_export/requirements.txt

echo "Done"
