from aqt import mw
from bs4 import BeautifulSoup
from .config import *
from .helpers import *
from aqt.utils import showInfo , askUser , showText , tooltip
import json

def updateBankField(list , note):
    logger.info(note['word'])
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



def matchWordsAndExamples(ids):
    '''
    Updates the bank field in notes with all the matching examples found
    in the bank sentence deck or the newly found sentences
    '''
    updated_notes = 0
    updateBankDeck()
    bank = getBank()
    res = createDict(bank)
    wordsDict = res[0]
    bankDict = res[1]

    for id in ids:
        frenchNote = mw.col.getNote(id)
        frenchWord = BeautifulSoup( frenchNote[forign_word],'html.parser').get_text().lower()
        type = BeautifulSoup( frenchNote['type'],'html.parser').get_text().lower()
        examples_list = []

        if frenchWord in wordsDict:
            listOfIds = wordsDict[frenchWord]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if frenchWord+"s" in wordsDict and ('noun' in type or 'adjective' in type)  :
            listOfIds = wordsDict[frenchWord+"s"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if frenchWord+"e" in wordsDict and 'adjective' in type:
            listOfIds = wordsDict[frenchWord+"e"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "d’"+frenchWord in wordsDict and ('noun' in type or 'adjective' in type) :
            listOfIds = wordsDict["d’"+frenchWord]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "l’"+frenchWord in wordsDict and ('noun' in type or 'adjective' in type) :
            listOfIds = wordsDict["l’"+frenchWord]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "d’"+frenchWord+"s" in wordsDict and ('noun' in type or 'adjective' in type) :
            listOfIds = wordsDict["d’"+frenchWord+"s"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "l’"+frenchWord+"s" in wordsDict and ('noun' in type or 'adjective' in type) :
            listOfIds = wordsDict["l’"+frenchWord+"s"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "d’"+frenchWord+"e" in wordsDict and  'adjective' in type :
            listOfIds = wordsDict["d’"+frenchWord+"e"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]

        if "l’"+frenchWord+"e" in wordsDict and  'adjective' in type:
            listOfIds = wordsDict["l’"+frenchWord+"e"]
            examples_list  += [bankDict[exId] for exId in listOfIds ]


        if len(examples_list) > 0:
            if updateBankField(examples_list , frenchNote) > 0:
                logger.info(str(updated_notes))
                updated_notes +=1

        '''
        if after updating or rebuilding the bank the main exaple is empty refresh the note to get a main example
        '''
        if frenchNote[example_field] == "" and frenchNote['Bank'] != "":
            refreshOneNote (frenchNote)


    showInfo('Updaiting The Bank Field Was Done Successfully' , title=ADDON_NAME ,  textFormat='rich')
    logger.info('Updaiting The Bank Field Was Done Successfully')
    return updated_notes
