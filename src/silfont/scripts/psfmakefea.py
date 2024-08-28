#!/usr/bin/env python3
'''Warning message about migration to feaxlib and makefea script'''


def cmd():
    '''the simplest function possible'''
    msg = """WARNING: psfmakefea is no longer to be used.
All feax capabilities have been moved to the separate feaxlib module.
Please adjust any scripts to use makefea from feaxlib instead (https://github.com/silnrsi/feax).
"""
    print(msg)


if __name__ == "__main__":
    cmd()
