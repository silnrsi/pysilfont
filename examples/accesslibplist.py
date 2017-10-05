#!/usr/bin/env python
'Sample script for accessing fields in lib.plist'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('field', {'help': 'field to access'},{})]

def doit(args):
    font = args.ifont
    field = args.field
    lib = font.lib

    if field in lib:
        val = lib.getval(field)
        print
        print val
        print
        print "Field " + field + " is type " + lib[field][1].tag + " in xml"

        print "The retrieved value is " + str(type(val)) + " in Python"
    else:
            print "Field not in lib.plist"

    return


def cmd(): execute("UFO", doit, argspec)
if __name__ == "__main__": cmd()
