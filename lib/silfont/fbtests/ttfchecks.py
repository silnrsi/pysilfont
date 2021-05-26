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

from collections import OrderedDict

# Set imports of standard ttf tests

profile_imports = ("fontbakery.profiles.universal",
                   "fontbakery.profiles.googlefonts",
                   "fontbakery.profiles.adobefonts",
                   "fontbakery.profiles.notofonts",
                   "fontbakery.profiles.fontval")

# Add our own checks. If variants of standard tests use same name structure

@check(
  id = 'org.sil.software/check/name/version_format',
  rationale = """
        Based on com.google.fonts/check/name/version_format but:
        - Checks for exactly 3 digits after decimal point
        Only give WARN if valid dev version, ie
        - Allows major version to be 0
        - Allows extra info after numbers, eg for beta or dev versions
  """
)
def org_sil_software_version_format(ttFont):
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

def make_profile(check_list, variable_font=False):
    profile = profile_factory(default_section=Section("SIL Fonts"))
    profile.auto_register(globals())

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
    profile = profile_factory(default_section=Section("SIL Fonts"))
    profile.auto_register(globals())
    check_dict=OrderedDict()

    for checkid in sorted(set(profile._check_registry.keys())):
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
psfcheck_list['com.google.fonts/check/STAT/axis_order']                           = {}
psfcheck_list['com.google.fonts/check/STAT/gf-axisregistry']                      = {}
psfcheck_list['com.google.fonts/check/STAT_strings']                              = {}
psfcheck_list['com.google.fonts/check/aat']                                       = {}
psfcheck_list['com.google.fonts/check/all_glyphs_have_codepoints']                = {'exclude': True}
psfcheck_list['com.google.fonts/check/canonical_filename']                        = {}
psfcheck_list['com.google.fonts/check/cjk_not_enough_glyphs']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics_regressions']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/cmap/unexpected_subtables']                 = {}
psfcheck_list['com.google.fonts/check/code_pages']                                = {}
psfcheck_list['com.google.fonts/check/contour_count']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/broken_links']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/eof_linebreak']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/family_update']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/git_url']                       = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/max_length']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/min_length']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/description/valid_html']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/dsig']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/dsig:adobefonts']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/epar']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/family_naming_recommendations']             = {}
psfcheck_list['com.google.fonts/check/family/control_chars']                      = {}
psfcheck_list['com.google.fonts/check/family/equal_font_versions']                = {}
#psfcheck_list['com.google.fonts/check/family/equal_glyph_names']                  = {} # Currently disabled by FB
#psfcheck_list['com.google.fonts/check/family/equal_numbers_of_glyphs']            = {}  # Currently disabled by FB
psfcheck_list['com.google.fonts/check/family/equal_unicode_encodings']            = {}
psfcheck_list['com.google.fonts/check/family/has_license']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/family_naming_recommendations']             = {}
psfcheck_list['com.google.fonts/check/family/panose_familytype']                  = {}
psfcheck_list['com.google.fonts/check/family/panose_proportion']                  = {}
psfcheck_list['com.google.fonts/check/family/single_directory']                   = {}
psfcheck_list['com.google.fonts/check/family/tnum_horizontal_metrics']            = {}
psfcheck_list['com.google.fonts/check/family/underline_thickness']                = {}
psfcheck_list['com.google.fonts/check/family/vertical_metrics']                   = {}
psfcheck_list['com.google.fonts/check/family/win_ascent_and_descent']             = {'exclude': True}
psfcheck_list['com.google.fonts/check/font_copyright']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/font_version']                              = {}
psfcheck_list['com.google.fonts/check/fontbakery_version']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontdata_namecheck']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontv']                                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontvalidator']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/fsselection']                               = {}
psfcheck_list['com.google.fonts/check/fstype']                                    = {}
psfcheck_list['com.google.fonts/check/ftxvalidator']                              = {'exclude': True}
psfcheck_list['com.google.fonts/check/ftxvalidator_is_available']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/fvar_name_entries']                         = {}
psfcheck_list['com.google.fonts/check/gasp']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/gdef_mark_chars']                           = {}
psfcheck_list['com.google.fonts/check/gdef_non_mark_chars']                       = {}
psfcheck_list['com.google.fonts/check/gdef_spacing_marks']                        = {}
psfcheck_list['com.google.fonts/check/glyf_non_transformed_duplicate_components'] = {}
psfcheck_list['com.google.fonts/check/gf-axisregistry/fvar_axis_defaults']        = {}
psfcheck_list['com.google.fonts/check/glyf_nested_components']                    = {}
psfcheck_list['com.google.fonts/check/glyf_unused_data']                          = {}
psfcheck_list['com.google.fonts/check/glyph_coverage']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/gpos_kerning_info']                         = {}
psfcheck_list['com.google.fonts/check/has_ttfautohint_params']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/hinting_impact']                            = {}
psfcheck_list['com.google.fonts/check/integer_ppem_if_hinted']                    = {}
psfcheck_list['com.google.fonts/check/italic_angle']                              = {}
psfcheck_list['com.google.fonts/check/kern_table']                                = {}
psfcheck_list['com.google.fonts/check/kerning_for_non_ligated_sequences']         = {'exclude': True}
psfcheck_list['com.google.fonts/check/ligature_carets']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/linegaps']                                  = {}
psfcheck_list['com.google.fonts/check/license/OFL_copyright']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/loca/maxp_num_glyphs']                      = {}
psfcheck_list['com.google.fonts/check/mac_style']                                 = {}
psfcheck_list['com.google.fonts/check/mandatory_avar_table']                      = {}
psfcheck_list['com.google.fonts/check/mandatory_glyphs']                          = {}
psfcheck_list['com.google.fonts/check/maxadvancewidth']                           = {}
psfcheck_list['com.google.fonts/check/metadata/broken_links']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/canonical_style_names']            = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/canonical_weight_value']           = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/category']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/consistent_axis_enumeration']      = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/copyright']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/copyright_max_length']             = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/designer_profiles']                = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/designer_values']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/escaped_strings']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/familyname']                       = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/filenames']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/fontname_not_camel_cased']         = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/gf-axisregistry_bounds']           = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/gf-axisregistry_valid_tags']       = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/has_regular']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/includes_production_subsets']      = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/italic_style']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/license']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/listed_on_gfonts']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/match_filename_postscript']        = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/match_fullname_postscript']        = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/match_name_familyname']            = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/match_weight_postscript']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/menu_and_latin']                   = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/multiple_designers']               = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/copyright']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/family_and_full_names']     = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/family_name']               = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/font_name']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/full_name']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/nameid/post_script_name']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/normal_style']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/os2_weightclass']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/parses']                           = {'exclude': True}
#psfcheck_list['com.google.fonts/check/metadata/profiles_csv']                     = {}  # Currently disabled by FB
psfcheck_list['com.google.fonts/check/metadata/regular_is_400']                   = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/reserved_font_name']               = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/subsets_order']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/undeclared_fonts']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/unique_full_name_values']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/unique_weight_style_pairs']        = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/unknown_designer']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/valid_copyright']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/valid_filename_values']            = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/valid_full_name_values']           = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/valid_name_values']                = {'exclude': True}
psfcheck_list['com.google.fonts/check/metadata/valid_post_script_name_values']    = {'exclude': True}
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
psfcheck_list['com.google.fonts/check/old_ttfautohint']                           = {'exclude': True}
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
psfcheck_list['com.google.fonts/check/repo/dirname_matches_nameid_1']             = {'exclude': True}
psfcheck_list['com.google.fonts/check/repo/fb_report']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/repo/vf_has_static_fonts']                  = {}
psfcheck_list['com.google.fonts/check/repo/zip_files']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/required_tables']                           = {}
psfcheck_list['com.google.fonts/check/rupee']                                     = {}
psfcheck_list['com.google.fonts/check/shaping/collides']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/forbidden']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/regression']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/smart_dropout']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/stylisticset_description']                  = {}
psfcheck_list['com.google.fonts/check/superfamily/list']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/superfamily/vertical_metrics']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/ttx-roundtrip']                             = {}
psfcheck_list['com.google.fonts/check/unicode_range_bits']                        = {}
psfcheck_list['com.google.fonts/check/unique_glyphnames']                         = {}
psfcheck_list['com.google.fonts/check/unitsperem']                                = {}
psfcheck_list['com.google.fonts/check/unitsperem_strict']                         = {'exclude': True}
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
psfcheck_list['com.google.fonts/check/varfont/generate_static']                   = {}
psfcheck_list['com.google.fonts/check/varfont/has_HVAR']                          = {}
psfcheck_list['com.google.fonts/check/varfont/bold_wght_coord']                   = {}
psfcheck_list['com.google.fonts/check/varfont/consistent_axes']                   = {}
psfcheck_list['com.google.fonts/check/varfont/generate_static']                   = {}
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
psfcheck_list['org.sil.software/check/name/version_format']                       = {}

profile = make_profile(check_list=psfcheck_list)
