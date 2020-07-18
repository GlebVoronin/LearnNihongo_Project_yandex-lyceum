from data.models.hiragana import Hiragana
from data.models.kanji import Kanji
from data.models.katakana import Katakana
from data.models.words import Word
"""Общие константы в программе для обозначения данных категорий"""
HIRAGANA = 'hiragana'
KATAKANA = 'katakana'
KANJI = 'kanji'
WORD = 'words'
IMAGE = 20
SOUND = 21
HARD = 2
CONTINUE = 1
NUMERABLE = -1
CLASSES_BY_TYPES_OF_ELEMENTS = {HIRAGANA: Hiragana,
                                KATAKANA: Katakana,
                                KANJI: Kanji,
                                WORD: Word}
COUNT_OF_LEARNING = 15  # Количество слов / иероглифов в 1 уроке
TIME_FOR_ONE_ELEMENT = {  # допустимое время тестирования одного элемента (в секундах)
    HIRAGANA: 2,
    KATAKANA: 2,
    WORD: 4,
    KANJI: 7
}
ERROR_PERCENT_FOR_TEST = 10  # допустимый процент ошибок для зачёта тестирования
DB_FILE_NAME = 'Main.sqlite'
LOG_FILE = 'Log.log'
