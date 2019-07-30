# Changelog

## [1.4.2] - 2019-07-30 - Maintenance release

Updated the execute() framework used by scripts to add support for opening fonts with fontParts and remove support for opening fonts with FontForge.

Updates to normalization and check&fix to work better with FontForge-based workflows

Improvements to command-line help to display info on params and default values

Improvements to log file creation, including logs, by default, going to a logs sub-directory

Some changes are detailed below, but check commit logs for full details.

### Added

| Command | Description |
| ------- | ----------- |
| [psfbuildcompgc](#psfbuildcompgc) | Add composite glyphs to UFO using glyphConstruction based on a CD file |
| [psfdeflang](#psfdeflang) | Changes default language behaviour in a font |
| [psfdupglyphs](#psfdupglyphs) | Duplicates glyphs in a UFO based on a csv definition |
| [psfexportmarkcolors](#psfexportmarkcolors) | Export csv of mark colors |
| [psffixffglifs](#psffixffglifs) | Make changes needed to a UFO following processing by FontForge |
| [psfgetglyphnames](#psfgetglyphnames) | Create a file of glyphs to import from a list of characters to import |
| [psfmakedeprecated](#psfmakedeprecated) | Creates deprecated versions of glyphs |
| [psfsetmarkcolors](#psfsetmarkcolors) | Set mark colors based on csv file |
| [psftuneraliases](#psftuneraliases) | Merge alias information into TypeTuner feature xml file |

### Changed

Multiple minor changes and bug fixes

### Removed

The following scripts moved from installed scripts to examples

- ffchangeglyphnames
- ffcopyglyphs
- ffremovealloverlaps

## [1.4.1] - 2019-03-04 - Maintenance release

Nearly all scripts should work under Python 2 & 3

**Future work will be tested just with Python 3** but most may still work with Python 2.

Some changes are detailed below, but check commit logs for full details.

### Added

psfversion - Report version info for pysilfont, python and various dependencies
psfufo2gylphs - Creates a .gypyhs file from UFOs using glyphsLib

### Changed

psfremovegliflibkeys now has -b option to remove keys beginning with specified string

psfglyphs2ufo updated to match new psfufo2glyphs.  Now has -r to restore specific keys

Many changes to .fea support

The pytest-based test setup has been expanded and refined

### Removed

Some scripts moved from installed scripts to examples

## [1.4.0] - 2018-10-03 - Python 2+3 support

### Added

### Changed

Libraries and most installed scripts updated to work with Python 2 and python 3

All scripts should work as before under Python 2, but a few scripts need further work to run under Python 3:
- All ff* scripts
- psfaddanchors
- psfcsv2comp
- psfexpandstroke
- psfsubset

The following scripts have not been fully tested with the new libraries
- psfchangegdlnames
- psfcompdef2xml
- psfcopymeta
- psfexportpsnames
- psfftml2odt
- psfremovegliflibkeys
- psfsetversion
- psfsyncmeta
- psftoneletters
- psfxml2compdef

### Removed

## [1.3.1] - 2018-09-27 - Stable release prior to Python 2+3 merge

### Added
- psfcopyglyphs
- psfcreateinstances
- psfcsv2comp
- psfmakefea
- psfremovegliflibkeys
- psfsetkeys
- psfsubset

Regression testing framework

### Changed

(Changes not documented here)

### Removed


## [1.3.0] - 2018-04-25 - First versioned release
