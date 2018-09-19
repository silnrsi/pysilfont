#!/usr/bin/env python
''' Test of script named in testname below
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import silfont.util
import sys, os, glob, subprocess
from silfont.core import execute
import silfont.scripts.psfsyncmasters as psfsyncmasters

def test_run():
    cl = "psfsyncmasters -n tests/input/font-psf-test/source/PsfTestRoman.designspace " \
         "tests/input/font-psf-test/source/PsfTestItalic.designspace -l local/testresults/ufo/psfsyncmasters.log"
    sys.argv = cl.split(" ")
    (args, font) = execute("UFO", psfsyncmasters.doit, psfsyncmasters.argspec, chain="first")
    args.logger.logfile.close()
    exp_counts = (0, 6)
    actual_counts = (args.logger.errorcount, args.logger.warningcount)
    if exp_counts == actual_counts:
        assert True
    else:
        print("Mis-match of logger errors/warnings: " + str(exp_counts) + " vs " + str(actual_counts))
        assert False

def test_diffs(): # Do a diff on all output files
    result = True
    sourcedir = "tests/input/font-psf-test/source/"
    refdir = "tests/reference/ufo/"
    resdir = "local/testresults/ufo/"
    # -n in commands will have created _new versions of changed files in the source directory,
    # so move them to results prior to dunning diff commands
    for f in glob.glob(resdir + "psfsyncmasters*.plist"): os.remove(f) # Delete any old results
    filelist = []
    for style in ("Regular", "Italic", "Bold", "BoldItalic"):
        ufodir = sourcedir + "PsfTest-" + style + ".ufo/"
        for f in glob.glob(ufodir + "*_new.plist"):
            (dir,filen) = os.path.split(f)
            filen = "fontinfo.plist" if filen[0] == "f" else "lib.plist"
            filen = style + "-" + filen
            filelist.append(filen)
            os.rename(f, resdir + "psfsyncmasters-" + filen )
    filelist.sort()
    expectedlist = ['Bold-fontinfo.plist', 'Bold-lib.plist', 'BoldItalic-fontinfo.plist', 'Italic-fontinfo.plist']
    if filelist != expectedlist:
        print("None-standard output files: \n" + str(filelist))
        print("Expected: \n" + str(expectedlist))
        result = False
    for f in filelist:
        # Need to diff the plists with subprocess("diff") to be able handle openTypeHeadCreated issue
        filen = "psfsyncmasters-" + f
        diff = subprocess.Popen(["diff", resdir +filen, refdir + filen, "-c1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = diff.communicate()
        if diff.returncode == 1:
            difftext = text[0].decode("utf-8").split("\n")
            # Need to rule out only change being openTypeHeadCreated (which should be the case for fontinfo)
            if not(difftext[4].strip() == "<key>openTypeHeadCreated</key>" and len(difftext) == 12):
                print(filen + " different from reference")
                for line in difftext: print(line)
                result = False

    diff = silfont.util.text_diff(resdir + "psfsyncmasters.log", refdir + "psfsyncmasters.log", ignore_chars=20)
    if diff.returncode:
        diff.print_text()
        result = False

    assert result

if __name__ == "__main__":
    test_run()
    test_diffs()