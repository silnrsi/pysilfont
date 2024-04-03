"""
SIL checks <https://software.sil.org/fonts/>
for version 0.12.X (and not just for ttfs)
"""
# pylint: disable=line-too-long  # This is data, not code

from fontbakery.prelude import (
    check,
    condition,
    disable,
    ERROR,
    SKIP,
    PASS,
    FAIL,
    FATAL,
    INFO,
    WARN,
    DEBUG,
)
from fontbakery.message import Message
from fontbakery.utils import exit_with_install_instructions
from fontbakery.constants import NameID, PlatformID, WindowsEncodingID, FsSelection
from fontbakery.testable import CheckRunContext, Font


@check(
    id="org.sil/check/name/version_format",
    rationale="""
        Based on com.google.fonts/check/name/version_format but:
        - Checks for two valid formats:
        - Production: exactly 3 digits after decimal point


        - Allows major version to be 0
        - Allows extra info after numbers, eg for beta or dev versions
  """,
)
def org_sil_version_format(ttFont):
    "Version format is correct in 'name' table?"

    from fontbakery.utils import get_name_entry_strings
    import re

    failed = False
    version_entries = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    if len(version_entries) == 0:
        failed = True
        yield FAIL, Message(
            "no-version-string",
            f"Font lacks a NameID.VERSION_STRING"
            f" (nameID={NameID.VERSION_STRING}) entry",
        )

    for ventry in version_entries:
        if not re.match(r"Version [0-9]+\.\d{3}( .+)*$", ventry):
            failed = True
            yield FAIL, Message(
                "bad-version-strings",
                f"The NameID.VERSION_STRING"
                f" (nameID={NameID.VERSION_STRING}) value must"
                f' follow the pattern "Version X.nnn devstring" with X.nnn'
                f" greater than or equal to 0.000."
                f' Current version string is: "{ventry}"',
            )
    if not failed:
        yield PASS, "Version format in NAME table entries is correct."


@check(id="org.sil/check/whitespace_widths")
def org_sil_whitespace_widths(ttFont):
    """Checks with widths of space characters in the font against best practice"""
    from fontbakery.utils import get_glyph_name

    allok = True
    space_data = {
        0x0020: ["Space"],
        0x00A0: ["No-break space"],
        0x2008: ["Punctuation space"],
        0x2003: ["Em space"],
        0x2002: ["En space"],
        0x2000: ["En quad"],
        0x2001: ["Em quad"],
        0x2004: ["Three-per-em space"],
        0x2005: ["Four-per-em space"],
        0x2006: ["Six-per-em space"],
        0x2009: ["Thin space"],
        0x200A: ["Hair space"],
        0x202F: ["Narrow no-break space"],
        0x002E: [
            "Full stop"
        ],  # Non-space character where the width is needed for comparison
    }
    for sp in space_data:
        spname = get_glyph_name(ttFont, sp)
        if spname is None:
            spwidth = None
        else:
            spwidth = ttFont["hmtx"][spname][0]
        space_data[sp].append(spname)
        space_data[sp].append(spwidth)

    # Other width info needed from the font
    upm = ttFont["head"].unitsPerEm
    fullstopw = space_data[46][2]

    # Widths used for comparisons
    spw = space_data[32][2]
    if spw is None:
        allok = False
        yield WARN, "No space in the font so No-break space (if present) can't be checked"
    emw = space_data[0x2003][2]
    if emw is None:
        allok = False
        yield WARN, f"No em space in the font. Will be assumed to be units per em ({upm}) for other checking"
        emw = upm
    enw = space_data[0x2002][2]
    if enw is None:
        allok = False
        yield WARN, f"No en space in the font. Will be assumed to be 1/2 em space width ({emw/2}) for checking en quad (if present)"
        enw = emw / 2

    # Now check all the specific space widths.  Only check if the space exists in the font
    def checkspace(spacechar, minwidth, maxwidth=None):
        sdata = space_data[spacechar]
        if sdata[1]:  # Name is set to None if not in font
            # Allow for width(s) not being integer (eg em/6) so test against rounding up or down
            minw = int(minwidth)
            if maxwidth:
                maxw = int(maxwidth)
                if maxwidth > maxw:
                    maxw += 1  # Had been rounded down, so round up
            else:
                maxw = (
                    minw if minw == minwidth else minw + 1
                )  # Had been rounded down, so allow rounded up as well
            charw = sdata[2]
            if not minw <= charw <= maxw:
                return (
                    f"Width of {sdata[0]} ({spacechar:#04x}) is {str(charw)}: ",
                    minw,
                    maxw,
                )
        return (None, 0, 0)

    # No-break space
    (message, minw, maxw) = checkspace(0x00A0, spw)
    if message:
        allok = False
        yield FAIL, message + f"Should match width of space ({spw})"
    # Punctuation space
    (message, minw, maxw) = checkspace(0x2008, fullstopw)
    if message:
        allok = False
        yield FAIL, message + f"Should match width of full stop ({fullstopw})"
    # Em space
    (message, minw, maxw) = checkspace(0x2003, upm)
    if message:
        allok = False
        yield WARN, message + f"Should match units per em ({upm})"
    # En space
    (message, minw, maxw) = checkspace(0x2002, emw / 2)
    if message:
        allok = False
        widths = f"{minw}" if minw == maxw else f"{minw} or {maxw}"
        yield WARN, message + f"Should be half the width of em ({widths})"
    # En quad
    (message, minw, maxw) = checkspace(0x2000, enw)
    if message:
        allok = False
        yield WARN, message + f"Should be the same width as en ({enw})"
    # Em quad
    (message, minw, maxw) = checkspace(0x2001, emw)
    if message:
        allok = False
        yield WARN, message + f"Should be the same width as em ({emw})"
    # Three-per-em space
    (message, minw, maxw) = checkspace(0x2004, emw / 3)
    if message:
        allok = False
        widths = f"{minw}" if minw == maxw else f"{minw} or {maxw}"
        yield WARN, message + f"Should be 1/3 the width of em ({widths})"
    # Four-per-em space
    (message, minw, maxw) = checkspace(0x2005, emw / 4)
    if message:
        allok = False
        widths = f"{minw}" if minw == maxw else f"{minw} or {maxw}"
        yield WARN, message + f"Should be 1/4 the width of em ({widths})"
    # Six-per-em space
    (message, minw, maxw) = checkspace(0x2006, emw / 6)
    if message:
        allok = False
        widths = f"{minw}" if minw == maxw else f"{minw} or {maxw}"
        yield WARN, message + f"Should be 1/6 the width of em ({widths})"
    # Thin space
    (message, minw, maxw) = checkspace(0x2009, emw / 6, emw / 5)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/6 and 1/5 the width of em ({minw} and {maxw})"
    # Hair space
    (message, minw, maxw) = checkspace(0x200A, emw / 16, emw / 10)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/16 and 1/10 the width of em ({minw} and {maxw})"
    # Narrow no-break space
    (message, minw, maxw) = checkspace(0x202F, emw / 6, emw / 5)
    if message:
        allok = False
        yield WARN, message + f"Should be between 1/6 and 1/5 the width of em ({minw} and {maxw})"

    if allok:
        yield PASS, "Space widths all match expected values"


@check(id="org.sil/check/number_widths")
def org_sil_number_widths(ttFont, config):
    """Check widths of latin digits 0-9 are equal and match that of figure space"""
    from fontbakery.utils import get_glyph_name

    num_data = {
        0x0030: ["zero"],
        0x0031: ["one"],
        0x0032: ["two"],
        0x0033: ["three"],
        0x0034: ["four"],
        0x0035: ["five"],
        0x0036: ["six"],
        0x0037: ["seven"],
        0x0038: ["eight"],
        0x0039: ["nine"],
        0x2007: ["figurespace"],  # Figure space should be the same as numerals
    }

    fontnames = []
    for x in (ttFont["name"].names[1].string, ttFont["name"].names[2].string):
        txt = ""
        for i in range(1, len(x), 2):
            txt += x.decode()[i]
        fontnames.append(txt)

    for num in num_data:
        name = get_glyph_name(ttFont, num)
        if name is None:
            width = -1  # So different from Zero!
        else:
            width = ttFont["hmtx"][name][0]
        num_data[num].append(name)
        num_data[num].append(width)

    zerowidth = num_data[48][2]
    if zerowidth == -1:
        yield FAIL, "No zero in font - remainder of check not run"
        return

    # Check non-zero digits are present and have same width as zero
    digitsdiff = ""
    digitsmissing = ""
    for i in range(49, 58):
        ndata = num_data[i]
        width = ndata[2]
        if width != zerowidth:
            if width == -1:
                digitsmissing += ndata[1] + " "
            else:
                digitsdiff += ndata[1] + " "

    # Check figure space
    figuremess = ""
    ndata = num_data[0x2007]
    width = ndata[2]
    if width != zerowidth:
        if width == -1:
            figuremess = "No figure space in font"
        else:
            figuremess = f"The width of figure space ({ndata[1]}) does not match the width of zero"
    if digitsmissing or digitsdiff or figuremess:
        if digitsmissing:
            yield FAIL, f"Digits missing: {digitsmissing}"
        if digitsdiff:
            yield WARN, f"Digits with different width from Zero: {digitsdiff}"
        if figuremess:
            yield WARN, figuremess
    else:
        yield PASS, "All number widths are OK"
