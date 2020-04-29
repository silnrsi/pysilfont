#!/usr/bin/env python
'''Run Font Bakery tests using a standard profile with option to specify an alternative profile
It defaults to ttfchecks.py - ufo checks are not supported yet'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import json, sys, glob, os

from textwrap import TextWrapper

from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.reporters.html import HTMLReporter
from fontbakery.checkrunner import distribute_generator, CheckRunner, get_module_profile, SKIP
from fontbakery.commands.check_profile import get_module

from silfont.core import execute

argspec = [
    ('fonts',{'help': 'font(s) to run checks against; wildcards allowed', 'nargs': "+"}, {'type': 'filename'}),
    ('--profile', {'help': 'profile to use instead of Pysilfont default'}, {}),
    ('--html', {'help': 'Write html report to htmlfile', 'metavar': "HTMLFILE"}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_runfbchecks.log'})]

def doit(args):

    logger = args.logger
    htmlfile = args.html

    # Process list of fonts supplied, expanding wildcards using glob if needed
    fonts = []
    fontstype = None
    for pattern in args.fonts:
        for fullpath in glob.glob(pattern):
            ftype = fullpath.lower().rsplit(".", 1)[-1]
            if ftype == "otf": ftype = "ttf"
            if ftype not in ("ttf", "ufo"):
                logger.log("Fonts must be OpenType or UFO - " + fullpath + " invalid", "S")
            if fontstype is None:
                fontstype = ftype
            else:
                if ftype != fontstype:
                    logger.log("All fonts must be of the same type - both UFO and ttf/otf fonts supplied", "S")
            fonts.append(fullpath)

    if fonts == [] : logger.log("No files match the filespec provided for fonts: " + str(args.fonts), "S")

    # Create the profile object
    if args.profile:
        proname = args.profile
    else:
        if fontstype == "ttf":
            proname = "silfont.fbtests.ttfchecks"
        else:
            logger.log("UFO fonts not yet supported", "S")

    try:
        module = get_module(proname)
    except Exception as e:
        logger.log("Failed to import profile: " + proname + "\n" + str(e), "S")
    
    profile = get_module_profile(module)
    psfcheck_list = module.psfcheck_list

    # Create the runner and reporter objetcs, then run the tests
    runner = CheckRunner(profile, values={"fonts": fonts})

    sr = SerializeReporter(runner=runner) # This produces results from all the tests in sr.getdoc for later analysis
    reporters = [sr.receive]

    if htmlfile:
        hr = HTMLReporter(runner=runner, loglevels = [SKIP])
        reporters.append(hr.receive)

    distribute_generator(runner.run(), reporters)

    # Process the results
    results = sr.getdoc()
    sections = results["sections"]

    checks = {}
    maxname = 11
    somedebug = False
    overrides = {}
    tempoverrides = False

    for section in sections:
        secchecks = section["checks"]
        for check in secchecks:
            checkid = check["key"][1][17:-1]
            fontfile = check["filename"] if "filename" in check else "Family-wide"
            path, fontname = os.path.split(fontfile)
            if fontname not in checks:
                checks[fontname] = {"ERROR": [], "FAIL": [], "WARN": [], "INFO": [], "SKIP": [], "PASS": [], "DEBUG": []}
                if len(fontname) > maxname: maxname = len(fontname)
            status = check["logs"][0]["status"]
            if checkid in psfcheck_list:
                # Look for status overrides
                (changetype, temp) = ("temp_change_status", True) if "temp_change_status" in psfcheck_list[checkid]\
                    else ("change_status", False)
                if changetype in psfcheck_list[checkid]:
                    change_status = psfcheck_list[checkid][changetype]
                    if status in change_status:
                        reason = change_status["reason"] if "reason" in change_status else None
                        overrides[fontname + ", " + checkid] = (status + " to " + change_status[status], temp, reason)
                        if temp: tempoverrides = True
                        status = change_status[status]
            checks[fontname][status].append(check)
            if status == "DEBUG": somedebug = True

    if htmlfile:
        logger.log("Writing results to " + htmlfile, "P")
        with open(htmlfile, 'w') as hfile:
            hfile.write(hr.get_html())

    fbstats   = ["ERROR", "FAIL", "WARN", "INFO", "SKIP", "PASS"]
    psflevels = ["E",     "E",    "W",    "I",    "I",    "V"]
    if somedebug: # Only have debug column if some debug statuses are present
        fbstats.append("DEBUG")
        psflevels.append("W")
    wrapper = TextWrapper(width=120, initial_indent="   ", subsequent_indent="   ")
    errorcnt = 0
    failcnt = 0
    summarymess = "Check status summary:\n"
    summarymess += "{:{pad}}ERROR  FAIL  WARN  INFO  SKIP  PASS".format("", pad=maxname+4)
    if somedebug: summarymess += "  DEBUG"
    fontlist = list(sorted(x for x in checks if x != "Family-wide")) + ["Family-wide"] # Sort with Family-wide last
    for fontname in fontlist:
        summarymess += "\n  {:{pad}}".format(fontname, pad=maxname)
        for i, status in enumerate(fbstats):
            psflevel = psflevels[i]
            checklist = checks[fontname][status]
            cnt = len(checklist)
            if cnt > 0 or status != "DEBUG": summarymess += "{:6d}".format(cnt) # Suppress 0 for DEBUG
            if cnt:
                if status == "ERROR": errorcnt += cnt
                if status == "FAIL": failcnt += cnt
                messparts = ["Checks with status {} for {}".format(status, fontname)]
                for check in checklist:
                    messparts.append(" > {}".format(check["key"][1][17:-1]))
                    messparts += wrapper.wrap(check["logs"][0]["message"])
                logger.log("\n".join(messparts) , psflevel)
    if overrides != {}:
        summarymess += "\n  Note: " + str(len(overrides)) + " Fontbakery statuses were overridden - see log file for details"
        if tempoverrides: summarymess += "\n        ******** Some of the overrides were temporary overrides ********"
    logger.log(summarymess, "P")

    if overrides != {}:
        for oname in overrides:
            override = overrides[oname]
            mess = "Status override for " + oname + ": " + override[0]
            if override[1]: mess += " (Temporary override)"
            logger.log(mess, "W")
            if override[2] is not None: logger.log("Override reason: " + override[2], "I")

    if errorcnt + failcnt > 0:
        mess = str(failcnt) + " test(s) gave a status of FAIL" if failcnt > 0 else ""
        if errorcnt > 0:
            if failcnt > 0: mess += "\n                              "
            mess += str(errorcnt) + " test(s) gave a status of ERROR which means they failed to execute properly." \
                                    "\n                              " \
                                    "   ERROR probably indicates a software issue rather than font issue"
        logger.log(mess, "S")
def cmd(): execute(None, doit, argspec)
if __name__ == "__main__": cmd()