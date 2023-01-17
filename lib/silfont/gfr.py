#!/usr/bin/env python
'''General classes and functions for use with SIL's github fonts repository, github.com/silnrsi/fonts
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2022 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import os, sys, json
import silfont.core
from silfont.util import prettyjson
from csv import reader as csvreader
from collections import OrderedDict

familyfields = OrderedDict([
    ("familyid",      {"opt": True,  "manifest": False}),
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

class familydata(object):
    """Family data key for use with families.json, font manifests and base files
    """
    def __init__(self, id=None, data=None, filename = None, type="f", logger=None):
        # Initial input can be a dictionary (data) in which case id nneds to be set
        # or it can be read from a file (containing just one family record), in which case id is taken from the file
        # Type can be f, b or m for families, base or manifest
        self.id = id
        self.data = data if data else {}
        self.filename = filename
        self.type = type
        self.logger = logger if logger else silfont.core.loggerobj()

    def fieldscheck(self, data, validfields, reqfields, logprefix, valid, logs):
        for key in data: # Check all keys have valid names
            if key not in validfields:
                logs.append((f'{logprefix}: Invalid field {key}', 'W'))
                valid = False
                continue
        # Are required fields present
        for key in reqfields:
            if key not in data:
                logs.append((f'{logprefix}: Required field {key} missing', 'W'))
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
        print(validfields)
        print(reqfields)
        (valid, logs) = self.fieldscheck(self.data, validfields, reqfields, "XXX", valid, logs)
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
            (valid, logs) = self.fieldscheck(ddata, validfields, reqfields, "Defaults:", valid, logs)

        return (valid, logs)

    def read(self, filename=None): # Read data from file
        if filename: self.filename = filename
        with open(self.filename) as inf:
            filedata = json.load(inf)
            if len(filedata) != 1:
                self.logger(f'Files must contain just one record; {filename} has {len(filedata)}')
            self.id = list(filedata.keys())[0]
            self.data = filedata[self.id]

    def write(self, filename=None):
        if filename is None: filename = self.filename
        print(f'Writing to {filename}')
        filedata = {self.id: self.data}
        with open(filename, "w", encoding="utf-8") as outf:
            outf.write(prettyjson(filedata, oneliners=["files"]))

