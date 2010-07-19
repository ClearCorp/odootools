# -*- encoding: utf-8 -*-
########################################################################
#
#       ccorp-fonts.py
#       
#       Copyright 2010 ClearCorp S.A. <info@clearcorp.co.cr>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
########################################################################

import reportlab
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

reportlab.rl_config.warnOnMissingFontGlyphs = 0
enc = 'UTF-8'

#AppleGaramond
pdfmetrics.registerFont(TTFont('AppleGaramond-Regular', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-Regular.ttf',enc))
pdfmetrics.registerFont(TTFont('AppleGaramond-Bold', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-Bold.ttf',enc))
pdfmetrics.registerFont(TTFont('AppleGaramond-Light', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-Light.ttf',enc))
pdfmetrics.registerFont(TTFont('AppleGaramond-Italic', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-Italic.ttf',enc))
pdfmetrics.registerFont(TTFont('AppleGaramond-BoldItalic', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-BoldItalic.ttf',enc))
pdfmetrics.registerFont(TTFont('AppleGaramond-LightItalic', '/usr/share/fonts/truetype/ClearCorp/AppleGaramond/AppleGaramond-LightItalic.ttf',enc))
addMapping('AppleGaramond', 0, 0, 'AppleGaramond-Regular')
addMapping('AppleGaramond', 1, 0, 'AppleGaramond-Bold')
addMapping('AppleGaramond', 0, 1, 'AppleGaramond-Italic')
addMapping('AppleGaramond', 1, 1, 'AppleGaramond-BoldItalic')
addMapping('AppleGaramond-Light', 0, 0, 'AppleGaramond-Light')
addMapping('AppleGaramond-Light', 0, 1, 'AppleGaramond-LightItalic')
#MyriadPro
pdfmetrics.registerFont(TTFont('MyriadPro-Regular', '/usr/share/fonts/truetype/ClearCorp/MyriadPro/MyriadPro-Regular.ttf',enc))
pdfmetrics.registerFont(TTFont('MyriadPro-Bold', '/usr/share/fonts/truetype/ClearCorp/MyriadPro/MyriadPro-Bold.ttf',enc))
pdfmetrics.registerFont(TTFont('MyriadPro-Italic', '/usr/share/fonts/truetype/ClearCorp/MyriadPro/MyriadPro-Italic.ttf',enc))
pdfmetrics.registerFont(TTFont('MyriadPro-BoldItalic', '/usr/share/fonts/truetype/ClearCorp/MyriadPro/MyriadPro-BoldItalic.ttf',enc))
addMapping('MyriadPro', 0, 0, 'MyriadPro-Regular')
addMapping('MyriadPro', 1, 0, 'MyriadPro-Bold')
addMapping('MyriadPro', 0, 1, 'MyriadPro-Italic')
addMapping('MyriadPro', 1, 1, 'MyriadPro-BoldItalic')
