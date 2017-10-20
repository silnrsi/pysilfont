#!/usr/bin/env python
'''Export fonts in a GlyphsApp file to UFOs'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute

import glyphsLib

argspec = [
    ('glyphsfont', {'help': 'Input font file'}, {'type': 'filename'}),
    ('masterdir', {'help': 'Output directory for masters'}, {}),
    ('--nofixes', {'help': 'Bypass code fixing data', 'action': 'store_true', 'default': False}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_glyphs2ufo.log'})]


def doit(args):
    logger = args.logger
    logger.log("Creating UFO objects from GlyphsApp file", "I")
    ufos = glyphsLib.load_to_ufos(args.glyphsfont, propagate_anchors=False)

    for ufo in ufos:
        # Fixes to the data
        if not args.nofixes:
            # glyphOrder has data as unicode rather than utf-8.
            new = []
            # changes = False
            for i,name in enumerate(ufo.lib["public.glyphOrder"]):
                if name == float("inf"):
                    print i
                    name = "Infinity"
                    logger.log("Infinity value corrected in public.glyphOrder", "I")
                #if isinstance(name, unicode):
                #    name = name.encode('utf8')
                #    changes = True
                new.append(name)
            # if changes: logger.log("Unicode fixes made to public.glyphOrder")
            ufo.lib["public.glyphOrder"] = new

        # Write ufo out
        logger.log("Writing out " + ufo.info.familyName + " " + ufo.info.styleName, "P")
        glyphsLib.write_ufo(ufo, args.masterdir)


def cmd(): execute(None, doit, argspec)
if __name__ == "__main__": cmd()
