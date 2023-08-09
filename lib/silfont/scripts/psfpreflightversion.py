#!/usr/bin/env python3
__doc__ = 'Display version info for pysilfont and dependencies, but only for preflight'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2023, SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import sys
import importlib
import silfont

def cmd():
    """gather the deps"""

    deps = (  # (module, used by, min recommended version)
        ('defcon', '?', ''),
        ('fontMath', '?', ''),
        ('fontParts', '?', ''),
        ('fontTools', '?', ''),
        ('glyphConstruction', '?', ''),
        ('glyphsLib', '?', ''),
        ('lxml','?', ''),
        ('mutatorMath', '?', ''),
        ('palaso', '?', ''),
        ('ufoLib2', '?', ''),
        )

    # Pysilfont info
    print("Pysilfont " + silfont.__copyright__ + "\n")
    print("   Version:           " + silfont.__version__)
    print("   Commands in:       " + sys.argv[0][:-10])
    print("   Code running from: " + silfont.__file__[:-12])
    print("   using:             Python " + sys.version.split(' \n', maxsplit=1)[0])

    for dep in deps:
        name = dep[0]

        try:
            module = importlib.import_module(name)
            path = module.__file__
            # Remove .py file name from end
            pyname = path.split("/")[-1]
            path = path[:-len(pyname)-1]
            version = "No version info"
            for attr in ("__version__", "version", "VERSION"):
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    break
        except Exception as e:
            etext = str(e)
            if etext == "No module named '" + name + "'":
                version = "Module is not installed"
            else:
                version = "Module import failed with " + etext
            path = ""

        print('{:20} {:15} {}'.format(name + ":", version, path))

if __name__ == "__main__": cmd()
