#!/usr/bin/env python
''' For running local tests, assuming setuplocalufotests.py has been run
The copy in pysilfont/tests should never be run.  setuplocalufotests makes a copy in local/tests and renames it to
test_localufos so that "pytest local" or "pytest local/ufotests" will find and run it
It assumes setuplocalufotests had run cleanly, so minimal checking for validity of csv file
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, csvreader
import silfont.util as UT
import silfont.scripts.psfnormalize as psfnormalize
import os, sys, shutil, glob, io


# Open config file
cfg = csvreader("local/ufotests/ufolist.csv")
cfg.numfields=4

# Clear out any previous results
resultsdir = "local/ufotests/results/"
if os.path.isdir(resultsdir):
    shutil.rmtree(resultsdir)
os.makedirs(resultsdir)

ufolist = []
for line in cfg: ufolist.append(line)

def test_normalize():
    allclear = True

    for (ufo, ufoname, errorcount, warningcount) in ufolist:
        cl = " ".join(["psfnormalize", ufo, "-l", resultsdir + ufoname + ".log", "-q", "-p", "checkfix=fix"])
        result = UT.test_run("UFO", cl, psfnormalize, resultsdir + ufoname + ".ufo", int(errorcount), int(warningcount))
        if not result:
            print("The above issues were with normalizing " + ufo)
            allclear = False

    assert allclear

def test_diffs():
    allclear = True

    for line in ufolist:
        ufoname = line[1]
        diff = UT.ufo_diff(resultsdir + ufoname + ".ufo", "local/ufotests/reference/" + ufoname + ".ufo")
        if diff.returncode:
            allclear = False
            diff.print_text()
        diff = UT.text_diff(resultsdir + ufoname + ".log", "local/ufotests/reference/" + ufoname + ".log", ignore_chars=20)
        if diff.returncode:
            allclear = False
            diff.print_text()

    assert allclear

if __name__ == "__main__":
    test_normalize()
    test_diffs()
