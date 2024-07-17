# Changelog

## [1.8.1] - - Placeholder for next release

General updates for new year, 2024

### Added

| Command                                                    | Description                 |
|------------------------------------------------------------|-----------------------------|
| [psfcsv2kern](docs/scripts.md#psfcsv2kern)                 | To be written (1.8.1.dev2?) |
| [psfkern2csv](docs/scripts.md#psfkern2csv)                 | To be written (1.8.1.dev2?) |


### Changed

- Added --compregex to psfufo2ttf
- Fix r-string SyntaxWarnings
- Deprecate psfmakefea in favor of makefea
- Handle CJK variants of ASCII characters in FTML builder that have
the same base glyph name (that is, with no extension) as the ASCII base glyph name. (1.8.1.dev2)
- Updated ttfchecks.py to match changes in Font Bakery checks (1.8.1.dev3)
- Changed fontbakery support to use standard Google checks now is_cjk has been fixed (1.8.1.dev3)
- Updated psfrunfbchecks to work with latest Font Bakery, ie v0.11 on (1.8.1.dev3)
- Updated profiles and checks in fbtests/ to work with latest refactored Font Bakery v0.12.X
- Fixed #86 "psfmakefea fails when there are different substitution types" (1.8.1.dev4)
- Updated psfrunfbchecks to output a warning indicating the script is no longer to be used (1.8.1.dev4)

### Removed

## [1.8.0] - 2023-11-22 Updated packaging

Updated the packaging to follow PEP621 guidelines

Also

- Added do forlet to fea extensions
- Updates to MacOS preflight support

## [1.7.0] - 2023-09-27 Maintenance Release - general updates

General updates over the last year

### Added

| Command                                                                    | Description                                                                                   |
|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [psfcheckproject](docs/scripts.md#psfcheckproject)                         | Check UFOs in designspace files have consistent glyph inventory & unicode values (1.6.1.dev2) |
| [update-preflight-libs-pyenv](preflight/update-preflight-libs-pyenv)       | Preflight/preglyphs libs update shell script for macOS users (1.6.1.dev6)                     |
| [psfpreflightversion](docs/scripts.md#psfpreflightversion)                 | Script to check version of modules but only for preflight (1.6.1.dev11)                                    |

### Changes

- check&fix, used by most UFO commands, no longer warns if styleMapFamilyName or styleMapStyleName are missing in fontinfo (1.6.1.dev1)
- Low-level bug fix to ufo.py found when running some temp code! Not previously found in live code. (1.6.1.dev1)
- Glyphs roundtrip now preserves openTypeHeadFlags key (1.6.1.dev2)
- Bug fix for psfmakefea for cases where there is adavnce height but no advance width got a glyph  (1.6.1.dev3)
- Update to core.py to avoid race condition creating logs folder (1.6.1.dev3)
- psfglyphs2ufo now removes any advance heights in glyphs to counteract glyphslib changes (1.6.1.dev3)
- psfsyncmasters now sets openTypeOS2WeightClass to be in the CSS coordinate space, 
not the design coordinate space. (1.6.1.dev5)
- Various updates to gfr.py to support the Find a Font service (1.6.1.dev6)
- psfsyncmasters now syncs public.skipExportGlyphs (1.6.1.dev7)
- Add -d to psfaddanchors (1.6.1.dev7)
- Global adjustments to use https: instead of http: (1.6.1.dev7)
- Corrected ufo.py so plists still have http: in the DOCTYPE (1.6.1.dev8)
- psfsyncmasters - removed checks relating to styleMapFamilyName and styleMapStyleName; --complex now does nothing (1.6.1.dev9)
- psfrunfbchecks - general updates to reflect new Font Bakery checks (1.6.1.dev9)
- psfrunfbchecks + fbtests modules - updates to relect structure changes in Font Bakery (1.6.1.dev10)
- psfsubset - Added filtering (1.6.1.dev11)
- psfufo2ttf - fix crash in cases where both `public` and `org.sil` keys for Variation Sequence data are present (1.6.1.dev11)
- psfbuildcomp - updated to use g_blue,g_purple as the default colours for -c (1.6.1.dev11)
- Fixed bug in setuptestdata.py used by pytest  (1.6.1.dev11)
- Bug-fix to check&fix where updates that empty an array failed  (1.6.1.dev11)
- update-preflight-libs-pyenv - adjusted dependencies, added conditional to modules installation report calling script only for the desired modules, made output terser, added stricter pyenv checking, dropped filename suffix (1.6.dev11)

### Removed

None

## [1.6.0] - 2022-07-25 Maintenance Release - general updates

General updates over the last two years, adding new scripts and updating existing in response to new
needs or to adjust for changes to third-party software.

### Added

| Command | Description |
| ------- | ----------- |
| [psfcheckclassorders](docs/scripts.md#psfcheckclassorders) | Verify classes defined in xml have correct ordering where needed |
| [psfcheckftml](docs/scripts.md#psfcheckftml) | Check ftml files for structural integrity |
| [psfcheckglyphinventory](docs/scripts.md#psfcheckglyphinventory) | Warn for differences in glyph inventory and encoding between UFO and input file (e.g., glyph_data.csv) |
| [psfcheckinterpolatable](docs/scripts.md#psfcheckinterpolatable) | Check UFOs in a designspace file are compatible with interpolation |
| [psffixfontlab](docs/scripts.md#psffixfontlab) | Make changes needed to a UFO following processing by FontLab |
| [psfsetdummydsig](docs/scripts.md#psfsetdummydsig) | Add a dummy DSIG table into a TTF font |
| [psfsetglyphdata](docs/scripts.md#psfsetglyphdata) | Update and/or sort glyph_data.csv based on input file(s) |
| [psfshownames](docs/scripts.md#psfshownames) | Display name fields and other bits for linking fonts into families |
| [psfwoffit](docs/scripts.md#psfwoffit) | Convert between ttf, woff, and woff2 |

### Changed

Multiple changes!

### Removed

None

## [1.5.0] - 2020-05-20 - Maintenance Release; Python 2 support removed

Added support for Font Bakery to make it simple for projects to run a standard set ot checks designed to fit in 
with [Font Development Best Practices](https://silnrsi.github.io/FDBP/en-US/index.html).

Improvements to feax support

Many other updates

### Added

| Command | Description |
| ------- | ----------- |
| [psfftml2TThtml](docs/scripts.md#psfftml2TThtml) | Convert FTML document to html and fonts for testing TypeTuner |
| [psfmakescaledshifted](docs/scripts.md#psfmakescaledshifted) | Creates scaled and shifted versions of glyphs |
| [psfrunfbchecks](docs/scripts.md#psfrunfbchecks) | Run Font Bakery checks using a standard profile with option to specify an alternative profile |
| [psfsetdummydsig](docs/scripts.md#psfsetdummydsig) | Put a dummy DSIG table into a TTF font |

### Changed

Multiple minor changes and bug fixes

### Removed

None

## [1.4.2] - 2019-07-30 - Maintenance release

Updated the execute() framework used by scripts to add support for opening fonts with fontParts and remove support for opening fonts with FontForge.

Updates to normalization and check&fix to work better with FontForge-based workflows

Improvements to command-line help to display info on params and default values

Improvements to log file creation, including logs, by default, going to a logs sub-directory

Some changes are detailed below, but check commit logs for full details.

### Added

| Command | Description |
| ------- | ----------- |
| [psfbuildcompgc](docs/scripts.md#psfbuildcompgc) | Add composite glyphs to UFO using glyphConstruction based on a CD file |
| [psfdeflang](docs/scripts.md#psfdeflang) | Changes default language behaviour in a font |
| [psfdupglyphs](docs/scripts.md#psfdupglyphs) | Duplicates glyphs in a UFO based on a csv definition |
| [psfexportmarkcolors](docs/scripts.md#psfexportmarkcolors) | Export csv of mark colors |
| [psffixffglifs](docs/scripts.md#psffixffglifs) | Make changes needed to a UFO following processing by FontForge |
| [psfgetglyphnames](docs/scripts.md#psfgetglyphnames) | Create a file of glyphs to import from a list of characters to import |
| [psfmakedeprecated](docs/scripts.md#psfmakedeprecated) | Creates deprecated versions of glyphs |
| [psfsetmarkcolors](docs/scripts.md#psfsetmarkcolors) | Set mark colors based on csv file |
| [psftuneraliases](docs/scripts.md#psftuneraliases) | Merge alias information into TypeTuner feature xml file |

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
