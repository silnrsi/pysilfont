# Pysilfont example scripts

In addition to the main pysilfont [scripts](scripts.md), there are many further scripts under pysilfont/examples and its sub-directories.

They are not maintained in the same way as the main scripts, and come in many categories including:

- Scripts under development
- Examples of how to do things
- Deprecated scripts
- Left-overs from previous development plans!

Note - all FontForge-based scripts need updating, since FontForge (as "FF") is no longer a supported tool for execute()

Some are documented below.

## Table of scripts

| Command | Status | Description |
| ------- | ------ | ----------- |
| [accesslibplist.py](#accesslibplist) | ? | Demo script for accessing fields in lib.plist |
| [chaindemo.py](#chaindemo) | ? | Demo of how to chain calls to multiple scripts together |
| [ffchangeglyphnames](#ffchangeglyphnames) | ? | Update glyph names in a ttf font based on csv file |
| [ffcopyglyphs](#ffcopyglyphs) | ? | Copy glyphs from one font to another, without using ffbuilder |
| [ffremovealloverlaps](#ffremovealloverlaps) | ? | Remove overlap on all glyphs in a ttf font |
| [FFmapGdlNames.py](#ffmapgdlnames) | ? | Write mapping of graphite names to new graphite names |
| [FFmapGdlNames2.py](#ffmapgdlnames2) | ? | Write mapping of graphite names to new graphite names |
| [FLWriteXml.py](#flwritexml) | ? | Outputs attachment point information and notes as XML file for TTFBuilder |
| [FTaddEmptyOT.py](#ftaddemptyot) | ? | Add empty Opentype tables to ttf font |
| [FTMLnorm.py](#ftmlnorm) | ? | Normalize an FTML file |
| [psfaddGlyphDemo.py](#psfaddglyphdemo) | ? | Demo script to add a glyph to a UFO font |
| [psfexpandstroke.py](#psfexpandstroke) | ? | Expands an unclosed UFO stroke font into monoline forms with a fixed width |
| [psfexportnamesunicodesfp.py](#psfexportnamesunicodesfp) | ? | Outputs an unsorted csv file containing the names of all the glyphs in the default layer |
| [psfgenftml.py](#psfgenftml) | ? | generate ftml tests from glyph_data.csv and UFO |
| [psftoneletters.py](#psftoneletters) | ? | Creates Latin script tone letters (pitch contours) |
| [xmlDemo.py](#xmldemo) | ? | Demo script for use of ETWriter |


---
#### accesslibplist
Usage: **` python accesslibplist.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script for accessing fields in lib.plist


---
#### chaindemo
Usage: **` python chaindemo.py ...`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Demo of how to chain calls to multiple scripts together.
Running

`python chaindemo.py infont outfont --featfile feat.csv --uidsfile uids.csv`

will run execute() against psfnormalize, psfsetassocfeat and psfsetassocuids passing the font, parameters
and logger objects from one call to the next.  So:
- the font is only opened once and written once
- there is a single log file produced


---
#### ffchangeglyphnames
Usage: **`ffchangeglyphnames [-i INPUT] [--reverse] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Update the glyph names in a ttf font based on csv file.

Example usage:

```
ffchangeglyphnames -i glyphmap.csv font.ttf
```
will update the glyph names in the font based on mapping file glyphmap.csv

If \-\-reverse  is used, it change names in reverse.

---
####  ffcopyglyphs
Usage: **`ffcopyglyphs -i INPUT [-r RANGE] [--rangefile RANGEFILE] [-n NAME] [--namefile NAMEFILE] [-a] [-f] [-s SCALE] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

_This section is Work In Progress!_

optional arguments:

```
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Font to get glyphs from
  -r RANGE, --range RANGE
                        StartUnicode..EndUnicode no spaces, e.g. 20..7E
  --rangefile RANGEFILE
                        File with USVs e.g. 20 or a range e.g. 20..7E or both
  -n NAME, --name NAME  Include glyph named name
  --namefile NAMEFILE   File with glyph names
  -a, --anchors         Copy across anchor points
  -f, --force           Overwrite existing glyphs in the font
  -s SCALE, --scale SCALE
                        Scale glyphs by this factor
```

---
#### ffremovealloverlaps
Usage: **`ffremovealloverlaps ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Remove overlap on all glyphs in a ttf font

---
#### FFmapGdlNames
Usage: **` python FFmapGdlNames2.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Write mapping of graphite names to new graphite names based on:
   - two ttf files
   - the gdl files produced by makeGdl run against those fonts
        This could be different versions of makeGdl
   - a csv mapping glyph names used in original ttf to those in the new font


---
#### FFmapGdlNames2
Usage: **` python FFmapGdlNames.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Write mapping of graphite names to new graphite names based on:
   - an original ttf font
   - the gdl file produced by makeGdl when original font was produced
   - a csv mapping glyph names used in original ttf to those in the new font
   - pysilfont's gdl library - so assumes pysilfonts makeGdl will be used with new font


---
#### FLWriteXml
Usage: **` python FLWriteXml.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Outputs attachment point information and notes as XML file for TTFBuilder


---
#### FTaddEmptyOT
Usage: **` python FTaddEmptyOT.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Add empty Opentype tables to ttf font


---
#### FTMLnorm
Usage: **` python FTMLnorm.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Normalize an FTML file


---
#### psfaddGlyphDemo
Usage: **` python psfaddGlyphDemo.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script to add a glyph to a UFO font


---
#### psfexpandstroke

Usage: **`psfexpandstroke infont outfont expansion`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Expands the outlines (typically unclosed) in an UFO stroke font into monoline forms with a fixed width.

Example that expands the stokes in a UFO font `SevdaStrokeMaster-Regular.ufo` by 13 units on both sides, giving them a total width of 26 units, and writes the result to `Sevda-Regular.ufo`.

```
psfexpandstroke SevdaStrokeMaster-Regular.ufo Sevda-Regular.ufo 13
```

Note that this only expands the outlines - it does not remove any resulting overlap.


---
#### psfexportnamesunicodesfp
Usage: **` python psfexportnamesunicodesfp.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Outputs an unsorted csv file containing the names of all the glyphs in the default layer and their primary unicode values.

Format name,usv


---
#### psfgenftml
Usage: **` python psfgenftml.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

generate ftml tests from glyph_data.csv and UFO


---
####  psftoneletters
Usage: **`psftoneletters infont outfont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This uses the parameters from the UFO lib.plist org.sil.lcg.toneLetters key to create Latin script tone letters (pitch contours).

Example usage:

```
psftoneletters Andika-Regular.ufo Andika-Regular.ufo
```


---
#### xmlDemo
Usage: **` python xmlDemo.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script for use of ETWriter
