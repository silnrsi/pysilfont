#!/usr/bin/env python3
'FontForge: Sample functions to call from other demo scripts'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import fontforge

def colLtnAGlyphs(font) :
    
    #print "Toggling colour of glyphs with LtnCapA in their name"
    for glyph in font:
        g = font[glyph]
        if glyph.find('LtnCapA') >= 0:
            if g.color != 0x00FF00:
                g.color = 0x00FF00 # Green
            else :
                 g.color = 0xFFFFFF # White           
    print "LtnCapA glyphs coloured"
    
def markOverlaps(font) :
    print "Toggling colour of glyphs where contours overlap"
    for glyph in font:
        g = font[glyph]
        if g.selfIntersects() :
            if g.color != 0xFF0000:
                g.color = 0xFF0000 # Red
            else :
                g.color = 0xFFFFFF # White           
    print "Glyphs coloured"
    
def markScaled(font) :
    print "Toggling colour of glyphs with scaled components"
    for glyph in font:
        g = font[glyph]
        for ref in g.references:
            transform=ref[1]
            if transform[0] != 1.0 or transform[3] != 1.0 :
                if g.color != 0xFF0000:
                    g.color = 0xFF0000 # Red
                else :
                    g.color = 0xFFFFFF # White           
    print "Glyphs coloured"

def clearColours(font) :
    for glyph in font :
        g = font[glyph]
        g.color = 0xFFFFFF
        
def functionList() :
    ''' Returns a dictionary to be used by callFunctions() and demoAddToMenu.py
    The dictionary is indexed by a group name which could be used as Tools menu 
    entry or to reference the group of functions. For each group there is a tuple 
    consisting of the Tools menu type (Font or Glyph) then one tuple per function.
    For each function the tuple contains:
            Function name
            Label for the individual function in dialog box called from Tools menu
            Actual function object'''
    funcList = {
        "Colour Glyphs":("Font",
        ("colLtnAGlyphs","Colour Latin A Glyphs",colLtnAGlyphs),
        ("markOverlaps","Mark Overlaps",markOverlaps),
        ("markScaled","Mark Scaled",markScaled),
        ("clearColours","Clear all colours",clearColours)),
        "Group with single item":("Font",
        ("clearColours","Clear all colours",clearColours))}
    return funcList

def callFunctions(functionGroup,font) :
    funcList=functionList()[functionGroup]
    i=0
    for tuple in funcList :
        if i == 0 :
            pass # Font/Glyph parameter not relevant here
        elif i == 1 :
            functionDescs=[tuple[1]]
            functions=[tuple[2]]
        else :
            functionDescs.append(tuple[1])
            functions.append(tuple[2])
        i=i+1
    
    if i == 2 : # Only one function in the group, so just call the function
        functions[0](font)
    else :
        functionNum=fontforge.ask(functionGroup,"Please choose the function to run",functionDescs)
        functions[functionNum](font)
        
    