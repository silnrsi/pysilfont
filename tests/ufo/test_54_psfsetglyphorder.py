#!/usr/bin/env python
''' Test of script named in testname below
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import silfont.util

# Next 7 lines of code may be test-specific
import silfont.scripts.psfsetglyphorder as testcommand
testname = "psfsetglyphorder"
cl = "psfsetglyphorder tests/input/font-psf-test/source/PsfTest-Italic.ufo -i tests/input/glyph_data.csv -l local/testresults/ufo/psfsetglyphorder.log -p loglevel=i"
outfont = "local/testresults/ufo/psfsetglyphorder.ufo" # Set to None for commands which don't output a font
diffexts = [".ufo", ".log"] # List of extensions of all output files
exp_errors = 0   # These may need updating if the test ufo is updated
exp_warnings = 7 # The test ufo should have some errors/warnings to test the code!

# Code after this can be the same for most/all tests; if needed to be different for a test remove this comment!

def test_run():
    result = silfont.util.test_run("UFO", cl, testcommand, outfont, exp_errors, exp_warnings)
    assert result

def test_diffs(): # Do a diff on all output files
    result = silfont.util.test_diffs("ufo", testname, diffexts)
    assert result

if __name__ == "__main__":
    test_run()
    test_diffs()





