__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2024 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
"""
SIL fontbakery profile for version 0.13.X
"""
# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "check_definitions": ["silfont.fbtests.checks"],
    "sections": {
        "SIL checks": [
            "silfonts/name/version_format",
            "silfonts/number_widths",
            "silfonts/whitespace_widths",
            "silfonts/repo/FONTLOG",
            "silfonts/repo/is_OFL_FAQ_present_and_current",
            "silfonts/repo/is_OFL_URL_current",
            "silfonts/repo/executable_bits"
        ],
        "Font Bakery checks": [
            "opentype/family/bold_italic_unique_for_nameid1",
            "opentype/family/consistent_family_name",
            "adobefonts/family/consistent_upm",
            "opentype/family/max_4_fonts_per_family_name",
            "opentype/fsselection_matches_macstyle",
            "opentype/name/empty_records",
            "empty_letters",
            "opentype/name/postscript_name_consistency",
            "adobefonts/nameid_1_win_english",
            "opentype/postscript_name",
            "sfnt_version",
            "unwanted_aat_tables",
            "alt_caron",
            "arabic_high_hamza",
            "arabic_spacing_symbols",
            "googlefonts/canonical_filename",
            "opentype/caret_slope",
            "case_mapping",
            "notofonts/cmap/unexpected_subtables",
            "opentype/code_pages",
            "dotted_circle",
            "opentype/family_naming_recommendations",
            "family/control_chars",
            "googlefonts/family/equal_codepoint_coverage",
            "opentype/family/equal_font_versions",
            "googlefonts/family/italics_have_roman_counterparts",
            "opentype/family/panose_familytype",
            "family/single_directory",
            "googlefonts/family/tnum_horizontal_metrics",
            "opentype/family/underline_thickness",
            "family/vertical_metrics",
            "family/win_ascent_and_descent",
            "file_size",
            "googlefonts/font_names",
            "opentype/font_version",
            "opentype/fsselection",
            "googlefonts/fstype",
            "opentype/gdef_mark_chars",
            "opentype/gdef_non_mark_chars",
            "opentype/gdef_spacing_marks",
            "glyf_nested_components",
            "opentype/glyf_non_transformed_duplicate_components",
            "opentype/glyf_unused_data",
            "opentype/gpos_kerning_info",
            "gpos7",
            "hinting_impact",
            "integer_ppem_if_hinted",
            "opentype/italic_angle",
            "opentype/kern_table",
            "opentype/layout_valid_feature_tags",
            "opentype/layout_valid_language_tags",
            "opentype/layout_valid_script_tags",
            "linegaps",
            "opentype/loca/maxp_num_glyphs",
            "opentype/mac_style",
            "mandatory_glyphs",
            "opentype/maxadvancewidth",
            "missing_small_caps_glyphs",
            "opentype/monospace",
            "opentype/cff_ascii_strings",
            "googlefonts/name/description_max_length",
            "name/family_and_style_max_length",
            "googlefonts/name/family_name_compliance",
            "googlefonts/name/familyname_first_char",
            "googlefonts/name/mandatory_entries",
            "opentype/name/match_familyname_fullfont",
            "name/no_copyright_on_description",
            "no_debugging_tables",
            "os2_metrics_match_hhea",
            "googlefonts/os2/use_typo_metrics",
            "ots",
            "opentype/post_table_version",
            "render_own_name",
            "required_tables",
            "STAT_in_statics",
            "stylisticset_description",
            "tabular_kerning",
            "transformed_components",
            "ttx_roundtrip",
            "notofonts/unicode_range_bits",
            "unique_glyphnames",
            "googlefonts/unitsperem",
            "unreachable_glyphs",
            "unwanted_tables",
            "typenetwork/usweightclass",
            "valid_glyphnames",
            "opentype/varfont/family_axis_ranges",
            "opentype/vendor_id",
            "vttclean",
            "whitespace_glyphs",
            "whitespace_ink",
            "whitespace_widths"
        ],
        "New checks from 0.12.10/Aug 2024": [
            "opentype/dsig",
            "opentype/family_naming_recommendations",
            "opentype/xavgcharwidth",
            "typoascender_exceeds_Agrave",
            "designspace_has_consistent_codepoints",
            "designspace_has_consistent_glyphset",
            "designspace_has_default_master",
            "designspace_has_sources",
            "gsub/smallcaps_before_ligatures",
            "googlefonts/name/mandatory_entries",
            "os2_metrics_match_hhea",
            "googlefonts/production_glyphs_similarity",
            "googlefonts/vertical_metrics_regressions",
            "empty_letters",
            "adobefonts/nameid_1_win_english",
            "no_mac_entries",
            "fontwerk/style_linking",
            "name/italic_names",
            "notofonts/cmap/unexpected_subtables",
            "notofonts/unicode_range_bits",
            "rupee",
            "microsoft/manufacturer",
            "name_id_1",
            "name_id_2",
            "name_length_req",
            "microsoft/office_ribz_req",
            "tnum_glyphs_equal_widths",
            "microsoft/trademark",
            "microsoft/version",
            "vtt_volt_data",
            "typenetwork/family/duplicated_names",
            "typenetwork/family/tnum_horizontal_metrics",
            "typenetwork/family/valid_strikeout",
            "typenetwork/family/valid_underline",
            "typenetwork/font_is_centered_vertically",
            "typenetwork/glyph_coverage",
            "typenetwork/marks_width",
            "typenetwork/name/mandatory_entries"
            ],
    },
    "overrides": {
        "alt_caron": [
            {
                "code": "decomposed-outline",
                "status": "PASS",
                "reason": "some SIL fonts intentionally use decomposed outlines for Lcaron, dcaron, lcaron and tcaron."
            }
            ],
        "legacy_accents": [
            {
                "code": "legacy-accent-components",
                "status": "PASS",
                "reason": "SIL disagrees with the premise of this check."
            }
        ],
        "whitespace_glyphs": [
            {
                "code": "missing-whitespace-glyph-0x00A0",
                "status": "WARN",
                "reason": "this is not as severe as assessed in the original check for 0x00A0.",
            }
        ],
    },
    "configuration_defaults": {
        "file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
