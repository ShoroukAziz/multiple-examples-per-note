from bs4 import BeautifulSoup
import logging
import json
import re
import random
from .config import *
from aqt.utils import askUser
import os

ADDON = os.path.dirname(os.path.abspath(__file__))
###############################################################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(ADDON + '/logs.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


################################################################################################################

def get_all_note_ids(models):
    ids = []
    for modelName in models:
        model = mw.col.models.byName(modelName)
        model_id = str(model['id'])
        notes_ids = mw.col.db.all("SELECT  id  from notes where mid = '" + model_id + "'")
        for note_id in notes_ids:
            note_id = str(note_id)[1:-2]
            ids.append(note_id)
    return ids


################################################################################################################


def get_bank():
    """
    loops over all the notes in the sentences bank and adds them to a dict  of dicts and returns that dict
    """
    # Get the model id of the sentences notes
    model = mw.col.models.byName(sentenceModelName)["id"]
    notes = mw.col.findNotes("mid:" + str(model))

    collected_example_id = 0
    bank = {}
    for note in notes:
        french_sentence_note = mw.col.getNote(note)
        try:
            example = {
                'fr': BeautifulSoup(french_sentence_note[target_lang_field], 'html.parser').get_text().replace("\'",
                                                                                                               "’"),
                'en': BeautifulSoup(french_sentence_note[mother_lang_field], 'html.parser').get_text().replace("\'",
                                                                                                               "’"),
                'audio': BeautifulSoup(french_sentence_note[audio_field], 'html.parser').get_text().replace("\'",
                                                                                                            "’"),
                'noteId': french_sentence_note.id}
            bank[collected_example_id] = example
            collected_example_id += 1
        except:
            pass
    logger.info('bank retrieved successfully')
    return bank


###############################################################################################################


def create_dict(bank):
    """
    creates a dictionary of all the words in the examples and which examples they appear on
    """

    logger.info("There are " + str(len(bank)) + " sentences")
    dictionary = {}
    for id in bank:
        example = bank[id]
        example['audio'] = example['audio'].split(',')[0]
        example['audio'] = example['audio'][7:-1]
        words = example['fr'].lower()
        words = words.replace('\\xa0', ' ')
        words = re.split('[.?!, «»()\"]', words)

        for word in words:
            word = word.replace(" d\'", "")
            word = word.replace(" l\'", "")
            word = word.replace(" d’", "")
            word = word.replace(" l’", "")
            if word.startswith("d\'"):
                word = word.replace("d\'", "")
            elif word.startswith("l\'"):
                word = word.replace("l\'", "")
            elif word.startswith("d’"):
                word = word.replace("d’", "")
            elif word.startswith("l’"):
                word = word.replace("l’", "")

            if word not in dictionary and len(word) > 1:
                idsList = []
                idsList.append(id)
                dictionary[word] = idsList
            elif word in dictionary:
                dictionary[word].append(id)

    from pprint import pformat

    logger.info(pformat(dictionary))
    logger.info("There are " + str(len(dictionary)) + " unique words")
    logger.info('dicts created successfully')
    return dictionary, bank


################################################################################################################


def update_bank_deck():
    """
    loops over all the notes in the (French (verbs , nouns , adv and adj ))
    and  add the examples found in them and not in the french sentence model to
    the french sentence deck
    """
    logger.info('updating bank deck .....')
    bank = get_bank()
    bank_keys = []
    for id in bank:
        example = bank[id]
        bank_keys.append(example['fr'])

    logger.info(len(bank_keys))

    new_examples_list = {}

    new_examples = 0

    for modelName in mainModelsNames:

        model_id = str(mw.col.models.by_name(modelName)['id'])
        french_sentences_ids = mw.col.db.all("SELECT  id  from notes where mid = '" + model_id + "'")

        for id in french_sentences_ids:
            id = str(id)[1:-1]
            id = int(id)

            french_note = mw.col.getNote(id)
            example = {'fr': BeautifulSoup(french_note[example_field], 'html.parser').get_text().replace("\'", "’"),
                       'en': BeautifulSoup(french_note[translated_example_field], 'html.parser').get_text().replace(
                           "\'",
                           "’"),
                       'audio': BeautifulSoup(french_note[example_audio_field], 'html.parser').get_text().replace("\'",
                                                                                                                  "’"),
                       'noteId': french_note.id}

            if example['fr'] not in bank_keys and example['fr'] != "":
                new_examples_list[new_examples] = example
                new_examples += 1

    if new_examples > 0:
        for newExample in new_examples_list:
            example = new_examples_list[newExample]
            did = mw.col.decks.id(bankDeckName)
            mw.col.decks.select(did)
            m = mw.col.models.byName(sentenceModelName)
            deck = mw.col.decks.get(did)
            deck['mid'] = m['id']
            mw.col.decks.save(deck)

            new_note = mw.col.newNote()
            mw.col.addNote(new_note)
            new_note[target_lang_field] = example['fr']
            new_note[mother_lang_field] = example['en']
            new_note[audio_field] = example['audio']
            new_note.flush()
            # mw.col.addNote(new_note)

        # tooltip(_("New Notes added to sentence bank"), period=1000)

        return new_examples, new_examples_list
    else:
        logger.info('No new sentences were found in the main notes')


###########################################################


def refresh_one_note(french_note):
    bank_field = french_note['Bank']

    if len(bank_field) > 0:
        examples_list = json.loads(bank_field)
        ex_count = len(examples_list)
        if ex_count > 0:

            selector = random.randint(0, ex_count - 1)
            # ensure the previous example doesn't appear again
            if examples_list[selector]['fr'] == french_note[example_field] and ex_count > 1:
                if selector >= 0 and selector < ex_count - 3:
                    selector += 1
                else:
                    selector -= 1

            french_note[example_field] = examples_list[selector]['fr']
            french_note[translated_example_field] = examples_list[selector]['en']
            french_note[example_audio_field] = "[sound:" + examples_list[selector]['audio'] + "]"
            french_note[example_id_field] = str(examples_list[selector]['noteId'])
            french_note.flush()
        else:
            french_note[example_field] = ""
            french_note[translated_example_field] = ""
            french_note[example_audio_field] = ""
            french_note[example_id_field] = ""
            french_note.flush()


########################################################################################################


def delete_example_from_note(note):
    try:
        old_bank = json.loads(note['Bank'])
        try:
            old_garbage = json.loads(note['garbage'])
        except:
            old_garbage = []

        current_example = note[example_field]
        logger.info(old_bank)
        logger.info(len(old_bank))
        if len(old_bank) == 1:
            msg = 'This Note has only this example are you sure you want to delete it ?'
            if not askUser(msg, title=ADDON_NAME):
                return

        for example in old_bank:
            if example['fr'] == note[example_field]:
                old_bank.remove(example)
                old_garbage.append(example)
                break
        note['Bank'] = json.dumps(old_bank, ensure_ascii=False)
        note['garbage'] = json.dumps(old_garbage, ensure_ascii=False)


    except:
        pass

    note[example_field] = ""
    note[translated_example_field] = ""
    note[example_audio_field] = ""
    note[example_id_field] = ""
    note.flush()

########################################################################################################
