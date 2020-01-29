#!/usr/bin/env python
'Example for running fontbakery ttf tests'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.fbtests.ttfchecks import remove_check_list, make_profile, check, PASS, FAIL

# Overrides for standard exclusions

remove_check_list.remove("com.google.fonts/check/dsig") # reinstage running fo dsig check

remove_check_list.append("com.google.fonts/check/hinting_impact") # don't run hinting_impact check

## Need to add details of how to create new tests

# Create the fontbakery profile
profile = make_profile(remove_check_list)

'''
Run this using 
    $ fontbakery check-profile fbchecks.py <ttf file(s) to check> --html <name of file for html results>
eg
    $ fontbakery check-profile fbchecks.py results/*.ttf --html results/Andika-Mtihani-fontbakery-ttfcheck-report.html
'''
