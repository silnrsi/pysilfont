#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
from copy import deepcopy
from UFOtestlib2 import *
import re, sys, os

if __name__ == '__main__' :

    print
    print
    font = Ufont(ufodir=sys.argv[1])
    
    font.outparams["UFOversion"] = 3
    #font.outparams["plistIndentFirst"] = "  "
    #font.outparams["indentFirst"] = "\t"
    #font.outparams["indentIncr"] = "\t"
    
    testn = "barx"
    if testn in font.layers[0] :
        glif = font.layers[0][testn]
        for i in glif :
            print "-------------------"
            print i
            print glif[i]
            index = glif[i]['index']
            print glif.etree[index]
        glif.outparams = font.outparams.copy()
        glif.outparams["indentFirst"] = "  "
        glif.outparams["indentIncr"] = "  "
    


    print "<<<< Writing font out >>>>"
    font.write("./out.ufo")
        
    sys.exit()

# ******************* Old dev code below
    
    uinput = sys.argv[1]
    if not os.path.isdir(uinput) :
        print uinput + " not a directory"
        sys.exit()
    
    # Read list of files and folders in top 2 levels; anything at lower levels just needs copying
    (upath,ubase) = os.path.split(uinput)
    utree={}
    for name in os.listdir(uinput) :
        item={}
        if os.path.isdir(os.path.join(uinput, name)) :
            item["type"] = "d"
            item["contents"] = {}
            for subname in os.listdir(os.path.join(uinput, name)) :
                item["contents"][subname] = {}
                if os.path.isdir(os.path.join(uinput, name, subname)) :
                    item["contents"][subname]["type"] = "d"
                else:
                    item["contents"][subname]["type"] = "f"
        else :
            item["type"] = "f"
        utree[name] = item
    
    for i in utree :
        print i, utree[i]
        #for j in utree[i] :
         #   print j, utree[i][j]

    sys.exit()
    
    # Sort the key,value pairs alphabetically
    if item.etree.tag == 'plist' :
        item.etree.doctype = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'
        pldict = item.etree[0]
        plist={}
        for i in range(0,len(pldict),2):
            key = pldict[i].text
            plist[key] = [pldict[i],pldict[i+1]]
        
        i=0    
        for key in sorted(plist.keys()):
            item.etree[0][i]=plist[key][0]
            item.etree[0][i+1]=plist[key][1]
            i=i+2

    newitem = deepcopy(item)
    newitem.xmlstring=""
    output = ETWriter(newitem.etree)
    if newitem.etree.tag == 'plist' : output.indentFirst = ""
    output.serialize_xml(newitem.write_to_xml)
    
    outfile=open("xmltest.xml","w")
    outfile.write(newitem.xmlstring)
    outfile.close