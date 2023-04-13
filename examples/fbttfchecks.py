#!/usr/bin/env python3
'''Example for making project-specific changes to the standard pysilfont set of Font Bakery ttf checks.
It will start with all the checks normally run by pysilfont's ttfchecks profile then modify as described below'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.fbtests.ttfchecks import psfcheck_list, make_profile, check, PASS, FAIL

#
# General settings
#
psfvariable_font = False  # Set to True for variable fonts, so different checks will be run

#
# psfcheck_list is a dictionary of all standard Fontbakery checks with a dictionary for each check indicating
# pysilfont's standard processing of that check
#
# Specifically:
# - If the dictionary has "exclude" set to True, that check will be excluded from the profile
# - If change_status is set, the status values reported by psfrunfbchecks will be changed based on its values
# - If a change in status is temporary - eg just until something is fixed, use temp_change_status instead
#
# Projects can edit this dictionary to change behaviour from Pysilfont defaults.  See examples below

# To reinstate the copyright check (which is normally excluded):
psfcheck_list["com.google.fonts/check/metadata/copyright"]["exclude"] = False

# To prevent the hinting_impact check from running:
psfcheck_list["com.google.fonts/check/hinting_impact"]["exclude"] = True

# To change a FAIL status for com.google.fonts/check/whitespace_glyphnames to WARN:
psfcheck_list["com.google.fonts/check/whitespace_glyphnames"]["temp_change_status"] = {
    "FAIL": "WARN", "reason": "This font currently uses non-standard names"}

#
#  Create the fontbakery profile
#
profile = make_profile(psfcheck_list, variable_font = psfvariable_font)

# Add any project-specific tests (This dummy test should normally be commented out!)

@profile.register_check
@check(
  id = 'org.sil/dummy',
  rationale = """
    There is no reason for this test!
    """
)
def org_sil_dummy():
  """Dummy test that always fails"""
  if True: yield FAIL, "Oops!"

'''
Run this using

  $ psfrunfbchecks --profile fbttfchecks.py <ttf file(s) to check> ...

It can also be used with fontbakery directly if you want to use options that psfrunfbchecks does not support, however
status changes will not be actioned.

  $ fontbakery check-profile fbttfchecks.py <ttf file(s) to check> ...    
  
'''