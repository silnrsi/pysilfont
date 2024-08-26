"""
SIL checks <https://software.sil.org/fonts/>
for version 0.12.10+
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
    id="org.sil.software/check/name/version_format",
    rationale="""SIL follows their own versionning scheme,
        Based on com.google.fonts/check/name/version_format but:
        - Checks for two valid formats:
        - Production: exactly 3 digits after decimal point

        - Allows major version to be 0
        - Allows extra info after numbers, eg for beta or dev versions
        """,
    proposal="https://github.com/silnrsi/pysilfont/issues",
)
def org_sil_software_version_format(ttFont):
    "Is the version format correct in the 'name' table?"

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


@check(
    id="org.sil.software/check/whitespace_widths",
    rationale="Whitespace characters must be following best practise",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_whitespace_widths(ttFont):
    """Are widths of whitespace characters in the font best practice?"""
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


@check(
    id="org.sil.software/check/number_widths",
    rationale="Widths of latin digits 0-9 must be equal and match figure space",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_number_widths(ttFont, config):
    """Are widths of latin digits 0-9 equal and match figure space"""
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


@check(
    id='org.sil.software/check/FONTLOG',
    rationale="Although optional, we recommend you have a FONTLOG.txt file in your font project",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_fontlog(family_directory):
    """Is the FONTLOG.txt file present?"""

    import os
    parent_path = os.path.abspath(os.path.join(family_directory, os.pardir))
    fontlog_file = os.path.join(parent_path, "FONTLOG.txt")
    if not os.path.exists(fontlog_file):
        yield WARN, Message(
                "fontlog-missing",
                "Although optional, we recommend you include it in your project. Get a template from https://openfontlicense.org",
        )
    else:
        yield PASS, Message("ok", "FONTLOG.txt is present.")


@check(
    id="org.sil.software/check/is_OFL_FAQ_present_and_current",
    rationale="Although optional, we recommend to have the current version of the OFL-FAQ in your font project",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_check_is_ofl_faq_present_and_current(family_directory):
    """Is OFL-FAQ.txt present and current?"""

    import os
    parent_path = os.path.abspath(os.path.join(family_directory, os.pardir))
    faq_file = os.path.join(parent_path, "OFL-FAQ.txt")
    if not os.path.exists(faq_file):
        yield WARN, Message(
            "OFL-FAQ-missing",
            "Although optional, we recommend you include it in your project. Get the most current version from https://openfontlicense.org",
        )
    else:
        with open(faq_file, 'r', encoding='utf-8') as file:
            data = file.read()
            if "Version 1.1-update7" not in data:
                yield WARN, Message(
                    "OFL-FAQ-old",
                    "The OFL-FAQ file is not the most current version, get the latest 1.1-update7 from November 2023 from https://openfontlicense.org",
                    )
            else:
                yield PASS, Message("ok", "OFL-FAQ.txt is most current version.")


@check(
    id="org.sil.software/check/repo/is_OFL_URL_current",
    rationale="In November 2023 a new OFL website was set up, you should use the new URL but the old one will redirect",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_check_repo_is_ofl_url_current(family_directory):
    """Is the OFL URL current?"""

    import os
    parent_path = os.path.abspath(os.path.join(family_directory, os.pardir))
    ofl_file = os.path.join(parent_path, "OFL.txt")
    with open(ofl_file, 'r', encoding='utf-8') as file:
        data = file.read()
        if "scripts.sil.org/OFL" in data:
            yield WARN, Message(
                    "OFL-URL-old",
                    "Although a redirection is in place, you should use to the new URL instead: https://openfontlicense.org",
                    )
        else:
            yield PASS, Message("ok", "OFL URL is current.")


@check(
    id="org.sil.software/check/repo/executable_bits",
    rationale="Various script files should have the expected execute bits, so they can be ran seperately, text files should not have execute bits",
    proposal="https://github.com/silnrsi/pysilfont/issues",
    )
def org_sil_software_check_repo_unneeded_exe_bits(family_directory):
    """Are all the basic script files executable?"""

    import os
    parent_path = os.path.abspath(os.path.join(family_directory, os.pardir))
    for root, dirs, files in os.walk(parent_path):
        for file in files:
            if file.endswith(".txt"):
                file = os.path.join(root, file)  # get absolute path
                if os.access(file, os.X_OK):
                    yield WARN, Message("text-files-no-need-exec-bits", f"Extra text files found that don't need executable bit set: \n\n({file})")

            if file.startswith("pre") or file.startswith("make"):
                file = os.path.join(root, file)  # get absolute path
                if not os.access(file, os.X_OK):
                    yield WARN, Message("script-files-need-exec-bits", f"Script files found which still need the executable bit set: \n\n({file})")
