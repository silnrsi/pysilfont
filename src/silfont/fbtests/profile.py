__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2024 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
"""
SIL fontbakery profile for version 0.12.X
"""
# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "check_definitions": ["silfont.fbtests.checks"],
    "sections": {
        "SIL Checks": [
            "org.sil/check/name/version_format",
            "org.sil/check/number_widths",
            "org.sil/check/whitespace_widths",
        ],
        "Google Fonts":[
            "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
            "com.adobe.fonts/check/family/consistent_family_name",
            "com.adobe.fonts/check/family/consistent_upm",
            "com.adobe.fonts/check/family/max_4_fonts_per_family_name",
            "com.adobe.fonts/check/fsselection_matches_macstyle",
            "com.adobe.fonts/check/name/empty_records",
            "com.adobe.fonts/check/find_empty_letters",
            "com.adobe.fonts/check/name/postscript_name_consistency",
            "com.adobe.fonts/check/nameid_1_win_english",
            "com.adobe.fonts/check/postscript_name",
            "com.adobe.fonts/check/sfnt_version",
            "com.google.fonts/check/aat",
            "com.google.fonts/check/alt_caron",
            "com.google.fonts/check/arabic_high_hamza",
            "com.google.fonts/check/arabic_spacing_symbols",
            "com.google.fonts/check/canonical_filename",
            "com.google.fonts/check/caret_slope",
            "com.google.fonts/check/case_mapping",
            "com.google.fonts/check/cmap/unexpected_subtables",
            "com.google.fonts/check/code_pages",
            "com.google.fonts/check/dotted_circle",
            "com.google.fonts/check/family_naming_recommendations",
            "com.google.fonts/check/family/control_chars",
            "com.google.fonts/check/family/equal_codepoint_coverage",
            "com.google.fonts/check/family/equal_font_versions",
            "com.google.fonts/check/family/italics_have_roman_counterparts",
            "com.google.fonts/check/family/panose_familytype",
            "com.google.fonts/check/family/single_directory",
            "com.google.fonts/check/family/tnum_horizontal_metrics",
            "com.google.fonts/check/family/underline_thickness",
            "com.google.fonts/check/family/vertical_metrics",
            "com.google.fonts/check/family/win_ascent_and_descent",
            "com.google.fonts/check/file_size",
            "com.google.fonts/check/font_names",
            "com.google.fonts/check/font_version",
            "com.google.fonts/check/fsselection",
            "com.google.fonts/check/fstype",
            "com.google.fonts/check/gdef_mark_chars",
            "com.google.fonts/check/gdef_non_mark_chars",
            "com.google.fonts/check/gdef_spacing_marks",
            "com.google.fonts/check/glyf_nested_components",
            "com.google.fonts/check/glyf_non_transformed_duplicate_components",
            "com.google.fonts/check/glyf_unused_data",
            "com.google.fonts/check/gpos_kerning_info",
            "com.google.fonts/check/gpos7",
            "com.google.fonts/check/hinting_impact",
            "com.google.fonts/check/integer_ppem_if_hinted",
            "com.google.fonts/check/italic_angle",
            "com.google.fonts/check/kern_table",
            "com.google.fonts/check/layout_valid_feature_tags",
            "com.google.fonts/check/layout_valid_language_tags",
            "com.google.fonts/check/layout_valid_script_tags",
            "com.google.fonts/check/linegaps",
            "com.google.fonts/check/loca/maxp_num_glyphs",
            "com.google.fonts/check/mac_style",
            "com.google.fonts/check/mandatory_glyphs",
            "com.google.fonts/check/maxadvancewidth",
            "com.google.fonts/check/missing_small_caps_glyphs",
            "com.google.fonts/check/monospace",
            "com.google.fonts/check/name/ascii_only_entries",
            "com.google.fonts/check/name/description_max_length",
            "com.google.fonts/check/name/family_and_style_max_length",
            "com.google.fonts/check/name/family_name_compliance",
            "com.google.fonts/check/name/familyname_first_char",
            "com.google.fonts/check/name/mandatory_entries",
            "com.google.fonts/check/name/match_familyname_fullfont",
            "com.google.fonts/check/name/no_copyright_on_description",
            "com.google.fonts/check/name/unwanted_chars",
            "com.google.fonts/check/no_debugging_tables",
            "com.google.fonts/check/os2_metrics_match_hhea",
            "com.google.fonts/check/os2/use_typo_metrics",
            "com.google.fonts/check/ots",
            "com.google.fonts/check/post_table_version",
            "com.google.fonts/check/render_own_name",
            "com.google.fonts/check/required_tables",
            "com.google.fonts/check/STAT_in_statics",
            "com.google.fonts/check/stylisticset_description",
            "com.google.fonts/check/tabular_kerning",
            "com.google.fonts/check/transformed_components",
            "com.google.fonts/check/ttx_roundtrip",
            "com.google.fonts/check/unicode_range_bits",
            "com.google.fonts/check/unique_glyphnames",
            "com.google.fonts/check/unitsperem",
            "com.google.fonts/check/unreachable_glyphs",
            "com.google.fonts/check/unwanted_tables",
            "com.google.fonts/check/usweightclass",
            "com.google.fonts/check/valid_glyphnames",
            "com.google.fonts/check/varfont/family_axis_ranges",
            "com.google.fonts/check/vendor_id",
            "com.google.fonts/check/vttclean",
            "com.google.fonts/check/whitespace_glyphnames",
            "com.google.fonts/check/whitespace_glyphs",
            "com.google.fonts/check/whitespace_ink",
            "com.google.fonts/check/whitespace_widths",
            "com.google.fonts/check/xavgcharwidth"
        ]
    },
    "overrides": {
        "com.google.fonts/check/alt_caron" : [
            {
                "code": "decomposed-outline",
                "status": "PASS",
                "reason": "some SIL fonts intentionally use decomposed outlines for Lcaron, dcaron, lcaron and tcaron."
            }
        ],
        "com.google.fonts/check/whitespace_glyphs": [
            {
                "code": "missing-whitespace-glyph-0x00A0",
                "status": "WARN",
                "reason": "this is not as severe as assessed in the original check for 0x00A0.",
            }
        ],
    },
    "configuration_defaults": {
        "com.google.fonts/check/file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
