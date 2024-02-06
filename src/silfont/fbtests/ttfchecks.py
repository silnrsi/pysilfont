#!/usr/bin/env python3
'Support for use of Fontbakery ttf checks'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.googlefonts import METADATA_CHECKS, REPO_CHECKS, DESCRIPTION_CHECKS
from fontbakery.profiles.ufo_sources import UFO_PROFILE_CHECKS
from silfont.fbtests.silttfchecks import *

from collections import OrderedDict

# Set imports of standard ttf tests

profile_imports = ("fontbakery.profiles.universal",
                   "fontbakery.profiles.googlefonts",
                   "fontbakery.profiles.adobefonts",
                   "fontbakery.profiles.notofonts",
                   "fontbakery.profiles.fontval")

def make_base_profile():
    profile = profile_factory(default_section=Section("SIL Fonts"))
    profile.auto_register(globals())

    # Exclude groups of checks that check files other than ttfs
    for checkid in DESCRIPTION_CHECKS + METADATA_CHECKS + REPO_CHECKS + UFO_PROFILE_CHECKS:
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
    for checkid in sorted(set(profile._check_registry.keys())):
        section = profile._check_registry[checkid]
        check = section.get_check(checkid)
        conditions = getattr(check, "conditions")
        exclude = False
        if variable_font and "not is_variable_font" in conditions: exclude = True
        if not variable_font and "is_variable_font" in conditions: exclude = True
        if "noto" in checkid.lower(): exclude = True # These will be specific to Noto fonts
        if ":adobefonts" in checkid.lower(): exclude = True # Copy of standard test with overridden results so no new info

        if exclude: profile.remove_check(checkid)
    # Remove further checks that are only relevant for variable fonts but don't use the is_variable_font condition
    if not variable_font:
        for checkid in (
            "com.adobe.fonts/check/stat_has_axis_value_tables",
            "com.google.fonts/check/STAT_strings",
            "com.google.fonts/check/STAT/axis_order"):
            if checkid in profile._check_registry.keys(): profile.remove_check(checkid)
    return profile

def all_checks_dict(): # An ordered dict of all checks designed for exporting the data
    profile = make_base_profile()
    check_dict=OrderedDict()

    for checkid in sorted(set(profile._check_registry.keys()), key=str.casefold):
        if "noto" in checkid.lower(): continue # We wxclude these in make_profile()
        if ":adobefonts" in checkid.lower(): continue # We wxclude these in make_profile()

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
psfcheck_list['com.adobe.fonts/check/family/consistent_family_name']              = {}
psfcheck_list['com.adobe.fonts/check/family/bold_italic_unique_for_nameid1']      = {}
psfcheck_list['com.adobe.fonts/check/family/consistent_upm']                      = {}
psfcheck_list['com.adobe.fonts/check/family/max_4_fonts_per_family_name']         = {}
psfcheck_list['com.adobe.fonts/check/find_empty_letters']                         = {}
psfcheck_list['com.adobe.fonts/check/freetype_rasterizer']                        = {'exclude': True}
#psfcheck_list['com.adobe.fonts/check/freetype_rasterizer:googlefonts']            = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/fsselection_matches_macstyle']               = {}
psfcheck_list['com.adobe.fonts/check/name/empty_records']                         = {}
psfcheck_list['com.adobe.fonts/check/name/postscript_name_consistency']           = {}
psfcheck_list['com.adobe.fonts/check/nameid_1_win_english']                       = {}
psfcheck_list['com.adobe.fonts/check/name/postscript_vs_cff']                     = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/postscript_name']                            = {}
psfcheck_list['com.adobe.fonts/check/sfnt_version']                               = {}
psfcheck_list['com.adobe.fonts/check/stat_has_axis_value_tables']                 = {}
psfcheck_list['com.adobe.fonts/check/STAT_strings']                               = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/unsupported_tables']                         = {'exclude': True}
psfcheck_list['com.adobe.fonts/check/varfont/distinct_instance_records']          = {}
psfcheck_list['com.adobe.fonts/check/varfont/foundry_defined_tag_name']           = {}
psfcheck_list['com.adobe.fonts/check/varfont/same_size_instance_records']         = {}
psfcheck_list['com.adobe.fonts/check/varfont/valid_axis_nameid']                  = {}
psfcheck_list['com.adobe.fonts/check/varfont/valid_default_instance_nameids']     = {}
psfcheck_list['com.adobe.fonts/check/varfont/valid_postscript_nameid']            = {}
psfcheck_list['com.adobe.fonts/check/varfont/valid_subfamily_nameid']             = {}
# psfcheck_list['com.fontwerk/check/inconsistencies_between_fvar_stat']             = {} # No longer in Font Bakery
# psfcheck_list['com.fontwerk/check/weight_class_fvar']                             = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/aat']                                       = {}
psfcheck_list['com.google.fonts/check/alt_caron']                                 = {}
psfcheck_list['com.google.fonts/check/alt_caron:googlefonts']                     = {}
psfcheck_list['com.google.fonts/check/arabic_high_hamza']                         = {}
psfcheck_list['com.google.fonts/check/arabic_spacing_symbols']                    = {}
# psfcheck_list['com.google.fonts/check/all_glyphs_have_codepoints']                = {'exclude': True} #  No longer in Font Bakery
psfcheck_list['com.google.fonts/check/canonical_filename']                        = {}
psfcheck_list['com.google.fonts/check/caret_slope']                               = {}
psfcheck_list['com.google.fonts/check/cjk_chws_feature']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_not_enough_glyphs']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics']                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/cjk_vertical_metrics_regressions']          = {'exclude': True}
psfcheck_list['com.google.fonts/check/cmap/alien_codepoints']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/cmap/format_12']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/cmap/unexpected_subtables']                 = {}
psfcheck_list['com.google.fonts/check/color_cpal_brightness']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/colorfont_tables']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/code_pages']                                = {}
psfcheck_list['com.google.fonts/check/contour_count']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/dotted_circle']                             = {}
psfcheck_list['com.google.fonts/check/dsig']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/empty_glyph_on_gid1_for_colrv0']            = {'exclude': True}
psfcheck_list['com.google.fonts/check/epar']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/family/control_chars']                      = {}
psfcheck_list['com.google.fonts/check/family/equal_codepoint_coverage']           = {}
psfcheck_list['com.google.fonts/check/family/equal_font_versions']                = {}
psfcheck_list['com.google.fonts/check/family/equal_unicode_encodings']            = {}
psfcheck_list['com.google.fonts/check/family/has_license']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/family/italics_have_roman_counterparts']    = {}
psfcheck_list['com.google.fonts/check/family/panose_familytype']                  = {}
psfcheck_list['com.google.fonts/check/family/panose_proportion']                  = {}
psfcheck_list['com.google.fonts/check/family/single_directory']                   = {}
psfcheck_list['com.google.fonts/check/family/tnum_horizontal_metrics']            = {}
psfcheck_list['com.google.fonts/check/family/underline_thickness']                = {}
psfcheck_list['com.google.fonts/check/family/vertical_metrics']                   = {}
psfcheck_list['com.google.fonts/check/family/win_ascent_and_descent']             = {}
#    {'change_status': {'FAIL': 'WARN', 'reason': 'Under review'}}
psfcheck_list['com.google.fonts/check/family_naming_recommendations']             = {}
psfcheck_list['com.google.fonts/check/file_size']                                 = {}
psfcheck_list['com.google.fonts/check/font_copyright']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/font_names']                                = {}
psfcheck_list['com.google.fonts/check/font_version']                              = {}
psfcheck_list['com.google.fonts/check/fontbakery_version']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontdata_namecheck']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontv']                                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/fontvalidator']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/fsselection']                               = {}
psfcheck_list['com.google.fonts/check/fstype']                                    = {}
psfcheck_list['com.google.fonts/check/fvar_instances']                            = {}
psfcheck_list['com.google.fonts/check/fvar_name_entries']                         = {}
psfcheck_list['com.google.fonts/check/gasp']                                      = {'exclude': True}
psfcheck_list['com.google.fonts/check/gdef_mark_chars']                           = {}
psfcheck_list['com.google.fonts/check/gdef_non_mark_chars']                       = {}
psfcheck_list['com.google.fonts/check/gdef_spacing_marks']                        = {}
psfcheck_list['com.google.fonts/check/gf_axisregistry/fvar_axis_defaults']        = {}
psfcheck_list['com.google.fonts/check/glyf_nested_components']                    = {}
psfcheck_list['com.google.fonts/check/glyf_non_transformed_duplicate_components'] = {}
psfcheck_list['com.google.fonts/check/glyf_unused_data']                          = {}
psfcheck_list['com.google.fonts/check/glyph_coverage']                            = {'exclude': True}
psfcheck_list['com.google.fonts/check/glyphsets/shape_languages']                 = {}
psfcheck_list['com.google.fonts/check/gpos7']                                     = {}
psfcheck_list['com.google.fonts/check/gpos_kerning_info']                         = {}
psfcheck_list['com.google.fonts/check/has_ttfautohint_params']                    = {'exclude': True}
psfcheck_list['com.google.fonts/check/hinting_impact']                            = {}
psfcheck_list['com.google.fonts/check/hmtx/comma_period']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/hmtx/encoded_latin_digits']                 = {'exclude': True}
psfcheck_list['com.google.fonts/check/hmtx/whitespace_advances']                  = {'exclude': True}
psfcheck_list['com.google.fonts/check/integer_ppem_if_hinted']                    = {}
psfcheck_list['com.google.fonts/check/interpolation_issues']                      = {}
psfcheck_list['com.google.fonts/check/italic_angle']                              = {}
psfcheck_list['com.google.fonts/check/italic_angle:googlefonts']                  = {}
psfcheck_list['com.google.fonts/check/italic_axis_in_stat']                       = {'exclude': True}
psfcheck_list['com.google.fonts/check/italic_axis_in_stat_is_boolean']            = {'exclude': True}
psfcheck_list['com.google.fonts/check/italic_axis_in_stat_is_boolean:googlefonts']= {'exclude': True}
psfcheck_list['com.google.fonts/check/italic_axis_last']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/italic_axis_last:googlefonts']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/kern_table']                                = {}
psfcheck_list['com.google.fonts/check/kerning_for_non_ligated_sequences']         = {'exclude': True}
psfcheck_list['com.google.fonts/check/layout_valid_feature_tags']                 = {}
psfcheck_list['com.google.fonts/check/layout_valid_language_tags']                = \
    {'change_status': {'FAIL': 'WARN', 'reason': 'The "invalid" ones are used by Harfbuzz'}}
psfcheck_list['com.google.fonts/check/layout_valid_script_tags']                  = {}
psfcheck_list['com.google.fonts/check/legacy_accents']                            = {}
psfcheck_list['com.google.fonts/check/ligature_carets']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/linegaps']                                  = {}
psfcheck_list['com.google.fonts/check/loca/maxp_num_glyphs']                      = {}
psfcheck_list['com.google.fonts/check/mac_style']                                 = {}
psfcheck_list['com.google.fonts/check/mandatory_avar_table']                      = {}
psfcheck_list['com.google.fonts/check/mandatory_glyphs']                          = {}
psfcheck_list['com.google.fonts/check/math_signs_width']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/maxadvancewidth']                           = {}
psfcheck_list['com.google.fonts/check/meta/script_lang_tags']                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/missing_small_caps_glyphs']                 = {}
psfcheck_list['com.google.fonts/check/monospace']                                 = {}
psfcheck_list['com.google.fonts/check/name/ascii_only_entries']                   = {}
psfcheck_list['com.google.fonts/check/name/copyright_length']                     = {}
psfcheck_list['com.google.fonts/check/name/description_max_length']               = {}
psfcheck_list['com.google.fonts/check/name/family_and_style_max_length']          = {}
psfcheck_list['com.google.fonts/check/name/family_name_compliance']               = {}
# psfcheck_list['com.google.fonts/check/name/familyname']                           = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/name/familyname_first_char']                = {}
# psfcheck_list['com.google.fonts/check/name/fullfontname']                         = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/name/italic_names']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/license']                              = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/license_url']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/line_breaks']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/name/mandatory_entries']                    = {}
psfcheck_list['com.google.fonts/check/name/match_familyname_fullfont']            = {}
psfcheck_list['com.google.fonts/check/name/no_copyright_on_description']          = {}
# psfcheck_list['com.google.fonts/check/name/postscriptname']                       = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/name/rfn']                                  = {'exclude': True}
# psfcheck_list['com.google.fonts/check/name/subfamilyname']                        = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/name/trailing_spaces']                      = {'exclude': True}
# psfcheck_list['com.google.fonts/check/name/typographicfamilyname']                = {} # No longer in Font Bakery
# psfcheck_list['com.google.fonts/check/name/typographicsubfamilyname']             = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/name/unwanted_chars']                       = {}
psfcheck_list['com.google.fonts/check/name/version_format']                       = {'exclude': True}
psfcheck_list['com.google.fonts/check/no_debugging_tables']                       = {}
psfcheck_list['com.google.fonts/check/old_ttfautohint']                           = {'exclude': True}
psfcheck_list['com.google.fonts/check/os2/use_typo_metrics']                      = {}
# psfcheck_list['com.google.fonts/check/os2/use_typo_metrics']                      = \  (Left a copy commented out as an
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
psfcheck_list['com.google.fonts/check/production_glyphs_similarity']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/render_own_name']                           = {}
psfcheck_list['com.google.fonts/check/required_tables']                           = {}
psfcheck_list['com.google.fonts/check/rupee']                                     = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/collides']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/forbidden']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/shaping/regression']                        = {'exclude': True}
psfcheck_list['com.google.fonts/check/smart_dropout']                             = {'exclude': True}
psfcheck_list['com.google.fonts/check/slant_direction']                           = {}
psfcheck_list['com.google.fonts/check/soft_dotted']                               = {'exclude': True}
psfcheck_list['com.google.fonts/check/soft_hyphen']                               = {'exclude': True}
psfcheck_list['com.google.fonts/check/STAT']                                      = {}
psfcheck_list['com.google.fonts/check/STAT/axis_order']                           = {}
psfcheck_list['com.google.fonts/check/STAT/gf_axisregistry']                      = {}
psfcheck_list['com.google.fonts/check/STAT_strings']                              = {}
psfcheck_list['com.google.fonts/check/STAT_in_statics']                           = {}
psfcheck_list['com.google.fonts/check/stylisticset_description']                  = {}
psfcheck_list['com.google.fonts/check/superfamily/list']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/superfamily/vertical_metrics']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/transformed_components']                    = {}
psfcheck_list['com.google.fonts/check/ttx_roundtrip']                             = {}
psfcheck_list['com.google.fonts/check/unicode_range_bits']                        = {}
psfcheck_list['com.google.fonts/check/unique_glyphnames']                         = {}
psfcheck_list['com.google.fonts/check/unitsperem']                                = {}
psfcheck_list['com.google.fonts/check/unitsperem_strict']                         = {'exclude': True}
psfcheck_list['com.google.fonts/check/unreachable_glyphs']                        = {}
psfcheck_list['com.google.fonts/check/unwanted_tables']                           = {}
psfcheck_list['com.google.fonts/check/usweightclass']                             = {}
psfcheck_list['com.google.fonts/check/valid_glyphnames']                          = {}
psfcheck_list['com.google.fonts/check/varfont_duplicate_instance_names']          = {}
# psfcheck_list['com.google.fonts/check/varfont_has_instances']                     = {} # No longer in Font Bakery
# psfcheck_list['com.google.fonts/check/varfont_instance_coordinates']              = {} # No longer in Font Bakery
# psfcheck_list['com.google.fonts/check/varfont_instance_names']                    = {} # No longer in Font Bakery
# psfcheck_list['com.google.fonts/check/varfont_weight_instances']                  = {} # No longer in Font Bakery
psfcheck_list['com.google.fonts/check/varfont/bold_wght_coord']                   = {}
psfcheck_list['com.google.fonts/check/varfont/consistent_axes']                   = {'exclude': True}
psfcheck_list['com.google.fonts/check/varfont/duplexed_axis_reflow']              = {}
psfcheck_list['com.google.fonts/check/varfont/generate_static']                   = {}
# psfcheck_list['com.google.fonts/check/varfont/grade_reflow']                      = {}  # No longer in Font Bakery
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
psfcheck_list['com.google.fonts/check/version_bump']                              = {'exclude': True}
psfcheck_list['com.google.fonts/check/vertical_metrics']                          = {'exclude': True}
psfcheck_list['com.google.fonts/check/vertical_metrics_regressions']              = {'exclude': True}
psfcheck_list['com.google.fonts/check/vttclean']                                  = {}
psfcheck_list['com.google.fonts/check/whitespace_glyphnames']                     = {}
psfcheck_list['com.google.fonts/check/whitespace_glyphs']                         = {}
psfcheck_list['com.google.fonts/check/whitespace_ink']                            = {}
psfcheck_list['com.google.fonts/check/whitespace_widths']                         = {}
psfcheck_list['com.google.fonts/check/xavgcharwidth']                             = {}
psfcheck_list['com.thetypefounders/check/vendor_id']                              = {'exclude': True}
psfcheck_list['com.typenetwork/check/varfont/ital_range']                         = {}
psfcheck_list['org.sil/check/number_widths']                                      = {}
psfcheck_list['org.sil/check/name/version_format']                                = {}
psfcheck_list['org.sil/check/whitespace_widths']                                  = {}

profile = make_profile(check_list=psfcheck_list)
