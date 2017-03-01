#!/usr/bin/env python
from __future__ import unicode_literals
#'read FTML file and generate LO writer .odt file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

from silfont.core import execute
from fontTools import ttLib
from xml.etree import ElementTree as ET ### used to parse input FTML (may not be needed if FTML parser used)
import re
import os
import io
from odf.opendocument import OpenDocumentText, OpaqueObject
from odf.config import ConfigItem, ConfigItemSet
from odf.office import FontFaceDecls
from odf.style import FontFace, ParagraphProperties, Style, TableCellProperties, TableColumnProperties, TableProperties, TextProperties
from odf.svg import FontFaceSrc, FontFaceUri, FontFaceFormat
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import H, P, SequenceDecl, SequenceDecls, Span

# specify two parameters: input file (FTML/XML format), output file (ODT format)
# preceded by optional log file plus zero or more font strings
argspec = [
    ('input',{'help': 'Input file in FTML format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file (LO writer .odt)'}, {'type': 'filename', 'def': '_out.odt'}),
    ('-l','--log',{'help': 'Log file', 'required': False},{'type': 'outfile', 'def': '_ftml2odt_log.txt'}),
    ('-r','--report',{'help': 'Set reporting level for log', 'type':str, 'choices':['X','S','E','P','W','I','V']},{}),
    ('-f','--font',{'help': 'font specification','action': 'append', 'required': False}, {}),
    ]

# RegExs for extracting font name from fontsrc element
findfontnamelocal = re.compile(r"""local\(  # begin with local(
                    (["']?)                 # optional open quote
                    (?P<fontstring>[^)]+)   # font name
                    \1                      # optional matching close quote
                    \)""", re.VERBOSE)      # and end with )
findfontnameurl =   re.compile(r"""url\(    # begin with local(
                    (["']?)                 # optional open quote
                    (?P<fontstring>[^)]+)   # font name
                    \1                      # optional matching close quote
                    \)""", re.VERBOSE)      # and end with )
fontspec =          re.compile(r"""^        # beginning of string
                    (?P<rest>[A-Za-z ]+?)   # Font Family Name
                    \s*(?P<bold>Bold)?      # Bold
                    \s*(?P<italic>Italic)?  # Italic
                    \s*(?P<regular>Regular)? # Regular
                    $""", re.VERBOSE)       # end of string
# RegEx for extracting feature(s) from feats attribute of style element
onefeat = re.compile(r"""^\s*
            '(?P<featname>[^']+)'\s*    # feature tag
            (?P<featval>[^', ]+)\s*     # feature value
            ,?\s*                       # optional comma
            (?P<remainder>.*)           # rest of line (with zero or more tag-value pairs)
            $""", re.VERBOSE)
# RegEx for extracting language (and country) from lang attribute of style element
langcode = re.compile(r"""^
                (?P<langname>[A-Za-z]+)     # language name
                (-                          # (optional) hyphen and
                (?P<countryname>[A-Za-z]+)  # country name
                (-[A-Za-z0-9][-A-Za-z0-9]*)? # (optional) hyphen and other codes
                )?$""", re.VERBOSE)
# RegEx to extract hex value from \uxxxxxx and function to generate Unicode character
# use to change string to newstring:
# newstring = re.sub(backu, hextounichr, string)
# or newstring = re.sub(backu, lambda m: unichr(int(m.group(1),16)), string)
backu = re.compile(r"\\u([0-9a-fA-F]{4,6})")
def hextounichr(match):
    return unichr(int(match.group(1),16))

def BoldItalic(bold, italic):
    rs = ""
    if bold:
        rs += " Bold"
    if italic:
        rs += " Italic"
    return rs

def parsefeats(inputline):
    featdic = {}
    while inputline != "":
        results = re.match(onefeat, inputline)
        if results:
            featdic[results.group('featname')] = results.group('featval')
            inputline = results.group('remainder')
        else:
            break ### warning about unrecognized feature string: inputline
    return ":" + "&".join( [f + '=' + featdic[f] for f in sorted(featdic)])

def getfonts(fontsourcestrings, logfile, fromcommandline=True):
    fontlist = []
    checkfontfamily = []
    checkembeddedfont = []
    for fs in fontsourcestrings:
        if not fromcommandline: # from FTML <fontsrc> either local() or url()
            installed = True    # Assume locally installed font
            results = re.match(findfontnamelocal, fs)
            fontstring = results.group('fontstring') if results else None
            if fontstring == None:
                installed = False
                results = re.match(findfontnameurl, fs)
                fontstring = results.group('fontstring') if results else None
            if fontstring == None:
                logfile.log("Invalid font specification: " + fs, "S")
        else:                   # from command line
            fontstring = fs
            if "." in fs:       # must be a filename
                installed = False
            else:               # must be an installed font
                installed = True
        if installed:
            # get name, bold and italic info from string
            results = re.match(fontspec, fontstring.strip())
            if results:
                fontname = results.group('rest')
                bold = results.group('bold') != None
                italic = results.group('italic') != None
                fontlist.append( (fontname, bold, italic, None) )
                if (fontname, bold, italic) in checkfontfamily:
                    logfile.log("Duplicate font specification: " + fs, "W") ### or more severe?
                else:
                    checkfontfamily.append( (fontname, bold, italic) )
            else:
                logfile.log("Invalid font specification: " + fontstring.strip(), "E")
        else:
            try:
                # peek inside the font for the name, weight, style
                f = ttLib.TTFont(fontstring)
                # take name from name table, NameID 1, platform ID 3, Encoding ID 1 (possible fallback platformID 1, EncodingID =0)
                n = f['name'] # name table from font
                fontname = n.getName(1,3,1).toUnicode() # nameID 1 = Font Family name
                # take bold and italic info from OS/2 table, fsSelection bits 0 and 5
                o = f['OS/2'] # OS/2 table
                italic = (o.fsSelection & 1) > 0
                bold = (o.fsSelection & 32) > 0
                fontlist.append( (fontname, bold, italic, fontstring) )
                if (fontname, bold, italic) in checkfontfamily:
                    logfile.log("Duplicate font specification: " + fs + BoldItalic(bold, italic), "W") ### or more severe?
                else:
                    checkfontfamily.append( (fontname, bold, italic) )
                if (os.path.basename(fontstring)) in checkembeddedfont:
                    logfile.log("Duplicate embedded font: " + fontstring, "W") ### or more severe?
                else:
                    checkembeddedfont.append(os.path.basename(fontstring))
            except IOError:
                logfile.log("Unable to find font file to embed: " + fontstring, "E")
            except fontTools.ttLib.TTLibError:
                logfile.log("File is not a valid font: " + fontstring, "E")
            except:
                logfile.log("Error occurred while checking font: " + fontstring, "E") # some other error
    return fontlist

def init(LOdoc, numfonts=1):
    totalwid = 6800 #6.8inches

    #compute column widths
    f = min(numfonts,4)
    ashare = 4*(6-f)
    dshare = 2*(6-f)
    bshare = 100 - 2*ashare - dshare
    awid = totalwid * ashare // 100
    dwid = totalwid * dshare // 100
    bwid = totalwid * bshare // (numfonts * 100)

    # create styles for table, for columns (one style for each column width)
    # and for one cell (used for everywhere except where background changed)
    tstyle = Style(name="Table1", family="table")
    tstyle.addElement(TableProperties(attributes={'width':str(totalwid/1000.)+"in", 'align':"left"}))
    LOdoc.automaticstyles.addElement(tstyle)
    tastyle = Style(name="Table1.A", family="table-column")
    tastyle.addElement(TableColumnProperties(attributes={'columnwidth':str(awid/1000.)+"in"}))
    LOdoc.automaticstyles.addElement(tastyle)
    tbstyle = Style(name="Table1.B", family="table-column")
    tbstyle.addElement(TableColumnProperties(attributes={'columnwidth':str(bwid/1000.)+"in"}))
    LOdoc.automaticstyles.addElement(tbstyle)
    tdstyle = Style(name="Table1.D", family="table-column")
    tdstyle.addElement(TableColumnProperties(attributes={'columnwidth':str(dwid/1000.)+"in"}))
    LOdoc.automaticstyles.addElement(tdstyle)
    ta1style = Style(name="Table1.A1", family="table-cell")
    ta1style.addElement(TableCellProperties(attributes={'padding':"0.035in", 'border':"0.05pt solid #000000"}))
    LOdoc.automaticstyles.addElement(ta1style)
    # text style used with non-<em> text
    t1style = Style(name="T1", family="text")
    t1style.addElement(TextProperties(attributes={'color':"#999999" }))
    LOdoc.automaticstyles.addElement(t1style)
    # create styles for Title, Subtitle
    tstyle = Style(name="Title", family="paragraph")
    tstyle.addElement(TextProperties(attributes={'fontfamily':"Arial",'fontsize':"24pt",'fontweight':"bold" }))
    LOdoc.styles.addElement(tstyle)
    ststyle = Style(name="Subtitle", family="paragraph")
    ststyle.addElement(TextProperties(attributes={'fontfamily':"Arial",'fontsize':"18pt",'fontweight':"bold" }))
    LOdoc.styles.addElement(ststyle)

def doit(args) :
    logfile = args.logger
    if args.report: logfile.loglevel = args.report

    try:
        root = ET.parse(args.input).getroot()
    except:
        logfile.log("Error parsing FTML input", "S")

    if args.font:                   # font(s) specified on command line
        fontlist = getfonts( args.font, logfile )
    else:                           # get font spec from FTML fontsrc element
        fontlist = getfonts( [root.find("./head/fontsrc").text], logfile, False )
        #fontlist = getfonts( [fs.text for fs in root.findall("./head/fontsrc")], False ) ### would allow multiple fontsrc elements
    numfonts = len(fontlist)
    if numfonts == 0:
        logfile.log("No font(s) specified", "S")
    if numfonts > 1:
        formattedfontnum = ["{0:02d}".format(n) for n in range(numfonts)]
    else:
        formattedfontnum = [""]
    logfile.log("Font(s) specified:", "V")
    for n, (fontname, bold, italic, embeddedfont) in enumerate(fontlist):
        logfile.log(" " + formattedfontnum[n] + " " + fontname + BoldItalic(bold, italic) + " " + str(embeddedfont), "V")

    # get optional fontscale; compute pointsize as int(12*fontscale/100). If result xx is not 12, then add "fo:font-size=xxpt" in Px styles
    pointsize = 12
    fontscaleel = root.find("./head/fontscale")
    if fontscaleel != None:
        fontscale = fontscaleel.text
        try:
            pointsize = int(int(fontscale)*12/100)
        except ValueError:
            # any problem leaves pointsize 12
            logfile.log("Problem with fontscale value; defaulting to 12 point", "W")

    # Get FTML styles and generate LO writer styles
    # P2 is paragraph style for string element when no features specified
    # each Px (for P3...) corresponds to an FTML style, which specifies lang or feats or both
    # if numfonts > 1, two-digit font number is appended to make an LO writer style for each FTML style + font combo
    # When LO writer style is used with attribute rtl="True", "R" appended to style name
    LOstyles = {}
    ftmlstyles = {}
    Pstylenum = 2
    LOstyles["P2"] = ("", None, None)
    ftmlstyles[0] = "P2"
    for s in root.findall("./head/styles/style"):
        Pstylenum += 1
        Pnum = "P" + str(Pstylenum)
        featstring = ""
        if s.get('feats'):
            featstring = parsefeats(s.get('feats'))
        langname = None
        countryname = None
        lang = s.get('lang')
        if lang != None:
            x = re.match(langcode, lang)
            langname = x.group('langname')
            countryname = x.group('countryname')
        # FTML <test> element @stylename attribute references this <style> element @name attribute
        ftmlstyles[s.get('name')] = Pnum
        LOstyles[Pnum] = (featstring, langname, countryname)

    # create LOwriter file and construct styles for tables, column widths, etc.
    LOdoc = OpenDocumentText()
    init(LOdoc, numfonts)
    # Initialize sequence counters
    sds = SequenceDecls()
    sd = sds.addElement(SequenceDecl(displayoutlinelevel = '0', name = 'Illustration'))
    sd = sds.addElement(SequenceDecl(displayoutlinelevel = '0', name = 'Table'))
    sd = sds.addElement(SequenceDecl(displayoutlinelevel = '0', name = 'Text'))
    sd = sds.addElement(SequenceDecl(displayoutlinelevel = '0', name = 'Drawing'))
    LOdoc.text.addElement(sds)

    # Create Px style for each (featstring, langname, countryname) tuple in LOstyles
    # and for each font (if >1 font, append to Px style name a two-digit number corresponding to the font in fontlist)
    # and (if at least one rtl attribute) suffix of nothing or "R"
    # At the same time, collect info for creating FontFace elements (and any embedded fonts)
    suffixlist = ["", "R"] if root.find(".//test/[@rtl='True']") != None else [""]
    fontfaces = {}
    for p in sorted(LOstyles, key = lambda x : int(x[1:])):  # key = lambda x : int(x[1:]) corrects sort order
        featstring, langname, countryname = LOstyles[p]
        for n, (fontname, bold, italic, embeddedfont) in enumerate(fontlist): # embeddedfont = None if no embedding needed
            fontnum = formattedfontnum[n]
            # Collect fontface info: need one for each font family + feature combination
            # Put embedded font in list only under fontname with empty featstring
            if (fontname, featstring) not in fontfaces:
                fontfaces[ (fontname, featstring) ] = []
            if embeddedfont:
                if (fontname, "") not in fontfaces:
                    fontfaces[ (fontname, "") ] = []
                if embeddedfont not in fontfaces[ (fontname, "") ]:
                    fontfaces[ (fontname, "") ].append(embeddedfont)
            # Generate paragraph styles
            for s in suffixlist:
                pstyle = Style(name=p+fontnum+s, family="paragraph")
                if s == "R":
                    pstyle.addElement(ParagraphProperties(textalign="end", justifysingleword="false", writingmode="rl-tb"))
                pstyledic = {}
                pstyledic['fontnamecomplex'] = \
                pstyledic['fontnameasian'] =\
                pstyledic['fontname'] = fontname + featstring
                pstyledic['fontsizecomplex'] = \
                pstyledic['fontsizeasian'] = \
                pstyledic['fontsize'] = str(pointsize) + "pt"
                if bold:
                    pstyledic['fontweightcomplex'] = \
                    pstyledic['fontweightasian'] = \
                    pstyledic['fontweight'] = 'bold'
                if italic:
                    pstyledic['fontstylecomplex'] = \
                    pstyledic['fontstyleasian'] = \
                    pstyledic['fontstyle'] = 'italic'
                if langname != None:
                    pstyledic['languagecomplex'] = \
                    pstyledic['languageasian'] = \
                    pstyledic['language'] = langname
                if countryname != None:
                    pstyledic['countrycomplex'] = \
                    pstyledic['countryasian'] = \
                    pstyledic['country'] = countryname
                pstyle.addElement(TextProperties(attributes=pstyledic))
#                LOdoc.styles.addElement(pstyle)    ### tried this, but when saving the generated odt, LO changed them to automatic styles
                LOdoc.automaticstyles.addElement(pstyle)

    fontstoembed = []
    for fontname, featstring in sorted(fontfaces):  ### Or find a way to keep order of <style> elements from original FTML?
        ff = FontFace(name=fontname + featstring, fontfamily=fontname + featstring, fontpitch="variable")
        LOdoc.fontfacedecls.addElement(ff)
        if fontfaces[ (fontname, featstring) ]:     # embedding needed for this combination
            for fontfile in fontfaces[ (fontname, featstring) ]:
                fontstoembed.append(fontfile)       # make list for embedding
                ffsrc = FontFaceSrc()
                ffuri = FontFaceUri( **{'href': "Fonts/" + os.path.basename(fontfile), 'type': "simple"} )
                ffformat = FontFaceFormat( **{'string': 'truetype'} )
                ff.addElement(ffsrc)
                ffsrc.addElement(ffuri)
                ffuri.addElement(ffformat)

    basename = "Table1.B"
    colorcount = 0
    colordic = {} # record color #rrggbb as key and "Table1.Bx" as stylename (where x is current color count)
    tablenum = 0

    # get title and comment and use as title and subtitle
    titleel = root.find("./head/title")
    if titleel != None:
        LOdoc.text.addElement(H(outlinelevel=1, stylename="Title", text=titleel.text))
    commentel = root.find("./head/comment")
    if commentel != None:
        LOdoc.text.addElement(P(stylename="Subtitle", text=commentel.text))

    # Each testgroup element begins a new table
    for tg in root.findall("./testgroup"):
        # insert label attribute of testgroup element as subtitle
        tglabel = tg.get('label')
        if tglabel != None:
            LOdoc.text.addElement(H(outlinelevel=1, stylename="Subtitle", text=tglabel))

        # insert text from comment subelement of testgroup element
        tgcommentel = tg.find("./comment")
        if tgcommentel != None:
            #print("commentel found")
            LOdoc.text.addElement(P(text=tgcommentel.text))

        tgbg = tg.get('background') # background attribute of testgroup element
        tablenum += 1
        table = Table(name="Table" + str(tablenum), stylename="Table1")
        table.addElement(TableColumn(stylename="Table1.A"))
        for n in range(numfonts):
            table.addElement(TableColumn(stylename="Table1.B"))
        table.addElement(TableColumn(stylename="Table1.A"))
        table.addElement(TableColumn(stylename="Table1.D"))
        for t in tg.findall("./test"):                # Each test element begins a new row
            # stuff to start the row
            labeltext = t.get('label')
            stylename = t.get('stylename')
            stringel = t.find('./string')
            commentel = t.find('./comment')
            rtlsuffix = "R" if t.get('rtl') == 'True' else ""
            comment = commentel.text if commentel != None else None
            colBstyle = "Table1.A1"
            tbg = t.get('background')   # get background attribute of test group (if one exists)
            if tbg == None: tbg = tgbg
            if tbg != None:             # if background attribute for test element (or background attribute for testgroup element)
                if tbg not in colordic: # if color not found in color dic, create new style
                    colorcount += 1
                    newname = basename + str(colorcount)
                    colordic[tbg] = newname
                    tb1style = Style(name=newname, family="table-cell")
                    tb1style.addElement(TableCellProperties(attributes={'padding':"0.0382in", 'border':"0.05pt solid #000000", 'backgroundcolor':tbg}))
                    LOdoc.automaticstyles.addElement(tb1style)
                colBstyle = colordic[tbg]

            row = TableRow()
            table.addElement(row)
            # fill cells
            # column A (label)
            cell = TableCell(stylename="Table1.A1", valuetype="string")
            if labeltext:
                cell.addElement(P(stylename="Table_20_Contents", text = labeltext))
            row.addElement(cell)

            # column B (string)
            for n in range(numfonts):
                Pnum = ftmlstyles[stylename] if stylename != None else "P2"
                Pnum = Pnum + formattedfontnum[n] + rtlsuffix
                ### not clear if any of the following can be moved outside loop and reused
                cell = TableCell(stylename=colBstyle, valuetype="string")
                par = P(stylename=Pnum)
                if len(stringel) == 0: # no <em> subelements
                    par.addText(re.sub(backu, hextounichr, stringel.text))
                else:   # handle <em> subelement(s)
                    if stringel.text != None:
                        par.addElement(Span(stylename="T1", text = re.sub(backu, hextounichr, stringel.text)))
                    for e in stringel.findall("em"):
                        if e.text != None:
                            par.addText(re.sub(backu, hextounichr, e.text))
                        if e.tail != None:
                            par.addElement(Span(stylename="T1", text = re.sub(backu, hextounichr, e.tail)))
                cell.addElement(par)
                row.addElement(cell)

            # column C (comment)
            cell = TableCell(stylename="Table1.A1", valuetype="string")
            if comment:
                cell.addElement(P(stylename="Table_20_Contents", text = comment))
            row.addElement(cell)

            # column D (stylename)
            cell = TableCell(stylename="Table1.A1", valuetype="string")
            if comment:
                cell.addElement(P(stylename="Table_20_Contents", text = stylename))
            row.addElement(cell)
        LOdoc.text.addElement(table)

    LOdoc.text.addElement(P(stylename="Subtitle", text="")) # Empty paragraph to end ### necessary?

    try:
        if fontstoembed: logfile.log("Embedding fonts in document", "V")
        for f in fontstoembed:
            LOdoc._extra.append(
                OpaqueObject(filename = "Fonts/" + os.path.basename(f),
                    mediatype = "application/x-font-ttf",      ### should be "application/font-woff" or "/font-woff2" for WOFF fonts, "/font-opentype" for ttf
                    content = io.open(f, "rb").read() ))
        ci = ConfigItem(**{'name':'EmbedFonts', 'type': 'boolean'}) ### (name = 'EmbedFonts', type = 'boolean')
        ci.addText('true')
        cis=ConfigItemSet(**{'name':'ooo:configuration-settings'})  ### (name = 'ooo:configuration-settings')
        cis.addElement(ci)
        LOdoc.settings.addElement(cis)
    except:
        logfile.log("Error embedding fonts in document", "E")
    logfile.log("Writing output file: " + args.output, "P")
    LOdoc.save(unicode(args.output))
    return

def cmd() : execute("PSFU",doit, argspec)

if __name__ == "__main__": cmd()

