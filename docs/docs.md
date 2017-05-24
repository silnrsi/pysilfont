# Pysilfont - utilities for font development

# ***** Note these docs are incomplete at present! *****

Pysilfont is a collection of tools to support font development, with an emphasis on [UFO](#ufo-support-in-pysilfont)-based workflows.

In addition to the UFO utilities, there is also support for testing using [FTML](#font-test-markup-language) and (composite definitions - how to phrase???).  

(Reference to Font Development Best Practices)

# Documentation

Documentation is held in the following documents:

- docs.md: This document with summary oy pysilfont, particularly with users in mind
- [scripts.md](scripts.md): List of all command line tools and scripts with usage instructions
- [technical.md](technical.md): Technical details for those wanting write scripts or other development tasks
- Other sub-documents, with links from the above

Installation instructions are in [README.md](README.md)

# Introduction

Most scripts are written to using a framework designed to give users a standard interface and simplify script writing.


# UFO support in Pysilfont

With some limitations, all UFO scripts in Pysilfont should work with UFO2 or UFO3 source files - and can convert from one format to the other.

In addition, most scripts will output UFOs in a normalized form, designed to work with source control systems. Most aspects of the normalization can be set by [parameters](parameters.md), so projects are not forced to use Pysilfont’s default normalization.

## Known limitations

The following are known limitations that will be addressed in the future:

- UFO 3 specific folders (data and images) are not copied
- Converting from UFO 3 to UFO 2 only handles data that has a place in UFO 2, but does include converting UFO 3 anchors to the standard way of handling them in UFO 2
- If a project uses non-standard files within the UFO folder, they are deleted

# Font Test Markup Language

FTML is described in the [FTML github project](https://github.com/silnrsi/ftml). Pysilfont includes some python scripts for working with FTML, and a python library so that new scripts can be written to read and write FTML files.

# Contributing to the project

Pysilfont is developed and maintained by SIL International’s [Non-Roman Script Initiative team](http://scripts.sil.org), though contributions from anyone are welcome. Pysilfont is copyright (c) 2014-2017 [SIL International](http://www.sil.org) and licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License). The project is hosted at [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont).


