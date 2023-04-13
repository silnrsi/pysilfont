#!/usr/bin/env python3
__doc__ = '''Run project-wide checks.  Currently just checking glyph inventory and unicode values for ufo sources in 
the designspace files supplied but maybe expanded to do more checks later'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2022 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
import fontTools.designspaceLib as DSD
import glob, os
import silfont.ufo as UFO
import silfont.etutil as ETU

argspec = [
    ('ds', {'help': 'designspace files to check; wildcards allowed', 'nargs': "+"}, {'type': 'filename'})
]

## Quite a few things are being set and then not used at the moment - this is to allow for more checks to be added in the future.
# For example projectroot, psource

def doit(args):
    logger = args.logger

    # Open all the supplied DS files and ufos within them
    dsinfos = []
    failures = False
    for pattern in args.ds:
        cnt = 0
        for fullpath in glob.glob(pattern):
            cnt += 1
            logger.log(f'Opening {fullpath}', 'P')
            try:
                ds = DSD.DesignSpaceDocument.fromfile(fullpath)
            except Exception as e:
                logger.log(f'Error opening {fullpath}: {e}', 'E')
                failures = True
                break
            dsinfos.append({'dspath': fullpath, 'ds': ds})
        if not cnt: logger.log(f'No files matched {pattern}', "S")
    if failures: logger.log("Failed to open all the designspace files", "S")

    # Find the project root based on first ds assuming the project root is one level above a source directory containing the DS files
    path = dsinfos[0]['dspath']
    (path, base, ext) = splitfn(path)
    (parent,dir) = os.path.split(path)
    projectroot = parent if dir == "source" else None
    logger.log(f'Project root: {projectroot}', "V")

    # Find and open all the unique UFO sources in the DSs
    ufos = {}
    refufo = None
    for dsinfo in dsinfos:
        logger.log(f'Processing {dsinfo["dspath"]}', "V")
        ds = dsinfo['ds']
        for source in ds.sources:
            if source.path not in ufos:
                ufos[source.path] = Ufo(source, logger)
                if not refufo: refufo = source.path # For now use the first found.  Need to work out how to choose the best one

    refunicodes = ufos[refufo].unicodes
    refglyphlist = set(refunicodes)
    (path,refname) = os.path.split(refufo)

    # Now compare with other UFOs
    logger.log(f'Comparing glyph inventory and unicode values with those in {refname}', "P")
    for ufopath in ufos:
        if ufopath == refufo: continue
        ufo = ufos[ufopath]
        logger.log(f'Checking {ufo.name}', "I")
        unicodes = ufo.unicodes
        glyphlist = set(unicodes)
        missing = refglyphlist - glyphlist
        extras = glyphlist - refglyphlist
        both = glyphlist - extras
        if missing: logger.log(f'These glyphs are missing from {ufo.name}: {str(list(missing))}', 'E')
        if extras: logger.log(f'These extra glyphs are in {ufo.name}: {", ".join(extras)}', 'E')
        valdiff = [f'{g}: {str(unicodes[g])}/{str(refunicodes[g])}'
                  for g in both if refunicodes[g] != unicodes[g]]
        if valdiff:
            valdiff = "\n".join(valdiff)
            logger.log(f'These glyphs in {ufo.name} have different unicode values to those in {refname}:\n'
                       f'{valdiff}', 'E')

class Ufo(object): # Read just the bits for UFO needed for current checks for efficientcy reasons
    def __init__(self, source, logger):
        self.source = source
        (path, self.name) = os.path.split(source.path)
        self.logger = logger
        self.ufodir = source.path
        self.unicodes =  {}
        if not os.path.isdir(self.ufodir): logger.log(self.ufodir + " in designspace doc does not exist", "S")
        try:
            self.layercontents = UFO.Uplist(font=None, dirn=self.ufodir, filen="layercontents.plist")
        except Exception as e:
            logger.log("Unable to open layercontents.plist in " + self.ufodir, "S")
        for i in sorted(self.layercontents.keys()):
            layername = self.layercontents[i][0].text
            if layername != 'public.default': continue
            layerdir = self.layercontents[i][1].text
            fulldir = os.path.join(self.ufodir, layerdir)
            self.contents = UFO.Uplist(font=None, dirn=fulldir, filen="contents.plist")
            for glyphn in sorted(self.contents.keys()):
                glifn = self.contents[glyphn][1].text
                glyph = ETU.xmlitem(os.path.join(self.ufodir,layerdir), glifn, logger=logger)
                unicode = None
                for x in glyph.etree:
                    if x.tag == 'unicode':
                        unicode = x.attrib['hex']
                        break
                self.unicodes[glyphn] = unicode

def cmd(): execute('', doit, argspec)
if __name__ == '__main__': cmd()
