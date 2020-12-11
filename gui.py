import os , sys
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtWidgets , QtGui
from PyQt5.QtWidgets import QAction, QProgressDialog, QWidget, QPushButton, QVBoxLayout
from aqt import mw
from .multiple_examples_per_note import *
from .config import *
from anki.hooks import addHook
from aqt.editor import Editor


refresh_icon = QtGui.QIcon()
refresh_icon.addFile( ICONS+'/refresh.png')

refresh_note_icon = QtGui.QIcon()
refresh_note_icon.addFile(ICONS+'/refresh_note.png')

delete_icon = QtGui.QIcon()
delete_icon.addFile(ICONS+'/delete.png')

search_icon = QtGui.QIcon()
search_icon.addFile(ICONS+'/search.png')

update_icon = QtGui.QIcon()
update_icon.addFile(ICONS+'/update.png')

rebuild_icon = QtGui.QIcon()
rebuild_icon.addFile(ICONS+'/rebuild.png')

about_icon = QtGui.QIcon()
about_icon.addFile(ICONS+'/about.png')


def show():
    parent = aqt.mw.app.activeWindow() or aqt.mw
    diag = QDialog(parent)
    diag.setWindowTitle(ADDON_NAME)

    about_icon = QtGui.QIcon()
    about_icon.addFile(ICONS+'/about.png')
    diag.setWindowIcon(about_icon)

    layout = QVBoxLayout(diag)
    diag.setLayout(layout)

    text = QTextBrowser()
    text.setOpenExternalLinks(True)
    txt = '''
    <body bgcolor="#f3f3f3">
    <center>
    <img  src='''+ICONS+'/logo.png'+'''>
    </center>
    <center>
    <big>
    <b><i><a href="href="https://github.com/ShoroukAziz/multiple-examples-per-note"> Multiple Examples per Note</a> </i></b> is an addon that allows you to have more than one example with audio for each note. that can be randomly changed<br>
    Detailed description of the addon and the models can be found in the <a href="https://github.com/ShoroukAziz/multiple-examples-per-note/wiki"> Github Wiki </a>
    <br>Develped By : <a href="https://shorouk.xyz"> Shorouk Abdelaziz </a>
    <big>
    </center>
    <center>
    <br>
    <a href='https://ko-fi.com/B0B51L5RI'>Support Me on Ko-fi</a>
    <br>
    Icons made by <a href="https://www.flaticon.com/authors/freepik"
     title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>

     </center>
    </body>
    '''
    text.setHtml(txt)
    text.toHtml()
    layout.addWidget(text)
    diag.setMinimumHeight(600)
    diag.setMinimumWidth(800)
    diag.exec_()



actionRfreshAllExamples = QAction("Refresh All notes", mw)
actionRfreshAllExamples.triggered.connect(refreshAllExamples)
actionRfreshAllExamples.setIcon(refresh_icon)

actionRefreshVerbs = QAction("Find Verbs conjugations", mw)
actionRefreshVerbs.triggered.connect(refreshVerbs)
actionRefreshVerbs.setIcon(search_icon)


showAbout = QAction("About", mw)
showAbout.triggered.connect(show)
showAbout.setIcon(about_icon)




#########################################################################################################
# Add buttons to Note Editor
#
#

def refreshNote(editor):
    selection = editor.note.id
    frenchNote = mw.col.getNote(int(selection))
    refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()

def updateBankforNote(editor):
    selection = editor.note.id
    frenchNote = mw.col.getNote(int(selection))
    updateBankDeck()
    bank = getBank()
    res = createDict(bank)
    matchWordsAndExamples( selection , res ,matching_type)
    mw.col.reset()
    mw.reset()


def delMainExample(editor):
    selection = editor.note.id
    frenchNote = mw.col.getNote(int(selection))
    deleteExampleFromANote(frenchNote)
    refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()

def setupEditorButtons(buttons, editor):

    a = editor.addButton(
        icon = ICONS+'/refresh.png',
        cmd="MEPNbutton1",
        func=refreshNote,
        tip="Refresh this notes's example "
    )
    b = editor.addButton(
        icon = ICONS+'/update.png',
        cmd="MEPNbutton2",
        func=updateBankforNote,
        tip="Update Bank for this note"
    )
    c = editor.addButton(
    icon = ICONS+'/delete.png',
    cmd="MEPNbutton3",
    func=delMainExample,
    tip="delete the main example"
    )
    buttons.append(a)
    buttons.append(b)
    buttons.append(c)
    return buttons
addHook("setupEditorButtons", setupEditorButtons)

#########################################################################################################

def run():


    def setupMenu(self):
        menu = QtWidgets.QMenu(ADDON_NAME, self.form.menubar)

        menu.addAction(actionRfreshAllExamples)
        menu.addAction(actionRefreshVerbs)
        menu.addSeparator()

        a = menu.addAction('Refresh Selected Notes')
        a.triggered.connect(lambda _, b=self: refreshSelectedNotesFromBrowser(b))
        a.setIcon(refresh_note_icon)

        b = menu.addAction('Remove main Examples from selected notes')
        b.triggered.connect(lambda _, b=self: removeThisExampleFromBrowser(b))
        b.setIcon(delete_icon)

        c=menu.addAction('Update Bank for selected Notes')
        c.triggered.connect(lambda _, b=self:updateBankForSelectedNotesInBrowser(b))
        c.setIcon(rebuild_icon)

        d=menu.addAction("Delte exapmle from collection")
        d.triggered.connect(lambda _, b=self:deleteExampleFromCollection(b))
        d.setIcon(delete_icon)

        menu.addSeparator()

        menu.addAction(showAbout)
        self.form.menubar.addMenu(menu)

    addHook("browser.setupMenus", setupMenu)


def runNonFrench():


    def setupMenu(self):
        menu = QtWidgets.QMenu(ADDON_NAME, self.form.menubar)


        menu.addAction(actionRfreshAllExamples)
        menu.addSeparator()

        a = menu.addAction('Refresh Selected Notes')
        a.triggered.connect(lambda _, b=self: refreshSelectedNotesFromBrowser(b))
        a.setIcon(refresh_note_icon)
        menu.addSeparator()
        b = menu.addAction('Remove main Examples from selected notes')
        b.triggered.connect(lambda _, b=self: removeThisExampleFromBrowser(b))
        b.setIcon(delete_icon)

        menu.addSeparator()

        menu.addAction(showAbout)
        self.form.menubar.addMenu(menu)

    addHook("browser.setupMenus", setupMenu)
