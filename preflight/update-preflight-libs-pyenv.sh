#!/bin/sh
# Update preflight libs (assumes a pyenv approach)

# Copyright (c) 2023, SIL International  (https://www.sil.org)
# Released under the MIT License (https://opensource.org/licenses/MIT)
# maintained by Nicolas Spalinger

echo "Update preflight libs pyenv - version 2023-08-09"

# checking we have pyenv installed 
if ! [ -x "$(command -v pyenv)" ]; then
  echo 'Error: pyenv is not installed. Check the workflow doc for details. '
  exit 0
fi

echo ""
echo "Active python version and location (via pyenv):"
pyenv version
type python3
echo ""

echo "Installing/Updating pip"
python3 -m pip install --upgrade pip setuptools wheel setuptools_scm
echo ""

echo "Populating/updating the preflight dependencies for the active pyenv interpreter"  

# components in editable mode:
# (with source at the root of the user's home directory so that src/ folders don't appear anywhere else)
python3 -m pip install -e git+https://github.com/silnrsi/pysilfont.git#egg=pysilfont --src "$HOME"/src

# components from main/master directly from upstream git repositories
python3 -m pip install git+https://github.com/silnrsi/palaso-python.git git+https://github.com/googlefonts/GlyphsLib.git git+https://github.com/fonttools/ufoLib2.git git+https://github.com/fonttools/fonttools.git git+https://github.com/typemytype/glyphConstruction.git git+https://github.com/robotools/fontParts.git --use-pep517

# components from stable releases on pypi
python3 -m pip install fs mutatorMath defcon fontMath lxml

echo ""
if [ -x "$(which psfpreflightversion)" ]; then
	psfpreflightversion
    else echo "psfpreflightversion not installed yet, re-run the install script"
fi
