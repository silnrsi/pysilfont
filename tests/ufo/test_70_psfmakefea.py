#!/usr/bin/env python
'Test for psfmakefea'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

import silfont.util
import pytest

# Next 5 lines of code are test-specific
import silfont.scripts.psfmakefea as testcommand
testname = "psfmakefea"
cl = "psfmakefea -i {} -o {}"
outfont = None
diffexts = [".ttf", ".log"]
exp_errors = 0   # These may need updating if the test ufo is updated
exp_warnings = 0 # The test ufo should have some errors/warnings to test the code!

# Code after this can be the same for most tests; if needed to be different for a test remove this comment!

@pytest.mark.parametrize("prefix",
    ["test1"])
def test_run(prefix):
    infile = os.path.join("..", "fea", prefix+"_in.feax")
    outfile = os.path.join("local", "testresults", prefix+".fea")
    reffile = os.path.join("..", "fea", prefix+"_ref.fea")
    c = cl.format(infile, outfile)
    result = silfont.util.test_run("UFO", cl, testcommand, outfont, exp_errors, exp_warnings)
    assert result
    diff = silfont.util.text_diff(infile, reffile)
    if diff.returncode:
        diff.print_text()
        assert(False)




