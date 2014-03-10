#!/usr/bin/env python
'FontForge: Demo code to paste into the "Execute Script" dialog'
__url__ = 'http://projects.palaso.org/projects/pysilfont'
__copyright__ = 'Copyright (c) 2013, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

import sys, os, fontforge
sys.path.append(os.path.join(os.environ['HOME'], 'src/pysilfont/scripts'))
import samples.demoFunctions # Loads demoFunctions.py module from src/pysilfont/scripts/samples
reload (samples.demoFunctions) # Reload the demo module each time you execute the script to pick up any recent edits
samples.demoFunctions.callFunctions("Colour Glyphs",fontforge.activeFont())

'''Demo usage:
Open the "Execute Script" dialog (from the FontForge File menu or press ctrl+.),
paste just the code section this (from "import..." to "samples...") into there then
run it (Alt+o) and see how it pops up a dialogue with a choice of 3 functions to run.
Edit demoFunctions.py and alter one of the functions.
Execute the script again and see that that the function's behaviour has changed.

Additional functions can be added to demoFunctions.py and, if also defined functionList() 
become availably immdiately.

If you want to see the output from print statements, or use commands like input, (eg
for degugging purposes) then start FontForge from a terminal window rather than the 
desktop launcher.

When starting from a terminal window, you can also specify the font to use,
eg $ fontforge /home/david/RFS/GenBasR.sfd'''