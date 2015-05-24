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
        '''�����̃��j�[�NID ��Ԃ�; ���������� �����񉻂������̂�ID�Ƃ���'''
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

        # �����o�̏�����
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

        # �����C���[�W�̃N���A
        self.memos = []
        self.selectedIndex = None

        # �C���[�W���X�g�̃��[�h
        os.chdir('memo') 
        for filepath in glob.glob("*.memo"):
            matobj = ptn.match( filepath )
            if matobj != None:
                # Memo �̐����Ə�����
                memo = Memo( datetime( int(matobj.group(1)),
                                       int(matobj.group(2)),
                                       int(matobj.group(3)),
                                       int(matobj.group(4)),
                                       int(matobj.group(5)),
                                       int(matobj.group(6)),
                                       int(matobj.group(7)) ) )
                memo.setText( open( filepath, 'r' ).read().decode('ms932') )

                # �o�^
                memo.addObserver(self)
                self.memos.insert(0, memo)
                print memo.getDatetime().__str__(),memo.getTitle()
        os.chdir('..') 

        # �J�[�\���̏�����
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
        trashbox �ɓ����ꂽ memo �̃C���[�W�t�@�C����
        memo/ ����폜���Amemo/trash/ �ɕۑ�����B
        '''
        for i in self.trashbox:
            try:
                os.remove( 'memo/%s' % self.memoToFilename(i) )

                f = open( 'memo/trash/%s' % self.memoToFilename(i), 'w' )
                f.write( i.getText().encode('ms932') )

            except OSError: # �C���[�W�t�@�C��������
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

        self.trashbox.append( rmvtarget ) # �C���[�W�t�@�C�����珜�����邽�߂Ɋo���Ă���
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
        # ��������A�N�V����
        if aspect == 'selectMemo': return

        # �A�N�V�����̋L�^
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

        # �t�@�C���ɏ����o��
        self.file.flush()



from Tkinter import *
from tkscrlist import *
from ScrolledText import *


class MemoPadFrame( Frame ):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        # Model�̏�����
        self.version = (0, 2, 5)
        self.memos = MemoPad()
        self.memos.addObserver(self)

        # change-logger �̃o�C���h
        self.changeLogger = ChangeLogger()
        self.memos.addObserver( self.changeLogger )

        # View-Controller �̏�����
        self.master.title( 'MemoPad %d.%d.%d' % self.version )
        self.make_listPanel(self)
        self.make_editAria(self)
        self.pack(fill=BOTH)

        # �f�[�^�̕��A
        self.memos.loadImage()


        def bye():
            self.saveMemo()    # ���ݕҏW���̃������Z�[�u
            self.memos.saveImage()

            print 'bye'
            self.master.destroy()

        self.master.protocol('WM_DELETE_WINDOW', bye )


    def make_listPanel(self, parent):
        frm = Frame(parent)

        # ���X�g�̐����E�z�u
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


        # �{�^���̍쐬
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
            '''�����R�[�h�B�܂�
            ���s��s�����s�̍폜�Ɏア�ł�
            '''
#            print self.text.index('1.end')
#            print self.text.index(INSERT)

            if self.text.index(INSERT).split('.')[0] == '1': # 1�s��
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

        # ���X�g�̕\�� (�S�X�V or �I���s�̕ύX)
        if aspect == "selectMemo":
            self.selectList()
        elif aspect == "setText":
            self.renderOneLine(self.memos.getSelectedIndex())
        else:
            self.renderList()

        # �e�L�X�g�G���A�̕\��
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
        except: # ���������I����������Ă��Ȃ�
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

        if memo.getText() == self.text.get('1.0', END)[:-1]: return # ���e�������ꍇ�͂Ȃɂ����Ȃ�

        self.memos.getSelectedItem().setText( self.text.get('1.0', END)[:-1] )
        print '--- save "%s"---' % memo.getTitle()

    def selectMemo( self, index ):
        self.memos.selectMemo( index )

if __name__ == '__main__':
    testwindow = MemoPadFrame()
    testwindow.mainloop()


