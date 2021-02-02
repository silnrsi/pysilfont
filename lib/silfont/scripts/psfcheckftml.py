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
from silfont.ftml import Fxml
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
        with open(fname,encoding='utf8') as f:
            ftml = Fxml(f)
            for testgroup in ftml.testgroups:
                for test in testgroup.tests:
                    if test.stylename:
                        sname = test.stylename
                        if sname is not None and sname not in ftml.head.styles and sname not in unknownStyles:
                            logger.log(f'    stylename "{test.stylename}" not found in head/styles', 'E')
                            unknownStyles.add(sname)

def cmd() : execute(None,doit, argspec)
if __name__ == "__main__": cmd()