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

ADDON_NAME="MPEN"


def progress(data, *args):
    """
    A very pythonic progress dialog.

    Iterate over progress(iterator)
    instead of iterator. That’s pretty much it.

    """
    # found at http://lateral.netmanagers.com.ar/weblog/posts/BB917.html
    # © 2000-2012 Roberto Alsina
    # Creative Commons Attribution-NonCommercial-ShareAlike 2.5 licence
    # http://creativecommons.org/licenses/by-nc-sa/2.5/
    it = iter(data)
    widget = QProgressDialog(*args + (0, it.__length_hint__()))
    c = 0
    for v in it:
        QCoreApplication.instance().processEvents()
        if widget.wasCanceled():
            raise StopIteration
        c += 1
        widget.setValue(c)
        yield(v)

###############################################################################################
# Use Cses:                                                                                   #
# ---------------------------------------------------------------------------------------------
# 1 update the bank field of the selected notes from the browser                              #
# ---------------------------------------------------------------------------------------------
# 2 Refresh all examples                                                                      #
# 3 Refresh selected examples from the browser                                                #
# ---------------------------------------------------------------------------------------------
# 4 Find verb conjugations for all verb notes (To be edited) -> in refreshVerbs.py            #
# ---------------------------------------------------------------------------------------------
# 5 Remove the main examples of the selected notes from the browser                           #
###############################################################################################

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
        modelId = str(model['id'])
        frenchSentencesIds = mw.col.db.all("SELECT  id  from notes where mid = '"+modelId+"'")
        for id in progress(frenchSentencesIds, _("Refreshing All Notes'examples"), _("Stop that!")):
            id = id[0]
            frenchNote = mw.col.getNote(id)
            refreshOneNote (frenchNote)
    mw.col.reset()
    mw.reset()
    showInfo('Refreshing Examples Was Done Successfully' , title=ADDON_NAME ,  textFormat='rich')
    logger.info('Refreshing Examples Was Done Successfully')

def updateBankForSelectedNotesInBrowser(self):
    msg = "Update the Bank Field for The selected Notes?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    nids= self.selectedNotes()
    updateBankDeck()
    bank = getBank()
    res = createDict(bank)

    for nid in progress(nids, _("Updating the Bank Field in selected notes"), _("Stop that!")):

        matchWordsAndExamples( nid , res ,matching_type)

    showInfo('Updaiting The Bank Field Was Done Successfully' , title=ADDON_NAME ,  textFormat='rich')
    logger.info('Updaiting The Bank Field Was Done Successfully')
    mw.col.reset()
    mw.reset()

def refreshSelectedNotesFromBrowser(self):
    msg =  "Change The Main Example for the Selected Notes ?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    nids= self.selectedNotes()
    for nid in progress(nids, _("Refreshing selected Notes'examples"), _("Stop that!")):
        frenchNote = mw.col.getNote(nid)
        refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()

def removeThisExampleFromBrowser(self):
    msg = "Do you Want to Delete the main Example of the selected Notes?\nNone of those examples will appear again on those notes.\nUnless, you remove them from the garbage and refresh the notes again."
    if not askUser(msg , title=ADDON_NAME):
        return

    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    nids= self.selectedNotes()
    for nid in progress(nids, _("Deleteing selected Notes' main examples"), _("Stop that!")):
        frenchNote = mw.col.getNote(nid)
        deleteExampleFromANote(frenchNote)
        refreshOneNote(frenchNote)
    mw.col.reset()
    mw.reset()


if CONFIG['autoRefresh']:
    hooks.addHook("profileLoaded", refreshExamples)


def deleteExampleFromCollection(self):
    msg = "Do you Want to Delete the main Example from the collection. This will remove it from all the notes"
    if not askUser(msg , title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip(_("No cards selected."), period=2000)
        return
    nids= self.selectedNotes()

    for nid in progress(nids, _("Deleteing selected Notes' main examples"), _("Stop that!")):
        frenchNote = mw.col.getNote(nid)
        exampleId = frenchNote[example_id_field]
        # showInfo(str(exampleId))
        if len(exampleId) > 0:
            #delete the example from all the banks
            modified_notes =  mw.col.db.all("SELECT  id  from notes where flds LIKE '%{}%' ".format(exampleId))
            showInfo("{} notes had this example ... deleteing it from them".format(len(modified_notes)))
            for id in modified_notes:
                note = mw.col.getNote(id[0])
                id_field = str(note[example_id_field])
                if id_field == exampleId:
                    note[example_field] = ""
                    note[translated_example_field] = ""
                    note[example_audio_field] = ""
                    note[example_id_field] = ""
                    note.flush()
                    refreshOneNote(note)

                bankField = note['Bank']
                bank = json.loads(bankField)
                for example in bank:
                    # showInfo(example['noteId'])
                    if str(example['noteId']) == exampleId:
                        showInfo(str(example))
                        bank.remove(example)
                        note['Bank'] = json.dumps(bank,ensure_ascii=False)
                        note.flush()
                        pass

            # delete the example note from the collection
            mw.col.db.execute("delete from notes where id =?", exampleId)
    mw.col.reset()
    mw.reset()
