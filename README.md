# Pysilfont - a collection of utilities for font development

Pysilfont is a collection of tools to support font development, with an emphasis on UFO-based workflows. With some limitations, all UFO scripts in Pysilfont should work with UFO2 or UFO3 source files - and can convert from one format to the other.

In addition, all scripts will output UFOs in a normalized form, designed to work with source control systems.

Please read the main [documentation](https://github.com/silnrsi/pysilfont/blob/master/docs/docs.md) in the docs folder for more details. Within there is a list of [scripts](https://github.com/silnrsi/pysilfont/blob/docs/scripts.md).

## Installation

Pysilfont requires Python 3.6+ and pip3. Some scripts also need other libraries.

### Updating your python toolchain to be current
```
sudo apt install python3-pip python3-setuptools
python3 -m pip install --upgrade pip setuptools wheel build
```

### Simple install
To just install the main scripts (only in the user's folder not system-wide) without cloning the GitHub repository run:
```
python3 -m pip install git+https://github.com/silnrsi/pysilfont
```

This will allow you to run the scripts listed in [scripts.md](https://github.com/silnrsi/pysilfont/blob/master/docs/scripts.md), but won’t give access
to the example scripts or give you the code locally to look at.

### Full install

First clone this repository or download the files from this [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont). To better isolate changes from your system Python we will use a virtual environment.
Then navigate to the newly created pysilfont directory and run:
```
sudo apt install python3-pip python3-venv python3-wheel python3-setuptools
```

Then create a virtual environment:
```
python3 -m venv venv
```
Get inside the virtual environment, you have to do this every time you want to use the pysilfont tools again:
```
source venv/bin/activate
```

Then install update the toolchain and install:
```
python3 -m pip install --upgrade pip setuptools wheel build
python3 -m pip install .
```

You can deactivate your virtual environment (venv) by typing:
```
deactivate
```
or by closing that Terminal. 


Alternatively to install in editable mode:
```
python3 -m pip install -e .
```

By default the dependencies pulled in are using releases. 



For developers: 

Install from git main/master to track the freshest versions of the dependencies:
```
python3 -m pip install --upgrade -e .[git]
```

To have more than one project in editable mode you should install each one separately and only install pysilfont at the last step, for example:
```
python3 -m pip install -e git+https://github.com/fonttools/fontbakery.git@main#egg=fontbakery
python3 -m pip install -e git+https://github.com/fonttools/fonttools@main#egg=fonttools
python3 -m pip install -e git+https://github.com/silnrsi/pysilfont.git@master#egg=silfont
```

### Uninstalling pysilfont

pip3 can be used to uninstall silfont:

locally for your user:
```
pip3 uninstall silfont
```

or to remove a venv (virtual environment):
```
deactivate (if you are inside the venv) 
rm -rf venv
```


or if you have it installed system-wide (only recommended inside a separate VM or container)
```
sudo pip3 uninstall silfont
```

If you need palaso, you will need to install it separately.
Follow the instructions on https://github.com/silnrsi/palaso-python

If you need fontbakery, you will need to install it separately.
Follow the instructions on https://font-bakery.readthedocs.io


## Contributing to the project

Pysilfont is developed and maintained by SIL International’s [Writing Systems Technology team ](https://software.sil.org/wstech/), though contributions from anyone are welcome. Pysilfont is copyright (c) 2014-2023 [SIL International](https://www.sil.org) and licensed under the [MIT license](https://en.wikipedia.org/wiki/MIT_License). The project is hosted at [https://github.com/silnrsi/pysilfont](https://github.com/silnrsi/pysilfont).
