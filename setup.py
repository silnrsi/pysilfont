#!/usr/bin/env python
'Setuptools installation file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__version__ = '1.1.1'

import sys

try:
	from setuptools import setup
except ImportError :
    print "pysilfont requires setuptools - see INSTALL.txt"
    sys.exit(1)

warnings = []
try:
	import fontTools
except ImportError : warnings.append("- Some modules require the python fonttools package which is not currently installed")

try:
	import odf
except ImportError : warnings.append("- Some modules require the python odfpy package which is not currently installed")

long_description =  "A growing collection of font utilities mainly written in Python designed to help with various aspects of font design and production.\n"
long_description += "Developed and maintained by SIL International's Non-Roman Script Initiative (NRSI).\n"
long_description += "Some of these utilites make use of the FontForge Python module."

setup(
    name = 'pysilfont',
    version = __version__,
    description = 'Python-based font utilities collection',
    long_description = long_description,
    maintainer = 'NRSI - SIL International',
    maintainer_email = 'fonts@sil.org',
    url = 'http://github.com/silnrsi/pysilfont',
    packages = ["silfont",
        "silfont.comp",
        "silfont.ftml",
        "silfont.gdl",
        "silfont.ufo",
        "silfont.scripts"
        ],
    package_dir = {'':'lib'},
    entry_points={
        'console_scripts': [
            'UFOconvert = silfont.scripts.UFOconvert:cmd',
            'ftml2odt = silfont.scripts.ftml2odt:cmd',
            ],
        },
    license = 'MIT',
    platforms = ['Linux','Win32','Mac OS X'],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Fonts"
        ],
)

if warnings :
    print
    print "***** Warnings *****"
    for warning in warnings : print warning

