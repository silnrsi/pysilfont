#!/usr/bin/env python3
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2024 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import subprocess

fbcommand = ["fontbakery", "check-profile", "silfont.fbtests.profile", "projects/Abyssinica/*.ttf", "--succinct", "--html", "test.html"]

test = subprocess.Popen(fbcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
text = test.communicate()
returncode = test.returncode

print(text[0].decode("utf-8"))
print(text[1].decode("utf-8"))
print(returncode)
