#!/usr/bin/env python3
__doc__ = 'Generate a ttf file without OpenType tables from a UFO'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

# Compared to fontmake it does not decompose glyphs or remove overlaps 
# and curve conversion seems to happen in a different way.

from silfont.core import execute
import defcon, ufo2ft.outlineCompiler, ufo2ft.preProcessor, ufo2ft.filters
import re

# ufo2ft v2.32.0b3 uses standard logging and the InstructionCompiler emits errors 
#  when a composite glyph is flattened, so filter out that message 
#  since it is expected in our workflow.
#  The error is legitimate and results from trying to set the flags on components
#   of composite glyphs from the UFO when it's unclear how to match the UFO components
#   to the TTF components.
import logging
class FlattenErrFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith("Number of components differ between UFO and TTF")
logging.getLogger('ufo2ft.instructionCompiler').addFilter(FlattenErrFilter())

argspec = [
    ('iufo', {'help': 'Input UFO folder'}, {}),
    ('ottf', {'help': 'Output ttf file name'}, {}),
    ('--removeOverlaps', {'help': 'Merge overlapping contours', 'action': 'store_true'}, {}),
    ('--decomposeComponents', {'help': 'Decompose componenets', 'action': 'store_true'}, {}),
    ('-c', '--compregex', {'help': "RegEx identifying names of component-only glyphs; remove any that are unreachable",'nargs': '?', 'const': r'^_'}, {}),
    ('-l', '--log', {'help': 'Optional log file'}, {'type': 'outfile', 'def': '_ufo2ttf.log', 'optlog': True})]

PUBLIC_PREFIX = 'public.'

def doit(args):
    # before we get too far, make sure regEx argument, if provided, is legit:
    try:
        compRegEx = re.compile(args.compregex) if args.compregex else None
    except re.error as e:
        args.logger.log(f'Error compiling --compregex argument "{e.pattern}": {e.msg}','S')

    ufo = defcon.Font(args.iufo)

    # if style is Regular and there are no openTypeNameRecords defining the full name (ID=4), then
    # add one so that "Regular" is omitted from the fullname
    if ufo.info.styleName == 'Regular':
        if ufo.info.openTypeNameRecords is None:
            ufo.info.openTypeNameRecords = []
        fullNameRecords = [ nr for nr in ufo.info.openTypeNameRecords if nr['nameID'] == 4]
        if not len(fullNameRecords):
            ufo.info.openTypeNameRecords.append( { 'nameID': 4, 'platformID': 3, 'encodingID': 1, 'languageID': 1033, 'string': ufo.info.familyName } )

#    args.logger.log('Converting UFO to ttf and compiling fea')
#    font = ufo2ft.compileTTF(ufo,
#        glyphOrder = ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'),
#        useProductionNames = False)

    args.logger.log('Converting UFO to ttf without OT', 'P')

    # default arg value for TTFPreProcessor class: removeOverlaps = False, convertCubics = True
    preProcessor = ufo2ft.preProcessor.TTFPreProcessor(ufo, removeOverlaps = args.removeOverlaps, convertCubics=True,
                                                       flattenComponents = True,
                                                       skipExportGlyphs = ufo.lib.get("public.skipExportGlyphs", []))

    # Need to handle cases if filters that are used are set in com.github.googlei18n.ufo2ft.filters with lib.plist
    dc = dtc = ftpos = None
    for (i,filter) in enumerate(preProcessor.preFilters):
        if isinstance(filter, ufo2ft.filters.decomposeComponents.DecomposeComponentsFilter):
            dc = True
        if isinstance(filter, ufo2ft.filters.decomposeTransformedComponents.DecomposeTransformedComponentsFilter):
            dtc = True
        if isinstance(filter, ufo2ft.filters.flattenComponents.FlattenComponentsFilter):
            ftpos = i
    # Add decomposeComponents if --decomposeComponents is used
    if args.decomposeComponents and not dc: preProcessor.preFilters.append(
        ufo2ft.filters.decomposeComponents.DecomposeComponentsFilter())
    # Add decomposeTransformedComponents if not already set via lib.plist
    if not dtc: preProcessor.preFilters.append(ufo2ft.filters.decomposeTransformedComponents.DecomposeTransformedComponentsFilter())
    # Remove flattenComponents if set via lib.plist since we set it via flattenComponents = True when setting up the preprocessor
    if ftpos: preProcessor.preFilters.pop(ftpos)

    glyphSet = preProcessor.process()
    outlineCompiler = ufo2ft.outlineCompiler.OutlineTTFCompiler(ufo,
        glyphSet=glyphSet,
        glyphOrder=ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'))
    font = outlineCompiler.compile()

    # handle uvs glyphs until ufo2ft does it for us.
    if 'public.unicodeVariationSequences' not in ufo.lib:
        uvsdict = getuvss(ufo)
        if len(uvsdict):
            from fontTools.ttLib.tables._c_m_a_p import cmap_format_14
            cmap_uvs = cmap_format_14(14)
            cmap_uvs.platformID = 0
            cmap_uvs.platEncID = 5
            cmap_uvs.cmap = {}
            cmap_uvs.uvsDict = uvsdict
            font['cmap'].tables.append(cmap_uvs)

    if compRegEx:
        ftshake(font, compRegEx, args.logger)

    args.logger.log('Saving ttf file', 'P')
    font.save(args.ottf)

    args.logger.log('Done', 'P')

def getuvss(ufo):
    uvsdict = {}
    uvs = ufo.lib.get('org.sil.variationSequences', None)
    if uvs is not None:
        for usv, dat in uvs.items():
            usvc = int(usv, 16)
            pairs = []
            uvsdict[usvc] = pairs
            for k, v in dat.items():
                pairs.append((int(k, 16), v))
        return uvsdict
    for g in ufo:
        uvs = getattr(g, 'lib', {}).get("org.sil.uvs", None)
        if uvs is None:
            continue
        codes = [int(x, 16) for x in uvs.split()]
        if codes[1] not in uvsdict:
            uvsdict[codes[1]] = []
        uvsdict[codes[1]].append((codes[0], (g.name if codes[0] not in g.unicodes else None)))
    return uvsdict

def ftshake(f, componentNameRE, logger):
    '''Using fontTools subsetter, Remove unreachable components that match the provided RegEx '''
    from fontTools import subset

    gnames = set(f.getGlyphSet().keys())
    allComponents = set(filter(componentNameRE.search, gnames))
    neededComponents = set()
    gtable = f['glyf']

    # In case nested composites haven't yet been flattened, use
    # recursion to make sure all components that are actually 
    # needed are identified
    def markneeded(gname):
        if gname in allComponents:
            neededComponents.add(gname)
        g = gtable[gname]
        if g.isComposite():
            for c in g.components:
                markneeded(c.glyphName)

    for gname in gnames - allComponents:
        markneeded(gname)

    toDelete = allComponents-neededComponents
    toKeep = gnames - toDelete

    # copied from nototools.subset
    opt = subset.Options()
    opt.name_IDs = ["*"]
    opt.name_legacy = True
    opt.name_languages = ["*"]
    opt.layout_features = ["*"]
    opt.notdef_outline = True
    opt.recalc_bounds = True
    # opt.recalc_timestamp = True
    # opt.canonical_order = True

    # Added for glyphshaker:
    opt.layout_features = ["*"]
    opt.layout_scripts = ["*"]
    opt.drop_tables = []
    opt.passthrough_tables = True
    opt.glyph_names = True
    opt.legacy_cmap = True
    opt.prune_unicode_ranges = False
    opt.prune_codepage_ranges = False

    # Invoke the subsetter!
    subsetter = subset.Subsetter(options=opt)
    subsetter.populate(glyphs=toKeep)
    subsetter.subset(f)
    logger.log(f'Subsetter: Of {len(gnames)} glyphs, found {len(allComponents)} matching components but can remove {len(toDelete)}, leaving {len(gnames)-len(toDelete)}.', 'P')

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
