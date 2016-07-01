#!/usr/bin/env python
'''Change graphite names within GDL based on a csv list in format
        old name, newname
    Logs any names not in list
    Also updates postscript names in postscript() statements based on psnames csv'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import os, re
import sys # Temp

argspec = [
    ('input',{'help': 'Input file or folder'}, {'type': 'filename'}),
    ('output',{'help': 'Output file or folder', 'nargs': '?'}, {}),
    ('-n','--names',{'help': 'Names csv file'}, {'type': 'incsv', 'def': 'gdlmap.csv'}),
    ('--names2',{'help': '2nd names csv file', 'nargs': '?'}, {'type': 'incsv', 'def': None}),
    ('--psnames',{'help': 'PS names csv file'}, {'type': 'incsv', 'def': 'psnames.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'GDLnameSwitch.log'})]

def doit(args) :
    logger = args.paramsobj.logger

    exceptions = ("glyph", "gamma", "greek_circ")

    # Process input which may be a single file or a directory
    input = args.input
    gdlfiles = []

    if os.path.isdir(input) :
        inputisdir = True
        indir = input
        for name in os.listdir(input) :
            ext = os.path.splitext(name)[1]
            if ext in  ('.gdl','.gdh') :
                gdlfiles.append(name)
    else :
        inputisdir = False
        indir,inname = os.path.split(input)
        gdlfiles = [inname]

    # Process output file name - execute() will not have processed file/dir name at all
    output = "" if args.output is None else args.output
    outdir,outfile = os.path.split(output)
    if outfile is not "" and os.path.splitext(outfile)[1] == "" : # if no extension on outfile, assume a dir was meant
        outdir = os.path.join(outdir,outfile)
        outfile = None
    if outfile == "" : outfile = None
    if outfile and inputisdir : logger.log("Can't specify an output file when input is a directory", "S")
    outappend = None
    if outdir is "" :
        if outfile is None :
            outappend = "_out"
        else :
            if outfile == gdlfiles[0] : logger.log("Specify a different output file", "S")
        outdir = indir
    else:
        if indir == outdir :
            if outfile :
                if outfile == gdlfiles[0] : logger.log("Specify a different output file", "S")
            else:
                logger.log("Specify a different output dir", "S")
        if not os.path.isdir(outdir) : logger.log("Output directory does not exist", "S")

    # Process names csv file
    args.names.numfields = 2
    names = {}
    for line in args.names : names[line[0]] = line[1]

    # Process names2 csv if present
    names2 = args.names2
    if names2 is not None :
        names2.numfields = 2
        for line in names2 :
            n1 = line[0]
            n2 = line[1]
            if n1 in names and n2 <> names[n1] :
                logger.log(n1 + "in both names and names2 with different values","E")
            else :
                names[n1] = n2

    # Process psnames csv file
    args.psnames.numfields = 2
    psnames = {}
    for line in args.psnames : psnames[line[1]] = line[0]

    missed = []
    psmissed = []
    for filen in gdlfiles:
        file = open(os.path.join(indir,filen),"r")
        if outappend :
            base,ext = os.path.splitext(filen)
            outfilen = base+outappend+ext
            print base,ext,outfilen
        else :
            outfilen = filen
        outfile = open(os.path.join(outdir,outfilen),"w")
        commentblock = False
        for line in file:
            line = line.rstrip()
            # Skip comment blocks
            if line[0:2] == "/*" :
                outfile.write(line + "\n")
                if line.find("*/") == -1 : commentblock = True
                continue
            if commentblock :
                outfile.write(line + "\n")
                if line.find("*/") <> -1 : commentblock = False
                continue
            # Scan for graphite names
            scan = line[0:line.find("//")] if line.find("//") <> -1 else line
            tmpline = ""
            lastend = 0
            for m in re.finditer('[\s(\[,]g\w+?[ )\],?]'," "+scan) :
                gname = m.group(0)[1:-1]
                if gname in names :
                    gname = names[gname]
                else :
                    if gname not in missed and gname not in exceptions :
                        logger.log(gname + " from '" + line.strip() + "' in " + filen + " missing from csv", "W")
                        missed.append(gname) # only log each missed name once
                tmpline = tmpline + line[lastend:m.start()] + gname
                lastend = m.end()-2
            tmpline = tmpline + line[lastend:]
            # Scan for postscript statements
            scan = tmpline[0:tmpline.find("//")] if tmpline.find("//") <> -1 else tmpline
            newline = ""
            lastend = 0

            for m in re.finditer('postscript\(.+?\)',scan) :
                psname = m.group(0)[12:-2]
                if psname in psnames :
                    psname = psnames[psname]
                else :
                    if psname not in psmissed :
                        logger.log(psname + " from '" + line.strip() + "' in " + filen + " missing from ps csv", "W")
                        psmissed.append(psname) # only log each missed name once
                newline = newline + scan[lastend:m.start()+12] + psname
                lastend = m.end()-2

            newline = newline + tmpline[lastend:]
            outfile.write(newline + "\n")
    file.close()
    outfile.close()
    if missed <> [] : logger.log("Names were missed from the csv file - see log file for details","E")
    return

execute("",doit, argspec)
