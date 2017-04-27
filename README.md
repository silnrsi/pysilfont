# Pysilfont - a framework and collection of utilities for font development

Pysilfont is a collection of tools to support font development, with an emphasis on UFO-based workflows. With some limitations, all UFO scripts in Pysilfont should work with UFO2 or UFO3 source files - and can convert from one format to the other.

In addition, all scripts will output UFO in a normalized form, designed to work with source control systems. Most aspects of the normalization can be set by [parameters](#parameters), so projects are not forced to use Pysilfont’s default normalization.

## Installation

Pysilfont requires Python version 2.7.x and python-setuptools. Some scripts also need FontForge or FontTools.

_Note: We are experiencing issues with upgrades to existing installations and with uninstalling, so these notes are under review._

### macOS and Linux

First clone this repository or download the files from [this github URL](https://github.com/silnrsi/pysilfont.git). Then navigate to the resulting pysilfont directory.

To install the module and the scripts for the current user only run:

```
python setup.py install --user --record installed-files.txt
sudo apt-get install python-setuptools
```

or to install for all users run:

```
sudo python setup.py install --record installed-files.txt
sudo apt-get install python-setuptools
```

If upgrading an existing installation you will need to clean up from previous installations by running this before the commands above:

```
python setup.py clean --all
```

_If you get warning messages about some modules requiring certain packages you can safely ignore them. We're working on it._

### Windows

(to be added)

### Uninstalling pysilfont

To uninstall pysilfont run:

```
sudo -H pip uninstall pysilfont
```

_This gives an error about an egg file missing, but does successfully complete. If you don't have pip installed, you will need to install it with ```sudo apt install python-pip```_.

To get rid of all the files installed run:

```
cat installed-files.txt | xargs sudo rm --verbose -vr
```

## Using the command-line tools

Pysilfont installs a few tools that can be run directly from the command line:

| Command | Description |
| ------- | ----------- |
| FTMLcreateOdt | Creates a LibreOffice Writer file from an FTML test description |
| UFOconvert | Normalizes a UFO and optionally converts it between UFO2 and UFO3 versions |
| UFOcopyMeta | Copies basic metadata from one UFO to another, such as between fonts in related families |
| UFOexportAnchors | Exports UFO anchor data to a separate XML file |
| UFOsetVersion | Changes all the version-related info in a UFO's fontinfo.plist |
| UFOsyncMeta | Copies basic metadata from one member of a font family (typically Regular) to all other family members |

Detailed instructions for these commands are in [the next section on installed tools](#installed-tools). You can also run any of these commands with the ```-h``` option to receive basic help, as in:

```
UFOconvert -h
```

## Other scripts

Pysilfont includes a wide variety of scripts that are not automatically installed as system tools but can be run like any other python script, and can be used as examples for your own custom scripts. Most of these scripts act directly on UFO files, however some are specific to FontForge, FontTools, or Graphite.

The scripts are located in three places:

- pysilfont/scripts
- pysilfont/scripts/examples
- pysilfont/lib/silfont/scripts - _these are the scripts installed as system tools_

These scripts can be run by navigating to the directory containing the script and running

```
python scriptname.py
```

As with installed tools, most scripts provide basic help with the ```-h``` option.

Here is a list of currently included scripts. Details of specific script usage not documented here. Read the script header for instructions.

| Script | Description |
| ------- | ----------- |
| UFOaddAnchors.py |  |
| (etc...) |  |



## Developing new scripts

(intended as a short description of what the framework provides with internal links to details in later sections)

## Future plans

Future planned enhancements include:

- Python 3 support
- and...

## Contributing to the project

Pysilfont is developed and maintained by SIL International’s [Non-Roman Script Initiative team](http://scripts.sil.org), though contributions from anyone are welcome. Pysilfont is copyright (c) 2014-2017 [SIL International](http://www.sil.org) and licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License). The project is hosted at [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont).

---

# Installed tools

#### FTMLcreateOdt

#### UFOconvert [-h] [-d] [-v VERSION] [-p PARAMS] ifont [ofont]

This converts UFO fonts from one version to another (such as UFO2 to UFO3), but if no version is specified it will only normalize the font without converting it. _Note that most pysilfont scripts automatically output normalized UFOs, so UFOconvert is normally only needed after fonts have been processed by external font tools._

Example that normalizes the named font:

```
UFOconvert Nokyung-Regular.ufo
```

The normalization has the following default behaviours, but these can be overriden using [custom parameters](#parameters):

- Uses 2 spaces as indents
- Doesn’t indent the <dict> for plists
- Sorts all <dict>s in ascending key order
- Stores values as integers if possible
- Limits <real> precision to 6
- Uses the UFO3 suggested algorithm for .glif file names
- Orders glif elements and attributes in the order they are described in the UFO spec

Known limitations that will be addressed in the future:
- UFO3 specific folders (data and images) are not copied
- Converting from UFO3 to UFO2 only handles data that has a place in UFO2, but does include converting UFO3 anchors to the common way of handling them in UFO2
- If a project includes non-standard files within the UFO folder, they are deleted

If you are a macOS user, see _scripts/tools/actionsosx/README.txt_ to install an action that will enable you to run UFOconvert without using the command line.

#### UFOcopyMeta



#### UFOexportAnchors



#### UFOsetVersion



#### UFOsyncMeta






---

# Options

## Reporting levels


## Displaying defaults


## File names and paths


## Backup options


---

# Parameters

---

# Developing scripts and tools

Most scripts are written to (?) using a framework designed to give users a standard interface and simplify script writing.
