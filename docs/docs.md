# Pysilfont - utilities for font development

# ***** Note these docs are incomplete at present! *****

Pysilfont is a collection of tools to support font development, with an emphasis on [UFO](#ufo-support-in-pysilfont)-based workflows.

In addition to the UFO utilities, there is also support for testing using [FTML](#font-test-markup-language) and [Composite Definitions](#linktobeset).

Some scripts are written specifically to fit in with the approaches recommended in [Font Development Best Practices](https://silnrsi.github.io/FDBP/en-US/index.html)

# Documentation

Documentation is held in the following documents:

- docs.md: This document - the main document for users
- [scripts.md](scripts.md): User documentation for all command-line tools and other scripts
- [technical.md](technical.md): Technical details for those wanting write scripts or other development tasks
- Other sub-documents, with links from the above

Installation instructions are in [README.md](../README.md)

# Scripts and commands
Many Pysilfont scripts are installed to be used as command-line tools, and these are all listed, with usage instructions, in [scripts.md](scripts.md).  This also has details of some other example python scripts.

All scripts work using a standard framework designed to give users a consistent interface across scripts, and common features of these scripts are described in the following sections, so the documentation below needs to be read in conjunction with that in scripts.md.

## Standard command line options

All scripts support these:

- `-h, --help`
  - Basic usage help for the command
- `-d, --defaults`
  - Display -h info with added info about default values
- `-q, --quiet`
  - Quiet mode - only display errors.  See reporting below
- `-l LOG, --log LOG`
  - Log file name (if not using default name)
- `-p PARAMS, --params PARAMS`
  - Other [parameters](#parameters)

The individual script documentation in scripts.md indicates which apply

## Default values

Most scripts have defaults for file names and other arguments - except for the main file the script is running against.

### Font/file name defaults

Once the initial input file (eg input font) has been given, most other font and file names will have defaults based on those.

This applies to other input font names, output font names, input file names and output file names and is done to minimise retyping repeated information like the path the files reside in.   For example, simply using:

	psfsetpsnames path/font.ufo
	
will:

(remainder to be written)

## Reporting

## Backups for fonts

# Parameters

# UFO support in Pysilfont

# Font Test Markup Language

# Composite definitions

# Contributing to the project

Pysilfont is developed and maintained by SIL International’s [Non-Roman Script Initiative team](http://scripts.sil.org), though contributions from anyone are welcome. Pysilfont is copyright (c) 2014-2017 [SIL International](http://www.sil.org) and licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License). The project is hosted at [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont).


