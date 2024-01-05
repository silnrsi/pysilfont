#!/usr/bin/env python3
__doc__ = '''Convert CSV triples (first, second, kern) into kerning.plist in a UFO font'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2024 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.core import execute
from silfont.ufo import Uplist
from xml.etree import ElementTree as ET
import csv


argspec = [
    ("ifont", {'help': 'Input font file'}, {'type': 'infont'}),
    ("ofont", {"help": "Output font file", "nargs": "?"}, {"type": "outfont"}),
    ("-i","--input", {"help": "Input CSV file"}, {"type": "infile"})
]

def doit(args):
    kerns = {}
    csvr = csv.reader(args.input)
    for r in csvr:
        key, skey, val = r
        kerns.setdefault(key, {})[skey] = val
    pd = ET.Element("plist")
    kd = ET.SubElement(pd, "dict")
    for k, v in kerns.items():
        ET.SubElement(kd, "key").text = k
        sd = ET.SubElement(kd, "dict")
        for s, n in v.items():
            ET.SubElement(sd, "key").text = s
            ET.SubElement(sd, "integer").text = n
    if hasattr(args.ifont, 'kerning'):
        args.ifont.kerning.etree = pd
    else:
        plist = Uplist(font=args.ifont)
        plist.etree = pd
        args.ifont.kerning = plist
    return args.ifont

def cmd() : execute("UFO", doit, argspec)

if __name__ == "__main__": cmd()

