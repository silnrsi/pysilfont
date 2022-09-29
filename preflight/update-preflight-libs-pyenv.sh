#!/bin/sh
# Update preflight libs (assumes a pyenv approach)

# Copyright (c) 2022, SIL International  (http://www.sil.org)
# Released under the MIT License (http://opensource.org/licenses/MIT)
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
python3 -m pip install --upgrade pip
echo ""

echo "Populating/updating the preflight dependencies for the active pyenv interpreter"  

python3 -m pip install -e git+https://github.com/silnrsi/pysilfont.git@master#egg=pysilfont

python3 -m pip install git+https://github.com/googlefonts/GlyphsLib.git@main#egg=glyphsLib git+https://github.com/fonttools/ufoLib2.git@master#egg=ufoLib2 git+https://github.com/fonttools/fonttools.git@main#egg=fontTools git+https://github.com/typemytype/glyphConstruction.git@master#egg=glyphConstruction

python3 -m pip install fs mutatorMath defcon fontMath

echo ""
echo "Please check these dependencies have been installed correctly: defcon, fontMath, fontTools, glyphConstruction, glyphsLib, MutatorMath, pysilfont and ufoLib2. Only these are currently needed for preflight."

echo ""
psfversion

