#!/usr/bin/env python
#-*- coding: shift_jis -*-

import sys
sys.path.append( 'C:\zworks\projects\smalltool\memopad' )
from memopad import *

if __name__ == '__main__':

    # Model �̐���
    model = MemoPad()
    model.addObserver( ChangeLogger() )
    model.loadImage()

    # V-C �ɘA��
    testwindow = MemoPadFrame(model, mode='r')
    testwindow.mainloop()


