#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

try:
	import fontforge
except:
	print "*** Warning: Some of the pysilfont utilities require the fontforge python module, see python-fontforge"

long_description =  "A growing collection of font utilities written in Python designed to help with various aspects of font design and production.\n"
long_description += "Developed and maintained by SIL International's Non-Roman Script Initiative (NRSI).\n"
long_description += "Some of these utilites make use of the FontForge Python module."

setup(
		name='pysilfont',
		version='1.0.0',
		description='Python-based font utilities collection',
		long_description=long_description,
		maintainer='NRSI - SIL International',
		maintainer_email='fonts@sil.org',
		url='http://github.com/silnrsi/pysilfont',
		packages = ["silfont"],
		package_dir = {'':'lib'},
		scripts=['scripts/UFOconvert'],
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
