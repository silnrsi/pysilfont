#!/bin/sh
# Update preflight libs

# Copyright (c) 2022, SIL International  (http://www.sil.org)
# Released under the MIT License (http://opensource.org/licenses/MIT)
# maintained by Nicolas Spalinger

echo "Which python are we using? and from where?"
type python3
python3 --version

echo "Installing/Updating pip"
python3 -m pip install --upgrade pip

echo "Populating/updating the preflight dependencies in user mode"  

python3 -m pip install -e git+https://github.com/silnrsi/pysilfont.git@master#egg=pysilfont git+https://github.com/googlefonts/GlyphsLib.git@main#egg=glyphsLib git+https://github.com/fonttools/ufoLib2.git@master#egg=ufoLib2 git+https://github.com/fonttools/fonttools.git@main#egg=fontTools git+https://github.com/typemytype/glyphConstruction.git@master#egg=glyphConstruction fs mutatorMath defcon fontMath --user 

echo ""
echo "Please check these dependencies have been installed correctly: defcon, fontMath, fontTools, glyphConstruction, glyphsLib, MutatorMath, pysilfont and ufoLib2. Only these are currently needed for preflight."
echo "make sure your PATH includes ~/Library/Python/3.10/bin where the scripts are installed" 
echo "add export PATH=\"\$PATH:\$HOME/Library/Python/3.10/bin\" to ~/.bash_profile or ~/.zshrc"

echo ""
type psfversion
echo ""
psfversion

