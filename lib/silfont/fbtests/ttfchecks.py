#!/usr/bin/env python
'Support for use of Fontbakery ttf checks'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from fontbakery.checkrunner import Section, PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.callable import condition, check, disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.constants import PriorityLevel, NameID, PlatformID, WindowsEncodingID

# Set imports of standard ttf tests

profile_imports = ("fontbakery.profiles.universal", "fontbakery.profiles.googlefonts", "fontbakery.profiles.adobefonts" )

# Create list of checks that we won't run (by default)

remove_check_list = [
        "com.adobe.fonts/check/cff_call_depth",
        "com.adobe.fonts/check/cff2_call_depth",
        "com.google.fonts/check/all_glyphs_have_codepoints",
        "com.google.fonts/check/points_out_of_bounds",
        "com.google.fonts/check/contour_count",
        "com.google.fonts/check/description/broken_links",
        "com.google.fonts/check/description/git_url",
        "com.google.fonts/check/description/max_length",
        "com.google.fonts/check/description/min_length",
        "com.google.fonts/check/description/valid_html",
        "com.google.fonts/check/description/variable_font",
        "com.google.fonts/check/epar",
        "com.google.fonts/check/family/has_license",
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/fontdata_namecheck",
        "com.google.fonts/check/fontv",
        "com.google.fonts/check/gasp",
        "com.google.fonts/check/has_ttfautohint_params",
        "com.google.fonts/check/kerning_for_non_ligated_sequences",
        "com.google.fonts/check/ligature_carets",
        "com.google.fonts/check/metadata/parses",
        "com.google.fonts/check/metadata/unknown_designer",
        "com.google.fonts/check/metadata/designer_values",
        "com.google.fonts/check/metadata/broken_links",
        "com.google.fonts/check/metadata/undeclared_fonts",
        "com.google.fonts/check/metadata/listed_on_gfonts",
        "com.google.fonts/check/metadata/unique_full_name_values",
        "com.google.fonts/check/metadata/unique_weight_style_pairs",
        "com.google.fonts/check/metadata/license",
        "com.google.fonts/check/metadata/menu_and_latin",
        "com.google.fonts/check/metadata/subsets_order",
        "com.google.fonts/check/metadata/copyright",
        "com.google.fonts/check/metadata/familyname",
        "com.google.fonts/check/metadata/has_regular",
        "com.google.fonts/check/metadata/regular_is_400",
        "com.google.fonts/check/metadata/nameid/family_name",
        "com.google.fonts/check/metadata/nameid/post_script_name",
        "com.google.fonts/check/metadata/nameid/full_name",
        "com.google.fonts/check/metadata/nameid/font_name",
        "com.google.fonts/check/metadata/match_fullname_postscript",
        "com.google.fonts/check/metadata/match_filename_postscript",
        "com.google.fonts/check/metadata/valid_name_values",
        "com.google.fonts/check/metadata/valid_full_name_values",
        "com.google.fonts/check/metadata/valid_filename_values",
        "com.google.fonts/check/metadata/valid_post_script_name_values",
        "com.google.fonts/check/metadata/valid_copyright",
        "com.google.fonts/check/metadata/reserved_font_name",
        "com.google.fonts/check/metadata/copyright_max_length",
        "com.google.fonts/check/metadata/filenames",
        "com.google.fonts/check/metadata/italic_style",
        "com.google.fonts/check/metadata/normal_style",
        "com.google.fonts/check/metadata/nameid/family_and_full_names",
        "com.google.fonts/check/metadata/fontname_not_camel_cased",
        "com.google.fonts/check/metadata/match_name_familyname",
        "com.google.fonts/check/metadata/canonical_weight_value",
        "com.google.fonts/check/metadata/os2_weightclass",
        "com.google.fonts/check/metadata/match_weight_postscript",
        "com.google.fonts/check/metadata/canonical_style_names",
        "com.google.fonts/check/metadata/nameid/copyright",
        "com.google.fonts/check/name/license",
        "com.google.fonts/check/name/license_url",
        "com.google.fonts/check/name/line_breaks",
        "com.google.fonts/check/name/rfn",
        "com.google.fonts/check/old_ttfautohint",
        "com.google.fonts/check/repo/dirname_matches_nameid_1",
        "com.google.fonts/check/unitsperem_strict",
        "com.adobe.fonts/check/name/postscript_vs_cff",
        "com.google.fonts/check/family/win_ascent_and_descent",
        "com.google.fonts/check/ftxvalidator",
        "com.google.fonts/check/name/trailing_spaces",
        "com.google.fonts/check/glyph_coverage",
# Tests after this added by DR to reduce noise whilst testing
        "com.google.fonts/check/smart_dropout",
        "com.google.fonts/check/fontbakery_version",
        "com.google.fonts/check/dsig",
        "com.google.fonts/check/dsig:adobefonts",
        "com.google.fonts/check/monospace",
        "com.google.fonts/check/monospace_max_advancewidth",
        "com.google.fonts/check/ftxvalidator_is_available"
]

# Add our own checks. If variants of standard tests use same name structure

@check(
  id = 'org.sil.software/check/name/version_format'
)
def org_sil_software_version_format(ttFont):
  """Version format is correct in 'name' table?
  Based on com_google_fonts_check_name_version_format but checks for exactly 3 digits after decimal point"""
  from fontbakery.utils import get_name_entry_strings
  import re
  def is_valid_version_format(value):
    return re.match(r'Version [1-9][0-9]*\.\d{3}$', value)

  failed = False
  version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    yield FAIL,\
          Message("no-version-string",
                  f"Font lacks a NameID.VERSION_STRING"
                  f" (nameID={NameID.VERSION_STRING}) entry")
  for ventry in version_entries:
    if not is_valid_version_format(ventry):
      failed = True
      yield FAIL,\
            Message("bad-version-strings",
                    f'The NameID.VERSION_STRING'
                    f' (nameID={NameID.VERSION_STRING}) value must'
                    f' follow the pattern "Version X.nnn" with X.nnn'
                    f' greater than or equal to 1.000.'
                    f' Current version string is: "{ventry}"')
  if not failed:
    yield PASS, "Version format in NAME table entries is correct."

def make_profile(remove_check_list):
    profile = profile_factory(default_section=Section("SIL Fonts"))
    profile.auto_register(globals())
    for checkid in remove_check_list:
        if checkid in profile._check_registry:
            profile.remove_check(checkid)
        else:
            print("********************* " + checkid + " not in profile **************************")
    return profile

profile = make_profile(remove_check_list)

