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
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
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
    logname = ufoname[:-4] + ".log"
    if not os.path.isdir(ufo):
        print (ufo + " is not a directory")
        continue
    if type == "copy":
        sourcedir = "local/ufotests/source/" + ufoname
        shutil.copytree(ufo, sourcedir)
    elif type == "insitu":
        sourcedir = ufo
    else:
        print("Invalid type '" + type + "' for " + ufo)
        continue

    sys.argv = ["psfnormalize", sourcedir, "-l", "local/ufotests/results/" + logname,  "-q", "-p", "checkfix=fix"]
    print("Normalizing " + sourcedir + " for reference")
    (args, font) = execute("UFO", psfnormalize.doit, psfnormalize.argspec, chain="first")
    font.write("local/ufotests/results/" + ufoname)
    # Move from results to reference - originally written to results to get reference log file correct
    os.rename("local/ufotests/results/" + ufoname, "local/ufotests/reference/" + ufoname)
    os.rename("local/ufotests/results/" + logname, "local/ufotests/reference/" + logname)
    #errorcount = args.logger.errorcount -1 if args.logger.errorcount else 0 # If there is an error, reduce count for extra error reporting that there were errors!
    ufolist.append((sourcedir, ufoname[:-4], str(args.logger.errorcount), str(args.logger.warningcount)))
args.logger.logfile.close() # Make sure final log file is closed

# Create ufolist.csv
ufofile = open("local/ufotests/ufolist.csv", "w")
for line in ufolist:
    ufofile.write(",".join(line) + "\n")

# Copy the main test to local/ufotests
shutil.copy("tests/runlocalufotests.py", "local/ufotests/test_localufos.py")
