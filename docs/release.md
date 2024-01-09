# Release steps

The release steps are currently:

- updating the Changelog (pinging others who may have added new scripts or made significant changes) 
- bumping up the version in `pyproject.toml` and `src/silfont/__init__.py`  (e.g. 1.9.0)
- tagging the repository with the release number (e.g. v1.9.0)
- merging the changes into the `release` branch
- removing the whole `[project.optional-dependencies]` section in pyproject.toml in the release branch
- building the package locally using `python3 -m build`  
- uploading the resulting package and source tarball in `dist/` to [PyPi the Python Package Index](http://pypi.org) using `twine` and credentials in `~/.pypirc`
- switching back to the `master` branch
- bumping up the version in `pyproject.toml` and `src/silfont/__init__.py` to add the devX prefix (e.g. 1.9.0.dev0)

