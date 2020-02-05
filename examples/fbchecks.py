#!/usr/bin/env python
'Example for running fontbakery ttf tests'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.fbtests.ttfchecks import remove_check_list, make_profile, check, PASS, FAIL

# remove_check_list is a list of all checks that will be removed from the standard list of check fontbakery runs

# This list cans be edited to override the standard exclusions


# To reinstate a check that is normally excluded, remove it from the exclude list
remove_check_list.remove("com.google.fonts/check/dsig") # The dsig check will now get run

# To prevent a standard check from running, add it to the exclude list

remove_check_list.append("com.google.fonts/check/hinting_impact") # hinting_impact will now not be run

# Create the fontbakery profile
profile = make_profile(remove_check_list)

# Add any project-specific tests.

@profile.register_check
@check(
  id = 'org.sil.software/dummy'
)
def org_sil_software_dummy():
  """Dummy test that always fails"""
  if True: yield FAIL, "Oops!"


'''
Run this using 
    $ fontbakery check-profile fbchecks.py <ttf file(s) to check> --html <name of file for html results>
eg
    $ fontbakery check-profile fbchecks.py results/*.ttf --html results/Andika-Mtihani-fontbakery-ttfcheck-report.html
'''
