#!/usr/bin/env python
''' Setup test based on locally-stored UFOs
Reads from tests/localufos.csv which has format ufopath,type where
- ufopath is the full path to the ufo
- type is either:
  - "copy" to copy the ufo to local/ufotests/source (to protect against future changes to the ufo
  - "insitu" to use the uso from where it is, for ufos unlikely to be changed during a development cycle
It should be run with stable pysilfont code prior to starting development and will create reference copies of the fonts
by normalizing with checkfix=fix
Once setup, "pytest local/ufotests" will again normalize all the fonts listed and compare with the reference fonts
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, csvreader
import silfont.scripts.psfnormalize as psfnormalize
import os, sys, shutil

# Check being run in pysilfont root directory
cwd = os.getcwd()
if os.path.split(cwd)[1] != "pysilfont":
    print("setupTestdata must be run in pysilfont root directory")
    sys.exit(1)

# Open config file
cfg = csvreader("tests/localufos.csv")
cfg.numfields=2

# Clear out any previous data and create directory tree
if os.path.isdir("local/ufotests"): shutil.rmtree("local/ufotests")
for type in ("source", "results", "reference", "logs"): os.makedirs("local/ufotests/" + type)

# Create source (for type=copy) and reference copies of the ufos
ufolist = []
for ufo,type in cfg:
    (path,ufoname) = os.path.split(ufo)
    if not os.path.isdir(ufo):
        print (ufo + "is not a directory")
        continue
    if type == "copy":
        sourcedir = "local/ufotests/source/" + ufoname
        shutil.copytree(ufo, sourcedir)
    elif type == "insitu":
        sourcedir = ufo
    else:
        print("Invlaid type '" + type + "' for " + ufo)
        continue

    sys.argv = ["psfnormalize", sourcedir, "local/ufotests/reference/" + ufoname, "-q", "-p", "checkfix=fix"]
    print("Normalizing " + sourcedir + " for reference")
    (args, font) = execute("UFO", psfnormalize.doit, psfnormalize.argspec)
    ufolist.append((sourcedir, ufoname, str(args.logger.errorcount), str(args.logger.warningcount)))

# Create ufolist.csv
ufofile = open("local/ufotests/ufolist.csv", "w")
for line in ufolist:
    ufofile.write(",".join(line) + "\n")

# Copy the main test to local/ufotests
shutil.copy("tests/runlocalufotests.py", "local/ufotests/test_localufos.py")
