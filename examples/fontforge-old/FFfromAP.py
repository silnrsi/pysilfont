#!/usr/bin/env python3
'''Import Attachment Point database into a fontforge font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.core import execute

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file'}, {'type': 'outfont'}),
    ('-a','--ap', {'nargs' : 1, 'help': 'Input AP database (required)'}, {})
]

def assign(varlist, expr) :
    """passes a variable to be assigned as a list and returns the value"""
    varlist[0] = expr
    return expr

def getuidenc(e, f) :
    if 'UID' in e.attrib :
        u = int(e.get('UID'), 16)
        return f.findEncodingSlot(u)
    else :
        return -1

def getgid(e, f) :
    if 'GID' in e.attrib :
        return int(e.get('GID'))
    else :
        return -1

def doit(args) :
    from xml.etree.ElementTree import parse

    f = args.ifont
    g = None
    etree = parse(args.ap)
    u = []
    for e in etree.getroot().iterfind("glyph") :
        name = e.get('PSName')
        if name in f :
            g = f[name]
        elif assign(u, getuidenc(e, f)) != -1 :
            g = f[u[0]]
        elif assign(u, getgid(e, f)) != -1 :
            g = f[u[0]]
        elif g is not None :    # assume a rename so just take next glyph
            g = f[g.encoding + 1]
        else :
            g = f[0]
        g.name = name
        g.anchorPoints = ()
        for p in e.iterfind('point') :
            pname = p.get('type')
            l = p[0]
            x = int(l.get('x'))
            y = int(l.get('y'))
            if pname.startswith('_') :
                ptype = 'mark'
                pname = pname[1:]
            else :
                ptype = 'base'
            g.addAnchorPoint(pname, ptype, float(x), float(y))
        comment = []
        for p in e.iterfind('property') :
            comment.append("{}: {}".format(e.get('name'), e.get('value')))
        for p in e.iterfind('note') :
            comment.append(e.text.strip())
        g.comment = "\n".join(comment)

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
