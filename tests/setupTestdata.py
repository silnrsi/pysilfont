#!/usr/bin/env python

import os, sys, shutil, glob

# Check being run in pysilfont root directory
cwd = os.getcwd()
if os.path.split(cwd)[1] != "pysilfont":
    print("setupTestdata must be run in pysilfont root directory")
    sys.exit(1)

resultsdir = os.path.join("local", "testresults")
oldresultsdir = os.path.join("local", "oldtestresults")

if os.path.isdir(resultsdir):
    if os.path.isdir(oldresultsdir): shutil.rmtree(oldresultsdir)
    os.rename(resultsdir, oldresultsdir)
os.makedirs(resultsdir)

# Copy standard UFO results across so that the log files consistently say:
#   "Progress: Output UFO already exists - reading for comparison"

ufos = glob.iglob(os.path.join("tests", "reference", "ufo", "*.ufo"))
for ufo in ufos:
    (base, ufoname) = os.path.split(ufo)
    resultufo = os.path.join(resultsdir, "ufo", ufoname)
    shutil.copytree(ufo, resultufo)

