# Pysilfont - a collection of utilities for font development

Pysilfont is a collection of tools to support font development, with an emphasis on UFO-based workflows. With some limitations, all UFO scripts in Pysilfont should work with UFO2 or UFO3 source files - and can convert from one format to the other.

In addition, all scripts will output UFOs in a normalized form, designed to work with source control systems.

Please read the main [documentation](docs/docs.md) is in the docs folder for more details.  Within there is a list of [scripts](docs/scripts.md).

# NOTICE - Python 2 support to be withdrawn

Pysilfont now works with Python 2 & 3.  Full support for Python 2 will be withdrawn shortly.

## Installation

Pysilfont requires Python (version 2.7.x or 3.6+) and python-setuptools. Some scripts also need other libraries.

_Note: We are experiencing issues with upgrades to existing installations and with uninstalling, so these notes are under review._

### macOS and Linux

First clone this repository or download the files from [this github URL](https://github.com/silnrsi/pysilfont.git). Then navigate to the resulting pysilfont directory.

To install the module and the scripts for the current user only run:

```
python setup.py install --user --record installed-files.txt
```

or, if multiple users use your system and you want to install for all users, run:

```
sudo python setup.py install --record installed-files.txt
```

If setup.py fails with a message that python-setuptools is missing, run the following to install it, then run setup.py again.

```
sudo apt-get install python-setuptools
```

If upgrading an existing installation you will need to clean up from previous installations by running this before the commands above:

```
python setup.py clean --all
```


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
cat installed-files.txt | xargs sudo rm -vr
```

## Contributing to the project

Pysilfont is developed and maintained by SIL International’s [Writing Systems Technology team ](https://software.sil.org/wstech/), though contributions from anyone are welcome. Pysilfont is copyright (c) 2014-2020 [SIL International](http://www.sil.org) and licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License). The project is hosted at [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont).
