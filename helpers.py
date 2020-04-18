from aqt import mw
from bs4 import BeautifulSoup
import logging
import json
import random
from .config import *
from aqt.utils import showInfo , askUser
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtWidgets , QtGui
from PyQt5.QtWidgets import QAction, QProgressDialog, QWidget, QPushButton, QVBoxLayout
import os , sys

ADDON = os.path.dirname(os.path.abspath(__file__))
###############################################################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(ADDON+'/logs.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


################################################################################################################

def getAllNoteIds(models):

    ids=[]
    for modelName in models :
        model = mw.col.models.byName(modelName)
        modelId = str(model['id'])
        notesIds = mw.col.db.all("SELECT  id  from notes where mid = '"+modelId+"'")
        for id in notesIds :
             id = str(id)[1:-2]
             ids.append(id)
    return(ids)

################################################################################################################
def getBank():
    '''
    loops over all the notes in the sentences bank and adds them to a dict  of dicts and returns that dict
    '''
    cards = mw.col.findCards("deck:'%s'" % bankDeckName)

    collectedExampleId = 0
    bank = {}
    for card in cards :
        frenchSentenceNote =  mw.col.getNote(mw.col.getCard(card).nid)
        example = {}
        example['fr']=BeautifulSoup(frenchSentenceNote[target_lang_field],'html.parser').get_text().replace("\'","’")
        example['en'] =BeautifulSoup( frenchSentenceNote[mother_lang_field],'html.parser').get_text().replace("\'","’")
        example['audio'] = BeautifulSoup( frenchSentenceNote[audio_field],'html.parser').get_text().replace("\'","’")
        bank[collectedExampleId] = example
        collectedExampleId += 1
    logger.info('bank retrived successfully')
    return bank


###############################################################################################################

def createDict(bank):
    '''
    creats a dictionary of all the words in the examples and which examples they appear on
    '''

    logger.info("There are "+str(len(bank))+" sentences")
    dictionary = {}
    for id in bank:
        example = bank[id]
        example['audio'] =example['audio'].split(',')[0]
        example['audio'] = example['audio'][7:-1]
        words = example['fr'].lower()
        words = words.replace('.', '')
        words = words.replace('?', '')
        words = words.replace('!', '')
        words = words.replace(',', '')


        words = words.split(" ")
        for word in words:
            if word not in dictionary:
                idsList  = []
                idsList.append(id)
                dictionary[word] = idsList
            else:
                 dictionary[word].append(id)

    logger.info("There are "+str(len(dictionary))+" unique words")
    logger.info('dicts created successfully')
    return dictionary , bank


################################################################################################################
def updateBankDeck():
    '''
    loops over all the notes in the (French (verbs , nouns , adv and adj ))
    and  add the examples found in them and not in the french sentence model to
    the french sentence deck
    '''
    logger.info('updating bank deck .....')
    bank = getBank()
    bankKeys = []
    for id in bank:
        example = bank[id]
        bankKeys.append(example['fr'])

    new_examples_list={}

    new_Examples = 0

    for modelName in mainModelsNames:

        model = mw.col.models.byName(modelName)
        modelId =str( model['id'])
        frenchSentencesIds = mw.col.db.all("SELECT  id  from notes where mid = '"+modelId+"'")

        for id in frenchSentencesIds:
            id = str(id)[1:-2]

            frenchNote = mw.col.getNote(id)
            example = {}
            example['fr'] =BeautifulSoup( frenchNote[example_field],'html.parser').get_text().replace("\'","’")
            example['en'] =BeautifulSoup( frenchNote[translated_example_field],'html.parser').get_text().replace("\'","’")
            example['audio'] =BeautifulSoup( frenchNote[example_audio_field],'html.parser').get_text().replace("\'","’")

            if (example['fr'] not in bankKeys  and example['en'] !=""):
                new_examples_list[new_Examples]=example
                new_Examples +=1

    if new_Examples > 0:
        for newExample in new_examples_list:
            example = new_examples_list[newExample]
            did = mw.col.decks.id(bankDeckName)
            mw.col.decks.select(did)
            m = mw.col.models.byName(sentenceModelName)
            deck = mw.col.decks.get(did)
            deck['mid'] = m['id']
            mw.col.decks.save(deck)

            new_note = mw.col.newNote()
            new_note[target_lang_field] = example['fr']
            new_note[mother_lang_field] = example['en']
            new_note[audio_field] = example['audio']
            new_note.flush()
            mw.col.addNote(new_note)


        # tooltip(_("New Notes added to sentence bank"), period=1000)

        return(new_Examples,new_examples_list)
    else:
        logger.info('No new sentences were found in the main notes')

###########################################################
def refreshOneNote (frenchNote):

    bankField = frenchNote['Bank']

    if len(bankField) > 0:
        examples_list = json.loads(bankField)
        ex_count = len(examples_list)
        if (ex_count > 0):

            selector =random.randint(0, ex_count-1)
            # ensure the privious example doesn't appear again
            if  examples_list[selector]['fr'] == frenchNote[example_field] and ex_count > 1 :
                if selector >= 0 and selector < ex_count-3:
                    selector +=1
                else :
                    selector -=1

            frenchNote[example_field] = examples_list[selector]['fr']
            frenchNote[translated_example_field] = examples_list[selector]['en']
            frenchNote[example_audio_field] = "[sound:"+examples_list[selector]['audio']+"]"
            frenchNote.flush()
        else:
            frenchNote[example_field] = ""
            frenchNote[translated_example_field] = ""
            frenchNote[example_audio_field] = ""
            frenchNote.flush()

########################################################################################################
def deleteExampleFromANote(note):
    try:
        old_bank =  json.loads(note['Bank'])
        try:
            old_garbage = json.loads(note['garbage'])
        except:
            old_garbage=[]

        current_example = note[example_field]
        logger.info(old_bank)
        logger.info(len(old_bank))
        if len(old_bank) == 1:
            msg = 'This Note has only this example are you sure you want to delete it ?'
            if not askUser(msg , title=ADDON_NAME):
                return

        for example in old_bank:
            if example['fr'] == note[example_field]:
                old_bank.remove(example)
                old_garbage.append(example)
                break
        note['Bank'] = json.dumps(old_bank,ensure_ascii=False)
        note['garbage'] = json.dumps(old_garbage,ensure_ascii=False)


    except:
        pass

    note[example_field] = ""
    note[translated_example_field] = ""
    note[example_audio_field] = ""
    note.flush()
