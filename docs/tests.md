# Test suite
pysilfont has a pytest-based test suite.

### install the test framework:
```
python3 -m pip install pytest
```

## set up the folders:
```
python3 tests/setuptestdata.py
```

## get extra modules:
```
python3 -m pip install git+https://github.com/silnrsi/palaso-python

python3 -m pip install git+https://github.com/typemytype/GlyphConstruction.git
```

## install the deps
```
python3 -m pip install .[git]


## run the test suite:
```
pytest --full-trace -v 
```
