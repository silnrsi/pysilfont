#!/usr/bin/env python 
'Set Glyph names to standard PostScript names based on values in the gsi.xml file.'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2013, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

import xml.sax
from silfont.fontforge import XmlFF
from silfont.fontforge.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Input gsi.xml file'}, {'type': 'filen', 'def': 'gsi.xml'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'setPSnames.log'})]

def doit(args) :
    font=args.ifont
    logf = args.log
# Parse the glyph supplemental info file
    parser = xml.sax.make_parser()
    handler = XmlFF.CollectXmlInfo()
    parser.setContentHandler(handler)
    print 'Parsing XML file: ',args.input
    try :
        parser.parse(args.input)
    except Exception as e :
        print e
        sys.exit()
    parser.parse(args.input)
    gsi_dict = handler.get_data_dict()

# Rename the glyphs
    for glyph in font:
        g = font[glyph]
        sil_name = g.glyphname
        ps_nm = None
        try:
            if gsi_dict[sil_name].glyph_active == u"0": #skip inactive glyphs
                continue
            ps_nm = gsi_dict[sil_name].ps_name_value.encode() #encode() converts from Unicode string to std string
            g.glyphname = ps_nm
            logf.write("Glyph renamed - SIL Name: %s  PS Name: %s\n" % (sil_name, ps_nm))
        except:
            print "Glyph not renamed - SIL Name: %s" % sil_name
            logf.write("** Glyph not renamed - SIL Name: %s  PS Name: %s\n" % (sil_name, ps_nm))
            
    logf.close()
    return font

execute(doit, argspec)
