# -*- coding: utf-8 -*-
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo , askUser , showText , tooltip
from aqt.qt import *
import json
import random
import re
import os , sys

from .config import *
from .helpers import *
from .matching import *
from .refreshVerbs import *
# from .gui import run

ADDON_NAME="French Delights"
###############################################################################################
# Use Cses:                                                                                   #
# ---------------------------------------------------------------------------------------------
# 1 Update Bank                                                                               #
# 2 update the bank field for a note in the reviewer                                          #
# 3 update the bank field of the selected notes from the browser                              #
# ---------------------------------------------------------------------------------------------
# 4 Refresh all examples                                                                      #
# 5 Refresh the example in the reviewer                                                       #
# 6 Refresh selected examples from the browser                                                #
# ---------------------------------------------------------------------------------------------
# 7 Find verb conjugations for all verb notes (To be edited) -> in refreshVerbs.py            #
# ---------------------------------------------------------------------------------------------
# 8 Remove the main example of a note in the reviewer                                         #
# 9 Remove the main examples of the selected notes from the browser                           #
###############################################################################################


def updateBank():
    msg = "Update the Bank Field in All notes ?"
    if not askUser(msg , title=ADDON_NAME):
        return

    ids = getAllNoteIds(mainModelsNames)
    updated = matchWordsAndExamples(ids)
    showInfo("updated "+str(updated)+" examples")
    mw.col.reset()
    mw.reset()


def updateBankForThisNote():
    msg = "Update the Bank Field for This Note ?"
    if not askUser(msg , title=ADDON_NAME):
        return
    noteId = mw.reviewer.card.note().id
    matchWordsAndExamples([noteId])
    mw.reviewer.show()


def updateBankForSelectedNotesInBrowser(self):
    msg = "Update the Bank Field for The selected Notes?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    for nid in self.selectedNotes():
        matchWordsAndExamples( [nid])

    mw.col.reset()
    mw.reset()


def refreshAllExamples():
    '''
    Chooses a random example from the bank field and makes it the main examples, also ensures That
    the privously main example doesn't appear as the main example again after refreshing
    '''
    msg ="Refresh The Example Field In All Notes ?"
    if not askUser(msg, title=ADDON_NAME):
        return

    for modelName in mainModelsNames :
        model = mw.col.models.byName(modelName)
        modelId = model['id']
        frenchSentencesIds = mw.col.db.all("SELECT  id  from notes where mid = '"+modelId+"'")
        for id in frenchSentencesIds :
            id = str(id)[1:-2]
            frenchNote = mw.col.getNote(id)
            refreshOneNote (frenchNote)
    mw.col.reset()
    mw.reset()
    showInfo('Refreshing Examples Was Done Successfully' , title=ADDON_NAME ,  textFormat='rich')
    logger.info('Refreshing Examples Was Done Successfully')



def refreshOneNoteFromReviewer(calledBy):
    if not calledBy == 'called':
        msg = "Change The Main Example for this Note ?"
        if not askUser(msg, title=ADDON_NAME):
            return
    frenchNote = mw.reviewer.card.note()
    refreshOneNote (frenchNote)
    mw.reviewer.show()


def refreshSelectedNotesFromBrowser(self):
    msg =  "Change The Main Example for the Selected Notes ?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    for nid in self.selectedNotes():
        frenchNote = mw.col.getNote(nid)
        refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()


def removeThisExampleFromReviewer():
    msg = "Do you Want to Delete the main Example of this Note?\nIt'll not appear again.\nUnless, you remove it from the garbage and update the note again."
    if not askUser(msg , title=ADDON_NAME):
        return
    note = mw.reviewer.card.note()
    deleteExampleFromANote(note)
    refreshOneNoteFromReviewer('called')


def removeThisExampleFromBrowser(self):
    msg = "Do you Want to Delete the main Example of the selected Notes?\nNone of those examples will appear again on those notes.\nUnless, you remove them from the garbage and refresh the notes again."
    if not askUser(msg , title=ADDON_NAME):
        return

    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    for nid in self.selectedNotes():
        frenchNote = mw.col.getNote(nid)
        deleteExampleFromANote(frenchNote)
        refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()





if CONFIG['autoRefresh']:
    hooks.addHook("profileLoaded", refreshExamples)
