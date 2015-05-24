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

    def getTag(self):
        ptn = re.compile( r"\[([^\[]+)\]" )
        matobj = ptn.match( self.getTitle() )
        if matobj == None: return ''
        else: return matobj.group(1)

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

        self.childDir = ''
        self.tag = ''


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

    def imageTitle(self):
        title = os.path.join( os.path.curdir,self.childDir)
#        if  != '': title += '%s/' % self.childDir
        if self.tag != '' : title += ' [%s]' % self.tag
        return title

    #==================================
    # selealization
    #==================================

    def loadImage(self, childDir='', tag=''):
        ptn = re.compile( r"(\d{4})-(\d{2})-(\d{2})T(\d{2})(\d{2})(\d{2})(\d{6})\.memo" )

        # �����C���[�W�̃N���A
        self.memos = []
        self.selectedIndex = None

        # �C���[�W���[�h�����̋L�� (save��, �C���[�W�^�C�g���������Ɏd�l)
        self.childDir = childDir
        self.tag = tag

        # �C���[�W���X�g�̃��[�h
        if self.childDir != '': os.chdir(self.childDir) 

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
#->3k                memo.setText( open( filepath, 'r' ).read().decode('ms932') )
                memo.setText( open( filepath, 'r' ).read() )

                # �^�O�ł̃t�B���^�����O
                if tag != '' and memo.getTag() != tag:
                    print('skip (no match tag[%s])' % tag, memo.getDatetime().__str__(),memo.getTitle())
                    continue

                # �o�^
                memo.addObserver(self)
                self.memos.insert(0, memo)
                print( memo.getDatetime().__str__(),memo.getTitle() )
        if self.childDir != '': os.chdir('..') 

        # �J�[�\���̏�����
        if len(self.memos) != 0:
            self.selectedIndex = 0

        self.notifyUpdate("loadImage", self)



    def memoToFilename(self, memo):
        return '%s.memo' % memo.getId()


    def saveImage(self):
        for i in self.memos:
#->3k            f = open( os.path.join(self.childDir, self.memoToFilename(i)), 'w' )
#->3k            f.write( i.getText().encode('ms932') )
            f = open( os.path.join(self.childDir, self.memoToFilename(i)),
                      'w',
                      encoding='ms932')
            f.write( i.getText() )

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

#->3k                f = open( 'memo/trash/%s' % self.memoToFilename(i), 'w' )
#->3k                f.write( i.getText().encode('ms932') )
                f = open( 'memo/trash/%s' % self.memoToFilename(i),
                          'w',
                          encoding='ms932')
                f.write( i.getText() )

            except OSError: # �C���[�W�t�@�C��������
                if not i.isEmpty():
#->3k                    f = open( 'memo/trash/%s' % self.memoToFilename(i), 'w' )
#->3k                    f.write( i.getText().encode('ms932') )
                    f = open( 'memo/trash/%s' % self.memoToFilename(i),
                              'w',
                              encoding='ms932')
                    f.write( i.getText() )





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
#->3k        self.file = open('change.log', 'a+')
        self.file = open('change.log', 'a+', encoding='ms932')
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
#->3k                self.file.write('+ %s\n' % line.encode('ms932'))
                self.file.write('+ %s\n' % line)
            self.file.write('\n')

        elif aspect == 'appendMemo':
            self.file.write('id=%s\n\n' % obj.getId() )

        elif aspect == 'removeMemo':
#->3k            self.file.write( 'id=%s / %s\n\n' % (obj.getId(), obj.getTitle().encode('ms932')) )
            self.file.write( 'id=%s / %s\n\n' % (obj.getId(), obj.getTitle()) )

        elif aspect == 'loadImage':
            self.file.write('\n')
            for item in obj:
#->3k                self.file.write( '>>> %s / %s\n' % (item.getId(), item.getTitle().encode('ms932')) )
                self.file.write( '>>> %s / %s\n' % (item.getId(), item.getTitle()) )
            self.file.write('\n')

        elif aspect == 'saveImage':
            self.file.write('\n')
            for item in obj:
#->3k                self.file.write( '<<< %s / %s\n' % (item.getId(), item.getTitle().encode('ms932')) )
                self.file.write( '<<< %s / %s\n' % (item.getId(), item.getTitle()) )
            self.file.write('\n')

        else:
            self.file.write('\n\n')

        # �t�@�C���ɏ����o��
        self.file.flush()



from tkinter import *
from tkscrlist_py3 import *
#->3k	from ScrolledText import *
from tkinter.scrolledtext import *

class MemoPadFrame( Frame ):

    def __init__(self, aMemoPad, mode='w', master=None):
        Frame.__init__(self, master)
        self.version = (0, 2, 7)

        # Model�̏�����
        self.memos = aMemoPad
        self.memos.addObserver(self)

        # View-Controller �̏�����
        self.master.title( 'MemoPad %d.%d.%d (for Python3)' % self.version + ' -' + self.memos.imageTitle() )
        self.make_listPanel(self, mode)
        self.make_editAria(self)
        self.pack(fill=BOTH)

        if mode == 'w':
            def bye():
                self.saveMemo()    # ���ݕҏW���̃������Z�[�u
                self.memos.saveImage()

                print( 'bye' )
                self.master.destroy()

            self.master.protocol('WM_DELETE_WINDOW', bye )

        self.update("", self.memos)


    def make_listPanel(self, parent, mode):
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
        if mode == 'w':
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
#->3k        self.text = ScrolledText( parent )
        self.text = ScrolledText( parent,
                                  width=60,
                                  height=20 )
        self.text.pack(side=TOP,
                       fill=BOTH)

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
                                          '%s%s%s' % ( self.text.get('1.0', INSERT), 
#->3k                                                        evt.char.decode('utf_8'),
                                                        evt.char,
                                                        self.text.get(INSERT, '1.end'))))
                self.memoList.selection_clear(0,END)
                self.memoList.selection_set(itemnum)
                self.memoList.see(itemnum)


        self.text.bind('<Key>', updateTitle )

        def ime_ctrl_M(evt):
            """
            IME��CTRL-M�őS���m�肵���Ƃ�
            ���͂��e�L�X�g�ɃC���T�[�g����Ȃ����ɑ΂���p�b�`
            �m����͂̂Ƃ��Aevt.keycode �� 0 �ɂȂ��Ă��邱�Ƃ𗘗p����
            """
            if evt.keycode == 0:
                self.text.insert( INSERT, evt.char )
        self.text.bind('<Control-Key>', ime_ctrl_M)

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

        print( "disyplay update (%s)" % aspect )



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
        print( '--- save "%s"---' % memo.getTitle() )

    def selectMemo( self, index ):
        self.memos.selectMemo( index )

if __name__ == '__main__':

    # Model �̐���
    model = MemoPad()
    model.addObserver( ChangeLogger() )
    model.loadImage('memo')
#    model.loadImage('memo', tag='X8')

    # V-C �ɘA��
    testwindow = MemoPadFrame(model)
#    testwindow = MemoPadFrame(model, mode='r')
    testwindow.mainloop()


