import logging
import os
import sys
import webbrowser
from shutil import copy2

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from werkzeug.security import check_password_hash

import data.register
import data.test
from data import db_session
from data.Nihongo import ProgramLearnJapaneseLanguage
from data.models.hiragana import Hiragana
from data.models.kanji import Kanji
from data.models.katakana import Katakana
from data.models.users import User
from data.models.words import Word
from data.style import *

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

logging.basicConfig(
    level=logging.ERROR,
    filename=LOG_FILE,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ProgramLearnJapaneseLanguage()
    main.show()


    def update_progress(type_of_learning, user):
        if user:
            session = db_session.create_session()
            user = session.query(User).filter(User.id == user.id).first()
            current = getattr(user, f'{type_of_learning}_save', 1)
            setattr(user, f'{type_of_learning}_save', current + 1)
            session.commit()
            main.load_user(user.login, user.password_hash, hashed=True)
    sys.exit(app.exec_())