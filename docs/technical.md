# Pysilfont Technical Documentation
This section is for script writers and developers.

See [docs.md](docs.md) for the main Pysilfont user documentation.

# Writing scripts
The Pysilfont modules are designed so that all scripts operate using a standard framework based on the execute() command in core.py.  The purpose of the framework is to:
- Simplify the writing of scripts, with much work (eg parameter parsing, opening fonts) being handled there rather than within the script.
- Provide a consistent user interface for all Pysilfont command-line scripts

The framework covers:
- Parsing arguments (parameters and options)
- Defaults for arguments
- Extended parameter support by command-line or config file
- Producing help text
- Opening fonts and other files
- Outputting fonts (including normalization for UFO fonts)
- Initial error handling
- Reporting - both to screen and log file

## Basic use of the framework

The structure of a command-line script should be:
```
<header lines>
<general imports, if any>

from silfont.core import execute

argspec = [ <parameter/option definitions> ]

def doit(args):
    <main script code>
    return <output font, if any>

<other function definitions>

def cmd() : execute(Tool,doit, argspec)
if __name__ == "__main__": cmd()
```

The following sections work through this, using psfnormalize, which normalizes a UFO, with the option to convert between different UFO versions:
```
#!/usr/bin/env python    
'''Normalize a UFO and optionally convert between UFO2 and UFO3.
- If no options are chosen, the output font will simply be a normalized version of the font.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_conv.log'}),
    ('-v','--version',{'help': 'UFO version to convert to'},{})]

def doit(args) :

    if args.version is not None : args.ifont.outparams['UFOversion'] = args.version

    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
```
#### Header lines
Sample headers:
```
#!/usr/bin/env python    
'''Normalize a UFO and optionally convert between UFO2 and UFO3.
- If no options are chosen, the output font will simply be a normalized version of the font.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
```
As well as providing the information for someone looking at the source file, the description comment (second line, which can be multi-line) is used by the framework when constructing the help text.

#### Import statement(s)
```
from silfont.core import execute
```
is required.  Other imports from pysilfont or other libraries should be added, if needed.
#### Argument specification
The argument specifications take the form of a list of tuples, with one tuple per argument, eg:
```
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_conv.log'}),
    ('-v','--version',{'help': 'UFO version to convert to'},{})]
```
Each argument has the format:
```
(argument name(s),argparse dict,framework-specific dict)
```
argument name is either
- name for positional parameters, eg *‘ifont’*
- *-n --name* or *--name* for other arguments, eg *‘-v’, ‘--version’*

**argparse dict** follows standard [argparse usage for .add_argument()](https://docs.python.org/2/library/argparse.html#the-add-argument-method).  Help should always be included.

**framework-specific dict** has optional values for:
- ‘type’ - the type of parameter, eg ‘outfile’
- ‘def’ - default for file names.  Only applies if ‘type’ is a font or file.

‘Type’ can be one of:

| Value | Action |
|-------|-------------------------------------|
|infont|Open a font of that name and pass the font to the main function|
|outfont|If the main function to returns a font, save that to the supplied name|
|infile|Open a file for read and pass the file handle to the main function|
|incsv|Open a csv file for input and pass iterator to the main function|
|outfile|Open a file for writing and pass the file handle to the main function|
|filename|Filename to be passed as text|
|optiondict|Expects multiple values in the form name=val and passes a dictionary containing them|

If ‘def’ is supplied, the parameter value is passed through the file name defaulting as specified below.  Applies to all the above types except for optiondict.

In addition to options supplied in argspec, the framework adds [standard options](docs.md#standard-command-line-options), ie:

-   -h, --help
-   -d, --defaults
-   -q, --quiet
-   -p, --params
-   -l, --log

so these do not need to be included in argspec.

#### doit() function
The main code of the script is in the doit() function.  

The name is just by convention - it just needs to match what is passed to execute() at the end of the script.  The
execute() function passes an args object to doit() containing:
- An entry for each command-line argument as appropriate based on the full name of the argument
  - eg with ``'-v','--version'``, args.version is set to the value given on the command line (or None if no value given).
  - this includes params, quiet and log added by the framework, but see below for params
- logger for the loggerobj()
- clarguments for a list of what was actually specified on the command line
- For parameters:
  - params is a list of what parameters, if any, were specified on the command line
  - paramsobj is the  parameters object containing all [parameter](parameters.md) details

The final lines

These should always be:
```
def cmd() : execute(Tool,doit, argspec)
if __name__ == "__main__": cmd()
```
The first line defines the function that actually calls execute() to do the work, where Tool is one of:
- “UFO” to open fonts with pysilfont’s ufo.py module, returning a Ufont object
- “FF” to open fonts with Fontforge, returning a font object
- “FT” to open fonts with FontTools, returning a TTfont object
- None if no font to be opened by execute()
- Other tools may be added in the future

The function must be called cmd(), since this is used by setup.py to install the commands.

The second line is the python way of saying, if you run this file as a script (rather than using it as a python module), execute the cmd() function.

Even if a script is initially just going to be used to be run manually, include these lines so no modification is needed to make it installable at a later date.

# Further framework notes
## Default values for arguments
Default values in [docs.md](docs.md#default-values) describes how file name defaulting works from a user perspective.

To set default values, either use the ‘default’ keyword in the argparse dict (for standard defaults) or the ‘def’ keyword in the framework-specific dict to use Pysilfont’s file-name defaulting mechanism.  Only one of these should be used.  'def' can't be used with the first positional parameter.

Note if you want a fixed file name - ie to bypass the file name defaulting mechanism, then use the argparse default keyword.

## Reporting
args.logger is a loggerobj(), and used to report messages to screen and log file.  If no log file is set, messages are just to screen.

Messages are sent using
```
logger.log(<message text>, [severity level]>
```
Where severity level has a default value of W and can be set to one of:
- X	Exception - for programming errors
- S	Severe - For fatal errors
- E	Errors
- P	Progress - Reports basic progress messages and all errors
- W	Warning - As P but with warning messages as well
- I	Info - As W but with information messages as well
- V	Verbose - even more messages!

Errors are reported to screen if the severity level is higher or equal to logger.scrlevel (default E) and to log based on loglevel (default W).  The defaults for these can be set via parameters or within a script, if needed.

With X and S, the script is terminated.  S should be used for user problems (eg file does not exists, font is invalid) and X for programming issues (eg an invalid value has been set by code).  Exception errors are mainly used by the libraries and force a stack trace.

With Ufont objects, font.logger also points to the logger, but this is used primarily within the libraries rather than in scripts.

There would normally only be a single logger object used by a script.

## Support for csv files
csv file support has been added to core.py with a csvreader() object (using the python csv module).  In addition to the basic handling that the csv module provides, the following are supported:
- Specifying the number of values expected (with minfields, maxfields, numfields)
- Comments (lines starting with #) are ignored
- Blank lines are also ignored

The csvreader() object is an iterator which returns the next line in the file after validating it against the min, max and num settings, if any, so the script does not have to do such validation.  For example:
```
incsv = csvreader(<filespec>)
incsv.minfields = 2
Incsv.maxfields = 3
for line in inscv:
    <code>
```
Will run `<code>` against each line in the file, skipping comments and blank lines.  If any lines don’t have 2 or 3 fields, an error will be reported and the line skipped.

## Parameters
[Parameters.md](parameters.md) contains user, technical and developer’s notes on these.

## Chaining
With ufo.py scripts, core.py has a mechanism for chaining script function calls together to avoid writing a font to disk then reading it in again for the next call.  In theory it could be used simply to call another script’s function from within a script.

This has not yet been used in practice, and will be documented (and perhaps debugged!) when there is a need, but there are example scripts to show how it was designed to work.

# pysilfont modules

These notes should be read in conjunction with looking at the comments in the code (and the code itself!).

## core.py

This is the main module that has the code to support:
- Reporting
- Logging
- The execute() function
- Chaining
- csvreader()

## etutil.py

Code to support xml handling based on xml.etree cElementTree objects.  It covers the following:
- ETWriter() - a general purpose pretty-printer for outputting xml in a normalized form including
  - Various controls on indenting
  - inline elements
  - Sorting attributes based on a supplied order
  - Setting decimal precision for specific attributes
  - doctype, comments and commentsafter
- xmlitem() class
  - For reading and writing xml files
  - Keeps record of original and final xml strings, so only need to write to disk if changed
  - write_to_xml() function to create outxmlstr using ETWriter()
- ETelement() class
  - For handling an ElementTree element
  - For each tag in the element, ETelement[tag] returns a list of sub-elements with that tag
  - process_attributes() processes the attributes of the element based on a supplied spec
  - process_subelements() processes the subelements of the element based on a supplied spec

xmlitem() and ETelement() are mainly used as parent classes for other classes, eg in ufo.py

The process functions validate the attributes/subelements against the spec.  See code comments for details.

## util.py

Module for general utilities.  Currently just contains dirtree code.

#### dirTree

A dirTree() object represents all the directories and files in a directory tree and keeps track of the status of the directories/files in various ways.  It was designed for use with ufo.py, so, after changes to the ufo, only files that had been added or changed were written to disk and files that were no longer part of the ufo were deleted.  Could have other uses!

Each dirTreeItem() in the tree has details about the directory or file:
- type
  - "d" or "f" to indicate directory or file
- dirtree
  - For sub-directories, a dirtree() for the sub-directory
- read
  - Item has been read by the script
- added
  - Item has been added to dirtree, so does not exist on disk
- changed
  - Item has been changed, so may need updating on disk
- towrite
  - Item should be written out to disk
- written
  - Item has been written to disk
- fileObject
  - An object representing the file
- fileType
  - The type of the file object
- flags
  - Any other flags a script might need


## ufo.py

See [ufo.md](ufo.md) for details

## ftml.py

To be written

## cd.py

To be written

# Developer's notes

To cover items relevent to extending the library modules or adding new

To be written
