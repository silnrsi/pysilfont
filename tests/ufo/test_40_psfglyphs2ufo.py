#!/usr/bin/env python
''' Test of script named in testname below
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import silfont.util
import sys
from silfont.core import execute
import silfont.scripts.psfglyphs2ufo as psfglyphs2ufo
import silfont.scripts.psfnormalize as psfnormalize

def test_run():
    cl = "psfglyphs2ufo --nofea tests/input/font-psf-test/source/PsfTestRoman.glyphs " \
         "local/testresults/ufo/psfglyphs2ufo -l local/testresults/ufo/psfglyphs2ufo.log"
    sys.argv = cl.split(" ")
    (args, font) = execute("UFO", psfglyphs2ufo.doit, psfglyphs2ufo.argspec, chain="first")
    args.logger.logfile.close()
    exp_counts = (1, 0)
    actual_counts = (args.logger.errorcount, args.logger.warningcount)
    # Now normalize the output ufos
    for weight in ("Regular", "Bold"):
        fontname = "local/testresults/ufo/psfglyphs2ufo/PsfTest-" + weight + ".ufo"
        cl = "psfnormalize " + fontname
        sys.argv = cl.split(" ")
        (args, font) = execute("UFO", psfnormalize.doit, psfnormalize.argspec, chain="first")
        font.write(fontname)

    if exp_counts == actual_counts:
        assert True
    else:
        print("Mis-match of logger errors/warnings: " + str(exp_counts) + " vs " + str(actual_counts))
        assert False

def test_diffs(): # Do a diff on all output files
    result = True
    refdir = "tests/reference/ufo/"
    resdir = "local/testresults/ufo/"

    ufodiff = False

    diff = silfont.util.ufo_diff(resdir + "psfglyphs2ufo/PsfTest-Regular.ufo", refdir + "psfglyphs2ufo/PsfTest-Regular.ufo")
    if diff.returncode:
        ufodiff = True
        diff.print_text()
        result = False

    diff = silfont.util.ufo_diff(resdir + "psfglyphs2ufo/PsfTest-Bold.ufo", refdir + "psfglyphs2ufo/PsfTest-Bold.ufo")
    if diff.returncode:
        diff.print_text()
        result = False

    diff = silfont.util.text_diff(resdir + "psfglyphs2ufo.log", refdir + "psfglyphs2ufo.log", ignore_chars=20)
    if diff.returncode:
        diff.print_text()
        result = False

    assert result

if __name__ == "__main__":
    test_run()
    test_diffs()
