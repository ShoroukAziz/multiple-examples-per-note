from .helpers import *
import json


def update_bank_field(list, note):
    found_examples = 0
    if note['doubleMeaning'] == 'y':
        english_word = note[translation]
        filtered_list = []
        for example in list:
            if english_word in example['en']:
                filtered_list.append(example)

        list = filtered_list

    if len(list) > 0:

        try:

            old_bank = json.loads(note['Bank'])
            old_french = [example['fr'] for example in old_bank]

        except:
            old_bank = []
            old_french = []

        try:
            garbage = json.loads(note['garbage'])
        except:
            garbage = []

        for ex in list:
            if (ex['fr'] not in old_french) and (ex not in garbage):
                old_bank.append(ex)
                found_examples = 1

        note['Bank'] = json.dumps(old_bank, ensure_ascii=False)
        note.flush()

    return found_examples


def french_match(words_dict, bank_dict, french_note):
    french_word = BeautifulSoup(french_note[foreign_word], 'html.parser').get_text().lower().replace("\'", "’")

    type = BeautifulSoup(french_note['type'], 'html.parser').get_text().lower()
    plural_word = BeautifulSoup(french_note['plural'], 'html.parser').get_text().lower()
    fem_word = BeautifulSoup(french_note['feminin version'], 'html.parser').get_text().lower()

    examples_list = []

    if french_word in words_dict:
        list_of_ids = words_dict[french_word]
        examples_list += [bank_dict[exId] for exId in list_of_ids]

    if plural_word in words_dict and plural_word != french_word:
        list_of_ids = words_dict[plural_word]
        examples_list += [bank_dict[exId] for exId in list_of_ids]

    if fem_word in words_dict and fem_word != french_word:
        list_of_ids = words_dict[fem_word]
        examples_list += [bank_dict[exId] for exId in list_of_ids]

    return examples_list


def strict_match(words_dict, bank_dict, french_note):
    french_word = BeautifulSoup(french_note[foreign_word], 'html.parser').get_text().lower()
    plural_word = BeautifulSoup(french_note['plural'], 'html.parser').get_text().lower()
    examples_list = []
    if french_word in words_dict:
        list_of_ids = words_dict[french_word]
        examples_list += [bank_dict[exId] for exId in list_of_ids]
    return examples_list


def match_words_and_examples(id, res, matchingType):
    """
    Updates the bank field in notes with all the matching examples found
    in the bank sentence deck or the newly found sentences
    """
    updated_notes = 0
    words_dict = res[0]
    bank_dict = res[1]

    french_note = mw.col.getNote(id)
    try:
        french_word = BeautifulSoup(french_note[foreign_word], 'html.parser').get_text().lower()
    except:
        return
    if matchingType == 'french':
        examples_list = french_match(words_dict, bank_dict, french_note)
    elif matchingType == 'strict':
        examples_list = strict_match(words_dict, bank_dict, french_note)

    if update_bank_field(examples_list, french_note) > 0:
        updated_notes += 1

    '''
    if after updating or rebuilding the bank the main exaple is empty refresh the note to get a main example
    '''
    if french_note[example_field] == "" and french_note['Bank'] != "":
        refresh_one_note(french_note)

    return updated_notes
