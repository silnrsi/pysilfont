#!/usr/bin/env python
__doc__ = '''Update and/or sort glyph_data.csv based on input file(s)'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import csv

argspec = [
    ('glyphdata', {'help': 'glyph_data csv file to update'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
    ('outglyphdata', {'help': 'Alternative output file name', 'nargs': '?'}, {'type': 'filename', 'def': None}),
    ('-a','--addcsv',{'help': 'Records to add to glyphdata'}, {'type': 'incsv', 'def': None}),
    ('-d', '--deletions', {'help': 'Records to delete from glyphdata'}, {'type': 'incsv', 'def': None}),
    ('-s', '--sortheader', {'help': 'Column header to sort by'}, {}),
    ('--sortalpha', {'help': 'Use with sortheader to sort alphabetically not numerically', 'action': 'store_true', 'default': False}, {}),
    ('-f', '--force', {'help': 'When adding, if glyph exists, overwrite existing data', 'action': 'store_true', 'default': False}, {}),
    ('-l','--log',{'help': 'Log file name'}, {'type': 'outfile', 'def': 'setglyphdata.log'}),
    ]

def doit(args):
    logger = args.logger
    gdcsv = args.glyphdata
    addcsv = args.addcsv
    dellist = args.deletions
    sortheader = args.sortheader
    force = args.force

    # Check arguments are valid
    if not(addcsv or dellist or sortheader): logger.log("At least one of -a, -d or -s must be specified", "S")
    if force and not addcsv: logger.log("-f should only be used with -a", "S")

    #
    # Process the glyph_data.csv
    #

    # Process the headers line
    gdheaders = gdcsv.firstline
    if 'glyph_name' not in gdheaders: logger.log("No glyph_name header in glyph data csv", "S")
    gdcsv.numfields = len(gdheaders)
    gdheaders = {header: col for col, header in enumerate(gdheaders)} # Turn into dict of form header: column
    gdnamecol = gdheaders["glyph_name"]
    if sortheader and sortheader not in gdheaders:
        logger.log(sortheader + " not in glyph data headers", "S")
    next(gdcsv.reader, None)  # Skip first line with headers in

    # Read the data in
    logger.log("Reading in existing glyph data file", "P")
    gddata = {}
    gdorder = []
    for line in gdcsv:
        gname = line[gdnamecol]
        gddata[gname] = line
        gdorder.append(gname)

    # Delete records from dellist

    if dellist:
        logger.log("Deleting items from glyph data based on deletions file", "P")
        dellist.numfields = 1
        for line in dellist:
            gname = line[0]
            if gname in gdorder:
                del gddata[gname]
                gdorder.remove(gname)
                logger.log(gname + " deleted from glyph data", "I")
            else:
                logger.log(gname + "not in glyph data", "W")

    #
    # Process the addcsv, if present
    #

    if addcsv:
        # Check if addcsv has headers; if not use gdheaders
        addheaders = addcsv.firstline
        headerssame = True
        if 'glyph_name' in addheaders:
            if addheaders != gdcsv.firstline: headerssame = False
            next(addcsv.reader)
        else:
            addheaders = gdheaders

        addcsv.numfields = len(addheaders)
        addheaders = {header: col for col, header in enumerate(addheaders)}  # Turn into dict of form header: column
        addnamecol = addheaders["glyph_name"]

        logger.log("Adding new records from add csv file", "P")
        for line in addcsv:
            gname = line[addnamecol]
            logtype = "added to"
            if gname in gdorder:
                if force: # Remove existing line
                    logtype = "replaced in"
                    del gddata[gname]
                    gdorder.remove(gname)
                else:
                    logger.log(gname + " already in glyphdata so new data not added", "W")
                    continue
            logger.log(f'{gname} {logtype} glyphdata', "I")

            if not headerssame: # need to construct new line based on addheaders
                newline = []
                for header in gdheaders:
                    val = line[addheaders[header]] if header in addheaders else ""
                    newline.append(val)
                line = newline

            gddata[gname] = line
            gdorder.append(gname)

    # Finally sort the data if sortheader supplied
    def numeric(x):
        try:
            numx = float(x)
        except ValueError:
            logger.log(f'Non-numeric value "{x}" in sort column; 0 used for sorting', "E")
            numx = 0
        return numx

    if sortheader:
        sortheaderpos = gdheaders[sortheader]
        if args.sortalpha:
            gdorder = sorted(gdorder, key=lambda x: gddata[x][sortheaderpos])
        else:
            gdorder = sorted(gdorder, key=lambda x: numeric(gddata[x][sortheaderpos]))

    # Now write the data out
    outfile = args.outglyphdata
    if not outfile:
        gdcsv.file.close()
        outfile = gdcsv.filename
    logger.log(f'Writing glyph data out to {outfile}', "P")
    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(gdcsv.firstline)
        for glyphn in gdorder:
            writer.writerow(gddata[glyphn])

def cmd() : execute("",doit,argspec)
if __name__ == "__main__": cmd()

