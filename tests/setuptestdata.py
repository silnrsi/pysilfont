#!/usr/bin/env python
''' Setup the test environment
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import os, sys, shutil, glob, io

# Check being run in pysilfont root directory
cwd = os.getcwd()
if os.path.split(cwd)[1] != "pysilfont":
    print("setupTestdata must be run in pysilfont root directory")
    sys.exit(1)

resultsdir = "local/testresults/"
oldresultsdir = "local/oldtestresults/"

if os.path.isdir(resultsdir):
    if os.path.isdir(oldresultsdir): shutil.rmtree(oldresultsdir)
    os.rename(resultsdir, oldresultsdir)
os.makedirs(resultsdir)
os.makedirs("local/testresults/ufo/psfglyphs2ufo")

# Copy standard UFO results across so that the log files consistently say:
#   "Progress: Output UFO already exists - reading for comparison"

ufos = glob.iglob("tests/reference/ufo/*.ufo")
for ufo in ufos:
    (base, ufoname) = os.path.split(ufo)
    resultufo = os.path.join(resultsdir, "ufo", ufoname)
    shutil.copytree(ufo, resultufo)

# Create reference log files from .lg files
for name in os.listdir("tests/reference/"):
    fulldir = "tests/reference/" + name
    if os.path.isdir(fulldir):
        for filen in os.listdir(fulldir):
            (base,ext) = os.path.splitext(filen)
            if ext == ".lg":
                inlog = io.open(os.path.join(fulldir, filen), mode="r", encoding="utf-8")
                outlog = io.open(os.path.join(fulldir, base + ".log"), mode="w", encoding="utf-8")
                for line in inlog:
                    line = line.replace("@cwd@", cwd)  # Replace placeholder with machine-specific cwd
                    outlog.write(line)
