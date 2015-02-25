import types, sys, os
import fontforge

args = len(sys.argv)
# Open the font
if args>1:
    infont = sys.argv[1]
else:
    infont = "/home/david/UFO/UFOtest/TestBase.ufo"

if args>2:
    outfont = sys.argv[2]
else:
    (base,ext) = os.path.splitext(infont)
    outfont = base + "_FF" + ext

print "Opening "+infont
fffont = fontforge.open(infont)

print "Closing "+outfont
fffont.generate(outfont)


