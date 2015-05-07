#!/usr/bin/env python

from setuptools import setup, find_packages
from glob import glob
import platform, sys

try:
	import fontforge
except:
	print "*** Warning: pysilfont requires the fontforge python module, see python-fontforge"

setup(
		name='pysilfont',
		version='0.0.1',
		description='Python-based font utilities collection and framework (often using FontForge)',
		long_description="A growing collection of font utilities written in Python designed to help with various aspects of font design and production. Developed and maintained by SIL Internationals' NRSI (Non-Roman Script Initiative). Many of these utilites make use of the FontForge Python module.",
		maintainer='NRSI - SIL International',
		maintainer_email='fonts@sil.org',
		url='http://github.com/silnrsi/pysilfont',
		packages = ["silfont"],
		scripts=glob("scripts/*.py"),
		license='MIT',
		platforms=['Linux','Win32','Mac OS X'],
		package_dir={'':'lib'},
		include_package_data=True,
		requires=['fontforge'],
		classifiers=[
		"Environment :: Console",
		"Programming Language :: Python :: 2.7",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Topic :: Text Processing :: Fonts",
		],
)


