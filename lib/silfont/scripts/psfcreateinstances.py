#!/usr/bin/env python
'Generate instance UFO(s) from a designspace document and master UFO(s)'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

#from mutatorMath.ufo.document import DesignSpaceDocumentReader
from mutatorMath.ufo import build as build_designspace
from silfont.core import execute

argspec = [
    ('designspace_path', {'help': 'Path to designspace document or folder of them'}, {}),
    ('--roundInstances', {'help': 'Apply integer rounding to all geometry when interpolating',
                           'action': 'store_true'}, {}),
    ('--progress', {'help': 'Show progress and errors', 'action': 'store_true'}, {})
]

logger = None
def progressFunc(state="update", action=None, text=None, tick=0):
    if logger:
        if (state == 'error'):
            logger.log("%s: %s\n%s" % (state, str(action), str(text)), 'W')
        else:
            logger.log("%s: %s\n%s" % (state, str(action), str(text)), 'P')

def doit(args):
    global logger
    logger = args.logger
    args.logger.log('Interpolating master UFOs from designspace', 'P')

    designspace_path = args.designspace_path
    roundInstances = args.roundInstances
    showProgress = args.progress

    # The below is an alternative implementation
    #  based loosely on fontmake's FontProject.run_from_designspace()
    #   but it always interpolates all instances
    #   and only generates those instances without building ttfs
    #
    # reader = DesignSpaceDocumentReader(designspace_path, ufoVersion=3,
    #                                    roundGeometry=round_instances)
    # reader.readInstances()

    # The below simply uses a utility function that's part of mutatorMath
    #  In addition to accepting a designspace file,
    #   it will accept a folder and processes all designspace files there
    #  It can also produce progress and error messages
    progressFn = progressFunc if showProgress else None
    build_designspace(designspace_path,
                      outputUFOFormatVersion=3, roundGeometry=roundInstances,
                      progressFunc=progressFn)

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()

# For reference:
# 	build() is a convenience function for reading and executing a designspace file.
# 		documentPath: 				filepath to the .designspace document
# 		outputUFOFormatVersion:		ufo format for output
# 		verbose:					True / False for lots or no feedback [to log file]
# 		logPath:					filepath to a log file
# 		progressFunc:				an optional callback to report progress.
# 									see mutatorMath.ufo.tokenProgressFunc
#
# Future development might use: fonttools\Lib\fontTools\designspaceLib to read
#  the designspace file (which is the most up-to-date approach)
#  then pass that object to mutatorMath, but there's no way to do that today.
