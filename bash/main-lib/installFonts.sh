#!/bin/bash
# addKey.sh

# Description:	Installs ClearCorp fonts on the system

function installFonts {
	cp -a $OPENERP_CCORP_DIR/main-lib/Fonts/ClearCorp /usr/share/fonts/truetype/
	fc-cache -f
}
