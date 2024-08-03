#! /usr/bin/env python3
'''Build fonts for all combinations of TypeTuner features needed for specific ftml then build html that uses those fonts'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute
from fontTools import ttLib
from lxml import etree as ET    # using this because it supports xslt and HTML
from collections import OrderedDict
from subprocess import check_output, CalledProcessError
import os, re
import gzip
from glob import glob


argspec = [
    ('ttfont', {'help': 'Input Tunable TTF file'}, {'type': 'filename'}),
    ('map', {'help': 'Feature mapping CSV file'}, {'type': 'incsv'}),
    ('-o', '--outputdir', {'help': 'Output directory. Default: tests/typetuner', 'default': 'tests/typetuner'}, {}),
    ('--ftml', {'help': 'ftml file(s) to process. Can be used multiple times and can contain filename patterns.', 'action': 'append'}, {}),
    ('--xsl', {'help': 'standard xsl file. Default: ../tools/ftml.xsl', 'default': '../tools/ftml.xsl'}, {'type': 'filename'}),
    ('--norebuild', {'help': 'assume existing fonts are good', 'action': 'store_true'}, {}),
    ]

# Define globals needed everywhere:

logger = None
sourcettf = None
outputdir = None
fontdir = None


# Dictionary of TypeTuner features, derived from 'feat_all.xml', indexed by feature name
feat_all = dict()

class feat(object):
    'TypeTuner feature'
    def __init__(self, elem, sortkey):
        self.name = elem.attrib.get('name')
        self.tag = elem.attrib.get('tag')
        self.default = elem.attrib.get('value')
        self.values = OrderedDict()
        self.sortkey = sortkey
        for v in elem.findall('value'):
            # Only add those values which aren't importing line metrics
            if v.find("./cmd[@name='line_metrics_scaled']") is None:
                self.values[v.attrib.get('name')] = v.attrib.get('tag')


# Dictionaries of mappings from OpenType tags to TypeTuner names, derived from map csv
feat_maps = dict()
lang_maps = dict()

class feat_map(object):
    'mapping from OpenType feature tag to TypeTuner feature name, default value, and all values'
    def __init__(self, r):
        self.ottag, self.ttfeature, self.default = r[0:3]
        self.ttvalues = r[3:]

class lang_map(object):
    'mapping from OpenType language tag to TypeTuner language feature name and value'
    def __init__(self,r):
        self.ottag, self.ttfeature, self.ttvalue = r

# About font_tag values
#
# In this code, a font_tag uniquely identifies a font we've built.
#
# Because different ftml files could use different style names for the same set of features and language, and we
# want to build only one font for any given combination of features and language, we don't depend on the name of the
# ftml style for identifying and caching the fonts we build. Rather we build a font_tag which is a the
# concatenation of the ftml feature/value tags and the ftml lang feature/value tag.

# Font object used to cache information about a tuned font we've created

class font(object):
    'Cache of tuned font information'

    def __init__(self, font_tag, feats, lang, fontface):
        self.font_tag = font_tag
        self.feats = feats
        self.lang = lang
        self.fontface = fontface


# Dictionaries for finding font objects

# Finding font from font_tag:
font_tag2font = dict()

# If an ftml style contains no feats, only the lang tag will show up in the html. Special mapping for those cases:
lang2font = dict()

# RE to match strings like: # "'cv02' 1"
feature_settingRE = re.compile(r"^'(\w{4,4})'(?:\s+(\w+))?$")
# RE to split strings of multiple features around comma (with optional whitespace)
features_splitRE = re.compile(r"\s*,\s*")


def cache_font(feats, lang, norebuild):
    'Create (and cache) a TypeTuned font and @fontface for this combination of features and lang'

    # feats is either None or a css font-feature-settings string using single quotes (according to ftml spec), e.g. "'cv02' 1, 'cv60' 1"
    # lang is either None or bcp47 langtag
    # norebuild is a debugging aid that causes the code to skip building a .ttf if it is already present thus making the
    #     program run faster but with the risk that the built TTFs don't match the current build.

    # First step is to construct a name for this set of languages and features, something we'll call the "font tag"

    parts = []
    ttsettings = dict() # place to save TT setting name and value in case we need to build the font
    fatal_errors = False

    if feats:
        # Need to split the font-feature-settings around commas and parse each part, mapping css tag and value to
        # typetuner tag and value
        for setting in features_splitRE.split(feats):
            m = feature_settingRE.match(setting)
            if m is None:
                logger.log('Invalid CSS feature setting in ftml: {}'.format(setting), 'E')
                fatal_errors = True
                continue
            f,v = m.groups()  # Feature tag and value
            if v in ['normal','off']:
                v = '0'
            elif v == 'on':
                v = '1'
            try:
                v = int(v)
                assert v >= 0
            except:
                logger.log('Invalid feature value {} found in map file'.format(setting), 'E')
                fatal_errors = True
                continue
            if not v:
                continue    # No need to include 0/off values

            # we need this one... so translate to TypeTuner feature & value using the map file
            try:
                fmap = feat_maps[f]
            except KeyError:
                logger.log('Font feature "{}" not found in map file'.format(f), 'E')
                fatal_errors = True
                continue

            f = fmap.ttfeature

            try:
                v = fmap.ttvalues[v - 1]
            except IndexError:
                logger.log('TypeTuner feature "{}" doesn\'t have a value index {}'.format(f, v), 'E')
                fatal_errors = True
                continue

            # Now translate to TypeTuner tags using feat_all info
            if f not in feat_all:
                logger.log('Tunable font doesn\'t contain a feature "{}"'.format(f), 'E')
                fatal_errors = True
            elif v not in feat_all[f].values:
                logger.log('Tunable font feature "{}" doesn\'t have a value {}'.format(f, v), 'E')
                fatal_errors = True
            else:
                ttsettings[f] = v   # Save TT setting name and value name in case we need to build the font
                ttfeat = feat_all[f]
                f = ttfeat.tag
                v = ttfeat.values[v]
                # Finally!
                parts.append(f+v)
    if lang:
            if lang not in lang_maps:
                logger.log('Language tag "{}" not found in map file'.format(lang), 'E')
                fatal_errors = True
            else:
                # Translate to TypeTuner feature & value using the map file
                lmap = lang_maps[lang]
                f = lmap.ttfeature
                v = lmap.ttvalue
                # Translate to TypeTuner tags using feat_all info
                if f not in feat_all:
                    logger.log('Tunable font doesn\'t contain a feature "{}"'.format(f), 'E')
                    fatal_errors = True
                elif v not in feat_all[f].values:
                    logger.log('Tunable font feature "{}" doesn\'t have a value {}'.format(f, v), 'E')
                    fatal_errors = True
                else:
                    ttsettings[f] = v  # Save TT setting name and value in case we need to build the font
                    ttfeat = feat_all[f]
                    f = ttfeat.tag
                    v = ttfeat.values[v]
                    # Finally!
                    parts.append(f+v)
    if fatal_errors:
        return None

    if len(parts) == 0:
        logger.log('No features or languages found'.format(f), 'E')
        return None

    # the Font Tag is how we name everything (the ttf, the xml, etc)
    font_tag = '_'.join(sorted(parts))

    # See if we've had this combination before:
    if font_tag in font_tag2font:
        logger.log('Found cached font {}'.format(font_tag), 'I')
        return font_tag

    # Path to font, which may already exist, and @fontface
    ttfname = os.path.join(fontdir, font_tag + '.ttf')
    fontface = '@font-face { font-family: {}; src: url(fonts/{}.ttf); } .{} {font-family: {}; }'.replace('{}',font_tag)

    # Create new font object and remember how to find it:
    thisfont = font(font_tag, feats, lang, fontface)
    font_tag2font[font_tag] = thisfont
    if lang and not feats:
        lang2font[lang] = thisfont

    # Debugging shortcut: use the existing fonts without rebuilding
    if norebuild and os.path.isfile(ttfname):
        logger.log('Blindly using existing font {}'.format(font_tag), 'I')
        return font_tag

    # Ok, need to build the font
    logger.log('Building font {}'.format(font_tag), 'I')

    # Create and save the TypeTuner feature settings file
    sfname = os.path.join(fontdir, font_tag + '.xml')
    root = ET.XML('''\
<?xml version = "1.0"?>
<!DOCTYPE features_set SYSTEM "feat_set.dtd">
<features_set version = "1.0"/>
''')
    # Note: Order of elements in settings file should be same as order in feat_all
    # (because this is the way TypeTuner does it and some fonts may expect this)
    for name, ttfeat in sorted(feat_all.items(), key=lambda x: x[1].sortkey):
        if name in ttsettings:
            # Output the non-default value for this one:
            ET.SubElement(root, 'feature',{'name': name, 'value': ttsettings[name]})
        else:
            ET.SubElement(root, 'feature', {'name': name, 'value': ttfeat.default})
    xml = ET.tostring(root,pretty_print = True, encoding='UTF-8', xml_declaration=True)
    with open(sfname, '+wb')as f:
        f.write(xml)

    # Now invoke TypeTuner to create the tuned font
    try:
        cmd = ['typetuner', '-o', ttfname, '-n', font_tag, sfname, sourcettf]
        res = check_output(cmd)
        if len(res):
            print('\n', res)
    except CalledProcessError as err:
        logger.log("couldn't tune font: {}".format(err.output), 'S')

    return font_tag

def doit(args) :

    global logger, sourcettf, outputdir, fontdir

    logger = args.logger
    sourcettf = args.ttfont

    # Create output directory, including fonts subdirectory, if not present
    outputdir = args.outputdir
    os.makedirs(outputdir, exist_ok = True)
    fontdir = os.path.join(outputdir, 'fonts')
    os.makedirs(fontdir, exist_ok = True)

    # Read and save feature mapping
    for r in args.map:
        # remove empty cells from the end
        while len(r) and len(r[-1]) == 0:
            r.pop()
        if len(r) == 0 or r[0].startswith('#'):
            continue
        elif r[0].startswith('lang='):
            if len(r[0]) < 7 or len(r) != 3:
                logger.log("Invalid lang mapping: '" + ','.join(r) + "' ignored", "W")
            else:
                r[0] = r[0][5:]
                lang_maps[r[0]] = lang_map(r)
        else:
            if len(r) < 4:
                logger.log("Invalid feature mapping: '" + ','.join(r) + "' ignored", "W")
            else:
                feat_maps[r[0]] = feat_map(r)

    # Open and verify input file is a tunable font; extract and parse feat_all from font.
    font = ttLib.TTFont(sourcettf)
    raw_data = font.getTableData('Silt')
    feat_xml = gzip.decompress(raw_data) # .decode('utf-8')
    root = ET.fromstring(feat_xml)
    if root.tag != 'all_features':
        logger.log("Invalid TypeTuner feature file: missing root element", "S")
    for i, f in enumerate(root.findall('.//feature')):
        # add to dictionary
        ttfeat = feat(f,i)
        feat_all[ttfeat.name] = ttfeat

    # Open and prepare the xslt file to transform the ftml:
    xslt = ET.parse(args.xsl)
    xslt_transform = ET.XSLT(xslt)


    # Process all ftml files:

    for arg in args.ftml:
        for infname in glob(arg):
            # based on input filename, construct output name
            # find filename and change extension to html:
            outfname = os.path.join(outputdir, os.path.splitext(os.path.basename(infname))[0] + '.html')
            logger.log('Processing: {} -> {}'.format(infname, outfname), 'P')

            # Each named style in the FTML ultimately maps to a TypeTuned font that will be added via @fontface.
            # We need to remember the names of the styles and their associated fonts so we can hack the html.
            sname2font = dict() # Indexed by ftml stylename; result is a font object

            # Parse the FTML
            ftml_doc = ET.parse(infname)

            # Adjust <title> to show this is from TypeTuner
            head = ftml_doc.find('head')
            title = head.find('title')
            title.text += " - TypeTuner"
            # Replace all <fontsrc> elements with two identical from the input font:
            #   One will remain unchanged, the other will eventually be changed to a typetuned font.
            ET.strip_elements(head, 'fontsrc')
            fpathname = os.path.relpath(sourcettf, outputdir).replace('\\','/')  # for css make sure all slashes are forward!
            head.append(ET.fromstring('<fontsrc>url({})</fontsrc>'.format(fpathname)))    # First font
            head.append(ET.fromstring('<fontsrc>url({})</fontsrc>'.format(fpathname)))    # Second font, same as the first

            # iterate over all the styles in this ftml file, building tuned fonts to match if not already done.
            for style in head.iter('style'):
                sname = style.get('name')    # e.g. "some_style"
                feats = style.get('feats')  # e.g "'cv02' 1, 'cv60' 1"  -- this we'll parse to get need tt features
                lang = style.get('lang')    # e.g., "sd"
                font_tag = cache_font(feats, lang, args.norebuild)
                # font_tag could be None due to errors, but messages should already have been logged
                # If it is valid, remember how to find this font from the ftml stylename
                if font_tag:
                    sname2font[sname] = font_tag2font[font_tag]

            # convert to html via supplied xslt
            html_doc = xslt_transform(ftml_doc)

            # Two modifications to make in the html:
            # 1) add all @fontface specs to the <style> element
            # 2) Fix up all occurrences of <td> elements referencing font2

            # Add @fontface to <style>
            style = html_doc.find('.//style')
            style.text = style.text + '\n' + '\n'.join([x.fontface for x in sname2font.values()])

            # Iterate over all <td> elements looking for font2 and a style or lang indicating feature settings

            classRE = re.compile(r'string\s+(?:(\w+)\s+)?font2$')

            for td in html_doc.findall('.//td'):
                tdclass = td.get('class')
                tdlang = td.get('lang')
                m = classRE.match(tdclass)
                if m:
                    sname = m.group(1)
                    if sname:
                        # stylename will get us directly to the font
                        try:
                            td.set('class', 'string {}'.format(sname2font[sname].font_tag))
                            if tdlang:  # If there is also a lang attribute, we no longer need it.
                                del td.attrib['lang']
                        except KeyError:
                            logger.log("Style name {} not available.".format(sname), "W")
                    elif tdlang:
                        # Otherwise we'll assume there is only the lang attribute
                        try:
                            td.set('class', 'string {}'.format(lang2font[tdlang].font_tag))
                            del td.attrib['lang'] # lang attribute no longer needed.
                        except KeyError:
                            logger.log("Style for langtag {} not available.".format(tdlang), "W")


            # Ok -- write the html out!
            html = ET.tostring(html_doc, pretty_print=True, method='html', encoding='UTF-8')
            with open(outfname, '+wb')as f:
                f.write(html)


def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
