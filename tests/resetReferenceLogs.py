#!/usr/bin/env python
''' Reset the reference log files following changes to tests
Works on one test group at a time.
Copies the results logs to reference .lg files, replacing making file paths generic.
setupTestdata.py then generates correct log files from .lg files
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import os, sys, shutil, glob, io

# Check being run in pysilfont root directory
cwd = os.getcwd()
if os.path.split(cwd)[1] != "pysilfont":
    print("resetReferenceLogs must be run in pysilfont root directory")
    sys.exit(1)

if len(sys.argv) != 2:
    print("Usage: resetReferenceLogs testgroupname")
    sys.exit()

testgroup = sys.argv[1]

if testgroup not in ("ufo"):
    print("Invalid test group")
    sys.exit()

logsdir = "local/testresults/" + testgroup + "/"
refdir = "tests/reference/" + testgroup + "/"

if not os.path.isdir(logsdir):
    print(logsdir + " does not exist")
    sys.exit()


# Read the new log files and create new .lg files from them
logs = glob.iglob(logsdir + "*.log")
for log in logs:
    inlog = io.open(log, mode="r", encoding="utf-8")
    testn = os.path.splitext(os.path.split(log)[1])[0]
    outn = refdir + testn + ".lg"
    outlog = io.open(outn, mode="w", encoding="utf-8")
    for line in inlog:
        line = line.replace(cwd, "@cwd@") # Replace machine-specific cwd with placeholder
        line = line.replace("\\","/") # Replace Windows \ with /
        outlog.write(line)
    print(outn +" recreated")
