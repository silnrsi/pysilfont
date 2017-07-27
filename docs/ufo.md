# Pysilfont - ufo support technical docs

# The Basics

UFO support is provided by the ufo.py library.

Most scripts work by reading a UFO into a Ufont object, making changes to it and writing it out again.  The Ufont object contains many separate objects representing the UFO in a UFO 3 based hierarchy, even if the original UFO was format 2 - see [UFO 2 or UFO 3?](#ufo-2-or-ufo-3-) below.

Details of the [Ufont Object Model](#ufont-object-model) are given below, but in summary:

- There is an object for each file within the UFO (based on [xmlitem](technical.md#etutil.py))
- There is an object for each xml element within a parent object (based on [ETelement](technical.md#etutil.py))
- Data within objects can always(?) be accessed via generic methods based on the xml element tags
- For much data, there are object-specific methods to access data, which is easier than the generic methods

For example, a .glif file is:
- Read into a Uglif object which has:
  - Methods for glyph-level data (eg name, format)
  - objects for all the sub-elements within a glyph (eg advance, outline)
  - Where an element type can only appear once in a glyph, eg advance, Uglif.*element-name* returns the relevant object
  - Where an element can occur multiple times (eg anchor), Uglif.*element-name* returns a list of objects
- If an sub-element itself has sub-elements, then there are usually sub-element objects for that following the same pattern, eg Uglif.outline has lists of Ucontour and Ucomponent objects

It is planned that more object-specific methods will be added as needs arise, so raise in issue if you see specific needs that are likely to be useful in multiple scripts.



### UFO 2 or UFO 3?

The Ufont() object model UFO 3 based, so UFO 2 format fonts are converted to UFO 3 when read and then converted back to UFO 2 when written out to disk.  Unless a script has code that is specific to a particular UFO format, scripts do not need to know the format of the font that was opened; rather they can just work in the UFO 3 format and leave the conversion to the library.

The main differences this makes in practice are:
- **Layers** The Ufont() always has layers. With UFO 2 fonts, there will be only one, and it can be accessed via Ufont.deflayer
- **Anchors** If a UFO 2 font uses the accepted practice of anchors being single point contours with a name and a type of "Move" then
  - On reading the font, they will be removed from the list of contours and added to the list of anchors
  - On writing the font, they will be added back into the list of contours

Despite being based on UFO 3 (for future-proofing), nearly all use of Pysilfont's UFO scripts has been with UFO 2-based projects so testing with UFO 3 has been minimal - and there are some [known limitations](docs.md#known-limitations).


# Ufont Object Model

A **Ufont** object represents the font using the following objects:

- font.**metainfo**: [Uplist](#uplist) object created from metainfo.plist
- font.**fontinfo**: [Uplist](#uplist) object created from fontinfo.plist, if present
- font.**groups**: [Uplist](#uplist) object created from groups.plist, if present
- font.**kerning**: [Uplist](#uplist) object created from kerning.plist, if present
- font.**lib**: [Uplist](#uplist) object created from lib.plist, if present
- self.**layercontents**: [Uplist](#uplist) object
  - created from layercontents.plist for UFO 3 fonts
  - synthesized based on the font's single layer for UFO 2 fonts
- font.**layers**: List of [Ulayer](#ulayer) objects, where each layer contains:
  - layer.**contents**: [Uplist](#uplist) oject created from contents.plist
  - layer[**_glyph name_**]: A [Uglif](#uglif) object for each glyph in the font which contains:
    - glif['**advance**']: Uadvance object
    - glif['**unicode**']: List of Uunicode objects
    - glif['**note**']: Unote object (UFO 3 only)
    - glif['**image**']: Uimage object (UFO 3 only)
    - glif['**guideline**']: List of Uguideline objects (UFO 3 only)
    - glif['**anchor**']: List of Uanchor objects
    - glif['**outline**']: Uoutline object which contains
      - outline.**contours**: List of Ucontour objects
      - outline.**components**: List of Ucomponent objects
    - glif['**lib**']: Ulib object
- font.**features**: UfeatureFile created from features.fea, if present

## General Notes

Except for UfeatureFile (and Ufont itself), all the above objects are set up as [immutable containers](technical.md#immutable-containers), though the contents, if any, depend on the particular object.

Objects usually have a link back to their parent object, eg glif.layer points to the Ulayer object containing that glif.

## Specific classes

**Note - the sections below don't list all the class details** so also look in the code in ufo.py if you need something not listed - it might be there!

### Ufont

In addition to the objects listed above, a Ufont object contains:
- self.params: The [parameters](parameters.md) object for the font
- self.paramsset: The parameter set within self.params specific to the font
- self.logger: The logger object for the script
- self.ufodir: Text string of the UFO location
- self.UFOversion: from formatVersion in metainfo.plist
- self.dtree: [dirTree](technical.md#dirtree) object representing all the files on fisk and their status
- self.outparams: The output parameters for the font, initially set from self.paramset
- self.deflayer:
  - The single layer for UFO 2 fonts
  - The layer called public.default for UFO 3 fonts

self.write(outputdir) will write the UFO to disk.  For basic scripts this will usually be done by the execute() funtion - see [writing scripts](technical.md#writing-scripts).

self.addfile(type) will add an empty entry for any of the optional plist files (fontinfo, groups, kerning or lib).

When writing to disk, the UFO is always normalized, and only changed files will actually be written to disk.  The format for normalization, as well as the output UFO version, are controlled by values in self.outparams.

### Uplist

Used to represent any .plist file, as listed above.

For each key,value pair in the file, self[key] contains a list:
- self[key][0] is an elementtree element for the key
- self[key][1] is an elementtree element for the value

self.getval(key) will return:
- the value, if the value type is integer, real or string
- a list containing elementree elements if the value type is array
- None, for other value types (which would only occur in lib.plist)
- It will throw an exception if the key does not exist

Methods are available for adding, changing and deleting values - see class \_plist in ufo.py for details.

self.font points to the parent Ufont object

### Ulayer

Represents a layer in the font.  With UFO 2 fonts, a single layer is synthesized from the glifs folder.

For each glyph, layer[glyphname] returns a Uglif object for the glyph.  It has addGlyph and delGlyph functions.

### Uglif

Represents a glyph within a layer.  It has child objects, as listed below, and functions self.add and self.remove for adding and removing them.  For UFO 2 fonts, and contours identified as anchors will have been removed from Uoutline and added as Uanchor objects.

#### glif child objects

There are 8 child objects for a glif:

| Name | Notes | UFO 2 | Multi |
| ---- | -------------------------------- | --- | --- |
| Uadvance | Has width & height attributes | Y |  |
| Uunicode | Has hex attribute | Y | Y |
| Uoutline |  | Y |  |
| Ulib |  | Y | |
| Unote |  | | |
| Uimage |  | | |
| Uguideline |  | | Y |
| Uanchor |  | | Y |

They all have separate object classes, but currently (except for setting attributes), only Uoutline and Ulib have any extra code - though more will be added in the future.

(With **Uanchor**, the conversion between UFO 3 anchors and the UFO 2 way of handling anchors is handled by code in Uglif and Ucontour)

**Ulib** shares a parent class (\_plist) with [Uplist](#uplist) so has the same functionality for managing key,value pairs.

#### Uoutline

This has Ucomponent and Ucontour child objects, with addobject, appendobject and insertobject methods for managing them.

With Ucontour, self['point'] returns a list of the point subelements within the contour, and points can be managed using the methods in Ulelement.  other than that, changes need to be made by changing the elements using elementtree methods.

# Module Developer Notes

To be written
