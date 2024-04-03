"""
SIL fontbakery profile  <https://software.sil.org/fonts/>
for version 0.12.X
"""
# pylint: disable=line-too-long  # This is data, not code
PROFILE = {
    "include_profiles": ["universal", "opentype", "googlefonts"],
    "check_definitions": ["silfont.fbtests.checks"],
    "sections": {
        "SIL Checks": [
            "org.sil/check/name/version_format",
            "org.sil/check/number_widths",
            "org.sil/check/whitespace_widths",
        ],
    },
    "overrides": {
        "com.google.fonts/check/whitespace_glyphs": [
            {
                "code": "missing-whitespace-glyph-0x00A0",
                "status": "WARN",
                "reason": "this is not as severe as assessed in the original check for 0x00A0.",
            }
        ],
    },
    "exclude_checks": [
        # don"t run these checks on the SIL profile:
        "com.google.fonts/check/canonical_filename",
        "com.thetypefounders/check/vendor_id",
        "com.google.fonts/check/version_bump",
        "com.google.fonts/check/vertical_metrics",
        "com.google.fonts/check/vertical_metrics_regressions",
        "com.google.fonts/check/varfont/consistent_axes"
        "com.google.fonts/check/unitsperem_strict"
        "com.google.fonts/check/superfamily/list"
        "com.google.fonts/check/superfamily/vertical_metrics",
        "com.google.fonts/check/soft_dotted",
        "com.google.fonts/check/soft_hyphen",
        "com.google.fonts/check/rupee",
        "com.google.fonts/check/shaping/collides",
        "com.google.fonts/check/shaping/forbidden",
        "com.google.fonts/check/shaping/regression",
        "com.google.fonts/check/smart_dropout",
        "com.google.fonts/check/glyph_coverage",
        "com.google.fonts/check/production_glyphs_similarity",
        "com.google.fonts/check/has_ttfautohint_params",
        "com.google.fonts/check/outline_alignment_miss",
        "com.google.fonts/check/outline_colinear_vectors",
        "com.google.fonts/check/outline_jaggy_segments",
        "com.google.fonts/check/outline_semi_vertical",
        "com.google.fonts/check/outline_short_segments",
        "com.google.fonts/check/points_out_of_bounds",
        "com.google.fonts/check/italic_axis_in_stat",
        "com.google.fonts/check/italic_axis_in_stat_is_boolean",
        "com.google.fonts/check/italic_axis_in_stat_is_boolean:googlefonts",
        "com.google.fonts/check/italic_axis_last",
        "com.google.fonts/check/italic_axis_last:googlefonts",
        "com.google.fonts/check/old_ttfautohint",
        "com.google.fonts/check/hmtx/comma_period",
        "com.google.fonts/check/hmtx/encoded_latin_digits",
        "com.google.fonts/check/hmtx/whitespace_advances",
        "com.google.fonts/check/name/version_format",
        "com.google.fonts/check/kerning_for_non_ligated_sequences",
        "com.google.fonts/check/name/rfn",
        "com.google.fonts/check/name/trailing_spaces",
        "com.google.fonts/check/ligature_carets",
        "com.google.fonts/check/name/italic_names",
        "com.google.fonts/check/name/license",
        "com.google.fonts/check/name/license_url",
        "com.google.fonts/check/name/line_breaks",
        "com.google.fonts/check/math_signs_width",
        "com.google.fonts/check/meta/script_lang_tags",
        "com.google.fonts/check/dsig",
        "com.google.fonts/check/empty_glyph_on_gid1_for_colrv0",
        "com.google.fonts/check/epar",
        "com.google.fonts/check/gasp",
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/family/has_license",
        "com.google.fonts/check/fontbakery_version",
        "com.google.fonts/check/fontdata_namecheck",
        "com.google.fonts/check/fontv",
        "com.google.fonts/check/fontvalidator",
        "com.google.fonts/check/contour_count",
        "com.google.fonts/check/color_cpal_brightness",
        "com.google.fonts/check/colorfont_tables",
        "com.google.fonts/check/cjk_chws_feature",
        "com.google.fonts/check/cjk_not_enough_glyphs",
        "com.google.fonts/check/cjk_vertical_metrics",
        "com.google.fonts/check/cjk_vertical_metrics_regressions",
        "com.google.fonts/check/cmap/alien_codepoints",
        "com.google.fonts/check/cmap/format_12",
        "com.adobe.fonts/check/STAT_strings",
        "com.adobe.fonts/check/unsupported_tables",
        "com.adobe.fonts/check/name/postscript_vs_cff",
        "com.adobe.fonts/check/freetype_rasterizer",
        "com.adobe.fonts/check/freetype_rasterizer:googlefonts",
        "com.adobe.fonts/check/cff_call_depth",
        "com.adobe.fonts/check/cff_deprecated_operators",
        "com.adobe.fonts/check/cff2_call_depth",
        "com.google.fonts/check/alt_caron:googlefonts",
        "com.google.fonts/check/glyphsets/shape_language",
        "com.google.fonts/check/italic_angle",
    ],
    "configuration_defaults": {
        "com.google.fonts/check/file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
}
