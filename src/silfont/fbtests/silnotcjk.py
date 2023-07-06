#!/usr/bin/env python
'''These are copies of checks that have the "not is_cjk" condition, but these versions have that condition removed.
The is_cjk condition was being matched by multiple fonts that are not cjk fonts - but do have some cjk punctuation characters.
These checks based on based on examples from Font Bakery, copyright 2017 The Font Bakery Authors, licensed under the Apache 2.0 license'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2022 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from fontbakery.status import PASS, FAIL, WARN, ERROR, INFO, SKIP
from fontbakery.callable import condition, check, disable
from fontbakery.message import Message
from fontbakery.profiles.shared_conditions import typo_metrics_enabled
import os
from fontbakery.constants import NameID, PlatformID, WindowsEncodingID

@check(
    id = 'org.sil/check/family/win_ascent_and_descent',
    conditions = ['vmetrics'],
    rationale = """
        Based on com.google.fonts/check/family/win_ascent_and_descent but with the 'not is_cjk' condition removed
    """
)
def org_sil_check_family_win_ascent_and_descent(ttFont, vmetrics):
    """Checking OS/2 usWinAscent & usWinDescent."""

    if "OS/2" not in ttFont:
        yield FAIL,\
              Message("lacks-OS/2",
                      "Font file lacks OS/2 table")
        return

    failed = False
    os2_table = ttFont['OS/2']
    win_ascent = os2_table.usWinAscent
    win_descent = os2_table.usWinDescent
    y_max = vmetrics['ymax']
    y_min = vmetrics['ymin']

    # OS/2 usWinAscent:
    if win_ascent < y_max:
        failed = True
        yield FAIL,\
              Message("ascent",
                      f"OS/2.usWinAscent value should be"
                      f" equal or greater than {y_max},"
                      f" but got {win_ascent} instead")
    if win_ascent > y_max * 2:
        failed = True
        yield FAIL,\
              Message("ascent",
                      f"OS/2.usWinAscent value"
                      f" {win_ascent} is too large."
                      f" It should be less than double the yMax."
                      f" Current yMax value is {y_max}")
    # OS/2 usWinDescent:
    if win_descent < abs(y_min):
        failed = True
        yield FAIL,\
              Message("descent",
                      f"OS/2.usWinDescent value should be equal or"
                      f" greater than {abs(y_min)}, but got"
                      f" {win_descent} instead.")

    if win_descent > abs(y_min) * 2:
        failed = True
        yield FAIL,\
              Message("descent",
                      f"OS/2.usWinDescent value"
                      f" {win_descent} is too large."
                      f" It should be less than double the yMin."
                      f" Current absolute yMin value is {abs(y_min)}")
    if not failed:
        yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"


@check(
    id = 'org.sil/check/os2_metrics_match_hhea',
    rationale="""
            Based on com.google.fonts/check/os2_metrics_match_hhea but with the 'not is_cjk' condition removed
        """
)
def org_sil_check_os2_metrics_match_hhea(ttFont):
    """Checking OS/2 Metrics match hhea Metrics."""

    filename = os.path.basename(ttFont.reader.file.name)

    # Check both OS/2 and hhea are present.
    missing_tables = False

    required = ["OS/2", "hhea"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL,\
                  Message(f'lacks-{key}',
                          f"{filename} lacks a '{key}' table.")

    if missing_tables:
        return

    # OS/2 sTypoAscender and sTypoDescender match hhea ascent and descent
    if ttFont["OS/2"].sTypoAscender != ttFont["hhea"].ascent:
        yield FAIL,\
              Message("ascender",
                      f"OS/2 sTypoAscender ({ttFont['OS/2'].sTypoAscender})"
                      f" and hhea ascent ({ttFont['hhea'].ascent})"
                      f" must be equal.")
    elif ttFont["OS/2"].sTypoDescender != ttFont["hhea"].descent:
        yield FAIL,\
              Message("descender",
                      f"OS/2 sTypoDescender ({ttFont['OS/2'].sTypoDescender})"
                      f" and hhea descent ({ttFont['hhea'].descent})"
                      f" must be equal.")
    elif ttFont["OS/2"].sTypoLineGap != ttFont["hhea"].lineGap:
        yield FAIL,\
              Message("lineGap",
                      f"OS/2 sTypoLineGap ({ttFont['OS/2'].sTypoLineGap})"
                      f" and hhea lineGap ({ttFont['hhea'].lineGap})"
                      f" must be equal.")
    else:
        yield PASS, ("OS/2.sTypoAscender/Descender values"
                     " match hhea.ascent/descent.")

@check(
    id = "org.sil/check/os2/use_typo_metrics",
    rationale="""
            Based on com.google.fonts/check/os2/use_typo_metrics but with the 'not is_cjk' condition removed
        """
    )
def corg_sil_check_os2_fsselectionbit7(ttFonts):
    """OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts."""

    bad_fonts = []
    for ttFont in ttFonts:
        if not ttFont["OS/2"].fsSelection & (1 << 7):
            bad_fonts.append(ttFont.reader.file.name)

    if bad_fonts:
        yield FAIL,\
              Message('missing-os2-fsselection-bit7',
                      f"OS/2.fsSelection bit 7 (USE_TYPO_METRICS) was"
                      f"NOT set in the following fonts: {bad_fonts}.")
    else:
        yield PASS, "OK"


'''@check(
    id = 'org.sil/check/vertical_metrics',
#    conditions = ['not remote_styles'],
    rationale="""
            Based on com.google.fonts/check/vertical_metrics but with the 'not is_cjk' condition removed
        """
)
def org_sil_check_vertical_metrics(ttFont):
    """Check font follows the Google Fonts vertical metric schema"""
    filename = os.path.basename(ttFont.reader.file.name)

    # Check necessary tables are present.
    missing_tables = False
    required = ["OS/2", "hhea", "head"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL,\
                  Message(f'lacks-{key}',
                          f"{filename} lacks a '{key}' table.")

    if missing_tables:
        return

    font_upm = ttFont['head'].unitsPerEm
    font_metrics = {
        'OS/2.sTypoAscender': ttFont['OS/2'].sTypoAscender,
        'OS/2.sTypoDescender': ttFont['OS/2'].sTypoDescender,
        'OS/2.sTypoLineGap': ttFont['OS/2'].sTypoLineGap,
        'hhea.ascent': ttFont['hhea'].ascent,
        'hhea.descent': ttFont['hhea'].descent,
        'hhea.lineGap': ttFont['hhea'].lineGap,
        'OS/2.usWinAscent': ttFont['OS/2'].usWinAscent,
        'OS/2.usWinDescent': ttFont['OS/2'].usWinDescent
    }
    expected_metrics = {
        'OS/2.sTypoLineGap': 0,
        'hhea.lineGap': 0,
    }

    failed = False
    warn = False

    # Check typo metrics and hhea lineGap match our expected values
    for k in expected_metrics:
        if font_metrics[k] != expected_metrics[k]:
            failed = True
            yield FAIL,\
                  Message(f'bad-{k}',
                          f'{k} is "{font_metrics[k]}" it should be {expected_metrics[k]}')

    hhea_sum = (font_metrics['hhea.ascent'] +
                abs(font_metrics['hhea.descent']) +
                font_metrics['hhea.lineGap']) / font_upm

    # Check the sum of the hhea metrics is not below 1.2
    # (120% of upm or 1200 units for 1000 upm font)
    if hhea_sum < 1.2:
        failed = True
        yield FAIL,\
            Message('bad-hhea-range',
                'The sum of hhea.ascender+abs(hhea.descender)+hhea.lineGap '
                f'is {int(hhea_sum*font_upm)} when it should be at least {int(font_upm*1.2)}')

    # Check the sum of the hhea metrics is below 2.0
    elif hhea_sum > 2.0:
        failed = True
        yield FAIL,\
            Message('bad-hhea-range',
                'The sum of hhea.ascender+abs(hhea.descender)+hhea.lineGap '
                f'is {int(hhea_sum*font_upm)} when it should be at most {int(font_upm*2.0)}')

    # Check the sum of the hhea metrics is between 1.1-1.5x of the font's upm
    elif hhea_sum > 1.5:
        warn = True
        yield WARN,\
            Message('bad-hhea-range',
                "We recommend the absolute sum of the hhea metrics should be"
                f" between 1.2-1.5x of the font's upm. This font has {hhea_sum}x ({int(hhea_sum*font_upm)})")

    if not failed and not warn:
        yield PASS, 'Vertical metrics are good'
'''

