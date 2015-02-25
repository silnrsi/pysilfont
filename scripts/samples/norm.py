import types, sys, os
from robofab.world import *

args = len(sys.argv)
# Open the font
if args>1:
    infont = sys.argv[1]
else:
    infont = "/home/david/UFO/Norm/ssp-r_Norm_FF_Norm_Rough.ufo"

(base,ext) = os.path.splitext(infont)

if args>2:
    outfont = sys.argv[2]
else:
    outfont = base + "_Norm" + ext

logname = base + "_Norm.log"
nlog = open(logname,"w")

def writelog(message):
    nlog.write(message + "\n")

writelog("Normalising "+infont)

print "Opening "+infont
rf = OpenFont(infont)

# Create pointers to main objects
finfo=rf.info
kern=rf.kerning
flib=rf.lib

# Read saved info from lib
nfikey="org.sil.normSavedFontinfo"
if nfikey in flib:
    savedfi=flib[nfikey]
else: savedfi={}

# Glyphs changes .null to null so change back
if rf.has_key("null"):
    writelog("null glyph name changed to .null")
    rf["null"].name=".null"

# Sort anchors and components in Glyphs alphabetically
for g in rf:
    new=sorted(g.anchors, key=lambda anc: anc.name )
    if new <> g.anchors:
        g.anchors=new
        writelog("Glyph anchors reordered for " + g._name)
    new=sorted(g.components, key=lambda comp: comp.baseGlyph + str(comp.offset) )
    if new <> g.components:
        g.components=new
        writelog("Glyph components reordered for " + g._name)
    

# Process changes in fontinfo.plist using previous copy saved in lib
for key in savedfi:
    if not(key in finfo.__dict__):
            finfo.__dict__[key]=savedfi[key]
            writelog(key + " added back into fontinfo.plist with value: " + str(savedfi[key]))
# Save current fontinfo values in lib for future normalisation runs
fidict=dict(finfo.__dict__) # Create new dictionary with current fontinfo values
del fidict['_object'] # Remove non-key attributes from dict
del fidict['changed']
del fidict['getParent']
del fidict['selected']
flib[nfikey]=fidict
 
print "Closing "+outfont
rf.save(outfont)

