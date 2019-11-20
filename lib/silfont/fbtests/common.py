# template profile for local testing of ttfs with fontbakery.
"""
Checks for SIL Fonts  http://software.sil.org/fonts
"""
import unicodedata
import os
import sys

from fontbakery.checkrunner import Section, INFO, WARN, ERROR, SKIP, PASS, FAIL
from fontbakery.callable import condition, check, disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.adobefonts import ADOBEFONTS_PROFILE_CHECKS
from fontbakery.constants import PriorityLevel, NameID, PlatformID, WindowsEncodingID

# our common selection of checks: imports and excludes:

profile_imports = ("fontbakery.profiles.universal", "fontbakery.profiles.googlefonts", "fontbakery.profiles.adobefonts" )

SILFONTS_PROFILE_CHECKS = (
    UNIVERSAL_PROFILE_CHECKS + GOOGLEFONTS_PROFILE_CHECKS + ADOBEFONTS_PROFILE_CHECKS + [
        "org.sil.software/check/helloworld-common",
        "org.sil.software/check/has-R-common"
    ]
)

profile = profile_factory(default_section=Section("SIL Fonts"))

# Our own checks below
# See https://font-bakery.readthedocs.io/en/latest/developer/writing-profiles.html

# We use `check` as a decorator to wrap an ordinary python
# function into an instance of FontBakeryCheck to prepare
# and mark it as a check.
# A check id is mandatory and must be globally and timely
# unique. See "Naming Things: check-ids" below.
@check(id='org.sil.software/check/helloworld-common')
# This check will run only once as it has no iterable
# arguments. Since it has no arguments at all and because
# checks should be idempotent (and this one is), there's
# not much sense in having it all. It will run once
# and always yield the same result.
def hello_world():
    """Simple "Hello (alphabets of the) World" example."""
    # The function name of a check is not very important
    # to create it, only to import it from another module
    # or to call it directly, However, a short line of
    # human readable description is mandatory, preferable
    # via the docstring of the check.

    # A status of a check can be `return`ed or `yield`ed
    # depending on the nature of the check, `return`
    # can only return just one status while `yield`
    # makes a generator out of it and it can produce
    # many statuses.
    # A status also always must be a tuple of (Status, Message)
    # For `Message` a string is OK, but for unit testing
    # it turned out that an instance of `fontbakery.message.Message`
    # can be very useful. It can additionally provide
    # a status code, better suited to figure out the exact
    # check result.
    yield PASS, 'Hello (alphabets of the) World'


@check(id='org.sil.software/check/has-R-common')
# This check will run once for each item in `fonts`.
# This is achieved via the iterag definition of font: fonts
def has_cap_r_in_name(font):
    """Filename contains an "R"."""
    # This test is not very useful again, but for each
    # input it can result in a PASS or a FAIL.
    if 'R' not in font:
        # This is our first check that can potentially fail.
        # To document this: return is also ok in a check.
        return FAIL, '"R" is not in font filename.'
    else:
        # since you can't return at one point in a function
        # and yield at another point, we always have to
        # use return within this check.
        return PASS, '"R" is in font filename.'


# Selection of checks to skip (they still appear but with a skip message)
def check_skip_filter(checkid, font=None, **iterargs):
    if checkid in (
        "com.adobe.fonts/check/cff_call_depth",
        "com.adobe.fonts/check/cff2_call_depth",
        "com.google.fonts/check/all_glyphs_have_codepoints",
        "com.google.fonts/check/points_out_of_bounds",
        "com.google.fonts/check/contour_count",
        "com.google.fonts/check/description_broken_links",
        "com.google.fonts/check/description_git_url",
        "com.google.fonts/check/description_max_length",
        "com.google.fonts/check/description_min_length",
        "com.google.fonts/check/description_valid_html",
        "com.google.fonts/check/description_variable_font",
        "com.google.fonts/check/epar",
        "com.google.fonts/check/family_has_license",
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
        "com.google.fonts/check/name_license",
        "com.google.fonts/check/name_license_url",
        "com.google.fonts/check/old_ttfautohint",
        "com.google.fonts/check/repo_dirname_match_nameid_1",
        "com.google.fonts/check/unitsperem_strict",
        "com.adobe.fonts/check/name_postscript_vs_cff",
        "com.daltonmaag/check/recommended_fields",
        "com.daltonmaag/check/unnecessary_fields",
        "com.google.fonts/check/family_win_ascent_and_descent",
        "com.google.fonts/check/ftxvalidator",
        "com.google.fonts/check/name_trailing_spaces",
        "com.google.fonts/check/glyph_coverage"
    ):
        return False, ('Skipping irrelevant check for SIL fonts')
    return True, None


profile.check_skip_filter = check_skip_filter
profile.auto_register(globals())

# attempt at full exclusion of checks
# exclude_checks = [
#      'com.google.fonts/check/name/ots',
#      'com.google.fonts/check/monospace',
#      'com.google.fonts/check/gpos_kerning_info',
#      'com.google.fonts/check/currency_chars',
#      'com.google.fonts/check/whitespace_ink',
#      'com.google.fonts/check/description/broken_links',
#      'com.google.fonts/check/name/rfn'
# ]

# def test_in_and_exclude_checks():
#     explicit_checks = ["com.google.fonts/check/name/ots", "com.google.fonts/check/monospace"]
#     exclude_checks = ["com.google.fonts/check/glyph_coverage", "com.google.fonts/check/ftxvalidator"]
#     iterargs = {"font": 1}
#     check_names = {
#         c[1].id for c in profile.execution_order(
#             iterargs,
#             explicit_checks=explicit_checks,
#             exclude_checks=exclude_checks)
#     }
#     check_names_expected = set()
#     for section in profile.sections:
#       for check in section.checks:
#         if any(i in check.id for i in explicit_checks) and not any(
#             x in check.id for x in exclude_checks):
#           check_names_expected.add(check.id)
#     assert check_names == check_names_expected

# profile.test_expected_checks(SILFONTS_PROFILE_CHECKS, exclusive=True)
