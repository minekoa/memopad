#!/usr/bin/env python
#-*- coding: shift_jis -*-

from datetime import *

class Memo (object):
    def __init__(self):
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



from Tkinter import *
from tkscrlist import *
from ScrolledText import *
import os
import os.path
import re


class MemoPad( Frame ):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.memos = []
        self.selectedIndex = -1


        self.version = (0, 1, 0)
        self.master.title( 'MemoPad %d.%d.%d' % self.version )

        ptn = re.compile( r"(\d{4})-(\d{2})-(\d{2})T(\d{2})(\d{2})(\d{2})(\d{6})\.memo" )

        for (root, dirs, files) in os.walk( os.path.join(os.curdir, 'memo') ):
            for filename in files:
                matobj = ptn.match( filename )
                if matobj != None:
                    memo = Memo()
                    memo.setDatetime( datetime( int(matobj.group(1)),
                                                int(matobj.group(2)),
                                                int(matobj.group(3)),
                                                int(matobj.group(4)),
                                                int(matobj.group(5)),
                                                int(matobj.group(6)),
                                                int(matobj.group(7)) ) )
                    memo.setText( open( os.path.join('memo', filename), 'r' ).read().decode('shift_jis') )
                    print memo.getDatetime().__str__(),memo.getText()
                    self.memos.append( memo )


        self.make_listPanel(self)
        self.make_editAria(self)

        self.pack(fill=BOTH)

        self.fill_testlist()
        self.memoList.selection_set( 0 )
        self.openMemo( self.memos[0] )



        def bye():
            for i in self.memos:
                f = open( 'memo/%s%06d.memo' % (i.getDatetime().strftime("%Y-%m-%dT%H%M%S"),
                                           i.getDatetime().microsecond), "w")
                f.write( i.getText().encode('shift_jis') )

            print 'bye'
            self.master.destroy()

        self.master.protocol('WM_DELETE_WINDOW', bye )


    def make_listPanel(self, parent):
        frm = Frame(parent)

        # リストの生成・配置
        self.memoList = ScrolledListbox(frm,
                                        selectmode=BROWSE,#SINGLE,
                                        width=50,
                                        height=5,
                                        )

        def say(evt):
            curSel = self.memoList.curselection()
            newIndex = int(curSel[0])

            if self.selectedIndex != -1:
                self.saveMemo( self.memos[self.selectedIndex] )
                print '--- save %d---' % self.selectedIndex

            self.selectedIndex = newIndex
            self.openMemo( self.memos[self.selectedIndex] )
            print '---select %d---' % self.selectedIndex

            self.fill_testlist()
            self.memoList.selection_set( self.selectedIndex )
            self.memoList.see( self.selectedIndex )





        self.memoList.bind("<ButtonRelease>", say )
        self.memoList.pack(side=LEFT, fill=BOTH)


        # ボタンの作成
        btnfrm = Frame(frm)

        self.newbtn = Button( btnfrm,
                              text='new',
                              command=self.addMemo )
        self.newbtn.pack(side=TOP)

        btnfrm.pack(side=LEFT)

        frm.pack(side=TOP)

    def make_editAria(self, parent):

        self.text = ScrolledText( parent )
        self.text.pack(side=TOP)



    def fill_testlist( self ):
        self.memoList.delete(0, END)
        for memo in self.memos:
            self.memoList.insert(END, 
                                 "%s | %s" % (memo.getDatetime(), memo.getTitle()))


    def addMemo(self):
        newMemo = Memo()
        self.memos.append( newMemo )
        newMemo.setText("abc def")

        self.fill_testlist()


    def openMemo( self,memo ):
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
    testwindow = MemoPad()
    testwindow.mainloop()


