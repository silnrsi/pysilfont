#!/usr/bin/env python
'''Outputs attachment point information and notes as XML file for TTFBuilder'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'M Hosken'

# user controls

# output entries for all glyphs even those with nothing interesting to say about them
all_glyphs = 1

# output the glyph id as part of the information
output_gid = 1

# output the glyph notes
output_note = 0

# output UID with "U+" prefix
output_uid_prefix = 0

# print progress indicator
print_progress = 0

# no user serviceable parts under here!
from xml.sax.saxutils import XMLGenerator
import os

def print_glyph(font, glyph, index):
    if print_progress and index % 100 == 0:
        print "%d: %s" % (index, glyph.name)
      
    if (not all_glyphs and len(glyph.anchors) == 0 and len(glyph.components) == 0 and
        not (glyph.note and output_note)):
        return
    attribs = {}
    if output_gid:
        attribs["GID"] = unicode(index)
    if glyph.unicode:
        if output_uid_prefix:
            attribs["UID"] = unicode("U+%04X" % glyph.unicode)
        else:
            attribs["UID"] = unicode("%04X" % glyph.unicode)
    if glyph.name:
        attribs["PSName"] = unicode(glyph.name)
    xg.startElement("glyph", attribs)
    
    for anchor in (glyph.anchors):
        xg.startElement("point", {"type":unicode(anchor.name), "mark":unicode(anchor.mark)})
        xg.startElement("location", {"x":unicode(anchor.x), "y":unicode(anchor.y)})
        xg.endElement("location")
        xg.endElement("point")

    for comp in (glyph.components):
        g = font.glyphs[comp.index]
        r = g.GetBoundingRect()
        x0 = 0.5 * (r.ll.x * (1 + comp.scale.x) + r.ur.x * (1 - comp.scale.x)) + comp.delta.x
        y0 = 0.5 * (r.ll.y * (1 + comp.scale.y) + r.ur.y * (1 - comp.scale.y)) + comp.delta.y
        x1 = 0.5 * (r.ll.x * (1 - comp.scale.x) + r.ur.x * (1 + comp.scale.x)) + comp.delta.x
        y1 = 0.5 * (r.ll.y * (1 - comp.scale.x) + r.ur.y * (1 + comp.scale.y)) + comp.delta.y

        attribs = {"bbox":unicode("%d, %d, %d, %d" % (x0, y0, x1, y1))}
        attribs["GID"] = unicode(comp.index)
        if (g.unicode):
            if output_uid_prefix:
                attribs["UID"] = unicode("U+%04X" % g.unicode)
            else:
                attribs["UID"] = unicode("%04X" % g.unicode)
        if (g.name):
            attribs["PSName"] = unicode(g.name)
        xg.startElement("compound", attribs)
        xg.endElement("compound")
        
    if glyph.mark:
        xg.startElement("property", {"name":unicode("mark"), "value":unicode(glyph.mark)})
        xg.endElement("property")
        
    if glyph.customdata:
        xg.startElement("customdata", {})
        xg.characters(unicode(glyph.customdata.strip()))
        xg.endElement("customdata")
        
    if glyph.note and output_note:
        xg.startElement("note", {})
        xg.characters(glyph.note)
        xg.endElement("note")
    xg.endElement("glyph")

outname = fl.font.file_name.replace(".vfb", "_tmp.xml")
fh = open(outname, "w")
xg = XMLGenerator(fh, "utf-8")
xg.startDocument()

#fl.font.full_name is needed to get the name as it appears to Windows
#fl.font.font_name seems to be the PS name. This messes up GenTest.pl when it generates WPFeatures.wpx
xg.startElement("font", {'name':unicode(fl.font.full_name), "upem":unicode(fl.font.upm)})
for i in range(0, len(fl.font.glyphs)):
    print_glyph(fl.font, fl.font.glyphs[i], i)
xg.endElement("font")

xg.endDocument()
fh.close()

#somehow this enables UNC naming (\\Gutenberg vs i:) to work when Saxon is called with popen
#without this, if outname is UNC-based, then drive letters and UNC volumes are invisible
# if outname is drive-letter-based, then drive letters and UNC volumes are already visible
if (outname[0:2] == r'\\'): 
    os.chdir("c:")
tidy = "tidy -i -xml -n -wrap 0 --char-encoding utf8 --indent-spaces 4 --quote-nbsp no --tab-size 4 -m %s"
saxon = "saxon %s %s" % ('"' + outname + '"', r'"C:\Roman Font\rfs_font\10 Misc Utils\glyph_norm.xsl"') #handle spaces in file name
f = os.popen(saxon, "rb")
g = open(outname.replace("_tmp.xml", ".xml"), "wb")
output = f.read()
g.write(output)
f.close()
g.close()

print "Done"
