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
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'psfrunfbprofile.log'})]

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

    # Create the profile object
    if args.profile:
        proname = args.profile
    else:
        if fontstype == "ttf":
            proname = "silfont.fbtests.ttfchecks"
        else:
            logger.log("UFO fonts not yet supported", "S")

    imported = get_module(proname)
    profile = get_module_profile(imported)

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
    totals = results["result"]
    sections = results["sections"]

    checks = {}
    maxname = 11
    somedebug = False

    for section in sections:
        secchecks = section["checks"]
        for check in secchecks:
            fontfile = check["filename"] if "filename" in check else "Family-wide"
            if fontfile not in checks:
                checks[fontfile] = {"ERROR": [], "FAIL": [], "WARN": [], "INFO": [], "SKIP": [], "PASS": [], "DEBUG": []}
                path, name = os.path.split(fontfile)
                checks[fontfile]["name"]=name
                if len(name) > maxname: maxname = len(name)
            status = check["logs"][0]["status"]
            checks[fontfile][status].append(check)
            if status == "DEBUG": somedebug = True

    if htmlfile:
        logger.log("Writing results to " + htmlfile, "P")
        with open(htmlfile, 'w') as hfile:
            hfile.write(hr.get_html())

    fbstats   = ["ERROR", "FAIL", "WARN", "INFO", "SKIP", "PASS"]
    psflevels = ["E",     "W",    "W",    "I",    "I",    "V"]
    if somedebug: # Only have debug column if some degus statuses are present
        fbstats.append("DEBUG")
        psflevels.append("W")
    wrapper = TextWrapper(width=120, initial_indent="   ", subsequent_indent="   ")
    errorcnt = 0
    summarymess = "Check status summary:\n"
    summarymess += "{:{pad}}ERROR  FAIL  WARN  INFO  SKIP  PASS".format("", pad=maxname+4)
    if somedebug: summarymess += "  DEBUG"
    fontlist = list(sorted(x for x in checks if x != "Family-wide")) + ["Family-wide"] # Sort with Family-wide last
    for fontfile in fontlist:
        summarymess += "\n  {:{pad}}".format(checks[fontfile]["name"], pad=maxname)
        for i, status in enumerate(fbstats):
            psflevel = psflevels[i]
            checklist = checks[fontfile][status]
            cnt = len(checklist)
            if cnt > 0 or status != "DEBUG": summarymess += "{:6d}".format(cnt) # Suppress 0 for DEBUG
            if cnt:
                if status == "ERROR": errorcnt += cnt
                messparts = ["Checks with status {} for {}".format(status, checks[fontfile]["name"])]
                for check in checklist:
                    messparts.append(" > {}".format(check["key"][1][17:-1]))
                    messparts += wrapper.wrap(check["logs"][0]["message"])
                logger.log("\n".join(messparts) , psflevel)
    logger.log(summarymess, "P")
    if errorcnt > 0:
        mess = str(errorcnt) + " test" if errorcnt == 1 else str(errorcnt) + " tests"
        logger.log(mess + " failed to run.  This probably indicates a software issue rather than font issue", "S")

def cmd(): execute(None, doit, argspec)
if __name__ == "__main__": cmd()
