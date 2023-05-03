#!/usr/bin/env python
__doc__ = 'Compress Graphite tables in a font'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

argspec = [
    ('ifont',{'help': 'Input TTF'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output TTF','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Optional log file'}, {'type': 'outfile', 'def': '_compressgr', 'optlog': True})
]

from silfont.core import execute
from fontTools.ttLib.tables.DefaultTable import DefaultTable
import lz4.block
import sys, struct

class lz4tuple(object) :
    def __init__(self, start) :
        self.start = start
        self.literal = start
        self.literal_len = 0
        self.match_dist = 0
        self.match_len = 0
        self.end = 0

    def __str__(self) :
        return "lz4tuple(@{},{}+{},-{}+{})={}".format(self.start, self.literal, self.literal_len, self.match_dist, self.match_len, self.end)

def read_literal(t, dat, start, datlen) :
    if t == 15 and start < datlen :
        v = ord(dat[start:start+1])
        t += v
        while v == 0xFF and start < datlen :
            start += 1
            v = ord(dat[start:start+1])
            t += v
        start += 1
    return (t, start)

def write_literal(num, shift) :
    res = []
    if num > 14 :
        res.append(15 << shift)
        num -= 15
        while num > 255 :
            res.append(255)
            num -= 255
        res.append(num)
    else :
        res.append(num << shift)
    return bytearray(res)

def parseTuple(dat, start, datlen) :
    res = lz4tuple(start)
    token = ord(dat[start:start+1])
    (res.literal_len, start) = read_literal(token >> 4, dat, start+1, datlen)
    res.literal = start
    start += res.literal_len
    res.end = start
    if start > datlen - 2 : 
        return res
    res.match_dist = ord(dat[start:start+1]) + (ord(dat[start+1:start+2]) << 8)
    start += 2
    (res.match_len, start) = read_literal(token & 0xF, dat, start, datlen)
    res.end = start
    return res

def compressGr(dat, version) :
    if ord(dat[1:2]) < version :
        vstr = bytes([version]) if sys.version_info.major > 2 else chr(version)
        dat = dat[0:1] + vstr + dat[2:]
    datc = lz4.block.compress(dat[:-4], mode='high_compression', compression=16, store_size=False)
    # now find the final tuple
    end = len(datc)
    start = 0
    curr = lz4tuple(start)
    while curr.end < end :
        start = curr.end
        curr = parseTuple(datc, start, end)
    if curr.end > end :
        print("Sync error: {!s}".format(curr))
    newend = write_literal(curr.literal_len + 4, 4) + datc[curr.literal:curr.literal+curr.literal_len+1] + dat[-4:]
    lz4hdr = struct.pack(">L", (1 << 27) + (len(dat) & 0x7FFFFFF))
    return dat[0:4] + lz4hdr + datc[0:curr.start] + newend

def doit(args) :
    infont = args.ifont
    for tag, version in (('Silf', 5), ('Glat', 3)) :
        dat = infont.getTableData(tag)
        newdat = bytes(compressGr(dat, version))
        table = DefaultTable(tag)
        table.decompile(newdat, infont)
        infont[tag] = table
    return infont

def cmd() : execute('FT', doit, argspec)
if __name__ == "__main__" : cmd()

