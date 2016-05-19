#!/usr/bin/env python
'Checks for standard headers and update version and copyright info in python files'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014-2016, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '2.0.0'

import silfont.param
from silfont.util import execute
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
    standards = {
        'version': params.sets['default']['version'],
        'copyright': params.sets['default']['copyright'],
        'url': 'http://github.com/silnrsi/pysilfont',
        'license': 'Released under the MIT License (http://opensource.org/licenses/MIT)'}

    pythonfiles = {}
    otherfiles = []

    for subdir, dirs, files in os.walk("."):
        if not (subdir=="." or subdir[0:5] in ("./lib","./scr")) : continue
        lib = (True if subdir[0:5] == "./lib" else False)
        for filen in files:
            if filen[-1:]=="~" : continue
            if filen[-3:]=="pyc" : continue
            if filen in ("__init__.py", "ez_setup.py") : continue
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
                        while line[-3:] <> "'''" :
                            line = nextline()
                            if line =="EOF" : break # Must be EOF
                            headers = headers + "\n"+line
                        if line =="EOF" : headererror.append("No closing ''' to description")
                    elif line[0:1] <> "'" : headererror.append("No description")
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
                            if varn == 'author' :
                                author = headvar[varn]
                            elif varn == "version" and not lib :
                                updatevars[varn] = "deleted"
                            else :
                                if headvar[varn] <> standards[varn] :
                                    updatevars[varn] = "updated"
                        else :
                            if varn == 'author' :
                                reportvars[varn] = "no author"
                            elif varn == "version" and not lib :
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
                if filen <> 'dwr.py' : continue
                outfile = open("update_headers_temp.txt", "w")
                outfile.write(headers + "\n")
                for varn in varlist :
                    if varn == "version" and not lib :
                        pass
                    elif varn == "author" :
                        if author : outfile.write("__author__ = '" + author + "'\n")
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

    '''print "\n"+"Non-python files"+"\n"
    for filen in otherfiles:
        print filen
    '''


    return

def nextline() :
    global file
    line = file.readline()
    line = ("EOF" if line == "" else line.strip())
    return line

execute(None,doit, argspec)

