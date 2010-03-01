#!/bin/bash
# addKey.sh

# Description:	Adds an apt key with the key id.

function addKey {
	gpg --recv-keys $1
	gpg --armor --export $1 | apt-key add -
}
