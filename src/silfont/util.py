#!/usr/bin/env python3
'General classes and functions for use in pysilfont scripts'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import os, subprocess, difflib, sys, io, json
from silfont.core import execute
from pkg_resources import resource_filename
from csv import reader as csvreader

try:
    from fontTools.ttLib import TTFont
except Exception as e:
    TTFont = None

class dirTree(dict) :
    """ An object to hold list of all files and directories in a directory
        with option to read sub-directory contents into dirTree objects.
        Iterates through readSub levels of subfolders
        Flags to keep track of changes to files etc"""
    def __init__(self,dirn,readSub = 9999) :
        self.removedfiles = {} # List of files that have been renamed or deleted since reading from disk
        for name in os.listdir(dirn) :
            if name[-1:] == "~" : continue
            item=dirTreeItem()
            if os.path.isdir(os.path.join(dirn, name)) :
                item.type = "d"
                if readSub :
                    item.dirtree = dirTree(os.path.join(dirn,name),readSub-1)
            self[name] = item

    def subTree(self,path) : # Returns dirTree object for a subtree based on subfolder name(s)
        # 'path' can be supplied as either a relative path (eg "subf/subsubf") or array (eg ['subf','subsubf']
        if type(path) in (bytes, str): path = self._split(path)
        subf=path[0]
        if subf in self:
            dtree =  self[subf].dirtree
        else : return None

        if len(path) == 1 :
            return dtree
        else :
            path.pop(0)
            return dtree.subTree(path)

    def _split(self,path) : # Turn a relative path into an array of subfolders
        npath = [os.path.split(path)[1]]
        while os.path.split(path)[0] :
            path = os.path.split(path)[0]
            npath.insert(0,os.path.split(path)[1])
        return npath

class dirTreeItem(object) :

    def __init__(self, type = "f", dirtree = None, read = False, added = False, changed = False, towrite = False, written = False, fileObject = None, fileType = None, flags = {}) :
        self.type = type                # "d" or "f"
        self.dirtree = dirtree          # dirtree for a sub-directory
        # Remaining properties are for calling scripts to use as they choose to track actions etc
        self.read = read                # Item has been read by the script
        self.added = added              # Item has been added to dirtree, so does not exist on disk
        self.changed = changed          # Item has been changed, so may need updating on disk
        self.towrite = towrite          # Item should be written out to disk
        self.written = written          # Item has been written to disk
        self.fileObject = fileObject    # An object representing the file
        self.fileType = fileType        # The type of the file object
        self.flags = {}                 # Any other flags a script might need

    def setinfo(self, read = None, added = None, changed = None, towrite = None, written = None, fileObject = None, fileType = None, flags = None) :
        pass
        if read : self.read = read
        if added : self.added = added
        if changed : self.changed = changed
        if towrite: self.towrite = towrite
        if written : self.written = written
        if fileObject is not None : self.fileObject = fileObject
        if fileType : self.fileType = fileType
        if flags : self.flags = flags

class ufo_diff(object): # For diffing 2 ufos as part of testing
    # returncodes:
    #   0 - ufos are the same
    #   1 - Differences were found
    #   2 - Errors running the difference (eg can't open file)
    # diff - text of the differences
    # errors - text of the errors

    def __init__(self, ufo1, ufo2, ignoreOHCtime=True):

        diffcommand = ["diff", "-r", "-c1", ufo1, ufo2]

        # By default, if only difference in fontinfo is the openTypeHeadCreated timestamp ignore that

        if ignoreOHCtime: # Exclude fontinfo if only diff is openTypeHeadCreated
                          # Otherwise leave it in so differences are reported by main diff
            fi1 = os.path.join(ufo1,"fontinfo.plist")
            fi2 = os.path.join(ufo2, "fontinfo.plist")
            fitest = subprocess.Popen(["diff", fi1, fi2, "-c1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            text = fitest.communicate()
            if fitest.returncode == 1:
                difftext = text[0].decode("utf-8").split("\n")
                if difftext[4].strip() == "<key>openTypeHeadCreated</key>" and len(difftext) == 12:
                    diffcommand.append("--exclude=fontinfo.plist")

        # Now do the main diff
        test = subprocess.Popen(diffcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = test.communicate()
        self.returncode = test.returncode
        self.diff = text[0].decode("utf-8")
        self.errors = text[1]

    def print_text(self): # Print diff info or errors from the diffcommand
        if self.returncode == 0:
            print("UFOs are the same")
        elif self.returncode == 1:
            print("UFOs are different")
            print(self.diff)
        elif self.returncode == 2:
            print("Failed to compare UFOs")
            print(self.errors)

class text_diff(object): # For diffing 2 text files with option to ignore common timestamps
    # See ufo_diff for class attribute details

    def __init__(self, file1, file2, ignore_chars=0, ignore_firstlinechars = 0):
        # ignore_chars - characters to ignore from left of each line; typically 20 for timestamps
        # ignore_firstlinechars - as above, but just for first line, eg for initial comment in csv files, typically 22
        errors = []
        try:
            f1 = [x[ignore_chars:-1].replace('\\','/') for x in io.open(file1, "r", encoding="utf-8").readlines()]
        except IOError:
            errors.append("Can't open " + file1)
        try:
            f2 = [x[ignore_chars:-1].replace('\\','/') for x in io.open(file2, "r", encoding="utf-8").readlines()]
        except IOError:
            errors.append("Can't open " + file2)
        if errors == []: # Indicates both files were opened OK
            if ignore_firstlinechars:  # Ignore first line for files with first line comment with timestamp
                f1[0] = f1[0][ignore_firstlinechars:-1]
                f2[0] = f2[0][ignore_firstlinechars:-1]
            self.errors = ""
            self.diff = "\n".join([x for x in difflib.unified_diff(f1, f2, file1, file2, n=0)])
            self.returncode = 0 if self.diff == "" else 1
        else:
            self.diff = ""
            self.errors = "\n".join(errors)
            self.returncode = 2

    def print_text(self): # Print diff info or errors the unified_diff command
        if self.returncode == 0:
            print("Files are the same")
        elif self.returncode == 1:
            print("Files are different")
            print(self.diff)
        elif self.returncode == 2:
            print("Failed to compare Files")
            print(self.errors)

class ttf_diff(object): # For diffing 2 ttf files.  Differences are not listed
    # See ufo_diff for class attribute details

    def __init__(self, file1, file2):
        errors=[]
        if TTFont is None:
            self.diff=""
            self.errors="Testing failed - class ttf_diff requires fontTools to be installed"
            self.returncode = 2
            return

        # Open the ttf files
        try:
            font1 = TTFont(file1)
        except Exception as e:
            errors.append("Can't open " + file1)
            errors.append(e.__str__())
        try:
            font2 = TTFont(file2)
        except Exception as e:
            errors.append("Can't open " + file2)
            errors.append(e.__str__())
        if errors:
            self.diff = ""
            self.errors = "\n".join(errors)
            self.returncode = 2
            return

        # Create ttx xml strings from each font
        ttx1 = _ttx()
        ttx2 = _ttx()
        font1.saveXML(ttx1)
        font2.saveXML(ttx2)

        if ttx1.txt() == ttx2.txt():
            self.diff = ""
            self.errors = ""
            self.returncode = 0
        else:
            self.diff = file1 + " and " + file2 + " are different - compare with external tools"
            self.errors = ""
            self.returncode = 1

    def print_text(self): # Print diff info or errors the unified_diff command
        if self.returncode == 0:
            print("Files are the same")
        elif self.returncode == 1:
            print("Files are different")
            print(self.diff)
        elif self.returncode == 2:
            print("Failed to compare Files")
            print(self.errors)

def test_run(tool, commandline, testcommand, outfont, exp_errors, exp_warnings): # Used by tests to run commands
    sys.argv = commandline.split(" ")
    (args, font) = execute(tool, testcommand.doit, testcommand.argspec, chain="first")
    if outfont:
        if tool in ("FT", "FP"):
            font.save(outfont)
        else:  # Must be Pyslifont Ufont
            font.write(outfont)
    args.logger.logfile.close() # Need to close the log so that the diff test can be run
    exp_counts = (exp_errors, exp_warnings)
    actual_counts = (args.logger.errorcount, args.logger.warningcount)
    result = exp_counts == actual_counts
    if not result: print("Mis-match of logger errors/warnings: " + str(exp_counts) + " vs " + str(actual_counts))
    return result

def test_diffs(dirname, testname, extensions): # Used by test to run diffs on results files based on extensions
    result = True
    for ext in extensions:
        resultfile = os.path.join("local/testresults", dirname, testname + ext)
        referencefile = os.path.join("tests/reference", dirname, testname + ext)
        if ext == ".ufo":
            diff = ufo_diff(resultfile, referencefile)
        elif ext == ".csv":
            diff = text_diff(resultfile, referencefile, ignore_firstlinechars=22)
        elif ext in (".log", ".lg"):
            diff = text_diff(resultfile, referencefile, ignore_chars=20)
        elif ext == ".ttf":
            diff = ttf_diff(resultfile, referencefile)
        else:
            diff = text_diff(resultfile, referencefile)

        if diff.returncode:
                    diff.print_text()
                    result = False
    return result

class _ttx(object): # Used by ttf_diff()

    def __init__(self):
        self.lines = []

    def write(self, line):
        if not("<checkSumAdjustment value=" in line or "<modified value=" in line) :
            self.lines.append(line)

    def txt(self):
        return "".join(self.lines)

# Functions for mapping color def to names based on the colors provided by app UIs
namestocolorslist = {
    'g_red': '0.85,0.26,0.06,1',    # g_ names refers to colors definable using the Glyphs UI
    'g_orange': '0.99,0.62,0.11,1',
    'g_brown': '0.65,0.48,0.2,1',
    'g_yellow': '0.97,1,0,1',
    'g_light_green': '0.67,0.95,0.38,1',
    'g_dark_green': '0.04,0.57,0.04,1',
    'g_cyan': '0,0.67,0.91,1',
    'g_blue': '0.18,0.16,0.78,1',
    'g_purple': '0.5,0.09,0.79,1',
    'g_pink': '0.98,0.36,0.67,1',
    'g_light_gray': '0.75,0.75,0.75,1',
    'g_dark_gray': '0.25,0.25,0.25,1'
}
colorstonameslist = {v: k for k, v in namestocolorslist.items()}

def nametocolor(color, default=None):
    global namestocolorslist
    if default is not None:
        return namestocolorslist.get(color,default)
    else:
        return namestocolorslist.get(color)

def colortoname(color, default=None):
    global colorstonameslist
    if default:
        return colorstonameslist.get(color,default)
    else:
        return colorstonameslist.get(color)

def parsecolors(colors, single = False, allowspecial = False): # Process a list of colors - designed for handling command-line input
    # Colors can be in RBGA format (eg (0.25,0.25,0.25,1)) or text name (eg g_dark_grey), separated by commas.
    # Function returns a list of tuples, one per color, (RGBA, name, logcolor, original color after splitting)
    # If the color can't be parsed, RGBA will be None and logocolor contain an error message
    # If single is set, just return one tuple rather than a list of tuples
    # Also can allow for special values of 'none' and 'leave' if allowspecial set

    # First tidy up the input string
    cols = colors.lower().replace(" ", "")

    if single: # If just one color, don't need to split the string and can allow for RGBA without brackets
        splitcols = ["(" + cols + ")"] if cols[0] in ("0", "1") else [cols]
    else:
        # Since RGBA colors which have parentheses and then commas within them, so can't just split on commas so add @ signs for first split
        cols = cols.replace(",(", "@(").replace("),", ")@").split("@")
        splitcols = []
        for color in cols:
            if color[0] == "(":
                splitcols.append(color)
            else:
                splitcols = splitcols + color.split(',')
    parsed = []
    for splitcol in splitcols:
        if allowspecial and splitcol in ("none", "leave"):
            RGBA = ""
            name = splitcol
            logcolor = splitcol
        else:
            errormess = ""
            name = ""
            RGBA = ""
            if splitcol[0] == '(':
                values = splitcol[1:-1].split(',') # Remove parentheses then split on commas
                if len(values) != 4:
                    errormess = "RGBA colours must have 4 values"
                else:
                    for i in (0, 1, 2, 3):
                        values[i] = float(values[i])
                        if values[i] < 0 or values[i] > 1: errormess = "RGBA values must be between 0 and 1"
                    if values[0] + values[1] + values[2] == 0: errormess = "At lease one RGB value must be non-zero"
                    if values[3] == 0: errormess = "With RGBA, A must not be zero"
                if errormess == "":
                    for i in (0, 1, 2, 3):
                        v = values[i]
                        if v == int(v): v = int(v)  # Convert integers to int type for correct formatting with str()
                        RGBA += str(v) + ","
                    RGBA = RGBA[0:-1]  # Strip trialing comma
                    name = colortoname(RGBA, "")
            else:
                name = splitcol
                RGBA = nametocolor(name)
                if RGBA is None: errormess = "Invalid color name"
            if errormess:
                logcolor = "Invalid color: " + splitcol + " - " + errormess
                RGBA = None
                name = None
            else:
                logcolor = RGBA
                if name: logcolor += " (" + name + ")"
        parsed.append((RGBA, name, logcolor,splitcol))
    if single: parsed = parsed[0]

    return parsed

# Provide dict of required characters which match the supplied list of sets - sets can be basic, rtl or sil
def required_chars(sets="basic"):
    if type(sets) == str: sets = (sets,) # Convert single string to a tuple
    rcfile = open(resource_filename('silfont','data/required_chars.csv'))
    rcreader = csvreader(rcfile)
    next(rcreader) # Read fist line which is headers
    rcdict = {}
    for line in rcreader:
        unicode = line[0][2:]
        item = {
            "ps_name": line[1],
            "glyph_name": line[2],
            "sil_set": line[3],
            "rationale": line[4],
            "notes": line[5]
        }
        if item["sil_set"] in sets: rcdict[unicode] = item
    return rcdict

# Pretty print routine for json files.
def prettyjson(data, oneliners=None, indent="", inkey=None, oneline=False):
    # data - json data to format
    # oneliners - lists of keys for which data should be output on a single line
    # indent, inkey & oneline - used when prettyjson calls itself interactively for sub-values that are dicts
    res = ["{"]
    thisoneline = oneline and (oneliners is None or inkey not in oneliners)
    for key, value in sorted(data.items()):
        line = ("" if thisoneline else indent) + '"{}": '.format(key)
        if isinstance(value, dict):
            val = prettyjson(value, oneliners=oneliners,
                             indent = indent + "    ", inkey = key,
                             oneline=(oneline if oneliners is None or key not in oneliners else True))
        else:
            val = json.dumps(value, ensure_ascii=False)
        res.append(line + val + ",")
    res[-1] = res[-1][:-1]
    res.append(("" if thisoneline else indent[:-4]) + "}")
    return (" " if thisoneline else "\n").join(res)

