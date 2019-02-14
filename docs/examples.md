# Pysilfont example scripts

In addition to the main pysilfont [scripts](scripts.md), there are many further scripts under pysilfont/examples and its sub-directories.

They are not maitained in the same way as the main scripts, and come in many categories including:

- Scripts under development
- Examples of how to do things
- Deprecated scripts
- Left-overs from previous development plans!

Some are documented below.

## Table of scripts

| Command | Status | Description |
| ------- | ------ | ----------- |
| [accesslibplist.py](#accesslibplist.py) | ? | Demo script for accessing fields in lib.plist |
| [chaindemo.py](#chaindemo.py) | ? | Demo of how to chain calls to multiple scripts together |
| [FFmapGdlNames.py](#FFmapGdlNames.py) | ? | Write mapping of graphite names to new graphite names |
| [FfmapGdlNames2.py](#FfmapGdlNames2.py) | ? | Write mapping of graphite names to new graphite names |
| [FLWriteXml.py](#FLWriteXml.py) | ? | Outputs attachment point information and notes as XML file for TTFBuilder |
| [FTaddEmptyOT.py](#FTaddEmptyOT.py) | ? | Add empty Opentype tables to ttf font |
| [FTMLnorm.py](#FTMLnorm.py) | ? | Normalize an FTML file |
| [psfaddGlyphDemo.py](#psfaddGlyphDemo.py) | ? | Demo script to add a glyph to a UFO font |
| [psfbuildcompgc.py](#psfbuildcompgc.py) | ? | Uses the GlyphConstruction library to build composite glyphs |
| [psfdupglyphsfp.py](#psfdupglyphsfp.py) | ? | Duplicates glyphs in a UFO based on a csv definition |
| [psfexpandstroke.py](#psfexpandstroke.py) | ? | Expands an unclosed UFO stroke font into monoline forms with a fixed width |
| [psfexportnamesunicodesfp.py](#psfexportnamesunicodesfp.py) | ? | Outputs an unsorted csv file containing the names of all the glyphs in the default layer |
| [psfgenftml.py](#psfgenftml.py) | ? | generate ftml tests from glyph_data.csv and UFO |
| [psfmakedeprecated.py](#psfmakedeprecated.py) | ? | Creates deprecated versions of glyphs |
| [psftoneletters.py](#psftoneletters.py) | ? | Creates Latin script tone letters (pitch contours) |
| [xmlDemo.py](#xmlDemo.py) | ? | Demo script for use of ETWriter |



---
#### accesslibplist.py
Usage: **` python accesslibplist.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script for accessing fields in lib.plist


---
#### chaindemo.py
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
#### FFmapGdlNames.py
Usage: **` python FFmapGdlNames2.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Write mapping of graphite names to new graphite names based on:
   - two ttf files
   - the gdl files produced by makeGdl run against those fonts
        This could be different versions of makeGdl
   - a csv mapping glyph names used in original ttf to those in the new font


---
#### FFmapGdlNames2.py
Usage: **` python FFmapGdlNames.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Write mapping of graphite names to new graphite names based on:
   - an original ttf font
   - the gdl file produced by makeGdl when original font was produced
   - a csv mapping glyph names used in original ttf to those in the new font
   - pysilfont's gdl library - so assumes pysilfonts makeGdl will be used with new font


---
#### FLWriteXml.py
Usage: **` python FLWriteXml.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Outputs attachment point information and notes as XML file for TTFBuilder


---
#### FTaddEmptyOT.py
Usage: **` python FTaddEmptyOT.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Add empty Opentype tables to ttf font


---
#### FTMLnorm.py
Usage: **` python FTMLnorm.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Normalize an FTML file


---
#### psfaddGlyphDemo.py
Usage: **` python psfaddGlyphDemo.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script to add a glyph to a UFO font


---
#### psfbuildcompgc.py
Usage: **` python psfbuildcompgc.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Uses the GlyphConstruction library to build composite glyphs


---
#### psfdupglyphsfp.py
Usage: **` python psfdupglyphsfp.py ...`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Duplicates glyphs in a UFO based on a csv definition: source,target.

Duplicates everything except unicodes.
Mainly a demonstration of using the fontParts library.


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
#### psfexportnamesunicodesfp.py
Usage: **` python psfexportnamesunicodesfp.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Outputs an unsorted csv file containing the names of all the glyphs in the default layer and their primary unicode values.

Format name,usv


---
#### psfgenftml.py
Usage: **` python psfgenftml.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

generate ftml tests from glyph_data.csv and UFO


---
#### psfmakedeprecated.py
Usage: **` python psfmakedeprecated.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Creates deprecated versions of glyphs: takes the specified glyph and creates a
duplicate with an additional box surrounding it so that it becomes reversed,
and assigns a new unicode encoding to it.

Input is a csv with three fields: original,new,unicode


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
#### xmlDemo.py
Usage: **` python xmlDemo.py ...`**

_([Standard options](docs.md#standard-command-line-options) may also apply)_

Demo script for use of ETWriter
