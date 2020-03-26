#!/usr/bin/env python
'''Example for making project-specific changes to the standard pysilfont set of Font Bakery ttf checks.
It will start with all the checks normally run by pysilfont's ttfchecks profile then modify as described below'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.fbtests.ttfchecks import exclude_list, make_profile, check, PASS, FAIL

#
# exclude_list is a list of all checks that will be removed from the standard list of ttf checks that Font Bakery runs
# This list cans be edited to override the standard exclusions - see examples below
#

  # To reinstate the copyright check (which is normally excluded), uncomment the following line
  #exclude_list.remove("com.google.fonts/check/metadata/copyright")

  # To prevent the hinting_impact check from running, uncomment the following line
  #exclude_list.append("com.google.fonts/check/hinting_impact")

#
#  Create the fontbakery profile
#
profile = make_profile(exclude_list) # Use ...(exclude_list, variable_font=True) to include variable font tests

# Add any project-specific tests (This dummy test should normally be commented out!)

@profile.register_check
@check(
  id = 'org.sil.software/dummy',
  rationale = """
    There is no reason for this test!
    """
)
def org_sil_software_dummy():
  """Dummy test that always fails"""
  if True: yield FAIL, "Oops!"


'''
Run this using

  $ psfrunfbprofile --profile fbttfchecks.py <ttf file(s) to check> ...

It can also be used with fontbakery directly if you want to use options that psfrunfbprofile does not support

  $ fontbakery check-profile fbttfchecks.py <ttf file(s) to check> ...    
  
See the docs for full details
'''