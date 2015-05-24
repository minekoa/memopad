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
    def __init__(self, createDate=None):
        Subject.__init__(self)

        self.text = ''
        if createDate == None:
            self.datetime = datetime.now()
        else:
            self.datetime = createDate

    def getDatetime(self):
        return self.datetime

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

    def isEmpty(self):
        return self.text == ''


import os
import os.path
import glob
import re


class MemoPad(Subject):
    def __init__(self):
        Subject.__init__(self)

        # メンバの初期化
        self.memos = []
        self.selectedIndex = -1

        self.trashbox = []


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
        os.chdir('memo') 
        for filepath in glob.glob("*.memo"):
            matobj = ptn.match( filepath )
            if matobj != None:
                # Memo の生成と初期化
                memo = Memo( datetime( int(matobj.group(1)),
                                       int(matobj.group(2)),
                                       int(matobj.group(3)),
                                       int(matobj.group(4)),
                                       int(matobj.group(5)),
                                       int(matobj.group(6)),
                                       int(matobj.group(7)) ) )
                memo.setText( open( filepath, 'r' ).read().decode('ms932') )

                # 登録
                memo.addObserver(self)
                self.memos.insert(0, memo)
                print memo.getDatetime().__str__(),memo.getTitle()
        os.chdir('..') 

        # カーソルの初期化
        if len(self.memos) != 0:
            self.selectedIndex = 0


    def memoToFilename(self, memo):
        return '%s%06d.memo' % (memo.getDatetime().strftime("%Y-%m-%dT%H%M%S"),
                                memo.getDatetime().microsecond )


    def saveImage(self):
        for i in self.memos:
            f = open( 'memo/%s' % self.memoToFilename(i), 'w' )
            f.write( i.getText().encode('ms932') )

        self.sendToTrashboxImage()

    def sendToTrashboxImage(self):
        '''
        trashbox に入れられた memo のイメージファイルを
        memo/ から削除し、memo/trash/ に保存する。
        '''
        for i in self.trashbox:
            try:
                os.remove( 'memo/%s' % self.memoToFilename(i) )

                f = open( 'memo/trash/%s' % self.memoToFilename(i), 'w' )
                f.write( i.getText().encode('ms932') )

            except OSError: # イメージファイルが無い
                if not i.isEmpty():
                    f = open( 'memo/trash/%s' % self.memoToFilename(i), 'w' )
                    f.write( i.getText().encode('ms932') )





    #==================================
    # list-operation
    #==================================

    def appendMemo(self):
        newMemo = Memo()
#        newMemo.setText("**no-subject**")
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

        self.trashbox.append( rmvtarget ) # イメージファイルから除去するために覚えておく
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
        self.version = (0, 2, 2)
        self.memos = MemoPad()
        self.memos.loadImage()
        self.memos.addObserver(self)

        # View-Controller の初期化
        self.master.title( 'MemoPad %d.%d.%d' % self.version )
        self.make_listPanel(self)
        self.make_editAria(self)
        self.pack(fill=BOTH)

        self.update(None,None)


        def bye():
            self.saveMemo( self.memos.getSelectedItem() ) # 現在編集中のメモをセーブ
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
            self.memos.selectMemo( newIndex )


        self.memoList = ScrolledListbox(frm,
                                        selectmode=BROWSE,
                                        width=70,
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

        frm.pack(side=TOP, fill=X)



    def make_editAria(self, parent):
        self.text = ScrolledText( parent )
        self.text.pack(side=TOP, fill=BOTH)


    def update(self, aspect, obj):
        if aspect != "selectMemo":
            self.renderList()

        self.renderTextArea()

        print "disyplay update (%s)" % aspect



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
        self.text.delete('1.0', END )
        self.text.insert(END, 
                         memo.getText() )

    def saveMemo( self, memo ):
        if memo.getText() == self.text.get('1.0', END)[:-1]: return

        memo.setText( self.text.get('1.0', END)[:-1] )
        print '--- save "%s"---' % memo.getTitle()





if __name__ == '__main__':
    testwindow = MemoPadFrame()
    testwindow.mainloop()


