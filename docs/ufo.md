# Pysilfont - ufo.py technical docs

This document is Work in Progess!

## UFO 2 or UFO 3?

The Ufont() object model UFO 3 based, so UFO 2 format fonts are converted to UFO 3 when read and then converted back to UFO 2 when written out to disk.  Unless a script has code that is specific to a particular UFO format, scripts do not need to know the format of the font that was opened; rather they can just work in the UFO 3 format and leave the conversion to the library.

The main differences this makes in practice are:
- **Layers** The Ufont() always has layers. With UFO 2 fonts, there will be only one, and it can be accessed via Ufont.defaultlayer
- **Anchors** If a UFO 2 font uses the accepted practice of anchors being single point contours with a name and a type of "Move" then
  - On reading the font, they will be removed from the list of contours and added to the list of anchors
  - On writing the font, they will be added back into the list of contours
