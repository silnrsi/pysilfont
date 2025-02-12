#!/usr/bin/env python3
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2024-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from sys import argv
from csv import writer as csvwriter
from fontbakery.fonts_profile import profile_factory, get_module

outfilebase = argv[1] if len(argv) == 2 else "checkslist"
checkslist = {}

# First load data for checks from googlefonts profile
profile = profile_factory(get_module("fontbakery.profiles.googlefonts"))
for section in profile.sections:
    for check in section.checks:
        checkslist[check.id] = {
            "section": section.name,
            "description": check.description,
            "rationale": check.rationale,
            "conditions": check.conditions,
            "experimental": check.experimental,
            "adobefonts": "",
            "notofonts": ""}

# Now add in data from other profiles
for profilename in ("adobefonts", "notofonts", "fontwerk", "opentype", "fontbureau", "notofonts", "typenetwork", "microsoft", "iso15008"):
    # Along with googlefonts, these are the profiles used in current ttfchecks.py except that:
    # - not universal, since googlefonts includes universal
    # - not fontval since we exclude the only check in there!
    profile = profile_factory(get_module("fontbakery.profiles." + profilename))

    for section in profile.sections:
        for check in section.checks:
            if check.id in checkslist:
                checkslist[check.id][profilename] = section.name
            else:
                checkslist[check.id] = {
                    "section": "",
                    "description": check.description,
                    "rationale": check.rationale,
                    "conditions": check.conditions,
                    "experimental": check.experimental,
                    "adobefonts": "",
                    "notofonts": ""
                }
                checkslist[check.id][profilename] = section.name

# Columns to output in addition to checkid
columnslist = ["section", "conditions", "experimental", "adobefonts", "notofonts"]

with open(outfilebase + "_full.csv", "w", encoding="utf-8") as outfilefull:
    with open(outfilebase + ".csv", "w", encoding="utf-8") as outfile:
        fullwriter = csvwriter(outfilefull)
        writer = csvwriter(outfile)
        fullwriter.writerow(["checkid"] + columnslist)
        writer.writerow(["checkid"] + columnslist)
        for checkid in sorted(checkslist):
            checkinfo = checkslist[checkid]
            row = [checkid] + [str(checkinfo[col]) for col in columnslist]
            fullwriter.writerow(row)
            # Exclude certain batches of checks
            #if checkinfo["section"] in ["Description Checks", "Metadata Checks", "Repository Checks", "UFO Sources"]: continue
            if checkinfo["section"] in [""]: continue
            if "is_variable_font" in checkinfo["conditions"]: continue
            if "has_STAT_table" in checkinfo["conditions"]: continue
            if "has_ital_axis" in checkinfo["conditions"]:  continue
            writer.writerow(row)

print("Exported cvs files: full list and selection")




