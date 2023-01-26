#!/usr/bin/env python
__doc__ = '''General classes and functions for use with SIL's github fonts repository, github.com/silnrsi/fonts'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2022 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import os, json
from silfont.util import prettyjson
from silfont.core import splitfn, loggerobj
from collections import OrderedDict

familyfields = OrderedDict([
    ("familyid",      {"opt": True,  "manifest": False}), # req for families.json but not for base files; handled in code
    ("fallback",      {"opt": True,  "manifest": False}),
    ("family",        {"opt": False, "manifest": True}),
    ("altfamily",     {"opt": True,  "manifest": False}),
    ("siteurl",       {"opt": True,  "manifest": False}),
    ("packageurl",    {"opt": True,  "manifest": False}),
    ("files",         {"opt": True,  "manifest": True}),
    ("defaults",      {"opt": True,  "manifest": True}),
    ("version",       {"opt": True,  "manifest": True}),
    ("status",        {"opt": True,  "manifest": False}),
    ("license",       {"opt": True,  "manifest": False}),
    ("distributable", {"opt": False, "manifest": False}),
    ("source",        {"opt": True,  "manifest": False}),
    ("googlefonts",   {"opt": True,  "manifest": False}),
    ("features",      {"opt": True,  "manifest": False})
    ])

filefields = OrderedDict([
    ("altfamily",   {"opt": True,  "manifest": True, "mopt": True}),
    ("url",         {"opt": True,  "manifest": False}),
    ("flourl",      {"opt": True,  "manifest": False}),
    ("packagepath", {"opt": True,  "manifest": True}),
    ("axes",        {"opt": False, "manifest": True})
    ])

defaultsfields = OrderedDict([
    ("ttf",   {"opt": True, "manifest": True}),
    ("woff",  {"opt": True, "manifest": True, "mopt": True}),
    ("woff2", {"opt": True, "manifest": True, "mopt": True})
    ])

class _familydata(object):
    """Family data key for use with families.json, font manifests and base files
    """
    def __init__(self, id=None, data=None, filename = None, type="f", logger=None):
        # Initial input can be a dictionary (data) in which case id nneds to be set
        # or it can be read from a file (containing just one family record), in which case id is taken from the file
        # Type can be f, b or m for families, base or manifest
        # With f, this would be for just a single entry from a families.json file
        self.id = id
        self.data = data if data else {}
        self.filename = filename
        self.type = type
        self.logger = logger if logger else loggerobj()

    def fieldscheck(self, data, validfields, reqfields, logprefix, valid, logs):
        for key in data: # Check all keys have valid names
            if key not in validfields:
                logs.append((f'{logprefix}: Invalid field "{key}"', 'W'))
                valid = False
                continue
        # Are required fields present
        for key in reqfields:
            if key not in data:
                logs.append((f'{logprefix}: Required field "{key}" missing', 'W'))
                valid = False
                continue
        return (valid, logs)

    def validate(self):
        global familyfields, filefields, defaultsfields
        logs = []
        valid = True
        if self.type == "m":
            validfields = reqfields = [key for key in familyfields if familyfields[key]["manifest"]]
        else:
            validfields = list(familyfields)
            reqfields = [key for key in familyfields if not familyfields[key]["opt"]]
        (valid, logs) = self.fieldscheck(self.data, validfields, reqfields, "Main", valid, logs)
        # Now check sub-fields
        if "files" in self.data:
            fdata = self.data["files"]
            if self.type == "m":
                validfields = [key for key in filefields if filefields[key]["manifest"]]
                reqfields = [key for key in filefields if filefields[key]["manifest"] and not ("mopt" in filefields[key] and filefields[key]["mopt"])]
            else:
                validfields = list(filefields)
                reqfields = [key for key in filefields if not filefields[key]["opt"]]
            # Now need to check values for each record in files
            for filen in fdata:
                frecord = fdata[filen]
                (valid, logs) = self.fieldscheck(frecord, validfields, reqfields, "Files: " + filen, valid, logs)
                if "axes" in frecord: # (Will already have been reported above if axes is missing!)
                    adata = frecord["axes"]
                    avalidfields = [key for key in adata if len(key) == 4]
                    areqfields = ["wght", "ital"] if self.type == "m" else []
                    (valid, logs) = self.fieldscheck(adata, avalidfields, areqfields, "Files, axes: " + filen, valid, logs)
        if "defaults" in self.data:
            ddata = self.data["defaults"]
            if self.type == "m":
                validfields = [key for key in defaultsfields if defaultsfields[key]["manifest"]]
                reqfields = [key for key in defaultsfields if defaultsfields[key]["manifest"] and not ("mopt" in defaultsfields[key] and defaultsfields[key]["mopt"])]
            else:
                validfields = list(defaultsfields)
                reqfields = [key for key in defaultsfields if not defaultsfields[key]["opt"]]
                if self.type == "f":
                    reqfields = reqfields + ["familyid"]
                else: # Must be b
                    validfields = validfields + ["hosturl", "filesroot"]

            (valid, logs) = self.fieldscheck(ddata, validfields, reqfields, "Defaults:", valid, logs)
        return (valid, logs)

    def read(self, filename=None): # Read data from file (not for families.json)
        if filename: self.filename = filename
        with open(self.filename) as infile:
            filedata = json.load(infile)
            if len(filedata) != 1:
                self.logger.log(f'Files must contain just one record; {self.filename} has {len(filedata)}')
            self.id = list(filedata.keys())[0]
            self.data = filedata[self.id]

    def write(self, filename=None): # Write data to a file (not for families.json)
        if filename is None: filename = self.filename
        self.logger.log(f'Writing to {filename}', 'P')
        filedata = {self.id: self.data}
        with open(filename, "w", encoding="utf-8") as outf:
            outf.write(prettyjson(filedata, oneliners=["files"]))

class gfr_manifest(_familydata):
    #
    def __init__(self, id=None, data=None, filename = None, logger=None):
        super(gfr_manifest, self).__init__(id=id, data=data, filename=filename, type="m", logger=logger)

    def validate(self, version=None, filename=None):
        # Validate the manifest.
        # If version is supplied, check that that matches the version in the manifest
        # If self.filename not already set, the filename of the manifest must be supplied

        (valid, logs) = super(gfr_manifest, self).validate() # Field name validation based on _familydata validation

        if filename is None: filename = self.filename
        data = self.data

        if "files" in data:
            files = data["files"]
            mfilelist = {x: files[x]["packagepath"] for x in files}

            # Check files that are on disk match the manifest files
            (path, base, ext) = splitfn(filename)
            fontexts = ['.ttf', '.woff', '.woff2']
            dfilelist = {}
            for dirname, subdirs, filenames in os.walk(path):
                for filen in filenames:
                    (base, ext) = os.path.splitext(filen)
                    if ext in fontexts:
                        dfilelist[filen] = (os.path.relpath(os.path.join(dirname, filen), start=path))

            if mfilelist == dfilelist:
                logs.append(('Files OK', 'I'))
            else:
                valid = False
                logs.append(('Files on disk and in manifest do not match.', 'W'))
                logs.append(('Files on disk:', 'I'))
                for filen in sorted(dfilelist):
                    logs.append((f'     {dfilelist[filen]}', 'I'))
                logs.append(('Files in manifest:', 'I'))
                for filen in sorted(mfilelist):
                    logs.append((f'     {mfilelist[filen]}', 'I'))

            if "defaults" in data:
                defaults = data["defaults"]
                # Check defaults exist
                allthere = True
                for default in defaults:
                    if defaults[default] not in mfilelist: allthere = False

                if allthere:
                    logs.append(('Defaults OK', 'I'))
                else:
                    valid = False
                    logs.append(('At least one default missing', 'W'))

        if version:
            if "version" in data:
                mversion = data["version"]
                if version == mversion:
                    logs.append(('Versions OK', 'I'))
                else:
                    valid = False
                    logs.append((f'Version mismatch: {version} supplied and {mversion} in manifest', "W"))

        return (valid, logs)

class gfr_base(_familydata):
    #
    def __init__(self, id=None, data=None, filename = None, logger=None):
        super(gfr_base, self).__init__(id=id, data=data, filename=filename, type="b", logger=logger)

class gfr_family(object): # For families.json.
    #
    def __init__(self, data=None, filename=None, logger=None):
        self.filename = filename
        self.logger = logger if logger else loggerobj()
        self.familyrecords = {}
        if data is not None: self.familyrecords = data

    def validate(self, familyid=None):
        allvalid = True
        alllogs = []
        if familyid:
            record = self.familyrecords[familyid]
            (allvalid, alllogs) = record.validate()
        else:
            for familyid in self.familyrecords:
                record = self.familyrecords[familyid]
                (valid, logs) = record.validate()
            if not valid:
                allvalid = False
                alllogs.append(logs)
        return allvalid, alllogs

    def write(self, filename=None): # Write data to a file
        if filename is None: filename = self.filename
        self.logger.log(f'Writing to {filename}', "P")
        with open(filename, "w", encoding="utf-8") as outf:
            outf.write(prettyjson(self.familyrecords, oneliners=["files"]))

def setpaths(logger): # Check that the script is being run from the root of the repository and set standard paths
    repopath = os.path.abspath(os.path.curdir)
    # Do cursory checks that this is the root of the fonts repo
    if repopath[-6:] != "/fonts" or not os.path.isdir(os.path.join(repopath, "fonts/sil")):
        logger.log("GFR scripts must be run from the root of the fonts repo", "S")
    # Set up standars paths for scripts to use
    silpath = os.path.join(repopath, "fonts/sil")
    otherpath = os.path.join(repopath, "fonts/other")
    basespath = os.path.join(repopath, "basefiles")
    if not os.path.isdir(basespath): os.makedirs(basespath)
    return repopath, silpath, otherpath, basespath