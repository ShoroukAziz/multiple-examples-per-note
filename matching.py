from aqt import mw
from bs4 import BeautifulSoup
from .config import *
from .helpers import *
from aqt.utils import showInfo , askUser , showText , tooltip
import json

def updateBankField(list , note):
    found_examples = 0
    if note['doubleMeaning'] == 'y':
        englishWord = note[translation]
        filtered_list = []
        for example in list:
            if englishWord in example['en'] :
                filtered_list.append(example)

        list = filtered_list

    if len(list) > 0:

        try:

            old_bank = json.loads(note['Bank'])
            old_french = [example['fr'] for example in old_bank]

        except:
            old_bank=[]
            old_french=[]

        try:
            garbage = json.loads(note['garbage'])
        except:
            garbage = []


        for ex in list:
            if (ex['fr'] not in old_french) and (ex not in garbage) :
                old_bank.append(ex)
                found_examples =1


        note['Bank'] =json.dumps(old_bank,ensure_ascii=False)
        note.flush()


    return found_examples






def french_match (wordsDict , bankDict , frenchNote  ):

    frenchWord = BeautifulSoup( frenchNote[forign_word],'html.parser').get_text().lower().replace("\'","’")

    type = BeautifulSoup( frenchNote['type'],'html.parser').get_text().lower()
    pluralWord = BeautifulSoup( frenchNote['plural'],'html.parser').get_text().lower()
    femWord = BeautifulSoup( frenchNote['feminin version'],'html.parser').get_text().lower()


    examples_list = []


    if frenchWord in wordsDict:
        listOfIds = wordsDict[frenchWord]
        examples_list  += [bankDict[exId] for exId in listOfIds ]

    if pluralWord in wordsDict and pluralWord != frenchWord  :
        listOfIds = wordsDict[pluralWord]
        examples_list  += [bankDict[exId] for exId in listOfIds ]

    if femWord  in wordsDict and femWord != frenchWord :
        listOfIds = wordsDict[femWord]
        examples_list  += [bankDict[exId] for exId in listOfIds ]


    return examples_list

def strict_match (wordsDict , bankDict , frenchNote ):
    frenchWord = BeautifulSoup( frenchNote[forign_word],'html.parser').get_text().lower()
    pluralWord = BeautifulSoup( frenchNote['plural'],'html.parser').get_text().lower()
    examples_list = []
    if frenchWord in wordsDict:
        listOfIds = wordsDict[frenchWord]
        examples_list  += [bankDict[exId] for exId in listOfIds ]
    return examples_list



def matchWordsAndExamples(id ,res, matchingType):
    '''
    Updates the bank field in notes with all the matching examples found
    in the bank sentence deck or the newly found sentences
    '''
    updated_notes = 0
    wordsDict = res[0]
    bankDict = res[1]

    frenchNote = mw.col.getNote(id)
    try:
        frenchWord = BeautifulSoup( frenchNote[forign_word],'html.parser').get_text().lower()
    except:
        return
    if matchingType == 'french':
        examples_list = french_match(wordsDict , bankDict , frenchNote)
    elif matchingType == 'strict':
        examples_list = strict_match(wordsDict , bankDict , frenchNote)


    if updateBankField(examples_list , frenchNote) > 0:
        updated_notes +=1

    '''
    if after updating or rebuilding the bank the main exaple is empty refresh the note to get a main example
    '''
    if frenchNote[example_field] == "" and frenchNote['Bank'] != "":
        refreshOneNote (frenchNote)


    return updated_notes
