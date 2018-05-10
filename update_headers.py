#!/usr/bin/env python
'Checks for standard headers and update version and copyright info in python files'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

cyear = "2016" # Year to use if no other copyright year present

from silfont.core import execute
import os,sys

argspec = [
    ('action',{'help': 'Action - report or update', 'nargs': '?', 'default': 'report', 'choices': ('report','update')},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'local/update_headers.log'})]

def doit(args) :
    global file
    action = args.action
    params = args.paramsobj
    logger=params.logger

    varlist = ['url', 'copyright', 'license', 'author', 'version']

    copyrightpre = 'Copyright (c) '
    copyrightpost =  ' SIL International (http://www.sil.org)'

    standards = {
        'copyright': copyrightpre + cyear + copyrightpost,
        'version': params.sets['default']['version'],
        'url': 'http://github.com/silnrsi/pysilfont',
        'license': 'Released under the MIT License (http://opensource.org/licenses/MIT)'}

    pythonfiles = {}
    otherfiles = []

    for subdir, dirs, files in os.walk("."):
        if not (subdir=="." or subdir[0:5] in ("./lib","./scr")) : continue
        if subdir[0:] == "./lib/pysilfont.egg-info" : continue

        for filen in files:
            if filen[-1:]=="~" : continue
            if filen[-3:]=="pyc" : continue
            if filen in ("__init__.py", "ez_setup.py") : continue
            needver = (True if filen in ('setup.py', 'param.py') else False)
            fulln = os.path.join(subdir,filen)
            file = open(fulln,"r")
            line1 = nextline()
            pyline1 = (True if line1 in ("#!/usr/bin/env python", "#!/usr/bin/python") else False)
            if pyline1 or filen[-3:] == ".py" :
                # Look for standard headers
                headererror = []
                headers = "#!/usr/bin/env python"
                if pyline1 :
                    # Read description which may be single or multiline
                    line = nextline()
                    headers = headers + "\n"+line
                    if line[0:3] == "'''" :
                        while line[-3:] != "'''" :
                            line = nextline()
                            if line =="EOF" : break # Must be EOF
                            headers = headers + "\n"+line
                        if line =="EOF" : headererror.append("No closing ''' to description")
                    elif line[0:1] != "'" : headererror.append("No description")
                    if headererror :
                        for line in headererror : logger.log(fulln + ": "+line,"E")
                        continue
                    # Read header variables
                    headvar={}
                    line = nextline()
                    while line[0:2] == "__" :
                        endn = line.find("__ = '")
                        if endn == -1 : std = headererror.append("Invalid variable line: " + line)
                        varn = line[2:endn]
                        val = line[endn+6:-1]
                        headvar[varn] = val
                        line = nextline()
                    # Check header variables
                    updatevars = {}
                    reportvars = {}
                    author = None
                    for varn in varlist :
                        if varn in headvar:
                            headval = headvar[varn]
                            if varn == 'author' : # Simply use existing author
                                author = headval
                            elif varn == "version" and not needver :
                                updatevars[varn] = "deleted"
                            elif varn == "copyright" : # Need to check dates and use oldest
                                # Find existing dates, assuming format 20nn and one or two dates
                                cdate = cyear
                                valid = True
                                datpos = headval.find("20")
                                if datpos != -1 :
                                    # read any more digits
                                    cdate='20'
                                    nextpos = datpos+2
                                    while headval[nextpos] in '0123456789' and nextpos < len(headval) :
                                        cdate = cdate + headval[nextpos]
                                        nextpos += 1
                                    # Look for second date
                                    rest = headval[nextpos:]
                                    datpos = rest.find("20")
                                    date2 = ""
                                    if datpos != -1 :
                                        date2 = '20'
                                        nextpos = datpos+2
                                        while rest[nextpos] in '0123456789' and nextpos < len(rest) :
                                            date2 = date2 + rest[nextpos]
                                            nextpos += 1
                                    cval=int(cdate)
                                    if cval < 2000 or cval > int(cyear) : valid = False
                                    if date2 != "" :
                                        val2 = int(date2)
                                        if val2 < cval or val2 > int(cyear) : valid = False
                                    if not valid : cdate = cyear
                                copyright = copyrightpre + cdate + copyrightpost
                                if headval != copyright :
                                    updatevars[varn] = ("updated" if valid else "update (invalid dates)")
                            else :
                                if headval != standards[varn] :
                                    updatevars[varn] = "updated"
                        else :
                            if varn == 'author' :
                                reportvars[varn] = "no author"
                            elif varn == "version" and not needver :
                                pass
                            else:
                                updatevars[varn] ="added"
                    for varn in headvar:
                        if varn not in varlist: reportvars[varn] = "non-standard"
                else :
                    logger.log( fulln + ": " + "No python header - first line is " + line1, "E")
                    continue
            else :
                otherfiles.append(fulln)
                continue

            # Now have python file with no errors, so can update headers
            if action == 'update' and updatevars :
                logger.log("Updating "+fulln,"P")
                outfile = open("update_headers_temp.txt", "w")
                outfile.write(headers + "\n")
                for varn in varlist :
                    if varn == "version" and not needver :
                        pass
                    elif varn == "author" :
                        if author : outfile.write("__author__ = '" + author + "'\n")
                    elif varn == "copyright" :
                        outfile.write("__copyright__ = '" + copyright + "'\n")
                    else:
                        outfile.write("__" + varn + "__ = '" + standards[varn] + "'\n")
                    if varn in updatevars :
                        reason = updatevars[varn]
                        if reason == "no author" :
                            logger.log("No author header variable ", "I")
                        else :
                            logger.log("Header variable " + varn + " " + reason, "I")
                for varn in reportvars :
                    reason = reportvars[varn]
                    if reason == "non-standard" :
                        outfile.write("__" + varn + "__ = '" + headvar[varn] + "'\n")
                        logger.log("Non-standard header variable " + varn + " retained", "W")
                    else:
                        logger.log("No author header variable", "I")
                # Write the rest of the file
                outfile.write(line + "\n") # last line read checking headers
                for line in file: outfile.write(line)
                outfile.close()
                file.close()
                os.rename(fulln, fulln+"~")
                os.rename("update_headers_temp.txt",fulln)
            else :
                for varn in updatevars :
                    logger.log(fulln + ": Header variable " + varn + " will be " + updatevars[varn], "I")
                for varn in reportvars :
                    reason = reportvars[varn]
                    if reason == "non-standard" :
                        logger.log(fulln + ": Non-standard header variable " + varn + " present", "W")
                    else:
                        logger.log(fulln + ": No author header variable", "I")

    print "\n"+"Non-python files"+"\n"
    for filen in otherfiles:
        print filen

    return

def nextline() :
    global file
    line = file.readline()
    line = ("EOF" if line == "" else line.strip())
    return line

execute(None,doit, argspec)

