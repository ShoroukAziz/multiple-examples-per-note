from aqt import mw
import os , sys

###############################################################
# Configurable sittings
#  - sentenceModelName : The name of the model containing all the sentences -> Default : "french sentence"
#  - model id's of note you wanna collect examples from
#    (in my case: french nouns , french adjectives , french adverbs , french verbs) :
#    ['1573430574304' , '1577565396172' , '1577565612747' , '1577564379922'   ]
#
################################################################

ADDON = os.path.dirname(os.path.abspath(__file__))
ICONS = ADDON+'/icons'
ADDON_NAME="MPER"

CONFIG = mw.addonManager.getConfig(__name__)

french = CONFIG['french']
sentenceModelName = CONFIG["sentenceModel"]["name"]
target_lang_field = CONFIG["sentenceModel"]["target_language_field"]
mother_lang_field = CONFIG["sentenceModel"]["mother_language_field"]
audio_field = CONFIG["sentenceModel"]["audio_field"]

mainModelsNames = CONFIG["mainModels"]["names"]
forign_word=CONFIG["mainModels"]["word"]
translation =CONFIG["mainModels"]["translated_word"]
example_field = CONFIG["mainModels"]["example_field"]
translated_example_field = CONFIG["mainModels"]["translated_example_field"]
example_audio_field = CONFIG["mainModels"]["examples_audio_field"]

bankDeckName = CONFIG["bankDeckName"]

matching_type = CONFIG["matching"]
