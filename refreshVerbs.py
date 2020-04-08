import aqt
from aqt import mw
from aqt.utils import showInfo , askUser , showText , tooltip

######################################################################
def refreshVerbs():
    msg = "Search for Examples That conatins verb conjugations and assign them the matching notes?"
    if not askUser(msg, title=ADDON_NAME):
        return
    try:

        res = createDict(getBank())
        wordsDict = res[0]
        bankDict = res[1]
        # showInfo('started assigning examples to words')

        m = mw.col.models.byName('french verbs')
        id = m['id']
        notes = mw.col.db.all("SELECT id ,  flds  from notes where mid= '%s'"%id)

        for row in notes:

            row = str(row)[1:-2]
            row = row.split(', ', 1)
            id = row[0].strip()
            fields = row[1][1:]
            fields = fields.split('\\x1f')

            indices = [i for i in range(14, 32)]
            for index in indices:
                f = BeautifulSoup( fields[index],'html.parser').get_text().lower()
                f = f.lower().replace("\\","").replace("\'","’")
                if len(f) > 0:
                    f = re.split("[/ ]+", f)
                    element_length = len(f)
                    example = None
                    if element_length == 1 :
                        if f[0] in wordsDict:
                            examples_list = wordsDict[f[0]]
                            example = bankDict[examples_list[0]]
                    elif element_length == 2:
                        pronoun = f[0]
                        acctual_f = f[1]
                        if acctual_f in wordsDict:
                            examples_list = wordsDict[acctual_f]
                            for i in examples_list :
                                ex = bankDict[i]
                                compare = ex['fr'].lower()
                                compare = compare.replace("\'","’")
                                if pronoun+" "+acctual_f in compare:
                                    example = ex
                                    break
                                elif pronoun+" ne "+acctual_f in compare:
                                    example = ex
                                    break

                    elif element_length == 3:
                        pronoun1 = f[0]
                        pronoun2 = f[1]
                        acctual_f = f[2]
                        if acctual_f in wordsDict:
                            examples_list = wordsDict[acctual_f]
                            for i in examples_list :
                                ex = bankDict[i]
                                compare = ex['fr'].lower()
                                if pronoun1+" "+pronoun2+" "+acctual_f in compare :
                                    example = ex
                                    break
                                elif pronoun1+" "+acctual_f in compare and  ( pronoun1 == 'il' or pronoun1 == 'ils' ) :
                                    example = ex
                                    break
                                elif pronoun2+" "+acctual_f in  compare  and ( pronoun1 == 'elle' or pronoun1 == 'elles' ) :
                                    example = ex
                                    break

                    elif element_length == 4:
                        pronoun1 = f[0]
                        pronoun2 = f[1]
                        pronoun3 = f[2]
                        acctual_f = f[3]
                        if acctual_f in wordsDict:
                            examples_list = wordsDict[acctual_f]
                            for i in examples_list :
                                ex = bankDict[i]
                                compare = ex['fr'].lower()
                                if pronoun1+" "+pronoun3+" "+acctual_f in compare :
                                    example = ex
                                    break
                                elif pronoun2+" "+pronoun3+" "+acctual_f in compare :
                                    example = ex
                                    break


                    else :
                        example = None


                    note = mw.col.getNote(id)
                    ex_f_name = str(index - 13)
                    sound_f_name = ex_f_name+'S'
                    if(example != None):
                        note[ex_f_name] = "<b>"+example['fr']+"</b><br>"+example['en']+"<br>"
                        note[sound_f_name] = example['audio']
                        note.flush()
                    else:
                        note[ex_f_name] =""
                        note[sound_f_name] = ""
                        note.flush()
                else:
                    note = mw.col.getNote(id)
                    note[ex_f_name] =""
                    note[sound_f_name] = ""
                    note.flush()


        mw.col.reset()
        mw.reset()
        logger.info('refreshing verbs done successfully')
        showInfo('refreshing verbs done successfully' , title=ADDON_NAME ,  textFormat='rich')
    except:
        logger.info('Error refreshing verbs')
        showInfo('Error refreshing verbs' , title=ADDON_NAME ,  textFormat='rich')
