#!/bin/sh
# Update preflight libs (assumes a pyenv approach)

# Copyright (c) 2023, SIL International  (https://www.sil.org)
# Released under the MIT License (https://opensource.org/licenses/MIT)
# maintained by Nicolas Spalinger

# checking we have pyenv installed 
if ! [ -x "$(command -v pyenv)" ]; then
  echo 'Error: pyenv is not installed. Try "brew install pyenv". ' 
fi

echo ""
echo "Which version of Python are we using? and from where?"
type python3
pyenv versions
echo ""

echo "Installing/Updating pip"
python3 -m pip install --upgrade pip setuptools wheel setuptools_scm
echo ""

echo "Populating/updating the preflight dependencies for the active pyenv interpreter"  

# components in editable mode:
# (with source at the root of the user's home directory so that src/ folder don't appear anywhere else)
python3 -m pip install -e git+https://github.com/silnrsi/pysilfont.git#egg=pysilfont --src "$HOME"/src
# moving to the root of the user's home directory so that src/ folder for editable mode don't appear everywhere

# components from main/master directly from upstream git repositories
python3 -m pip install git+https://github.com/silnrsi/palaso-python.git git+https://github.com/googlefonts/GlyphsLib.git git+https://github.com/fonttools/ufoLib2.git git+https://github.com/fonttools/fonttools.git git+https://github.com/typemytype/glyphConstruction.git git+https://github.com/robotools/fontParts.git --use-pep517

# components from stable releases on pypi
python3 -m pip install fs mutatorMath defcon fontMath lxml

echo ""
echo "Please check these dependencies have been installed correctly: defcon, fontMath, fontTools, glyphConstruction, glyphsLib, MutatorMath, pysilfont, palaso, lxml, ufoLib2 and fontParts. Only these are currently needed for preflight."

echo ""
psfversion

