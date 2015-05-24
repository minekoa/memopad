#!/usr/bin/env python
#-*- coding: shift_jis -*-

from datetime import *


class Subject(object):
    def __init__(self):
        self.observers = []

    def notifyUpdate(self, aspect, obj=None):
        for observer in self.observers:
            observer.update( aspect , obj )

    def addObserver(self, observer):
        self.observers.append(observer)



class Memo (Subject):
    def __init__(self):
        Subject.__init__(self)

        self.text = ''
        self.datetime = datetime.now()


    def getDatetime(self):
        return self.datetime

    def setDatetime(self, datetime):
        self.datetime = datetime
    

    def getTitle(self):
        try:
            return self.text.splitlines()[0]
        except IndexError:
            return self.text


    def getText(self):
        return self.text

    def setText(self, text):
        self.text = text
        self.notifyUpdate("setText", self)



import os
import os.path
import re


class MemoPad(Subject):
    def __init__(self):
        Subject.__init__(self)

        # メンバの初期化
        self.memos = []
        self.selectedIndex = -1



    #==================================
    # accessing
    #==================================

    def getSelectedItem(self):
        if self.selectedIndex == -1 : return None
        return self.memos[self.selectedIndex]

    def getSelectedIndex(self):
        return self.selectedIndex


    #==================================
    # selealization
    #==================================

    def loadImage(self):
        ptn = re.compile( r"(\d{4})-(\d{2})-(\d{2})T(\d{2})(\d{2})(\d{2})(\d{6})\.memo" )

        # 既存イメージのクリア
        self.memos = []
        self.selectedIndex = -1

        # イメージリストのロード
        for (root, dirs, files) in os.walk( os.path.join(os.curdir, 'memo') ):
            print '***', root, '***'
            for filename in files:
                matobj = ptn.match( filename )
                if matobj != None:

                    # Memo の生成と初期化
                    memo = Memo()
                    memo.setDatetime( datetime( int(matobj.group(1)),
                                                int(matobj.group(2)),
                                                int(matobj.group(3)),
                                                int(matobj.group(4)),
                                                int(matobj.group(5)),
                                                int(matobj.group(6)),
                                                int(matobj.group(7)) ) )
                    memo.setText( open( os.path.join('memo', filename), 'r' ).read().decode('shift_jis') )
                    memo.addObserver(self)

                    print memo.getDatetime().__str__(),memo.getTitle()

                    # 登録
                    self.memos.insert(0, memo)


        # カーソルの初期化
        if len(self.memos) != 0:
            self.selectedIndex = 0


    def saveImage(self):
        for i in self.memos:
            f = open( 'memo/%s%06d.memo' % (i.getDatetime().strftime("%Y-%m-%dT%H%M%S"),
                                            i.getDatetime().microsecond), "w")
            f.write( i.getText().encode('shift_jis') )


    #==================================
    # list-operation
    #==================================

    def appendMemo(self):
        newMemo = Memo()
        newMemo.setText("**no-subject**")
        newMemo.addObserver(self)

        self.memos.insert(0, newMemo )
        self.selectedIndex = 0

        self.notifyUpdate("appendMemo", self)


    def removeMemo(self):
        if self.selectedIndex == -1: return

        rmvtarget = self.memos[self.selectedIndex]
        self.memos.remove( rmvtarget )

        if len(self.memos) <= self.selectedIndex:
            self.selectedIndex = len(self.memos) -1

        print "rmv「", rmvtarget.getText(), "」"
        self.notifyUpdate("removeMemo", self)


    def selectMemo(self, index):
        if index < 0 or len(self.memos) <= index:
            raise IndexError( "%d is not contain [0..%d)" % (index, len(self.memos)) )

        self.selectedIndex = index

        self.notifyUpdate("selectMemo", self)


    #==================================
    # observer
    #==================================

    def update( self, aspect, obj ):
        self.notifyUpdate(aspect, obj)


    #==================================
    # iterator
    #==================================

    def __getitem__(self, key):
        return self.memos[key]

    def __setitem__(self, key, value):
        self.memos[key] = value

    def __len__(self):
        return self.memos.__len__()


from Tkinter import *
from tkscrlist import *
from ScrolledText import *


class MemoPadFrame( Frame ):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        # Modelの初期化
        self.version = (0, 2, 0)
        self.memos = MemoPad()
        self.memos.loadImage()
        self.memos.addObserver(self)

        # View-Controller の初期化
        self.master.title( 'MemoPad %d.%d.%d' % self.version )
        self.make_listPanel(self)
        self.make_editAria(self)
        self.pack(fill=BOTH)

        self.update(None,None)

#        self.fill_testlist()
#        self.memoList.selection_set( 0 )
#        self.openMemo( self.memos[0] )



        def bye():
            self.memos.saveImage()
            print 'bye'
            self.master.destroy()

        self.master.protocol('WM_DELETE_WINDOW', bye )


    def make_listPanel(self, parent):
        frm = Frame(parent)

        # リストの生成・配置
        def changeTarget(evt):
            curSel = self.memoList.curselection()
            newIndex = int(curSel[0])

            self.saveMemo( self.memos.getSelectedItem() )
            print '--- save %d---' % self.memos.getSelectedIndex()

            self.memos.selectMemo( newIndex )


        self.memoList = ScrolledListbox(frm,
                                        selectmode=BROWSE,#SINGLE,
                                        width=50,
                                        height=5 )
        self.memoList.bind("<ButtonRelease>", changeTarget )
        self.memoList.pack(side=LEFT, fill=BOTH)


        # ボタンの作成
        btnfrm = Frame(frm)

        def appendMemo():
            self.memos.appendMemo()

        Button( btnfrm,
                text='new',
                command=appendMemo ).pack(side=TOP, fill=X)


        def deleteMemo():
            self.memos.removeMemo()

        Button( btnfrm,
                text='delete',
                command=deleteMemo ).pack(side=TOP, fill=X)


        btnfrm.pack(side=LEFT)

        frm.pack(side=TOP)



    def make_editAria(self, parent):
        self.text = ScrolledText( parent )
        self.text.pack(side=TOP)


    def update(self, aspect, obj):
        print "disyplay update (%s)" % aspect
        self.renderList()
        self.renderTextArea()



    #==================================
    # rendering
    #==================================

    def renderList(self):
        self.memoList.delete(0, END)
        for memo in self.memos:
            self.memoList.insert(END, 
                                 "%s | %s" % (memo.getDatetime().strftime("%Y-%m-%d %H:%M"),
                                              memo.getTitle()))

        self.memoList.selection_set( self.memos.getSelectedIndex() )
        self.memoList.see( self.memos.getSelectedIndex() )


    def renderTextArea(self):
        self.openMemo( self.memos.getSelectedItem() )


    def updateLine( index ):
        self.memoList.delete(index)
        self.memoList.insert(index, 
                             "%s | %s" % (self.memos[index].getDatetime().strftime("%Y-%m-%d %H:%M"),
                                          self.memos[index].getTitle()))


    #==================================
    # editing
    #==================================

    def openMemo( self, memo ):
        try:
            self.text.delete('1.0', END )
            self.text.insert(END, 
                             memo.getText() )
        except Exception, err:
            print err

    def saveMemo( self, memo ):
        try:
            memo.setText( self.text.get('1.0', END)[:-1] )

        except Exception, err:
            print err





if __name__ == '__main__':
    testwindow = MemoPadFrame()
    testwindow.mainloop()


