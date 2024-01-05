
#!/usr/bin/env python3

from silfont.core import execute
import csv, sys

argspec = [
    ("ifont", {'help': 'Input font file'}, {'type': 'infont'}),
    ('-o', '--output', {'help': 'Output CSV file'}, {'type': 'outfile'})
]

def decode_element(e):
    '''Convert plist element into python structures'''
    res = None
    if e.tag == 'string':
        return e.text
    elif e.tag == 'integer':
        return int(e.text)
    elif e.tag== 'real':
        return float(e.text)
    elif e.tag == 'array':
        res = [decode_element(x) for x in e]
    elif e.tag == 'dict':
        res = {}
        for p in zip(e[::2], e[1::2]):
            res[p[0].text] = decode_element(p[1])
    return res

def doit(args):
    f = args.ifont # ufo.Ufont(args.ifont)
    if not hasattr(f, 'kerning'):
        return
    csvw = csv.writer(args.output)
    for k, v in f.kerning._contents.items():
        key = k.lstrip('@')
        subelements = decode_element(v[1])
        for s, n in subelements.items():
            skey = s.lstrip('@')
            csvw.writerow([key, skey, n])

def cmd() : execute("UFO", doit, argspec)

if __name__ == "__main__": cmd()

