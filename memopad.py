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

    def getId(self):
        '''メモのユニークID を返す; 生成時刻を 文字列化したものをIDとする'''
        return '%s%06d' % (self.datetime.strftime("%Y-%m-%dT%H%M%S"),
                           self.datetime.microsecond )

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
        self.selectedIndex = None

        self.trashbox = []


    #==================================
    # accessing
    #==================================

    def getSelectedItem(self):
        if self.selectedIndex == None : return None
        return self.memos[self.selectedIndex]

    def getSelectedIndex(self):
        return self.selectedIndex

    def size(self):
        return len(self.memos)

    #==================================
    # selealization
    #==================================

    def loadImage(self):
        ptn = re.compile( r"(\d{4})-(\d{2})-(\d{2})T(\d{2})(\d{2})(\d{2})(\d{6})\.memo" )

        # 既存イメージのクリア
        self.memos = []
        self.selectedIndex = None

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

        self.notifyUpdate("loadImage", self)



    def memoToFilename(self, memo):
        return '%s.memo' % memo.getId()


    def saveImage(self):
        for i in self.memos:
            f = open( 'memo/%s' % self.memoToFilename(i), 'w' )
            f.write( i.getText().encode('ms932') )

        self.sendToTrashboxImage()
        self.notifyUpdate("saveImage", self)

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
        newMemo.addObserver(self)

        self.memos.insert(0, newMemo )
        self.selectedIndex = 0

        self.notifyUpdate("appendMemo", newMemo)


    def removeMemo(self):
        if self.selectedIndex == -1: return

        rmvtarget = self.memos[self.selectedIndex]
        self.memos.remove( rmvtarget )

        if len(self.memos) <= self.selectedIndex:
            self.selectedIndex = len(self.memos) -1

        self.trashbox.append( rmvtarget ) # イメージファイルから除去するために覚えておく
        self.notifyUpdate("removeMemo", rmvtarget)


    def selectMemo(self, index):
        if index < 0 or len(self.memos) <= index:
            raise IndexError( "%d is not contain [0..%d)" % (index, len(self.memos)) )

        if self.selectedIndex == index: return

        self.selectedIndex = index
        self.notifyUpdate("selectMemo", self.getSelectedItem())


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


class ChangeLogger(object):
    def __init__(self):
        self.file = open('change.log', 'a+')
        self.file.write( '\n\nopen: %s\n' % datetime.now() )
        self.file.write( '=' * 40 + '\n' )

    def update( self, aspect, obj ):
        # 無視するアクション
        if aspect == 'selectMemo': return

        # アクションの記録
        self.file.write( '@@%s (%s): ' % (aspect, datetime.now()) )

        if aspect == 'setText':
            self.file.write('id=%s\n' % obj.getId() )
            for line in obj.getText().splitlines():
                self.file.write('+ %s\n' % line.encode('ms932'))
            self.file.write('\n')

        elif aspect == 'appendMemo':
            self.file.write('id=%s\n\n' % obj.getId() )

        elif aspect == 'removeMemo':
            self.file.write( 'id=%s / %s\n\n' % (obj.getId(), obj.getTitle().encode('ms932')) )

        elif aspect == 'loadImage':
            self.file.write('\n')
            for item in obj:
                self.file.write( '>>> %s / %s\n' % (item.getId(), item.getTitle().encode('ms932')) )
            self.file.write('\n')

        elif aspect == 'saveImage':
            self.file.write('\n')
            for item in obj:
                self.file.write( '<<< %s / %s\n' % (item.getId(), item.getTitle().encode('ms932')) )
            self.file.write('\n')

        else:
            self.file.write('\n\n')

        # ファイルに書き出し
        self.file.flush()



from Tkinter import *
from tkscrlist import *
from ScrolledText import *


class MemoPadFrame( Frame ):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        # Modelの初期化
        self.version = (0, 2, 5)
        self.memos = MemoPad()
        self.memos.addObserver(self)

        # change-logger のバインド
        self.changeLogger = ChangeLogger()
        self.memos.addObserver( self.changeLogger )

        # View-Controller の初期化
        self.master.title( 'MemoPad %d.%d.%d' % self.version )
        self.make_listPanel(self)
        self.make_editAria(self)
        self.pack(fill=BOTH)

        # データの復帰
        self.memos.loadImage()


        def bye():
            self.saveMemo()    # 現在編集中のメモをセーブ
            self.memos.saveImage()

            print 'bye'
            self.master.destroy()

        self.master.protocol('WM_DELETE_WINDOW', bye )


    def make_listPanel(self, parent):
        frm = Frame(parent)

        # リストの生成・配置
        def changeTarget(evt):
            try: index = int(self.memoList.curselection()[0])
            except: index = None

            self.saveMemo()
            if index != None: self.selectMemo( index )


        self.memoList = ScrolledListbox(frm,
                                        selectmode=BROWSE,
                                        width=72,
                                        height=7 )
        self.memoList.bind("<ButtonRelease>", changeTarget )
        self.memoList.bind('<B1-Motion>', changeTarget )
        self.memoList.pack(side=LEFT, fill=BOTH)


        # ボタンの作成
        btnfrm = Frame(frm)

        def appendMemo():
            self.saveMemo()
            self.memos.appendMemo()

        Button( btnfrm,
                text='new',
                command=appendMemo ).pack(side=TOP, fill=X)


        def deleteMemo():
            self.saveMemo()
            self.memos.removeMemo()

        Button( btnfrm,
                text='delete',
                command=deleteMemo ).pack(side=TOP, fill=X)


        btnfrm.pack(side=LEFT)

        frm.pack(side=TOP, fill=X)



    def make_editAria(self, parent):
        self.text = ScrolledText( parent )
        self.text.pack(side=TOP, fill=BOTH)

        def updateTitle(evt):
            '''実験コード。まだ
            改行や行末改行の削除に弱いです
            '''
#            print self.text.index('1.end')
#            print self.text.index(INSERT)

            if self.text.index(INSERT).split('.')[0] == '1': # 1行目
                itemnum = self.memos.getSelectedIndex()

                self.memoList.delete(itemnum)
                self.memoList.insert(itemnum,
                             "%s | %s" % (self.memos[itemnum].getDatetime().strftime("%Y-%m-%d %H:%M"),
                                          u'%s%s%s' % ( self.text.get('1.0', INSERT), 
                                                        evt.char.decode('utf_8'),
                                                        self.text.get(INSERT, '1.end'))))
                self.memoList.selection_clear(0,END)
                self.memoList.selection_set(itemnum)
                self.memoList.see(itemnum)


        self.text.bind('<Key>', updateTitle )

    #==================================
    # observer
    #==================================

    def update(self, aspect, obj):
        if aspect == 'saveImage' : return

        # リストの表示 (全更新 or 選択行の変更)
        if aspect == "selectMemo":
            self.selectList()
        elif aspect == "setText":
            self.renderOneLine(self.memos.getSelectedIndex())
        else:
            self.renderList()

        # テキストエリアの表示
        if aspect != "setText":
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

        if self.memos.getSelectedItem() != None:
            self.memoList.selection_set( self.memos.getSelectedIndex() )
            self.memoList.see( self.memos.getSelectedIndex() )


    def selectList(self):
        try:
            if int(self.memoList.curselection()[0]) == self.memos.getSelectedIndex():
                return
        except: # そもそも選択が成されていない
            pass

        self.memoList.selection_clear(0,END)
        self.memoList.selection_set( self.memos.getSelectedIndex() )
        self.memoList.see( self.memos.getSelectedIndex() )



    def renderOneLine(self, index ):
        if self.memoList.get(index) == self.memos[index].getTitle(): return

        try: indexbackup = int(self.memoList.curselection()[0])
        except: indexbackup = self.memos.getSelectedIndex()

        self.memoList.delete(index)
        self.memoList.insert(index,
                             "%s | %s" % (self.memos[index].getDatetime().strftime("%Y-%m-%d %H:%M"),
                                          self.memos[index].getTitle()))

        if indexbackup != None:
            self.memoList.selection_clear(0,END)
            self.memoList.selection_set(indexbackup)
            self.memoList.see(indexbackup)



    def renderTextArea(self):
        self.text.delete('1.0', END )
        if self.memos.getSelectedItem() != None:
            self.text.insert(END, self.memos.getSelectedItem().getText())



    #==================================
    # controller-function (VC->M)
    #==================================

    def saveMemo( self, memo=None ):
        if memo == None:
            memo = self.memos.getSelectedItem()
            if memo == None: return

        if memo.getText() == self.text.get('1.0', END)[:-1]: return # 内容が同じ場合はなにもしない

        self.memos.getSelectedItem().setText( self.text.get('1.0', END)[:-1] )
        print '--- save "%s"---' % memo.getTitle()

    def selectMemo( self, index ):
        self.memos.selectMemo( index )

if __name__ == '__main__':
    testwindow = MemoPadFrame()
    testwindow.mainloop()


