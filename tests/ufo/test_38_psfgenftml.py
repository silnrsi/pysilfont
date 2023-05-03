#!/usr/bin/env python
''' Test of script named in testname below
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

import silfont.util
import silfont.ftml_builder as FB

# There is no one psfgenftml script -- each project will have its own. So here is what we'll use for testing:

class testcommand(object):
    argspec = [
        ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
        ('output',{'help': 'Output file ftml in XML format', 'nargs': '?'}, {'type': 'outfile', 'def': '_out.ftml'}),
        ('-i','--input',{'help': 'Glyph info csv file'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
        ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_ftml.log'}),
    ]

    @staticmethod
    def doit(args):
        logger = args.logger

        # Read input csv
        builder = FB.FTMLBuilder(logger, incsv = args.input, font = args.ifont)

        # Initialize FTML document:
        test = "ftml_builder test"
        ftml = FB.FTML(test, logger)

        # all chars that should be in the font:
        ftml.startTestGroup('Encoded characters')
        for uid in sorted(builder.uids()):
            if uid < 32: continue
            c = builder.char(uid)
            # iterate over all permutations of feature settings that might affect this character:
            for featlist in builder.permuteFeatures(uids = (uid,)):
                ftml.setFeatures(featlist)
                builder.render((uid,), ftml)
                # Test one character with RTL enabled:
                if uid == 67:
                    builder.render((uid,), ftml, rtl = True)
                # Don't close test -- collect consecutive encoded chars in a single row
            ftml.clearFeatures()
            for langID in sorted(c.langs):
                ftml.setLang(langID)
                builder.render((uid,), ftml)
            ftml.clearLang()

        # Write the output ftml file
        ftml.writeFile(args.output)

testname = "psfgenftml"
cl = testname + " -i tests/input/psfgenftml.csv -l local/testresults/ufo/psfgenftml.log " \
     "tests/input/font-psf-test/source/PsfTest-Italic.ufo local/testresults/ufo/psfgenftml.ftml"
outfont = None
diffexts = [".ftml", ".log"]
exp_errors = 0   # These may need updating if the test ufo is updated
exp_warnings = 11 # The test ufo should have some errors/warnings to test the code!

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
