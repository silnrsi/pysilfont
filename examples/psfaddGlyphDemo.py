#!/usr/bin/env python3
'''Demo script for UFOlib to add a glyph to a UFO font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ufo as ufo
from xml.etree import cElementTree as ET

suffix = '_addGlyph'
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'log'})]

def doit(args) :
    ''' This will add the following glyph to the font

    <?xml version="1.0" encoding="UTF-8"?>
    <glyph name="Test" format="1">
    <unicode hex="007D"/>
    <outline>
    <contour>
      <point x="275" y="1582" type="line"/>
      <point x="275" y="-493" type="line"/>
    </contour>
    </outline>
    </glyph>
    '''

    font = args.ifont

    # Create basic glyph
    newglyph = ufo.Uglif(layer = font.deflayer, name = "Test")
    newglyph.add("unicode", {"hex": "007D"})
    # Add an outline
    newglyph.add("outline")
    # Create a contour and add to outline
    element = ET.Element("contour")
    ET.SubElement(element, "point", {"x": "275", "y": "1582", "type": "line"})
    ET.SubElement(element, "point", {"x": "275", "y": "-493", "type": "line"})
    contour =ufo.Ucontour(newglyph["outline"],element)
    newglyph["outline"].appendobject(contour, "contour")

    font.deflayer.addGlyph(newglyph)

    return args.ifont

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()

