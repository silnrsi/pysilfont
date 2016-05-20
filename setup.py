#!/usr/bin/env python
'Setuptools installation file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__version__ = '1.1.0'

try:
	from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

long_description =  "A growing collection of font utilities mainly written in Python designed to help with various aspects of font design and production.\n"
long_description += "Developed and maintained by SIL International's Non-Roman Script Initiative (NRSI).\n"
long_description += "Some of these utilites make use of the FontForge Python module."

setup(
		name='pysilfont',
		version=__version__,
		description='Python-based font utilities collection',
		long_description=long_description,
		maintainer='NRSI - SIL International',
		maintainer_email='fonts@sil.org',
		url='http://github.com/silnrsi/pysilfont',
		packages = ["silfont",
            "silfont.compdef",
            "silfont.ftml",
            "silfont.gdl",
            "silfont.ufo",
                   ],
		package_dir = {'':'lib'},
		scripts=['scripts/UFOconvert', 'scripts/makeGdl'],
		license='MIT',
		platforms=['Linux','Win32','Mac OS X'],
		classifiers=[
		"Environment :: Console",
		"Programming Language :: Python :: 2.7",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Topic :: Text Processing :: Fonts",
		],
)
