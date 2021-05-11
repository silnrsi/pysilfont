# Pysilfont commands and scripts

Below is a table listing all the commands installed by Pysilfont followed by descriptions of each command.

All these commands work in consistent ways in terms of certain standard options (eg -h for help) and default names for many files - see details in [Pysilfont Documentation](docs.md#standard-command-line-options).

There are further example scripts supplied with Pysilfont, and some of these are also documented in [examples.md](examples.md)

## Table of scripts

| Command | Description |
| ------- | ----------- |
| [psfaddanchors](#psfaddanchors) | Read anchor data from XML file and apply to UFO |
| [psfbuildcomp](#psfbuildcomp) | Add composite glyphs to UFO based on a Composite Definitions file |
| [psfbuildcompgc](#psfbuildcompgc) | Add composite glyphs to UFO using glyphConstruction based on a CD file |
| [psfbuildfea](#psfbuildfea) | Compile a feature (.fea) file against an existing input TTF |
| [psfchangegdlnames](#psfchangegdlnames) | Change graphite names within GDL based on mappings files |
| [psfchangettfglyphnames](#psfchangettfglyphnames) | Change glyph names in a ttf from working names to production names |
| [psfcheckbasicchars](#psfcheckbasicchars) | Check UFO for glyphs that represent recommended basic characters |
| [psfcheckclassorders](#psfcheckclassorders) | Verify classes defined in xml have correct ordering where needed |
| [psfcheckftml](#psfcheckftml) | Check ftml files for structural integrity |
| [psfcheckglyphinventory](#psfcheckglyphinventory) | Warn for differences in glyph inventory and encoding between UFO and input file (e.g., glyph_data.csv) |
| [psfcompdef2xml](#psfcompdef2xml) | Convert composite definition file to XML format |
| [psfcompressgr](#psfcompressgr) | Compress Graphite tables in a ttf font |
| [psfcopyglyphs](#psfcopyglyphs) | Copy glyphs from one UFO to another with optional scale and rename |
| [psfcopymeta](#psfcopymeta) | Copy basic metadata from one UFO to another, for fonts in related families |
| [psfcreateinstances](#psfcreateinstances) | Create one or more instance UFOs from one or more designspace files |
| [psfcsv2comp](#psfcsv2comp) | Create composite definition file from csv |
| [psfdeflang](#psfdeflang) | Changes default language behaviour in a font |
| [psfdeleteglyphs](#psfdeleteglyphs) | Deletes glyphs from a UFO based on a list |
| [psfdupglyphs](#psfdupglyphs) | Duplicates glyphs in a UFO based on a csv definition |
| [psfexportanchors](#psfexportanchors) | Export UFO anchor data to a separate XML file |
| [psfexportmarkcolors](#psfexportmarkcolors) | Export csv of mark colors |
| [psfexportpsnames](#psfexportpsnames) | Export a map of glyph name to PS name to a csv file |
| [psfexportunicodes](#psfexportunicodes) | Export a map of glyph name to unicode value to a csv file |
| [psffixffglifs](#psffixffglifs) | Make changes needed to a UFO following processing by FontForge |
| [psffixfontlab](#psffixfontlab) | Make changes needed to a UFO following processing by FontLab |
| [psfftml2TThtml](#psfftml2tthtml) | Convert FTML document to html and fonts for testing TypeTuner |
| [psfftml2odt](#psfftml2odt) | Create a LibreOffice Writer file from an FTML test description |
| [psfgetglyphnames](#psfgetglyphnames) | Create a file of glyphs to import from a list of characters to import |
| [psfglyphs2ufo](#psfglyphs2ufo) | Export all the masters in a .glyphs file to UFOs |
| [psfmakedeprecated](#psfmakedeprecated) | Creates deprecated versions of glyphs |
| [psfmakefea](#psfmakefea) | Make a features file base on input UFO or AP database |
| [psfmakescaledshifted](#psfmakescaledshifted) | Creates scaled and shifted versions of glyphs |
| [psfmakewoffmetadata](#psfmakewoffmetadata) | Make the WOFF metadata xml file based on input UFO |
| [psfnormalize](#psfnormalize) | Normalize a UFO and optionally converts it between UFO2 and UFO3 versions |
| [psfremovegliflibkeys](#psfremovegliflibkeys) | Remove keys from glif lib entries |
| [psfrenameglyphs](#psfrenameglyphs) | Within a UFO and class definition, assign new working names to glyphs based on csv input file |
| [psfrunfbchecks](#psfrunfbchecks) | Run Font Bakery checks using a standard profile with option to specify an alternative profile |
| [psfsetassocfeat](#psfsetassocfeat) | Add associate feature info to glif lib based on a csv file |
| [psfsetassocuids](#psfsetassocuids) | Add associate UID info to glif lib based on a csv file |
| [psfsetdummydsig](#psfsetdummydsig) | Add a dummy DSIG table into a TTF font |
| [psfsetglyphorder](#psfsetglyphorder) | Load glyph order data into public.glyphOrder based on a text file |
| [psfsetkeys](#psfsetkeys) | Set key(s) with given value(s) in a UFO p-list file |
| [psfsetmarkcolors](#psfsetmarkcolors) | Set mark colors based on csv file |
| [psfsetpsnames](#psfsetpsnames) | Add public.postscriptname to glif lib based on a csv file |
| [psfsetunicodes](#psfsetunicodes) | Set unicode values for a glif based on a csv file |
| [psfsetversion](#psfsetversion) | Change all the version-related info in a UFO's fontinfo.plist |
| [psfsubset](#psfsubset) | Create a subset of an existing UFO |
| [psfsyncmasters](#psfsyncmasters) | Sync metadata in master UFO files based on a Designspace file |
| [psfsyncmeta](#psfsyncmeta) | Copy basic metadata from one member of a font family to other family members |
| [psftuneraliases](#psftuneraliases) | Merge alias information into TypeTuner feature xml file |
| [psfufo2glyphs](#psfufo2glyphs) | Generate a glyphs files from a designspace file and UFO(s) |
| [psfufo2ttf](#psfufo2ttf) | Generate a ttf file without OpenType tables from a UFO |
| [psfversion](#psfversion) | Display version info for pysilfont and dependencies |
| [psfwoffit](#psfwoffit) | Convert between ttf, woff, and woff2 |
| [psfxml2compdef](#psfxml2compdef) | Convert composite definition file from XML format |

---

####  psfaddanchors
Usage: **`psfaddanchors [-i ANCHORINFO]  [-a] [-r {X,S,E,P,W,I,V}] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

_This section is Work In Progress!_

Read anchor data from XML file and apply to UFO

optional arguments:

```
  -i ANCHORINFO, --anchorinfo ANCHORINFO
                        XML file with anchor data
  -a, --analysis        Analysis only; no output font generated  
  -r {X,S,E,P,W,I,V}, --report {X,S,E,P,W,I,V}
                        Set reporting level for log file
```

---

#### psfbuildfea
Usage: **`psfbuildfea -o output.ttf [-m map.txt] [-v] input.fea input.ttf`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Uses fontTools to compile a feature (.fea) file against an existing input TTF, optionally creating a lookup map.

required arguments:

```
  -o output.ttf, --output output.ttf   Output file to create
  input.fea                            Source features file
  input.ttf                            Source ttf
```

optional arguments:

```
  -m map.txt, --lookupmap map.txt      Mapping file to create
  -v, --verbose                        repeat to increase verbosity
```

If `-m` parameter is supplied, the designated file will be created listing, in alphabetical order by name, each OpenType lookup name, its table (GSUB or GPOS) and its feature index. For example:
```
AlefMark2BelowAfterLam,GPOS,13
AyahAlternates,GSUB,46
CommaAlternates,GSUB,48
```

---

####  psfbuildcomp
Usage: **`psfbuildcomp [-i CDFILE] [-a] [-c] [--colors] [-f] [-n] [--remove] [--preserve] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Creates or updates composite glyphs in a UFO based on an external text file of definitions. The syntax for these definitions is described in [composite.md](composite.md).

Example usage:

```
# add composites to font (making backup first)
psfbuildcomp -i composites.txt font.ufo

# add composites even for glyphs that have outlines, and write to a new font
psfbuildcomp -i comps.txt -f -r V Andika-BoldItalic.ufo new.ufo

# report only, with no change to font
psfbuildcomp -i comps.txt -a -r I font.ufo

# remove unwanted anchors 'above' and 'below', including '_' versions:
psfbuildcomp -i comps.txt --remove "_?(above|below)" font.ufo

# also preserve 'diaA' and 'diaB' on composites that exist but are being replaced:
psfbuildcomp -i comps.txt --remove "_?(above|below)" --preserve "dia[AB]" font.ufo

```

optional arguments:

```
  -i CDFILE, --cdfile CDFILE
                        Composite Definitions input file
  -a, --analysis        Analysis only; no output font generated
  -c, --color           Set the markColor of of generated glyphs dark green
  --colors              Set the markColor of the generated glyphs based on color(s) supplied
                        (more details below)
  -f, --force           Force overwrite of glyphs having outlines
  -n, --noflatten       Do not flatten component references
  --remove REMOVE       a regex matching anchor names that should always be
                        removed from generated composite glyphs
  --preserve PRESERVE   a regex matching anchor names that, if present in
                        glyphs about to be replaced, should not be overwritten
```

Using --colors, three colors can be supplied:

- The first for glyphs already in the font which are unchanged in this run of the script
- The second for glyphs already in the font which are updated
- The third for new glyphs added

If just one color is supplied, this is used for all three uses above

If two colors are supplied, the second is also used for new glyphs

Colors can be specified as described in [Specifying colors on the command line](#specifying-colors-on-the-command-line)

---
####  psfbuildcompgc
Usage: **`psfbuildcompgc [-i CDFILE] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Creates or updates composite glyphs in a UFO based on an external text file of definitions. The syntax for these definitions *not* the same as that described in [composite.md](composite.md). It uses the [GlyphConstruction syntax](https://github.com/typemytype/GlyphConstruction).

Example usage:

```
psfbuildcompgc -i composites.txt font.ufo
```

optional arguments:

```
  -i CDFILE, --cdfile CDFILE
                        Composite Definitions input file
```

---
#### psfchangegdlnames
Usage: **`psfchangegdlnames [-n NAMES] [--names2 [NAMES2]] [--psnames PSNAMES] input [output]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Changes the graphite names within GDL files(s) based on mappings file(s). It can work on an individual file or on all the gdl/gdh files within a folder. It also updates postscript names in postscript() statements

Two mappings files are required (NAMES and PSNAMES).  Optionally a second GDL names mapping file, NAMES2 can be supplied.

The mapping files are csv files of the format `"old name,new name"`. It logs if any graphite names are in the GDL but not found in the mapping files.

Example usage:

```
psfchangegdlnames -n gdlmap.csv --psnames psnames.csv source/graphite
```
will update all the .gdl and.gdh files within the source/graphite folder.

---
#### psfchangettfglyphnames
Usage: **`psfchangettfglyphnames iufo ittf ottf`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Used to change the glyph names in a ttf from working names to production names, typically as the last step in a build sequence.

The name map is obtained from the `public.postscriptNames` attribute in the input UFO and then applied to the input ttf to create the output ttf.

Example usage:

```
psfchangettfglyphnames source/Harmattan-Regular.ufo results/in.ttf results/out.ttf
```

---
#### psfcheckbasicchars
Usage: **`psfcheckbasicchars [-r] [-s] ufo`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Used to check a UFO for the presence of glyphs that represent the characters in the list of 
[Recommended characters for Non-Roman fonts](https://github.com/silnrsi/pysilfont/blob/master/lib/silfont/data/required_chars.csv).
Any missing characters are noted in the resulting log file along with the recommended AGL glyph name.

By default only characters needed for all fonts (both LTR and RTL) will be checked.\
To also check for characters that only RTL fonts need, use the -r option.\
To include characters that are in SIL's PUA block, use the -s option.

Example usage:

```
psfcheckbasicchars Nokyung-Regular.ufo
```

There is more documentation about the character list [here](https://github.com/silnrsi/pysilfont/blob/master/lib/silfont/data/required_chars.md) 
and additional information can be shown on screen or in the log file by increasing the log level to I (-p scrlevel=i or -p loglevel=i)

---
#### psfcheckclassorders
usage: **`psfcheckclassorders [--gname GNAME] [--sort HEADER] [classes] [glyphdata]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Verify classes defined in xml have correct ordering where needed.

Looks for comment lines in the `classes` file that match the string:
```
  *NEXT n CLASSES MUST MATCH*
```
where `n` is the number of upcoming class definitions that must result in the
same glyph alignment when glyph names are sorted by TTF order.

```
optional arguments:
  classes           Class definition file in XML format (default `classes.xml`)
  glyphdata         Glyph info csv file (default `glyph_data.csv`)
  --gname GNAME     Column header for glyph name (default `glyph_name`)
  --sort HEADER     Column header for sort order (default `sort_final`)
```
#### Notes

Classes defined in xml format (typically `source/classes.xml`) can be accessed by both Graphite and OpenType code. For historical reasons there is a difference in the way they are processed: for Graphite (only), the members of the classes are re-ordered based on the glyphIDs in the ttf. 

For classes used just for rule contexts, glyph order doesn't matter. But for classes used for n-to-n substitutions, order *does* matter and the classes have to be "aligned".

Based on the sort order information extracted from the `glyphdata` file, this tool examines specially-marked groups of class definitions from the `classes` file to determine if they remain aligned after classes are reordered, and issues error messages if not. Here is an example identifying a set of three classes that must align:
```
    <!-- *NEXT 3 CLASSES MUST MATCH* -->
        
    <class name='Damma'>
        damma-ar shadda_damma-ar hamza_damma-ar
    </class>
    
    <class name='Damma_filled'>
        damma-ar.filled shadda_damma-ar.filled hamza_damma-ar.filled
    </class>
    
    <class name='Damma_short'>
        damma-ar.short shadda_damma-ar.short hamza_damma-ar.short
    </class>
  ```

Note that the Graphite workflow extracts glyph order from the ttf file, but `psfcheckclassorders` gets it from `glyphdata` argument; there is, therefore, an assumption that the glyph order indicated in `glyphdata` actually matches that in the ttf file.

`psfcheckclassorders` will also issue warning a warning message if there are glyphs named in the `classes` file which are not included in the `glyphdata` file. While this is [intentionally] not an error for either Graphite or OpenType (relavent tools simply ignore such missing glyphs), it may be helpful in catching typos that result in class miss-alignment and therefore bugs.  By default warning messages are sent to the log file;
use `-p scrlevel=W` to also route them to the terminal.

---
#### psfcheckftml
usage: **`psfcheckftml [inftml]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Test structural integrity of one or more ftml files

Assumes ftml files have already validated against [`FTML.dtd`](https://github.com/silnrsi/ftml/blob/master/FTML.dtd), for example by using:

```   xmllint --noout --dtdvalid FTML.dtd inftml.ftml```

`psfcheckftml` verifies that:
  - `silfont.ftml` can parse the file
  - every `stylename` is defined the `<styles>` list 

```
positional arguments:
  inftml                Input ftml filename pattern (default: *.ftml)

other arguments:
  -h, --help            show this help message and exit
  -l LOG, --log LOG     Log file
  -p PARAMS, --params PARAMS
                        Other parameters - see parameters.md for details
  -q, --quiet           Quiet mode - only display severe errors
```

---
#### psfcheckglyphinventory
Usage: **`psfcheckglyphinventory [--indent n] [-i input] ifont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

`psfcheckglyphinventory` compares and warns for differences in glyph inventory and encoding between UFO and input file (e.g., glyph_data.csv).
input file can be:
- simple text file with one glyph name per line
- csv file with headers, using headers `glyph_name` and, if present, `USV`

required arguments:

```
  ifont       input UFO
```

optional arguments:
```
  -i INPUT, --input INPUT
              input file, default is glyph_data.csv in current directory
  -indent n   number of spaces to indent output lists (default 10)
```

---
#### psfcompdef2xml
Usage: **`psfcompdef2xml [-p PARAMS] input output log`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Convert composite definition file to XML format

_This section is Work In Progress!_

  input                 Input file of CD in single line format
  output                Output file of CD in XML format
  log                   Log file

  -p PARAMS, --params PARAMS
                        XML formatting parameters: indentFirst, indentIncr,
                        attOrder

 Defaults    
    output              \_out.xml
    log                 \_log.txt

---
#### psfcompressgr
Usage: **`psfcompressgr ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Compress Graphite tables in a font

---
####  psfcopyglyphs
Usage: **`psfcopyglyphs [-i INPUT] -s SOURCE ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Copy selected glyphs from a source UFO to a target UFO.

required arguments:

```
  ifont                 Target font into which glyphs will be copied
  -s SOURCE, --source SOURCE
                        Font to get glyphs from
```

optional arguments:
```
  ofont                 output font to create instead of rewriting ifont
  -i INPUT, --input INPUT
                        CSV file identifying glyphs to copy
  -n NAME, --name NAME  Include glyph named NAME
  -f, --force           Overwrite existing glyphs in the target font
  --scale SCALE         Scale glyphs by this factor
  --rename COLHEADER    Names column in CSV containing new names for glyphs
  --unicode COLHEADER   Names column in CSV containing USVs to assign to glyphs
```

Glyphs to be copied are specified by the `INPUT` CSV file and/or on the command line.

When provided, if the CSV file has only one column, a column header is not needed and each line names one glyph to be copied.

If the CSV file has more than one column, then it must have headers, including at least:

- `glyph_name`  contains the name of the glyph in the SOURCE that is to be copied.

If `--rename` parameter is supplied, it identifies the column that will provide a new name for the glyph in the target font. For any particular glyph, if this column is empty then the glyph is not renamed.

If `--unicode` parameter is supplied, it identifies the column that provides an optional Unicode Scalar Value (USV) for the glyph in the target font. For any particular glyph, if this column is empty then the glyph will not be encoded.

Glyphs to be copied can also be specified on the command line via one or more `--name` parameters. Glyphs specified in this way will not be renamed or encoded.

If any glyph identified by the CSV or `--name` parameter already exists in the target font, it will not be overwritten unless the `--force` parameter is supplied.

If any glyph being copied is a composite glyph, then its components are also copied. In the case that a component has the same name as a glyph already in the font, the component is renamed by appending `.copyN` (where N is 1, 2, 3, etc.) before being copied.

Limitations:

- At present, the postscript glyph names in the target font are left unchanged and may therefore be inaccurate. Use `psfsetpsnames` if needed.

---
####  psfcopymeta
Usage: **`psfcopymeta [-r] fromfont tofont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This copies selected fontlist.plist and lib.plist metadata (eg copyright, openTypeNameVersion, decender) between fonts in different (related) families.

It is usually run against the master (regular) font in each family then data synced within family afterwards using [psfsyncmeta](#psfsyncmeta).

Example usage:

```
psfcopymeta GentiumPlus-Regular.ufo GentiumBookPlus-Bold
```

If run with -r or \-\-reportonly it just reports what values would be updated.

Look in psfcopymeta.py for a full list of metadata copied.  Note that only fontinfo.plist and lib.plist are updated; the target font is not normalized.

Also psfcopymeta does not use Pysilfont's backup mechanism for fonts.

---
#### psfcreateinstances
Usage:

**`psfcreateinstances -f [--roundInstances] designspace_file_or_folder`**

**`psfcreateinstances [-i INSTANCENAME] [-a INSTANCEATTR] [-v INSTANCEVAL] [-o OUTPUT]
[--forceInterpolation] [--roundInstances] [--weightfix|-W] designspace_file`**


Create one or more instance UFOs from one or more designspace files.

There are two modes of operation, differentiated by the `-f` (folder) option:

When `-f` is specified:
- the final parameter can be either:
  - a single designspace file
  - a folder, in which case all designspace files within the folder are processed.
- all instances specified in the designspace file(s) are created.
- interpolation is always done, even when the designspace coordinates of an instance match a master.

Omitting the `-f` requires that the final parameter be a designspace file (not a folder) but gives more control over instance creation, as follows:

- Specific instance(s) to be created can be identified by either:
  - instance name, specified by `-i`, or
  - a point on one of the defined axes, specified by `-a` and `-v`. If more than one instance matches this axis value, all are built.
- The default location for the generated UFO(s) can be changed using `-o` option to specify a path to be prefixed to that specified in the designspace.
- In cases where the designspace coordinates of an instance match a master, glyphs will be copied rather than interpolated, which is useful for masters that do not have compatible glyph designs and thus cannot be interpolated. This behavior can be overridden using the `--forceInterpolation` option.

Whenever interpolation is done, the calculations can result in non-integer values within the instance UFOs. The `--roundInstances` option will apply integer rounding to all such values.

When `--weightfix` (or `-W`) is provided, instance weights are changed to either 700 (Bold) or 400 (Regular) based on whether or not the `stylemapstylename` instance attribute begins with `bold`.

---
#### psfcsv2comp
Usage: **`psfcsv2comp [-i INPUT] [--gname GNAME] [--base BASE] [--anchors ANCHORS] [--usv USV] output.txt`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Create a composite definitions file based on data extracted from a csv file.

The INPUT csv file must have column headers and must include columns for the following data:
- the name of the composite glyph
- the name of the base glyph used to create the composites
- one column for each possible anchor to which a component can be attached. The column headers identify the name of the anchor to be used, and the column content names the glyph (if any) to be attached at that anchor.

Optionally, another column can be used to specify the USV (codepoint) for the composite.

Command-line options:

- INPUT: Name of input csv file (default `glyph_data.csv`)
- GNAME:  the column header for the column that contains the name of the composite glyph (default `gname`)
- BASE: the column header for the column that contains the base of the composites (default `base`)
- ANCHORS: comma-separated list of column headers naming the attachment points (default `above,below`).
- USV: the column header for the column that contains hexadecimal USV

**Limitations:** At present, this tool supports only a small subset of the capabilities of composite definition syntax. Note, in particular, that it assumes all components are attached to the _base_ rather than the _previous glyph_.

---
####  psfdeflang
Usage: **`psfdeflang -L lang infont [outfont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This changes the default language behaviour of a .ttf font from its current default to that of the language specified. It supports both OpenType and Graphite tables.

For example this command creates a new font which by default has Khamti behaviour:

```
psfdeflang -L kht Padauk-Regular.ttf Padauk_kht-Regular.ttf
```

---
####  psfdeleteglyphs
Usage: **`psfdeleteglyphs [-i DELETELIST] [--reverse] infont [outfont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This deletes glyphs in a UFO based on an external file with one glyphname per line. 
The `--reverse` option will instead delete all glyphs in the UFO that are not in the list.

It only deletes glyphs that do exist in the default layer, but for such glyphs they are also deleted from other layers, as well as in groups.plist and kerning.plist.
Kern groups based on the glyph name, ie public.kern1._glyphname_ or public.kern2._glyphname_ are also deleted.

It does not analyze composites, so be careful not to delete glyphs that are referenced as components in other glyphs.

The following example will delete all glyphs that are _not_ listed in `keepthese.txt`:

```
psfdeleteglyphs Andika-Regular.ufo -i keepthese.txt --reverse
```

---
####  psfdupglyphs
Usage: **`psfdupglyphs [-i INPUT] [--reverse] infont [outfont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This duplicates glyphs in a UFO based on a csv definition: source,target. It duplicates everything except unicodes.

Example usage:

```
psfdupglyphs Andika-Regular.ufo -i dup.csv
```

---
####  psfexportanchors
Usage: **`psfexportanchors [-r {X,S,E,P,W,I,V}]  [-g] [-s] ifont [output]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This exports anchor data from a UFO font to an XML file. (An "anchor" is also called an "attachment point" which is sometimes abbreviated to "AP".)

Example that exports the anchors contained in the UFO font `CharisSIL-Regular.ufo`, sorts the resulting glyph elements by public.glyphOrder rather than glyph ID (GID), and writes them to an XML file `CharisSIL-Regular_ap.xml`.

```
psfexportanchors -s font-charis/source/CharisSIL-Regular.ufo CharisSIL-Regular_ap.xml
```

If the command line includes

- -g, then the GID attribute will be present in the glyph element.
- -s, then the glyph elements will be sorted by public.glyphOrder in lib.plist (rather than by GID attribute).
- -u, then the UID attribute will include a "U+" prefix

---
#### psfexportmarkcolors
Usage: **`psfexportmarkcolors [-c COLOR] [-n] [-o OUTPUT] [--nocomments] ifont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This exports a mapping of glyph name to cell mark color to a csv file, format "glyphname,colordef". 
Colordef is exported as a double-quoted string according to the [color definition standard](http://unifiedfontobject.org/versions/ufo3/conventions/#colors). It includes comments at the start saying when it was run etc unless --nocomments is specified. The csv produced will include all glyphs, whether or not they have a color definition.

In some cases (see options below) colors can be reported or referred to by text names as in "g_purple". See [Specifying colors on the command line](#specifying-colors-on-the-command-line)

If the command line includes

- -c COLOR, then the script will instead produce a list of glyph names, one per line, of glyphs that match that single color.
- -n, then the csv file will report colors using text names (see above) rather than using numerical definitions. 
If there is no name that matches a particular color definition then it will be exported numerically.

Example that exports a csv file (glyphname, colordef) listing every glyph and its color as in `LtnSmA,"0.5,0.09,0.79,1"`:

```
psfexportmarkcolors Andika-Regular.ufo -o markcolors.csv
```

Example that exports a list of glyphs that are colored purple:

```
psfexportmarkcolors Andika-Regular.ufo -o glyphlist.txt -c "g_purple"
```

---
####  psfexportpsnames
Usage: **`psfexportpsnames [-o OUTPUT] [--nocomments] ifont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Export a mapping of glyph name to postscript name to a csv file, format "glyphname,postscriptname"

It includes comments at the start saying when it was run etc unless \-\-nocomments is specified

---
####  psfexportunicodes
Usage: **`psfexportunicodes  [-o OUTPUT] [--nocomments] [--allglyphs] ifont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Export a mapping of glyph name to unicode to a csv file, format "glyphname,unicode" for glyphs that have a defined unicode. _Note: multiple-encoded glyphs will be ignored._

It includes comments at the start saying when it was run etc unless \-\-nocomments is specified

A complete list of glyphs (both encoded and unencoded) can be generated with \-\-allglyphs.

---
####  psffixffglifs
Usage: **`psffixffglifs ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Make changes needed to a UFO following processing by FontForge. Currently FontForge copies advance and unicode fields from the default layer to the background layer; this script removes all advance and unicode fields from the background layer.

Note that other changes are reversed by standard [normalization](docs.md#Normalization) and more by using pysilfont's standard check&fix system, so running psffixffglyphs with check&fix may be useful:

```
psffixffglifs font.ufo -p checkfix=y
```

####  psffixfontlab
Usage: **`psffixfontlab ifont` **

_([Standard options](docs.md#standard-command-line-options) also apply)_

Make changes needed to a UFO following processing by FontLab, including restoring information from the backup of the UFO.

When exporting from Fontlab, the option _Existing Font Files:_ must be set to _rename_ in order to create the backup needed.
If there are multiple backup files, the oldest will be used on the assumption that several exports have been run since psffixfontlab was last used.
So it is important that any old backups are deleted before re-editing a font.

The changes made by `psffixfontlab` include:
- Restoring groups.plist, kerning.plist and any layerinfo.plist files from the backups
- Deleting various keys from fontinfo.list and lib.plist
- Restoring guidelines in fontinfo.plist and plublic.glyphOrder from lib.plist

Sample usage
```
psffixfontlab font.ufo -p checkfix=None
```
Notes
- The above example has checkfix=None, since otherwise it will report errors and warnings prior to the script fixing them
- Pysilfont's normal backup mechanism for fonts is not used.

---
#### psfftml2TThtml
Usage: **`usage: psfftml2TThtml --ftml FTML --xslt XSLT ttfont map`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Used for testing TypeTuner code, this tool:
- for each FTML document supplied:
  - based on the styles therein, creates TypeTuned fonts that should do the same thing
  - emits an HTML document that shows the FTML data rendered using both:
    - The original font (using font features or language tags)
    - The corresponding TypeTuned font


positional arguments:
```
  ttfont                Input Tunable TTF file
  map                   Feature mapping CSV file
```

The `map` parameter must be a CSV that maps names of font feature tags, font feature values and language tags used in the FTML document(s) to the corresponding TypeTuner feature names and values. For example the following CSV file:

```
# Langage tag mappings:
# lang=langtag,TT feat,value
lang=sd,Language,Sindhi
lang=ur,Language,Urdu

# Feature tag mappings:
# OT feature,TT feat,default,value 1,value 2,...
cv48,Heh,Standard,Sindhi-style,Urdu-style
```
maps:
- langtag `sd` to the TypeTuner feature named `Language` with value `Sindhi`
- langtag `ur` to the TypeTuner feature named `Language` with value `Urdu`
- font feature `cv48` to the TypeTuner feature named `Heh`, with following TypeTuner value names:
  - cv48 value `0` to `Standard`
  - cv48 value `1` to `Sindhi-style`
  - cv48 value `2` to `Urdu-style`

other arguments:
```
  -h, --help            show this help message and exit
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory, default: tests/typetuner
  --ftml FTML           ftml file(s) to process. Can be used multiple
                        times and can contain filename patterns.
  --xsl XSL             standard xsl file. Default: ../tools/ftml.xsl
  --norebuild           assume existing fonts are good
  -l LOG, --log LOG     Log file
  -p PARAMS, --params PARAMS
                        Other parameters - see parameters.md for details
  -q, --quiet           Quiet mode - only display severe errors
```

For reliability, the program re-builds each needed font even if that font was built during a previous run of the program. For debugging, specifying `--norebuild` will speed up the program by assuming previously built fonts are usable.

---
#### psfftml2odt
Usage: **`psfftml2odt [-f FONT] input [output]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This creates a LibreOffice writer document based on input test data in [Font Test Markup Language](https://github.com/silnrsi/ftml) format and font information specified with command line parameters.

Example that uses FTML input contained in the file `test-ss.xml` and creates a LibreOffice writer document named `test-ss.odt`. There will be two columns in the output document, one for the installed font `Andika New Basic` and one for the font contained in the file `AndikaNewBasic-Regular.ttf`. (This compares a newly built font with an installed reference.)

```
psfftml2odt -f "Andika New Basic" -f "AndikaNewBasic-Regular.ttf" test-ss.xml test-ss.odt
```

If the font specified with the -f parameter contains a '.' it is assumed to be a file name, otherwise it is assumed to be the name of an installed font. In the former case, the font is embedded in the .odt document, in the latter case the font is expected to be installed on the machine that views the .odt document.

---
#### psfgetglyphnames
Usage: **`psfgetglyphnames [-i INPUT] [-a AGLFN] ifont glyphs`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Given a list of characters to import in INPUT
(format is one character per line, using four or more hex digits)
and a source UFO infont (probably the source of Latin glyphs for a non-roman font),
create a list of glyphs to import for use with the
[psfcopyglyphs](#psfcopyglyphs) tool.

The AGLFN option will rename glyphs on import if found in the
Adobe Glyph List For New Fonts (AGLFN).
The format for this file is the same as the AGLFN from Adobe,
except that the delimiter is a comma, not a semi-colon.

---
####  psfglyphs2ufo
Usage: **`psfglyphs2ufo [--nofixes] [--nofea] [--restore] fontfile.glyphs masterdir`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Exports one UFO file per master found in the fontfile.glyphs file, and places it in the directory specified as masterdir.

In a round-trip ufo -> glyphs -> ufo there is currently there is some data loss in the standard glyphs -> ufo conversion, so (unless `--nofixes` is set) the script fixes some data and restores some fields from the original ufos if they are present in the masterdir.

Additional fields to restore can be added using `-r, --restore`. This will restore the fields listed if found in either fontinfo.plist or lib.plist

Currently features.fea does not round-trip sucessfully, so `--nofea` can be used to suppress the production of a features.fea file.

Example usage:

```
psfglyphs2ufo CharisSIL-RB.glyphs masterufos
psfglyphs2ufo CharisSIL-RB.glyphs masterufos -r key1,key2
```

If this Glyphs file contains two masters, Regular and Bold, then it will export a UFO for each into a 'masterufos' directory. To have the fonts exported to the current directory, give it a blank directory name:

```
psfglyphs2ufo CharisSIL-RB.glyphs ""
```
---
####  psfmakedeprecated
Usage: **`psfmakedeprecated [-i INPUT] [--reverse] infont [outfont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Creates deprecated versions of glyphs: takes the specified glyph and creates a duplicate with an additional box surrounding it so that it becomes reversed, and assigns a new unicode encoding to it.
Input is a csv with three fields: original,new,unicode

Example usage:

```
psfmakedeprecated Andika-Regular.ufo -i deprecate.csv
```

---
#### psfmakefea
Usage: **`usage: psfmakefea [-i INPUT] [-o OUTPUT] [-c CLASSFILE]
                  [--classprops] [--omitaps OMITAPS] infile`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Creates OUTPUT feature (FEA) file by merging the INPUT feature (FEA or FEAX) file with information gleaned from an input UFO or [attachment point (AP)](https://metacpan.org/pod/distribution/Font-TTF-Scripts/scripts/ttfbuilder#Attachment-Points) xml file. For more information about FEAX see [Fea Extensions](feaextensions.md) documentation.

required arguments:

```
  infile      UFO or AP xml files
  INPUT       FEA or FEAX input file
```

optional arguments:
```
  OUTPUT       name of FEA file to create (if not supplied, only error checking is done)
  CLASSFILE    name of xml class definition file
  --classprops  if specified, class properties will be read from CLASSFILE
  OMITAPS       comma-separated list of attachment points to ignore when creating classes
```

---
####  psfmakescaledshifted
Usage: **`psfmakescaledshifted [-c] [--color COLOR] -i INPUT -t TRANSFORM infont [outfont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Creates scaled and shifted versions of glyphs: takes the specified glyph and creates a duplicate that is scaled and shifted according to the specified transform, and assigns a new unicode encoding to it. Optional -c marks cells of generated glyphs (dark blue).

Input is a csv with three fields: *original,new,unicode*.

Transform takes two types of input:

- a string of the form "(xx, xy, yx, yy, x, y)" where xx = amount to scale horizontally, yy = amount to scale vertically, x = amount to shift horizontally, y = amount to shift vertically. xy and yx are generally not used and remain 0.
- the name of a specific type of transform defined in the UFO lib.plist *org.sil.lcg.transforms* key, such as superscript. Example:

```
<key>org.sil.lcg.transforms</key>
<dict>
  <key>superscript</key>
  <dict>
    <key>adjustMetrics</key>
    <integer>0</integer>
    <key>scaleX</key>
    <real>0.66</real>
    <key>scaleY</key>
    <real>0.6</real>
    <key>shiftX</key>
    <integer>-125</integer>
    <key>shiftY</key>
    <integer>-460</integer>
    <key>skew</key>
    <real>-0.01</real>
  </dict>
</dict>
```

Note that this second type of input allows for two other parameters:

- _adjustMetrics_ indicates how much additional space in units should be added to _both_ sides fo the glyph.

- _skew_ indicates how much the glyph should be skewed, with a skew of 1 indicating a 45° skew. The origin for the skew is (0,0).

There are also two further transformation parameters that can be added to _org.sil.lcg.transforms_ solely for the purpose of documenting post-transformation manual design adjustments. **These are not read or applied by the script. They are only to hold information for the designer.**:

- _manAdjustX_ indicates how much x-axis weight in units should be manually added to glyphs after the script has been applied.

- _manAdjustY_ indicates how much y-axis weight in units should be manually added to glyphs after the script has been applied.

Examples:

```
psfmakescaledshifted -i newglyphs.csv DoulosSIL-Regular.ufo -t "(0.72, 0, 0, 0.6, 10, 806)"
```

This will take the definitions in newglyphs.csv and create the new glyphs using a transformation that includes x-scale 72%, y-scale 60%, x-shift 10 units, y-shift 806 units.

```
psfmakescaledshifted -i newglyphs.csv DoulosSIL-Regular.ufo -t superscript
```

This will take the definitions in newglyphs.csv and create the new glyphs using the *superscript* transformation defined in the UFO lib.plist *org.sil.lcg.transforms* key.

`-c` or `--color COLOR` can be used to set the mark color for the generated glpyhs.  `-c` sets the color to blue, and with
`--color` the color specified as described in [Specifying colors on the command line](#specifying-colors-on-the-command-line)

---
#### psfmakewoffmetadata
Usage: **`psfmakewoffmetadata -n PRIMARYFONTNAME -i ORGID [-f FONTLOG]  [-o OUTPUT]  [--populateufowoff] [--force] fontfile.ufo`**


Make the WOFF metadata xml file based on input UFO.  If woffMetadataCredits and/or woffMetadataDescription are missing
from the UFO, they will be constructed from FONTLOG - see below

Note: Currently fontTools, which several pysilfont scripts use, can't open UFO files with with woff fields in, so until it
does it is recommended that:

- FONTLOG is used as the source for the credits and description
- `--populateufowoff` is not used.

The primary font name and orgid need to be supplied on the command line. By default it outputs to *primaryfontname*-WOFF-metadata.xml.

Example:

```
psfmakewoffmetadata -n "Nokyung" -i "org.sil.fonts" source/Nokyung-Regular.ufo
```

It constructs the information needed from:

- The supplied primary font name and orgid
- Information within the primary font file

If it needs to construct the credits and description fields from FONTLOG, that file needs to be formatted according to the pattern used for most SIL font packages. The description is created using the contents of the FONTLOG, starting after the "Basic Font Information" header and finishing before the "Information for Contributors" header (if present) or the "Acknowledgements" header otherwise. The credits are created from the N:, W:, D: and E: sets of values in the acknowledgements section, though E: is not used. One credit is created from each set of values and sets should be separated by blank lines. By default it reads FONTLOG.txt from the folder it is run in.

If woffMetadataCredits and woffMetadataDescription are missing from the UFO, there are options to update the UFO with the values constructed from FONTLOG:

```
  --populateufowoff  Add woffMetadataCredits and woffMetadataDescription to UFO if missing
  --force            Update the above fields from FONTLOG even if already present in UFO  
```

---
####  psfnormalize
Usage: **`psfnormalize [-v VERSION] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This normalizes a UFO font (and optionally converts from one version to another if -v is specified). _Note that most pysilfont scripts automatically output normalized UFOs, so psfnormalize is normally only needed after fonts have been processed by external font tools._

Example that normalizes the named font:

```
psfnormalize Nokyung-Regular.ufo
```

The normalization follows the [default behaviours](docs.md#normalization), but these can be overridden using [custom parameters](parameters.md)

\-v VERSION can be 2, 3

If you are a macOS user, see _pysilfont/actionsosx/README.txt_ to install an action that will enable you to run psfnormalize without using the command line.

---
####  psfremovegliflibkeys
Usage: **`psfremovegliflibkeys [-o OFONT] ifont [key [key ...]] [-b [BEGINS [BEGINS ...]]]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This removes the specified key(s) from the lib section of .glif files if they exist.

```
psfremovegliflibkeys GentiumPlus-Regular.ufo key1 key2 -b start1 start2
```

This will remove any keys that match key1 or key2 or begin with start1 or start2

Note - Special handling for com.schriftgestaltung.Glyphs.originalWidth:
- Due to a glyphsLib bug, advance width is sometimes moved to this key, so if this key is set for deletion
  - If advance width is not set in the glif, it is set to com.schriftgestaltung.Glyphs.originalWidth
  - com.schriftgestaltung.Glyphs.originalWidth is then deleted

---
####  psfrenameglyphs
Usage: **`psfrenameglyphs [--mergecomps] [-c CLASSFILE] -i INPUT ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Assign new working names to glyphs based on csv input file, format "oldname,newname". The algorithm will handle circular rename specifications such as:
```
glyph1,glyph2
glyph2,glyph1
```
Unless default value for `renameGlyphs` [parameter](parameters.md) is overridden, the .glif filenames in the UFO will also be adjusted.

This program modifies the glyphs themselves and, if present in lib.plist, the `public.glyphOrder`, `public.postscriptNames`, `com.schriftgestaltung.glyphOrder` and `com.schriftgestaltung.customParameter.GSFont.DisplayStrings` definitions. Any composite glyphs that reference renamed glyphs are adjusted accordingly.

If groups.plist is present, glyph names in groups are renamed. In addition, groups named public.kern1._glyphname_ or public.kern2._glyphname_ will also be renamed, but group names not matching that pattern are left unchanged.

If kerning.plist is present, glyph names in kern pairs are changed and kern group names that match the pattern described above are also changed.

If -c specified, the changes are also made to the named classes definition file.  

When there are multiple layers in the UFO, glyphs will be renamed in all layers providing the glyph is in the default layer.  If the glyph is only in non-default layers the glyph will need renaming manually.

In normal usage, all oldnames and all newnames mentioned in the csv must be unique.

The `--mergecomps` option enables special processing that allows newnames to occur more than once in the csv, with the result that the first mention is a normal rename while subsequent mentions indicate glyphs that should be deleted but any references updated to the first (renamed) glyph. Any moving anchors (i.e., those whose names start with `_`) on the deleted glyphs will be copied to the first glyph. For example:
```
dotabove,dot1      # this glyph has _above anchor
dotbelow,dot1      # this glyph has _below anchor
dotcenter,dot1     # this glyph has _center anchor
```
would cause `dotabove` to be renamed `dot1` while `dotbelow` and `dotabove` would be deleted. Any composite glyphs that reference any of `dotabove`, `dotbelow`, or `dotcenter` will be adjusted to refer to `dot1`. The `_below` anchor from `dotbelow` and the `_center` anchor from `dotcenter` will be copied to `dot1` (overwriting any anchors by the same names).

Any `--mergecomps` run should be done in a separate run of `psfrenameglyphs` from other renaming, and group and kerning data is not processed on mergecomps runs.

---
####  psfrunfbchecks
Usage: **`psfrunfbchecks [--profile PROFILE] [--html HTMLFILE] [--csv CSV]
                      [--ttfaudit] fonts [fonts ...]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Run Font Bakery tests using a standard profile and report results in a table on screen.  Multiple fonts can be specified, 
including using wildcards, but all should be in the same directory.  
For ttf files, the profile will be Pysilfont's ttfchecks.py.  UFO files are not yet supported.

An alternative profile can be specified with `--profile`.  This profile needs to be specifically designed to work with this script - see examples/fbttfchecks.py.  This profile amends the behaviour of ttfchecks.py and includes options to change which checks are run and to override the status reported by checks.  Project-specific checks can also be added.

Example use with a project-specific profile:

```
psfrunfbchecks --profile fbttfchecks.py results/*.ttf
```
To see more details of results, use `--html HTMLFILE` to write an html file in the same format that Font Bakery outputs.
  
`--csv CSV` creates a csv file with one line per check that is run.  This can be used with diff tools to compare results from different runs (or following upgrades to Font Bakery.)
   
Pysilfont's standard logging parameters (-p scrlevel and -p loglevel) also change the level of information `psfrunfbchecks` outputs.

A special option, `--ttfaudit` compares the list of checks within ttfchecks.py against those in Font Bakery and reports any descrepancies to screen.
It also writes a csv file containing a list of all checks.  Usage `psfrunfbchecks --ttfaudit csvfile`

---
####  psfsetassocfeat
Usage: **`psfsetassocfeat [-i INPUT] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Add associate feature info to  org.sil.assocFeatureValue glif lib based on a csv file, format "glyphname,featurename[,featurevalue]"

---
####  psfsetassocuids
Usage: **`psfsetassocuids [-i INPUT] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Add associate UID info to org.sil.assocUIDs in glif lib based on a csv file - could be one value for variant UIDs and multiple for ligatures,   format "glyphname,UID[,UID]"

---
#### psfsetdummydsig
Usage: **`psfsetdummydsig -i inputfont -o outputfont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Put a dummy DSIG table into a font in TTF format (using fontTools)

```
-i [--ifont] inputfont    (Input file in TTF format)
-o [--ofont] outputfont   (Output file in TTF format)
```

---
####  psfsetglyphorder
Usage: **`psfsetglyphorder [--gname GNAME] [--header HEADER] [--field FIELD] [-i INPUT] [-x] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

From the INPUT file, load `public.glyphOrder` in lib.plist to control the order of glyphs in generated TTF files. FIELD can be used to specify a different order to load, such as `com.schriftgestaltung.glyphOrder`.

The input file can be in one of two formats:
- Plain text file with one glyph name per line in the desired order
- csv file with headers using glyph_name and sort_final columns

With the csv file:
- The glyph names are sorted by the values in the sort_final column, which can be integer or real. HEADER can be used to specify alternate column header to sort_final.  Multiple comma-separated values can be used with `--header` and `--field` to update two or more orders in a single command call.
- GNAME can be used to specify column header to use instead of glyph_name.

By default all entries in the input file are added, even if the glyph is not in the font.  The UFO spec allows this so a common list can be used across groups of fonts. Use -x to only add entries for glyphs that exist in the font.

Example that imports the data based on glyph_name and sort_final columns in the csv, only adding entries for glyphs in the font:
```
psfsetglyphorder Andika-Regular.ufo -i glyphdata.csv -x
```
Example that imports the data from the sort_final column to public.glyphorder and from the sort_designer into com.schriftgestaltung.glyphOrder:
```
psfsetglyphorder Andika-Regular.ufo -i glyphdata.csv --header sort_final,sort_designer --field public.glyphOrder,com.schriftgestaltung.glyphOrder
```
---
####  psfsetkeys
Usage: **`psfsetkeys [--plist PLIST] [-i INPUT] [-k KEY] [-v VALUE] [--file FILE] [--filepart FILEPART] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Set keys in a UFO p-list file.
A single key can be set by specifying KEY and one of VALUE, FILE, or FILEPART.
VALUE should be a single line string, FILE and FILEPART should be a filename.
With FILEPART, the contents of the file are read until the first blank line.
This is useful for setting the copyright key from the OFL.txt file.

Multiple keys can be set using a csv INPUT file, format "key,value".
A filename to read cannot be specified in the csv file.

By default keys are stored with type string in the UFO.
Values of true or false are converted to type boolean.
Values that can be converted to integer are stored as type integer.

PLIST selects which p-list to modify.
If not specified defaults to `fontinfo` which means the `fontinfo.plist` file is modified.

Example:

Set a key in the file `lib.plist`.
```
psfsetkeys --plist lib -k com.schriftgestaltung.width -v Regular font.ufo
```

---
#### psfsetmarkcolors
Usage: **`psfsetmarkcolors [-c COLOR] [-i INPUT] [-u] [-x]  ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This sets the cell mark color of a glyph according to the [color definition standard](http://unifiedfontobject.org/versions/ufo3/conventions/#colors) based on a list of glyph names in INPUT, one glyph name per line.
COLOR may be defined as described in [Specifying colors on the command line](#specifying-colors-on-the-command-line)

If the command line includes:
- -u, then the INPUT file will be treated as a list of unicode values rather than glyph names, and the color set on any glyph that is encoded with those unicode values.
- -x, then the color definition will be removed altogether. If no INPUT is given all color definitions will be removed from all glyphs.

Example that sets the cell mark color of all glyphs listed in glyphlist.txt to purple (0.5,0.09,0.79,1):
```
psfsetmarkcolors Andika-Regular.ufo -i glyphlist.txt -c "0.5,0.09,0.79,1"
```
Example that sets the cell mark color of all glyphs that have the unicode values listed in unicode.txt to purple (0.5,0.09,0.79,1):
```
psfsetmarkcolorss Andika-Regular.ufo -u -i unicode.txt -c "g_purple"
```
Example that sets the cell mark color of all glyphs that have the unicode values listed in unicode.txt to purple (0.5,0.09,0.79,1):
```
psfsetmarkcolors Andika-Regular.ufo -u -i unicode.txt -c "g_purple"
```
Example that removes all color definitions from all glyphs: (this is effectively equivalent to `psfremovegliflibkeys Andika-Regular.ufo public.markColor`)
```
psfsetmarkcolors Andika-Regular.ufo -x
```

---
####  psfsetpsnames
Usage: **`psfsetpsnames [--gname GNAME] [-i INPUT] [-x] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

From the INPUT file, populate `public.postscriptName` in lib.plist to specify final production names for glyphs.

The input file can be in one of two formats:
- simple csv in form glyphname,postscriptname
- csv file with headers using glyph_name and ps_name columns

With the csv file, GNAME can be used to specify column header to use instead of glyph_name.

By default all entries in the input file are added, even if the glyph is not in the font.  The UFO spec allows this so a common list can be used across groups of fonts. Use -x to only add entries for glyphs that exist in the font.

Example usage:
```
psfsetpsnames Andika-Regular.ufo -i psnames.txt
```

---
####  psfsetunicodes
Usage: **`psfsetunicodes [-i INPUT] ifont [ofont]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Set the unicodes of glyphs in a font based on a csv file. With no header row, the csv format is assumed to be "glyphname,UID", otherwise column headers `glyph_name` and `USV` are used. Unicode values must be hex digits with no prefix.

The input font may have any number of Unicode values associated with any glyph. In the case that there is exactly one for a specific glyph, then the first time that glyph appears in the csv, that Unicode value will be replaced. In subsequent mentions of that glyph, or if there are already more than one Unicode values associated with a glyph, new values are simply appended.

When replacing or adding a Unicode value, any other glyph that has that same Unicode value will have it removed.

---
####  psfsetversion
Usage: **`psfsetversion font [newversion]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This updates the various font version fields based on 'newversion' supplied which may be:

- Full openTypeNameVersion string, except for the opening "Version " text, eg "1.234 beta2"
- +1 to increment to the patch version number - see below
- not supplied, in which case the current values will be validated and existing openTypeNameVersion string displayed

It will update the openTypeNameVersion, versionMajor and versionMinor fields. It works assuming that openTypeNameVersion is of the form:

"Version M.mpp" or "Version M.mpp extrainfo", eg "Version 1.323 Beta2"


Based on [FDBP](https://silnrsi.github.io/FDBP/en-US/Versioning.html), the version number is parsed as M.mpp where M is major, m is minor and pp is patch number.  M matches the versionMajor and mpp the versionMinor fields.

Incrementing will fail if either the openTypeNameVersion is not formatted correctly or the version numbers in there don’t match those in versionMajor and versionMinor.

Examples of usage:

```
psfsetversion font.ufo "1.423"
```

will set:

- openTypeNameVersion to "Version 1.423"
- versionMajor to 1
- versionMinor to 423

`psfsetversion font.ufo +1`

If values were originally as in the first example, openTypeNameVersion will be changed to "Version 1.424" and versionMinor to 424

Note that only fontinfo.plist is updated, so the font is not normalized and Pysilfont's backup mechanism for fonts is not used.

---
#### psfsubset
Usage: **`psfsubset -i INPUT [--header HEADER] ifont ofont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This script writes an output UFO that is a subset of the input UFO. The subset contains only the glyphs identified in the INPUT file (plus any components needed for them).

The INPUT file can be a plain text file (one glyph per line) or a csv file. In the case of csv, the HEADER parameter is used to indicate which column from the csv to use (default is `glyph_name`).

Glyphs can be identified either by their name or the Unicode codepoint (USV). Glyph names and USVs can be intermixed in the list: anything that is between 4 and 6 hexadecimal digits is first processed as a USV and then, if there is no glyph encoded with that USV, processed as a glyph name.

Glyph orders and psname mappings, if present in the font, are likewise subsetted.

---
####  psfsyncmasters
Usage: **`psfsyncmasters primaryds [secondds] [--complex][-n]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Synchronises/validates some fontinfo.plist and lib.plist metadata across a family of fonts based
on a designspace file. It looks in the designspace file for a master with `info copy="1"` set then syncs the values from that master to other masters defined in the file.

If a second designspace file is supplied, it also syncs to masters found in there.  

Some validation is different for complex families (ie not RIBBI families) - use `--complex` to inicate that a family is complex.

Example usage:

```
psfsyncmasters CharisSIL.designspace
```

Note that only fontinfo.plist and lib.plist files are updated, so fonts are not normalized and Pysilfont's backup mechanism for fonts is not used.

-n (--new) appends \_new to ufo and file names for testing purposes

Note that currently the code also assumes a family is complex if the ufo names include 'master', though this check will
removed in the future, so `--complex` should be used instead of relying on this.

---
####  psfsyncmeta
Usage: **`psfsyncmeta [-s] [-m [MASTER]] [-r] [-n] [--normalize] ifont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Verifies and synchronises some fontinfo.plist and lib.plist metadata across a family of fonts.  By default it uses the regular font as the master and updates any other fonts that exist assuming standard name endings of -Regular, -Italic, -Bold and -BoldItalic.  Optionally a single font file can be synced against any other font as master, regardless of file naming.

Example usage for family of fonts:

```
psfsyncmeta CharisSIL-Regular.ufo
```

This will sync the metadata in CharisSIL-Italic, CharisSIL-Bold and CharisSIL-BoldItalic against values in CharisSIL-Regular.  In addition it will verify certain fields in all fonts (including Regular) are valid and follow [FDBP](https://silnrsi.github.io/FDBP/en-US/index.html) best-practice standards.

Example usages for a single font:

```
psfsyncmeta -s font-Italic.ufo
psfsyncmeta -s font-Italic.ufo -m otherfont.ufo
```
The first will sync font-Italic against font-Regular and the second against otherfont.

Look in psfsyncmeta.py for a full details of metadata actions.

Note that by default only fontinfo.plist and lib.plist are updated, so fonts are not normalized.  Use \-\-normalize to additionally normalize all fonts in the family.

Also psfsyncmeta does not use Pysilfont's backup mechanism for fonts.

-n (--new) appends \_new to ufo and file names for testing purposes

---
####  psftuneraliases
Usage: **`psftuneraliases [-m map.csv] [-f font.ttf] feat_in.xml feat_out.xml`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Merges lookup identifiers gleaned from the map.csv file (emitted from [psfbuildfea](#psfbuildfea)), along with OpenType and Graphite feature identifiers (obtained from a compiled font), into the `<aliases>` section of a TypeTuner features.xml file. At least one of `-m` and `-f` must be provided.

Aliases for OpenType features will generated only for the default language of each script and the alias names will be of the form `<featureTag>_<scriptTag>_dflt`. Alias names for Graphite features will be of the form `gr_<featureID>`.

As per prior technology, the OpenType feature alias names do not distinguish between GSUB and GPOS lookups and features, therefore using the same lookup name or feature tag for both GSUB and GPOS will cause the program to exit with an error.

---
####  psfufo2glyphs
Usage: **`psfufo2glyphs designspace [glyphsfile]`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This generate a glyphs files from a designspace file and associated UFO(s).

If no glyphsfile is specified, one will be created in the same directory as the designspace file and based on the name of the designspace file.

Example usage:

```
psfglyphs2ufo AndikaItalic.designspace AndikaItalic.glyphs
```

Note: This is just bare-bones code at present so does the same as glyphsLib's ufo2glyphs command.  It was designed so that data could be massaged, if necessary, on the way but no such need has been found so far

---
#### psfufo2ttf
Usage: **`psfufo2ttf [--removeOverlap] iufo ottf`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

This generates a ttf file without OpenType tables from a UFO.

It is based on ufo2ft and uses ufo2ft's decomposeTransformedComponents and flattenComponents filters.

If `--removeOverlap` is used it merges overlapping contours

---
#### psfversion
Usage: **`psfversion`**

This displays version info for pysilfont and many of its dependencies.  It is inteneded for troubleshooting purposes - eg send the output in if reporting a problem - and includes which version of Python is being used and where the code is being executed from.

---
#### psfwoffit
Usage: **`usage: psfwoffit[-m METADATA] [--privatedata PRIVATEDATA] [-v VERSION]
                 [--ttf [TTF] [--woff [WOFF]] [--woff2 [WOFF2]] infont`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Converts between ttf, woff, and woff2

required arguments:

```
  infont      an input font; can be ttf, woff, or woff2
```

optional arguments:
```
  -m METADATA, --metadata METADATA
                        file containing XML WOFF metadata
  --privatedata PRIVATEDATA
                        file containing WOFF privatedata
  -v VERSION, --version VERSION
                        woff font version number in major.minor
  --ttf [TTF]           name of ttf file to be written
  --woff [WOFF]         name of woff file to be written
  --woff2 [WOFF2]       name of woff2 file to be written
```
The `--version`, `--metatadata` and `--privatedata` provide data to be added to the WOFF file. 
Each of these is optional and if absent the following rules apply

* if the input file is woff or woff2:
  * the missing values are copied from the input file
* if the input file is a ttf:
  * missing `metadata` or `privatedata` will be empty in the output fonts
  * the version will be taken from the `fontRevison` field of the `head` table of the input ttf file.  
 
The output filenames can be omitted (as long as another option follows) or `-`; in either case
the output filename are calculated from the `infont` parameter.

Examples:

```
psfwoffit --woff2 output.woff2 input.woff
```
creates an output woff2 font file from an input woff font file, copying the version as well any metadata and privatedata from the input woff.

```
psfwoffit -m woffmetadata.xml -v 1.3 --woff output.woff --woff2 output.woff2 input.ttf
```
creates explicitly named woff and woff2 font files from an input ttf, setting woff metadata and version from the command line.
 
```
psfwoffit --woff --woff2 -m woffmetadata.xml -v 1.3 path/font.ttf
```
creates implicitly named `path/font.woff` and `path/font.woff2`, setting woff metadata and version from the command line.

```
psfwoffit --woff - --woff2 - -m woffmetadata.xml path/to/font.ttf
```
same as above but uses font version from the ttf.

---
#### psfxml2compdef
Usage: **`psfxml2compdef input output`**

_([Standard options](docs.md#standard-command-line-options) also apply)_

Convert composite definition file from XML format

_This section is Work In Progress!_

- input                 Input file of CD in XML format
- output                Output file of CD in single line format


---

### Specifying colors on the command line

A color can be specified as a name (eg g_dark_green) or in RBGA format (eg (0,0.67,0.91,1)).

Where multiple colors are supplied they should be separated by commas.

Two special cases are also allowed (if applicable for the script):

- "none" where the color should be removed
- "leave" where any existing color should be left unchanged

All values are case-insensitive

Examples:

```
--colors="g_cyan,g_blue"
--colors="g_dark_green, leave, (0,0.67,0.91,1)"
--color=g_red
```
Color names can be one of the 12 cell colors definable in the GlyphsApp UI: g_red, g_orange, g_brown, g_yellow,
 g_light_green, g_dark_green, g_cyan, g_blue, g_purple, g_pink, g_light_gray, g_dark_gray.



## Example Scripts

When Pysilfont is downloaded, there are example scripts in pysilfont/examples.  These are a mixture of scripts that are under development, scripts that work but would likely need amending for a specific project's need and others that are just examples of how things could be done.  Deprecated scripts are also placed in there.

See [examples.md](examples.md) for further information
