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
from fontbakery.constants import NameID, PlatformID, WindowsEncodingID
from fontbakery.profiles.googlefonts import METADATA_CHECKS, REPO_CHECKS, DESCRIPTION_CHECKS
from fontbakery.profiles.ufo_sources import UFO_PROFILE_CHECKS
from fontbakery.profiles.universal import DESIGNSPACE_CHECKS

from collections import OrderedDict

# Set imports of standard ttf tests

profile_imports = ("fontbakery.profiles.universal",
                   "fontbakery.profiles.googlefonts",
                   "fontbakery.profiles.adobefonts",
                   "fontbakery.profiles.notofonts",
                   "fontbakery.profiles.fontval")

# Add our own checks. If variants of standard tests use same name structure

@check(
  id = 'org.sil/check/name/version_format',
  rationale = """
        Based on com.google.fonts/check/name/version_format but:
        - Checks for exactly 3 digits after decimal point
        Only give WARN if valid dev version, ie
        - Allows major version to be 0
        - Allows extra info after numbers, eg for beta or dev versions
  """
)
def org_sil_version_format(ttFont):
  "Version format is correct in 'name' table?"

  from fontbakery.utils import get_name_entry_strings
  import re

  failed = False
  warned = False
  version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
  if len(version_entries) == 0:
    failed = True
    yield FAIL,\
          Message("no-version-string",
                  f"Font lacks a NameID.VERSION_STRING"
                  f" (nameID={NameID.VERSION_STRING}) entry")

  for ventry in version_entries:
    if not re.match(r'Version [0-9]+\.\d{3}( .+)*$', ventry):
      failed = True
      yield FAIL,\
            Message("bad-version-strings",
                    f'The NameID.VERSION_STRING'
                    f' (nameID={NameID.VERSION_STRING}) value must'
                    f' follow the pattern "Version X.nnn devstring" with X.nnn'
                    f' greater than or equal to 0.000.'
                    f' Current version string is: "{ventry}"')
    elif not re.match(r'Version [1-9][0-9]*\.\d{3}$', ventry):
        warned = True
        yield WARN, \
              Message("nonproduction-version-strings",
                      f'For production fonts, the NameID.VERSION_STRING'
                      f' (nameID={NameID.VERSION_STRING}) value must'
                      f' follow the pattern "Version X.nnn" with X.nnn'
                      f' greater than or equal to 1.000.'
                      f' Current version string is: "{ventry}"')
  if not failed and not warned:
    yield PASS, "Version format in NAME table entries is correct."

@check(
    id = 'org.sil/check/whitespace_widths'
)
def org_sil_whitespace_widths(ttFont):
    """Checks with widths of space characters in the font against best practice"""
    from fontbakery.utils import get_glyph_name

    allok = True
    space_data = {
        0x0020: ['Space'],
        0x00A0: ['No-break space'],
#        0x2007: ['Figure space'], # Figure space to be handled by a tabular numerals width check
        0x2008: ['Punctuation space'],
        0x2003: ['Em space'],
        0x2002: ['En space'],
        0x2000: ['En quad'],
        0x2001: ['Em quad'],
        0x2004: ['Three-per-em space'],
        0x2005: ['Four-per-em space'],
        0x2006: ['Six-per-em space'],
        0x2009: ['Thin space'],
        0x200A: ['Hair space'],
        0x202F: ['Narrow no-break space'],
        0x002E: ['Full stop'], # Non-space character where the width is needed for comparison
    }
    for sp in space_data:
        spname = get_glyph_name(ttFont, sp)
        if spname is None:
            spwidth = None
        else:
            spwidth = ttFont['hmtx'][spname][0]
        space_data[sp].append(spname)
        space_data[sp].append(spwidth)

    # Other width info needed from the font
    upm = ttFont['head'].unitsPerEm
    fullstopw = space_data[46][2]

    # Widths used for comparisons
    spw = space_data[32][2]
    if spw is None:
        allok = False
        yield WARN, "No space in the font so No-break space (if present) can't be checked"
    emw = space_data[0x2003][2]
    if emw is None:
        allok = False
        yield WARN, f'No em space in the font. Will be assumed to be units per em ({upm}) for other checking'
        emw = upm
    enw = space_data[0x2002][2]
    if enw is None:
        allok = False
        yield WARN, f'No en space in the font. Will be assumed to be 1/2 em space width ({emw/2}) for checking en quad (if present)'
        enw = emw/2

    # Now check all the specific space widths.  Only check if the space exists in the font
    def checkspace(spacechar, minwidth, maxwidth=None):
        sdata = space_data[spacechar]
        if sdata[1]: # Name is set to None if not in font
            # Allow for width(s) not being integer (eg em/6) so test against rounding up or down
            minw = int(minwidth)
            if maxwidth:
                maxw = int(maxwidth)
                if maxwidth > maxw: maxw += 1 # Had been rounded down, so round up
            else:
                maxw = minw if minw == minwidth else minw +1 # Had been rounded down, so allow rounded up as well
            charw = sdata[2]
            if not(minw <= charw <= maxw):
                return (f'Width of {sdata[0]} ({spacechar:#04x}) is {str(charw)}: ', minw, maxw)
        return (None,0,0)

    # No-break space
    (message, minw, maxw) = checkspace(0x00A0, spw)
    if message: allok = False; yield FAIL, message + f"Should match width of space ({spw})"
    # Punctuation space
    (message, minw, maxw) = checkspace(0x2008, fullstopw)
    if message: allok = False; yield FAIL, message + f"Should match width of full stop ({fullstopw})"
    # Em space
    (message, minw, maxw) = checkspace(0x2003, upm)
    if message: allok = False; yield WARN, message + f"Should match units per em ({upm})"
    # En space
    (message, minw, maxw) = checkspace(0x2002, emw/2)
    if message:
        allok = False
        widths = f'{minw}' if minw == maxw else f'{minw} or {maxw}'
        yield WARN, message + f"Should be half the width of em ({widths})"
    # En quad
    (message, minw, maxw) = checkspace(0x2000, enw)
    if message: allok = False; yield WARN, message + f"Should be the same width as en ({enw})"
    # Em quad
    (message, minw, maxw) = checkspace(0x2001, emw)
    if message: allok = False; yield WARN, message + f"Should be the same width as em ({emw})"
    # Three-per-em space
    (message, minw, maxw) = checkspace(0x2004, emw/3)
    if message:
        allok = False
        widths = f'{minw}' if minw == maxw else f'{minw} or {maxw}'
        yield WARN, message + f"Should be 1/3 the width of em ({widths})"
    # Four-per-em space
    (message, minw, maxw) = checkspace(0x2005, emw/4)
    if message:
        allok = False
        widths = f'{minw}' if minw == maxw else f'{minw} or {maxw}'
        yield WARN, message + f"Should be 1/4 the width of em ({widths})",
    # Six-per-em space
    (message, minw, maxw) = checkspace(0x2006, emw/6)
    if message:
        allok = False
        widths = f'{minw}' if minw == maxw else f'{minw} or {maxw}'
        yield WARN, message + f"Should be 1/6 the width of em ({widths})",
    # Thin space
    (message, minw, maxw) = checkspace(0x2009, emw/6, emw/5)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/6 and 1/5 the width of em ({minw} and {maxw})"
    # Hair space
    (message, minw, maxw) = checkspace(0x200A,
                         emw/16, emw/10)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/16 and 1/10 the width of em ({minw} and {maxw})"
    # Narrow no-break space
    (message, minw, maxw) = checkspace(0x202F,
                         emw/6, emw/5)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/6 and 1/5 the width of em ({minw} and {maxw})"

    if allok:
        yield PASS, "Space widths all match expected values"

def make_base_profile():
    profile = profile_factory(default_section=Section("SIL Fonts"))
    profile.auto_register(globals())

    # Exclude groups of checks that check files other than ttfs
    for checkid in DESCRIPTION_CHECKS + DESIGNSPACE_CHECKS + METADATA_CHECKS + REPO_CHECKS + UFO_PROFILE_CHECKS:
        if checkid in profile._check_registry: profile.remove_check(checkid)
    return profile

def make_profile(check_list, variable_font=False):
    profile = make_base_profile()

    # Exclude all the checks we don't want to run
    for checkid in check_list:
        if checkid in profile._check_registry:
            check_item = check_list[checkid]
            exclude = check_item["exclude"] if "exclude" in check_item else False
            if exclude: profile.remove_check(checkid)

    # Exclude further sets of checks to reduce number of skips and so have less clutter in html results
    # (Currently just working with variable font tests, but structured to cover more types of checks later)
    for checkid in sorted(set(profile._check_registry.keys())):
        section = profile._check_registry[checkid]
        check = section.get_check(checkid)
        conditions = getattr(check, "conditions")
        exclude = False

        if variable_font and "not is_variable_font" in conditions: exclude = True
        if not variable_font and "is_variable_font" in conditions: exclude = True

        if exclude: profile.remove_check(checkid)
    if not variable_font: # Remove this check manually since it does not have is_variable_font condition
        profile.remove_check("com.google.fonts/check/STAT_strings")

    return profile

def all_checks_dict(): # An ordered dict of all checks designed for exporting the data
    profile = make_base_profile()
    check_dict=OrderedDict()

    for checkid in sorted(set(profile._check_registry.keys()), key=str.casefold):
        section = profile._check_registry[checkid]
        check = section.get_check(checkid)

        conditions = getattr(check, "conditions")
        conditionstxt=""
        for condition in conditions:
            conditionstxt += condition + "\n"
        conditionstxt = conditionstxt.strip()

        rationale = getattr(check,"rationale")
        rationale = "" if rationale is None else rationale.strip().replace("\n        ", "\n") # Remove extraneous whitespace

        psfaction = psfcheck_list[checkid] if checkid in psfcheck_list else "Not in psfcheck_list"

        item = {"psfaction": psfaction,
                "section": section.name,
                "description": getattr(check, "description"),
                "rationale": rationale,
                "conditions": conditionstxt
                }
        check_dict[checkid] = item

    for checkid in psfcheck_list: # Look for checks no longer in Font Bakery
        if checkid not in check_dict:
            check_dict[checkid] = {"psfaction": psfcheck_list[checkid],
                "section": "Missing",
                "description": "Check not found",
                "rationale": "",
                "conditions": ""
                }

    return check_dict

psfcheck_list = {}
psfcheck_list['com.adobe.fonts/check/cff_call_depth']                             = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/cff_deprecated_operators']                   = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/cff2_call_depth']                            = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/family/bold_italic_unique_for_nameid1']      = {}
psfcheck_list['com.adobe.fonts/check/family/consistent_upm']                      = {}
psfcheck_list['com.adobe.fonts/check/family/max_4_fonts_per_family_name']         = {}
psfcheck_list['com.adobe.fonts/check/find_empty_letters']                         = {}
psfcheck_list['com.adobe.fonts/check/fsselection_matches_macstyle']               = {}
psfcheck_list['com.adobe.fonts/check/name/empty_records']                         = {}
psfcheck_list['com.adobe.fonts/check/name/postscript_name_consistency']           = {}
psfcheck_list['com.adobe.fonts/check/name/postscript_vs_cff']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/aat']                                       = {}
psfcheck_list['com.google.fonts/check/all_glyphs_have_codepoints']                = {'exclude': True}
psfcheck_list['com.google.fonts/check/canonical_filename']                        = {}
psfcheck_list['com.google.fonts/check/cjk_chws_feature']                          = {}
psfcheck_list['com.google.fonts/check/cjk_not_enough_glyphs']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics_regressions']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/cmap/unexpected_subtables']                 = {}
psfcheck_list['com.google.fonts/check/code_pages']                                = {}
psfcheck_list['com.google.fonts/check/contour_count']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/dsig']                                      = {'exclude': True}
# psfcheck_list['com.google.fonts/check/dsig:adobefonts']                           = {'exclude': True} #No longer in FB
psfcheck_list['com.google.fonts/check/epar']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/family/control_chars']                      = {}
psfcheck_list['com.google.fonts/check/family/equal_font_versions']                = {}
#psfcheck_list['com.google.fonts/check/family/equal_glyph_names']                  = {} # Currently disabled by FB
#psfcheck_list['com.google.fonts/check/family/equal_numbers_of_glyphs']            = {}  # Currently disabled by FB
psfcheck_list['com.google.fonts/check/family/equal_unicode_encodings']            = {}
psfcheck_list['com.google.fonts/check/family/has_license']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/family/italics_have_roman_counterparts']    = {}
psfcheck_list['com.google.fonts/check/family/panose_familytype']                  = {}
psfcheck_list['com.google.fonts/check/family/panose_proportion']                  = {}
psfcheck_list['com.google.fonts/check/family/single_directory']                   = {}
psfcheck_list['com.google.fonts/check/family/tnum_horizontal_metrics']            = {}
psfcheck_list['com.google.fonts/check/family/underline_thickness']                = {}
psfcheck_list['com.google.fonts/check/family/vertical_metrics']                   = {}
psfcheck_list['com.google.fonts/check/family/win_ascent_and_descent']             = {'exclude': True}
psfcheck_list['com.google.fonts/check/family_naming_recommendations']             = {}
psfcheck_list['com.google.fonts/check/file_size']                                 = {}
psfcheck_list['com.google.fonts/check/font_copyright']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/font_version']                              = {}
psfcheck_list['com.google.fonts/check/fontbakery_version']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontdata_namecheck']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontv']                                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontvalidator']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/fsselection']                               = {}
psfcheck_list['com.google.fonts/check/fstype']                                    = {}
psfcheck_list['com.google.fonts/check/fvar_name_entries']                         = {}
psfcheck_list['com.google.fonts/check/gasp']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/gdef_mark_chars']                           = {}
psfcheck_list['com.google.fonts/check/gdef_non_mark_chars']                       = {}
psfcheck_list['com.google.fonts/check/gdef_spacing_marks']                        = {}
psfcheck_list['com.google.fonts/check/gf-axisregistry/fvar_axis_defaults']        = {}
psfcheck_list['com.google.fonts/check/glyf_nested_components']                    = {}
psfcheck_list['com.google.fonts/check/glyf_non_transformed_duplicate_components'] = {}
psfcheck_list['com.google.fonts/check/glyf_unused_data']                          = {}
psfcheck_list['com.google.fonts/check/glyph_coverage']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/gpos_kerning_info']                         = {}
psfcheck_list['com.google.fonts/check/has_ttfautohint_params']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/hinting_impact']                            = {}
psfcheck_list['com.google.fonts/check/integer_ppem_if_hinted']                    = {}
psfcheck_list['com.google.fonts/check/italic_angle']                              = {}
psfcheck_list['com.google.fonts/check/kern_table']                                = {}
psfcheck_list['com.google.fonts/check/kerning_for_non_ligated_sequences']         = {'exclude': True}
psfcheck_list['com.google.fonts/check/layout_valid_feature_tags']                 = {}
psfcheck_list['com.google.fonts/check/layout_valid_language_tags']                = \
    {'change_status': {'FAIL': 'WARN', 'reason': 'The "invalid" ones are used by Harfbuzz'}}
psfcheck_list['com.google.fonts/check/layout_valid_script_tags']                  = {}
psfcheck_list['com.google.fonts/check/ligature_carets']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/linegaps']                                  = {}
psfcheck_list['com.google.fonts/check/loca/maxp_num_glyphs']                      = {}
psfcheck_list['com.google.fonts/check/mac_style']                                 = {}
psfcheck_list['com.google.fonts/check/mandatory_avar_table']                      = {}
psfcheck_list['com.google.fonts/check/mandatory_glyphs']                          = {}
psfcheck_list['com.google.fonts/check/maxadvancewidth']                           = {}
psfcheck_list['com.google.fonts/check/meta/script_lang_tags']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/missing_small_caps_glyphs']                 = {}
psfcheck_list['com.google.fonts/check/monospace']                                 = {}
psfcheck_list['com.google.fonts/check/name/ascii_only_entries']                   = {}
psfcheck_list['com.google.fonts/check/name/copyright_length']                     = {}
psfcheck_list['com.google.fonts/check/name/description_max_length']               = {}
psfcheck_list['com.google.fonts/check/name/family_and_style_max_length']          = {}
psfcheck_list['com.google.fonts/check/name/familyname']                           = {}
psfcheck_list['com.google.fonts/check/name/familyname_first_char']                = {}
psfcheck_list['com.google.fonts/check/name/fullfontname']                         = {}
psfcheck_list['com.google.fonts/check/name/license']                              = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/license_url']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/line_breaks']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/mandatory_entries']                    = {}
psfcheck_list['com.google.fonts/check/name/match_familyname_fullfont']            = {}
psfcheck_list['com.google.fonts/check/name/no_copyright_on_description']          = {}
psfcheck_list['com.google.fonts/check/name/postscriptname']                       = {}
psfcheck_list['com.google.fonts/check/name/rfn']                                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/subfamilyname']                        = {}
psfcheck_list['com.google.fonts/check/name/trailing_spaces']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/typographicfamilyname']                = {}
psfcheck_list['com.google.fonts/check/name/typographicsubfamilyname']             = {}
psfcheck_list['com.google.fonts/check/name/unwanted_chars']                       = {}
psfcheck_list['com.google.fonts/check/name/version_format']                       = {'exclude': True}
psfcheck_list['com.google.fonts/check/no_debugging_tables']                       = {}
psfcheck_list['com.google.fonts/check/old_ttfautohint']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/os2/use_typo_metrics']                      = {}
#psfcheck_list['com.google.fonts/check/os2/use_typo_metrics']                      = \  (Left  a copy commented out as an
#    {'change_status': {'FAIL': 'WARN', 'reason': 'Under review'}}                      example of an override!)
psfcheck_list['com.google.fonts/check/os2_metrics_match_hhea']                    = {}
psfcheck_list['com.google.fonts/check/ots']                                       = {}
psfcheck_list['com.google.fonts/check/outline_alignment_miss']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/outline_colinear_vectors']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/outline_jaggy_segments']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/outline_semi_vertical']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/outline_short_segments']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/points_out_of_bounds']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/post_table_version']                        = {}
#psfcheck_list['com.google.fonts/check/production_encoded_glyphs']                 = {} # Currently disabled by FB
psfcheck_list['com.google.fonts/check/production_glyphs_similarity']              = {}
psfcheck_list['com.google.fonts/check/render_own_name']                                       = {}
psfcheck_list['com.google.fonts/check/required_tables']                           = {}
psfcheck_list['com.google.fonts/check/rupee']                                     = {}
psfcheck_list['com.google.fonts/check/shaping/collides']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/forbidden']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/regression']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/smart_dropout']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/STAT/axis_order']                           = {}
psfcheck_list['com.google.fonts/check/STAT/gf-axisregistry']                      = {}
psfcheck_list['com.google.fonts/check/STAT_strings']                              = {}
psfcheck_list['com.google.fonts/check/stylisticset_description']                  = {}
psfcheck_list['com.google.fonts/check/superfamily/list']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/superfamily/vertical_metrics']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/transformed_components']                    = {}
psfcheck_list['com.google.fonts/check/ttx-roundtrip']                             = {}
psfcheck_list['com.google.fonts/check/unicode_range_bits']                        = {}
psfcheck_list['com.google.fonts/check/unique_glyphnames']                         = {}
psfcheck_list['com.google.fonts/check/unitsperem']                                = {}
psfcheck_list['com.google.fonts/check/unitsperem_strict']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/unreachable_glyphs']                        = {}
psfcheck_list['com.google.fonts/check/unwanted_tables']                           = {}
psfcheck_list['com.google.fonts/check/usweightclass']                             = {}
psfcheck_list['com.google.fonts/check/valid_glyphnames']                          = {}
psfcheck_list['com.google.fonts/check/valid_glyphnames:adobefonts']               = {}
psfcheck_list['com.google.fonts/check/varfont_duplicate_instance_names']          = {}
psfcheck_list['com.google.fonts/check/varfont_has_instances']                     = {}
psfcheck_list['com.google.fonts/check/varfont_instance_coordinates']              = {}
psfcheck_list['com.google.fonts/check/varfont_instance_names']                    = {}
psfcheck_list['com.google.fonts/check/varfont_weight_instances']                  = {}
psfcheck_list['com.google.fonts/check/varfont/bold_wght_coord']                   = {}
psfcheck_list['com.google.fonts/check/varfont/consistent_axes']                   = {}
psfcheck_list['com.google.fonts/check/varfont/generate_static']                   = {}
psfcheck_list['com.google.fonts/check/varfont/grade_reflow']                      = {}
psfcheck_list['com.google.fonts/check/varfont/has_HVAR']                          = {}
psfcheck_list['com.google.fonts/check/varfont/regular_ital_coord']                = {}
psfcheck_list['com.google.fonts/check/varfont/regular_opsz_coord']                = {}
psfcheck_list['com.google.fonts/check/varfont/regular_slnt_coord']                = {}
psfcheck_list['com.google.fonts/check/varfont/regular_wdth_coord']                = {}
psfcheck_list['com.google.fonts/check/varfont/regular_wght_coord']                = {}
psfcheck_list['com.google.fonts/check/varfont/slnt_range']                        = {}
psfcheck_list['com.google.fonts/check/varfont/stat_axis_record_for_each_axis']    = {}
psfcheck_list['com.google.fonts/check/varfont/unsupported_axes']                  = {}
psfcheck_list['com.google.fonts/check/varfont/wdth_valid_range']                  = {}
psfcheck_list['com.google.fonts/check/varfont/wght_valid_range']                  = {}
psfcheck_list['com.google.fonts/check/vendor_id']                                 = {}
psfcheck_list['com.google.fonts/check/version_bump']                              = {}
psfcheck_list['com.google.fonts/check/vertical_metrics_regressions']              = {}
psfcheck_list['com.google.fonts/check/vttclean']                                  = {}
psfcheck_list['com.google.fonts/check/whitespace_glyphnames']                     = {}
psfcheck_list['com.google.fonts/check/whitespace_glyphs']                         = {}
psfcheck_list['com.google.fonts/check/whitespace_glyphs:adobefonts']              = {}
psfcheck_list['com.google.fonts/check/whitespace_ink']                            = {}
psfcheck_list['com.google.fonts/check/whitespace_widths']                         = {}
psfcheck_list['com.google.fonts/check/xavgcharwidth']                             = {}
psfcheck_list['org.sil/check/name/version_format']                                = {}
psfcheck_list['org.sil/check/whitespace_widths']                                  = {}

profile = make_profile(check_list=psfcheck_list)
