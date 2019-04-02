#!/usr/bin/env python
from __future__ import print_function
'Display version info for pysilfont and dependencies'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import sys, imp
import silfont

def cmd() :

    deps = (  # (module, used by, min reccomended version)
        ('defcon', '?', ''),
        ('fontMath', '?', ''),
        ('fontParts', '?', ''),
        ('fontTools', '?', ''),
        ('glyphConstruction', '?', ''),
        ('glyphsLib', '?', ''),
        ('harfbuzz', '?', ''),
        ('icu', '?', ''),
        ('lz4', '?', ''),
        ('mutatorMath', '?', ''),
        ('odf', '?', ''),
        ('ufo2ft', '?', ''),
        )

    # Pysilfont info
    print("Pysilfont " + silfont.__copyright__ + "\n")
    print("   Version:           " + silfont.__version__)
    print("   Commands in:       " + sys.argv[0][:-10])
    print("   Code running from: " + silfont.__file__[:-12])
    print("   using:             Python " + sys.version.split(" \n")[0] + "\n")

    for dep in deps:
        name = dep[0]
        try:
            (fp, path, desc) = imp.find_module(name)
            module = imp.load_module(name, fp, path, desc)
            version = "No version info"
            for attr in ("__version__", "version", "VERSION"):
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    break

        except ImportError as e:
            etext = str(e)
            if etext == "No module named '" + name + "'":
                version = "Module is not installed"
            else:
                version = "Module import failed with " + etext
            path = ""

        print('{:20} {:15} {}'.format(name + ":", version, path))


    return

if __name__ == "__main__": cmd()
