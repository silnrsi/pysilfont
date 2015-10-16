This folder contains actions for use in Mac OS X based on tools in pysilfont.

UFO NORMALIZE

This action takes a .ufo (Unified Font Object) and normalizes the file to standardize the formatting. Some of the changes include:
  - standard indenting in the xml files
  - sorting plists alphabetically
  - uniform handling of capitals & underscores in glif filenames

To install and use the UFO Normalize action:

- install the pysilfont package using the steps in INSTALL.txt (important!)
- copy the action to your ~/Library/Services folder
- right-click on a UFO file, and choose Services>UFO Normalize

The action first makes a copy of the UFO in a backups subfolder.
