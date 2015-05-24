#!/usr/bin/env python
#-*- coding: shift_jis -*-

import sys
sys.path.append( 'C:\zworks\projects\smalltool\memopad' )
from memopad import *

if __name__ == '__main__':

    # Model の生成
    model = MemoPad()
    model.addObserver( ChangeLogger() )
    model.loadImage()

    # V-C に連結
    testwindow = MemoPadFrame(model, mode='r')
    testwindow.mainloop()


