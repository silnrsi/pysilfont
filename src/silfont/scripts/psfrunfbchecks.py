#!/usr/bin/env python3
'''Simple warning message about the new ways to run Font Bakery'''


def cmd():
    '''the simplest function possible'''
    msg = """psfrunfbchecks is no longer functional.
Please use *smith fbchecks* or fontbakery directly with the pysilfont profile:
*fontbakery check-profile silfont.fbtests.profile [options] *-Regular.ttf*"""
    print(msg)


if __name__ == "__main__":
    cmd()
