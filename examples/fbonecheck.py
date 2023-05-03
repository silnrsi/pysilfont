#!/usr/bin/env python
'''Example profile for use with psfrunfbchecks that will just run one or more specified checks'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2022 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.fbtests.ttfchecks import psfcheck_list, make_profile, check, PASS, FAIL

# Exclude all checks bar those listed
for check in psfcheck_list:
    if check not in ["org.sil/check/whitespace_widths"]:
        psfcheck_list[check] = {'exclude': True}

#  Create the fontbakery profile
profile = make_profile(psfcheck_list, variable_font = False)

