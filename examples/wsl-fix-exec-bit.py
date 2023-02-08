#!/usr/bin/python3
'''simple script to fix WSL's executable bit limitations'''

import subprocess

print("Fixing the execute bit in the current git local clone")

subprocess.call('chmod -c u+x $(git ls-files --stage | grep -e "^100755" | cut -f2)', shell=True)
