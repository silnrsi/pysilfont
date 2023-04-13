#!/usr/bin/env python3
'FontForge: Demo script to add menu items to FF tools menu'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import sys, os, fontforge
sys.path.append(os.path.join(os.environ['HOME'], 'src/pysilfont/scripts'))
import samples.demoFunctions
from samples.demoFunctions import functionList, callFunctions
#from samples.demoCallFunctions import callFunctions

def toolMenuFunction(functionGroup,font) :
    reload (samples.demoFunctions)
    callFunctions(functionGroup,font)
    
funcList=functionList()

for functionGroup in funcList :
    menuType = funcList[functionGroup][0]
    fontforge.registerMenuItem(toolMenuFunction,None,functionGroup,menuType,None,functionGroup);
    print functionGroup, " registered"

''' This script needs to be called from one of the folders that FontForge looks in for scripts to
run when it is started. With current versions of FontForge, one is Home/.config/fontforge/python.
You may need to turn on showing hidden files (ctrl-H in Nautilus) before you can see the .config 
folder.  Within there create a one-line python script, say call sampledemo.py containing a call 
to this script, eg:

execfile("/home/david/src/pysilfont/scripts/samples/demoAddToMenu.py")

Due to the reload(samples.demoFunctions) line above, changes functions defined in demoFunctions.py 
are dynamic, ie FontForge does not have to be restarted (as would be the case if the functions were
called directly from the tools menu. Functions can even be added dynamically to the function groups.

If new function groups are defined, FontForge does have to be restarted to add them to the tools menu.
'''
