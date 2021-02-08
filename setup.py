#!/usr/bin/env python
from __future__ import print_function
'Setuptools installation file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__version__ = '1.5.1.dev0'

import sys, os, importlib

try:
    from setuptools import setup
except ImportError :
    print("pysilfont requires setuptools - see installation notes in README.md")
    sys.exit(1)

if sys.version_info < (3,6): sys.exit('Sorry, Python < 3.6 is not supported')

warnings = []
if sys.argv[1] in ('develop', 'install') :
    for m in ('Brotli', 'defcon', 'fontbakery','fontMath', 'fontParts', 'fontTools', 'glyphConstruction', 'glyphsLib', 'lxml', 'lz4', 'mutatorMath', 'palaso', 'odf', 'ufo2ft', 'ufoLib2'):
        try:
            module = importlib.import_module(m)
        except ImportError : warnings.append("- Some modules/scripts require the python %s package which is not currently installed" % m)

long_description =  "A growing collection of font utilities mainly written in Python designed to help with various aspects of font design and production.\n"
long_description += "Developed and maintained by SIL International's by SIL International's WSTech department (formerly NRSI).\n"
long_description += "Some of these utilites make use of the FontForge Python module."


# Create entry_points console scripts entry
cscripts = []
for file in os.listdir("lib/silfont/scripts/") :
    (base,ext) = os.path.splitext(file)
    if ext == ".py" and base != "__init__" : cscripts.append(base + " = silfont.scripts." + base + ":cmd")

setup(
    name = 'pysilfont',
    version = __version__,
    description = 'Python-based font utilities collection',
    long_description = long_description,
    maintainer = 'SIL International',
    maintainer_email = 'fonts@sil.org',
    url = 'http://github.com/silnrsi/pysilfont',
    packages = ["silfont", "silfont.scripts", "silfont.fbtests"],
    package_dir = {'':'lib'},
    package_data = {"silfont": ["data/*.*"]},
    entry_points={'console_scripts': cscripts},
    license = 'MIT',
    platforms = ['Linux','Win32','Mac OS X'],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Fonts"
        ],
)

if warnings :
    print ("\n***** Warnings *****")
    for warning in warnings : print(warning)

