#!/usr/bin/env python
'Generate instance UFOs from a designspace document and master UFOs'

# Python 2.7 script to build instance UFOs from a designspace document
# If a file is given, all instances are built
# If a folder is given, all instances in all designspace files are built
# A particular instance to build can be specified
#  though only if a file (not a folder) is specified
# The particular instance can be identified using the -i option
#  and the 'name' attribute value for an 'instance' element in the designspace file
# Or it can be identified using the -a and -v options
#  to specify any attribute and value pair for an 'instance' in the designspace file
# If more than one instances matches, both will be built

__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

import os
from mutatorMath.ufo.document import DesignSpaceDocumentReader
from mutatorMath.ufo import build as build_designspace
from silfont.core import execute

argspec = [
    ('designspace_path', {'help': 'Path to designspace document or a folder of them'}, {}),
    ('-i', '--instanceName', {'help': 'Font name for instance to build', 'action': 'store'}, {}),
    ('-a', '--instanceAttr', {'help': 'Attribute used to specify instance to build'}, {}),
    ('-v', '--instanceVal', {'help': 'Value of attribute specifying instance to build'}, {}),
    ('--roundInstances', {'help': 'Apply integer rounding to all geometry when interpolating',
                           'action': 'store_true'}, {}),
    ('--progress', {'help': 'Show progress and errors', 'action': 'store_true'}, {}),
    ('-l','--log',{'help': 'Log file (default: *_createinstances.log)'}, {'type': 'outfile', 'def': '_createinstances.log'}),
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
    instance_font_name = args.instanceName
    instance_attr = args.instanceAttr
    instance_val = args.instanceVal
    round_instances = args.roundInstances
    show_progress = args.progress

    if instance_font_name and (instance_attr or instance_val):
        args.logger.log('--instanceName is mutually exclusive with --instanceAttr or --instanceVal','S')
    if (instance_attr and not instance_val) or (instance_val and not instance_attr):
        args.logger.log('--instanceAttr and --instanceVal must be used together', 'S')

    progress_func = progressFunc if show_progress else None

    if instance_font_name or instance_attr:
        if not os.path.isfile(designspace_path):
            args.logger.log('Specifying an instance requires a designspace file--not a folder', 'S')
        reader = DesignSpaceDocumentReader(designspace_path, ufoVersion=3,
                                           roundGeometry=round_instances,
                                           progressFunc=progress_func)
        key_attr = instance_attr if instance_val else 'name'
        key_val = instance_val if instance_attr else instance_font_name
        reader.readInstance((key_attr, key_val))
    else:
        # The below uses a utility function that's part of mutatorMath
        #  In addition to accepting a designspace file,
        #  it will accept a folder and processes all designspace files there
        progressFn = progressFunc if show_progress else None
        build_designspace(designspace_path,
                          outputUFOFormatVersion=3, roundGeometry=round_instances,
                          progressFunc=progress_func)

        # The below is an alternative implementation that uses DesignSpaceDocumentReader
        #  instead of the build_designspace utililty function
        # It's based loosely on fontmake's FontProject.run_from_designspace()
        #  but it always interpolates all instances
        #  and only generates those instances without building ttfs
        # It does NOT accept a folder of designspace files
        reader = DesignSpaceDocumentReader(designspace_path, ufoVersion=3,
                                           roundGeometry=round_instances,
                                           progressFunc=progress_func)
        reader.readInstances()

    args.logger.log('Done', 'P')

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()

# Future development might use: fonttools\Lib\fontTools\designspaceLib to read
#  the designspace file (which is the most up-to-date approach)
#  then pass that object to mutatorMath, but there's no way to do that today.
#
#
# For reference:
# from mutatorMath/ufo/__init__.py:
# 	build() is a convenience function for reading and executing a designspace file.
# 		documentPath: 				filepath to the .designspace document
# 		outputUFOFormatVersion:		ufo format for output
# 		verbose:					True / False for lots or no feedback [to log file]
# 		logPath:					filepath to a log file
# 		progressFunc:				an optional callback to report progress.
# 									see mutatorMath.ufo.tokenProgressFunc
#
# class DesignSpaceDocumentReader(object):
# def __init__(self, documentPath,
#         ufoVersion,
#         roundGeometry=False,
#         verbose=False,
#         logPath=None,
#         progressFunc=None
#         ):
#
# def readInstance(self, key, makeGlyphs=True, makeKerning=True, makeInfo=True):
