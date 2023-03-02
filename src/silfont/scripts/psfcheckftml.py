#!/usr/bin/env python
'''Test structural integrity of one or more ftml files

Assumes ftml files have already validated against FTML.dtd, for example by using:
   xmllint --noout --dtdvalid FTML.dtd inftml.ftml

Verifies that:
  - silfont.ftml can parse the file
  - every stylename is defined the <styles> list '''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

import glob
from silfont.ftml import Fxml, Ftest
from silfont.core import execute

argspec = [
    ('inftml', {'help': 'Input ftml filename pattern (default: *.ftml) ', 'nargs' : '?', 'default' : '*.ftml'}, {}),
]

def doit(args):
    logger = args.logger
    fnames = glob.glob(args.inftml)
    if len(fnames) == 0:
        logger.log(f'No files matching "{args.inftml}" found.','E')
    for fname in glob.glob(args.inftml):
        logger.log(f'checking {fname}', 'P')
        unknownStyles = set()
        usedStyles = set()

        # recursively find and check all <test> elements in a <testsgroup>
        def checktestgroup(testgroup):
            for test in testgroup.tests:
                # Not sure why, but sub-testgroups are also included in tests, so filter those out for now
                if isinstance(test, Ftest) and test.stylename:
                    sname = test.stylename
                    usedStyles.add(sname)
                    if sname is not None and sname not in unknownStyles and \
                            not (hasStyles and sname in ftml.head.styles):
                        logger.log(f'  stylename "{sname}" not defined in head/styles', 'E')
                        unknownStyles.add(sname)
            # recurse to nested testgroups if any:
            if testgroup.testgroups is not None:
               for subgroup in testgroup.testgroups:
                   checktestgroup(subgroup)

        with open(fname,encoding='utf8') as f:
            # Attempt to parse the ftml file
            ftml = Fxml(f)
            hasStyles = ftml.head.styles is not None  # Whether or not any styles are defined in head element

            # Look through all tests for undefined styles:
            for testgroup in ftml.testgroups:
                checktestgroup(testgroup)

            if hasStyles:
                # look for unused styles:
                for style in ftml.head.styles:
                    if style not in usedStyles:
                        logger.log(f'  defined style "{style}" not used in any test', 'W')

def cmd() : execute(None,doit, argspec)
if __name__ == "__main__": cmd()
