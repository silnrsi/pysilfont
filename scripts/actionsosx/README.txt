This folder contains actions for use in Mac OS X based on tools in pysilfont.

UFO2 NORMALIZE

This action takes a .ufo (Unified Font Object) and converts it to a UFO v2 source font. If the original .ufo is v2 then it effectively normalizes the file to make it more like the UFOv2 files produced by tools such as Robofab. Some of the changes include:
  - sorting plists alphabetically
  - uniform handling of capitals & underscores in glif filenames

To install and use the UFO2 Normalize action:

- install the pysilfont pacakge using the steps in INSTALL.txt (important!)
- copy the action to your ~/Library/Services folder
- right-click on a UFO file, and choose 'UFO2 Normalize'

The action first saves the original .ufo as (filename).ufo.orig which is displayed as a folder rather than a single package bundle. To recover the original .ufo, simply remove .orig from the folder name.
