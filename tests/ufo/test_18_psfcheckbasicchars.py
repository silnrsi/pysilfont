#!/usr/bin/env python
'Test for psfcheckbasicchars'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import silfont.util

# Next 5 lines of code are test-specific
import silfont.scripts.psfcheckbasicchars as testcommand
testname = "psfcheckbasicchars"
cl = "psfcheckbasicchars tests/input/ufo/test.ufo -l local/testresults/ufo/psfcheckbasicchars.lg"
outfont = None
diffexts = [".lg"]
exp_errors = 0   # These may need updating if test.ufo is updated
exp_warnings = 271 # test.ufo should have some errors/warnings to test the code!

# Code after this can be the same for most tests; if needed to be different for a test remove this comment!

def test_run():
    result = silfont.util.test_run("UFO", cl, testcommand, outfont, exp_errors, exp_warnings)
    assert result

def test_diffs(): # Generic function for all UFO tests
    result = silfont.util.test_diffs("ufo", testname, diffexts)
    assert result

if __name__ == "__main__":
    test_run()
    test_diffs()




