# -*- coding: utf-8 -*-
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, askUser, showText, tooltip
from aqt.qt import *
import json
import random
import re
import os, sys

from .config import *
from .helpers import *
from .matching import *
from .refreshVerbs import *

# from .gui import run

ADDON_NAME = "MPEN"


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
        yield (v)


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

def refresh_all_examples():
    """
    Chooses a random example from the bank field and makes it the main examples, also ensures That
    the previously main example doesn't appear as the main example again after refreshing
    """
    msg = "Refresh The Example Field In All Notes ?"
    if not askUser(msg, title=ADDON_NAME):
        return

    for modelName in mainModelsNames:
        model = mw.col.models.byName(modelName)
        model_id = str(model['id'])
        french_sentences_ids = mw.col.db.all("SELECT  id  from notes where mid = '" + model_id + "'")
        for id in progress(french_sentences_ids, "Refreshing All Notes' examples", "Stop that!"):
            id = id[0]
            french_note = mw.col.getNote(id)
            refresh_one_note(french_note)
    mw.col.reset()
    mw.reset()
    showInfo('Refreshing Examples Was Done Successfully', title=ADDON_NAME, textFormat='rich')
    logger.info('Refreshing Examples Was Done Successfully')


def update_bank_for_selected_notes_in_browser(self):
    msg = "Update the Bank Field for The selected Notes?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip("No cards selected.", period=2000)
        return
    nids = self.selectedNotes()
    update_bank_deck()
    bank = get_bank()
    res = create_dict(bank)

    for nid in progress(nids, "Updating the Bank Field in selected notes", "Stop that!"):
        match_words_and_examples(nid, res, matching_type)

    showInfo('Updating The Bank Field Was Done Successfully', title=ADDON_NAME, textFormat='rich')
    logger.info('Updating The Bank Field Was Done Successfully')
    mw.col.reset()
    mw.reset()


def refresh_selected_notes_from_browser(self):
    msg = "Change The Main Example for the Selected Notes ?"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip("No cards selected.", period=2000)
        return
    nids = self.selectedNotes()
    for nid in progress(nids, "Refreshing selected Notes'examples", "Stop that!"):
        french_note = mw.col.getNote(nid)
        refresh_one_note(french_note)
    mw.col.reset()
    mw.reset()


def remove_this_example_from_browser(self):
    msg = "Do you Want to Delete the main Example of the selected Notes?\nNone of those examples will appear again on " \
          "those notes.\nUnless, you remove them from the garbage and refresh the notes again. "
    if not askUser(msg, title=ADDON_NAME):
        return

    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip("No cards selected.", period=2000)
        return
    nids = self.selectedNotes()
    for nid in progress(nids, "Deleteing selected Notes' main examples", "Stop that!"):
        french_note = mw.col.getNote(nid)
        delete_example_from_note(french_note)
        refresh_one_note(french_note)
    mw.col.reset()
    mw.reset()


# if CONFIG['autoRefresh']:
#     hooks.addHook("profileLoaded", refreshExamples)


def deleteExampleFromCollection(self):
    msg = "Do you Want to Delete the main Example from the collection. This will remove it from all the notes"
    if not askUser(msg, title=ADDON_NAME):
        return
    mw = self.mw
    cids = self.selectedCards()
    if not cids:
        tooltip("No cards selected.", period=2000)
        return
    nids = self.selectedNotes()

    for nid in progress(nids, "Deleteing selected Notes' main examples", "Stop that!"):
        frenchNote = mw.col.getNote(nid)
        example_id = frenchNote[example_id_field]
        # showInfo(str(exampleId))
        if len(example_id) > 0:
            # delete the example from all the banks
            modified_notes = mw.col.db.all("SELECT  id  from notes where flds LIKE '%{}%' ".format(example_id))
            showInfo("{} notes had this example ... deleting it from them".format(len(modified_notes)))
            for id in modified_notes:
                note = mw.col.getNote(id[0])
                id_field = str(note[example_id_field])
                if id_field == example_id:
                    note[example_field] = ""
                    note[translated_example_field] = ""
                    note[example_audio_field] = ""
                    note[example_id_field] = ""
                    note.flush()
                    refresh_one_note(note)

                bank_field = note['Bank']
                bank = json.loads(bank_field)
                for example in bank:
                    # showInfo(example['noteId'])
                    if str(example['noteId']) == example_id:
                        showInfo(str(example))
                        bank.remove(example)
                        note['Bank'] = json.dumps(bank, ensure_ascii=False)
                        note.flush()
                        pass

            # delete the example note from the collection
            mw.col.db.execute("delete from notes where id =?", example_id)
    mw.col.reset()
    mw.reset()
