#!/bin/bash

# Check the script is running as root.
function checkRoot(){
	if [[ $EUID -ne 0 ]]; then
		# Exits with return = 1 if user is not root.
		echo "This script must be executed as root."
		exit 1
	fi
}
