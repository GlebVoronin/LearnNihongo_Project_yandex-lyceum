import logging
import os
import sys
import webbrowser
from copy import deepcopy
from random import shuffle
from threading import Thread
from time import sleep

from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (QLCDNumber, QApplication, QMainWindow, QPushButton, QLabel,
                             QFileDialog, QLineEdit, QSpinBox, QListWidget, QListWidgetItem, )

from data import db_session
from data.models.hiragana import Hiragana
from data.models.kanji import Kanji
from data.models.katakana import Katakana
from data.models.words import Word

"""Общие константы в программе для обозначения данных категорий"""
HIRAGANA = 'hiragana'
KATAKANA = 'katakana'
KANJI = 'kanji'
WORDS = 'words'
IMAGE = 20
SOUND = 21
NEW = 0
HARD = 2
CONTINUE = 1
NUMERABLE = -1
CLASSES_BY_TYPES_OF_ELEMENTS = {HIRAGANA: Hiragana,
                                KATAKANA: Katakana,
                                KANJI: Kanji,
                                WORDS: Word}
COUNT_OF_LEARNING = 15  # Количество слов / иероглифов в 1 уроке
TIME_TO_TEST_FOR_ONE_WORD = 4  # В секундах
TIME_TO_TEST_FOR_ONE_KANJI = 9  # В секундах
TIME_TO_TEST_FOR_ONE_KANA_SYMBOL = 2  # В секундах
DB_FILE_NAME = 'Main.sqlite'
LOG_FILE = 'Log.log'

logging.basicConfig(
    level=logging.ERROR,
    filename=LOG_FILE,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


class ProgramLearnJapaneseLanguage(QMainWindow):
    def __init__(self):
        super().__init__()
        db_session.global_init(f'db/{DB_FILE_NAME}')
        self.temporary_files = {'sound': None, 'image': None}
        self.current_user = None
        self.path = os.getcwd()  # Путь к текущей папке программы
        self.setupUi()

    @staticmethod
    def get_lesson_elements_by_type(elements_type, lesson_number=1, all_lessons=False):
        """
        Данная функция принимает в качестве аргументов: тип элемента и номер урока
        Если номер урока не был указан, то будет выбран 1 урок.
        Функция возвращат список объектов модели указанного элемента
        Например:
        result = get_lesson_elements_by_type(HIRAGANA, lesson_number=2)
        result == [Hiragana, Hiragana ...Hiragana]
        result[0] == Hiragana(id=1, title='あ', reading='А')
        result[7] == Hiragana(id=7, title='ま', reading='Ма')
        """
        class_of_element = CLASSES_BY_TYPES_OF_ELEMENTS.get(elements_type)
        if not class_of_element:
            return logging.error('Type of element not found in classes list')
        session = db_session.create_session()
        # Опрделение id нужных элементов (начиная с последнего, количество за 1 урок)
        if all_lessons:
            start_id = 1
        else:
            start_id = COUNT_OF_LEARNING * (lesson_number - 1) + 1
        end_id = COUNT_OF_LEARNING * lesson_number
        elements = session.query(class_of_element).filter(
            class_of_element.id >= start_id, class_of_element.id <= end_id).all()
        return elements

    def create_small_main_menu_button(self):
        return_button = QPushButton('Меню', self)
        return_button.setGeometry(660, 0, 40, 40)
        return_button.clicked.connect(self.return_to_start_menu)
        self.enable_ui([return_button])
        self.ui_list.append(return_button)

    def create_normal_main_menu_button(self):
        return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
        return_to_menu_button.setGeometry(50, 100, 600, 50)
        return_to_menu_button.clicked.connect(self.return_to_start_menu)
        return_to_menu_button.setFont(self.font_20)
        self.ui_list.append(return_to_menu_button)
        self.enable_ui([return_to_menu_button])

    def return_to_start_menu(self):
        self.disable_ui()
        self.enable_ui([self.start_learn_button, self.start_checking_button,
                        self.setup_button, self.answer_button])

    def disable_ui(self):
        for ui_item in self.ui_list:
            ui_item.setVisible(False)
            ui_item.setEnabled(False)

    def enable_ui(self, list_of_ui):
        """
        Данная функция активирует видимость элемента пользовательского интерфейса
        и возможность взаимоодействия с ним
        Также устанавливает стиль элементов"""
        for ui_element in list_of_ui:
            ui_element.setVisible(True)
            ui_element.setEnabled(True)
            self.set_style(ui_element)

    @staticmethod
    def set_style(ui_element):
        """Функция устанавливает стиль элемента"""
        if hasattr(ui_element, 'setStyleSheet'):
            if isinstance(ui_element, QPushButton):
                ui_element.setStyleSheet('background-color: rgb(70, 70, 200)')
            else:
                ui_element.setStyleSheet('background-color: rgb(120, 120, 255)')

    def register(self):
        pass

    def login(self):
        pass

    def answer_of_users_questions(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        answer_label = QLabel(self)
        answer_label.setAlignment(Qt.AlignTop)
        answer_label.setGeometry(25, 25, 630, 430)
        text = """
<font color="black">1) Данна программа позволяет выучить две азбуки японского алфавита,<br>
слова и кандзи.</font><br>
<font color="yellow">Но программа не содержит уроков по грамматике японского языка</font><br>
<font color="black">2) Сначала рекомендуется изучить азбуки(катакана и хирагана),<br>
а уже потом слова и кандзи<br>
3) Новые слова и кандзи, которых нет в программе, вы можете<br>
добавить в настройках в главном меню.<br>
4) Если слово или кандзи есть в программе, но не имеет звука или<br>
изображения, вы можете добавить их,<br>
если введёте написание, чтение и значения такими,<br>
какими они написаны в программе<br>
5) В конце каждого урока вам будет предложено пройти тест,<br>
чтобы перейти к следующему уроку.</font><br>
<font color="yellow">Чтобы пройти тест вам необходимо допустить менее 1 % ошибок.<br>
В тесте из 15 вопросов, следовательно, 0 ошибок.<br>
В тесте из 700 вопрос — не более 7 ошибок.</font><br>
<font color="black">6)　Вы можете пройти тест по всем изученным словам или<br>
иероглифам в пункте "Проверка" главного меню.<br>
Также вы можете повторить любой из изученных уроков и / или<br>
пройти по нему тест заново.</font><br>
<font color="yellow">Если вы провалите уже пройденный тест, ваш прогресс утерян не будет.</font><br>
<font color="black">7) Вы всегда можете сбросить свои сохранения для каждого<br>
раздела отдельно, нажав на кнопку "Начать сначала".</font><br>"""
        answer_label.setText(text)
        font = QFont()
        font.setPointSize(11)
        answer_label.setFont(font)
        self.ui_list.extend([answer_label])
        self.enable_ui([answer_label])

    def setupUi(self):
        self.font_14 = QFont()
        self.font_14.setPointSize(14)
        self.font_20 = QFont()
        self.font_20.setPointSize(20)
        self.resize(700, 450)
        self.setStyleSheet('background-color: rgb(120, 120, 255)')
        self.centralwidget = QtWidgets.QWidget(self)
        self.start_learn_button = QPushButton(self.centralwidget)
        self.start_learn_button.setGeometry(25, 58, 650, 40)
        self.start_learn_button.setFont(self.font_14)
        self.start_checking_button = QPushButton(self.centralwidget)
        self.start_checking_button.setGeometry(25, 156, 650, 40)
        self.start_checking_button.setFont(self.font_14)
        self.setup_button = QPushButton(self.centralwidget)
        self.setup_button.setGeometry(25, 254, 650, 40)
        self.setup_button.setFont(self.font_14)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(0, 0, 700, 21)
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.start_learn_button.setText("Обучение")
        self.start_checking_button.setText("Проверка")
        self.setup_button.setText("Настройка")
        self.setup_button.clicked.connect(self.open_setup_menu)
        self.start_learn_button.clicked.connect(self.start_learn)
        self.start_checking_button.clicked.connect(self.checking)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.answer_button = QPushButton('Справка', self)
        self.answer_button.setGeometry(25, 352, 650, 40)
        self.answer_button.clicked.connect(self.answer_of_users_questions)
        self.answer_button.setFont(self.font_14)
        self.ui_list = [self.setup_button, self.start_checking_button,
                        self.start_learn_button, self.answer_button]
        self.enable_ui(self.ui_list)

    def checking(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        self.create_main_types_of_learning_button_with_function(self.menu_of_checking)

    def menu_of_checking(self, type_of_checking):
        session = db_session.create_session()
        self.disable_ui()
        self.create_small_main_menu_button()
        continue_test_button = QPushButton('Пройти тест по последнему уроку', self)
        continue_test_button.setGeometry(100, 40, 500, 50)
        continue_test_button.clicked.connect(lambda: self.start_checking_by_type(type_of_checking, CONTINUE))

        def get_lesson(number_of_lesson_object: QSpinBox, function_of_test, type_of_checking):
            number_of_lesson = number_of_lesson_object.value()
            function_of_test(type_of_checking, number_of_lesson)

        number_of_lesson_obj = QSpinBox(self)
        number_of_lesson_obj.setGeometry(610, 140, 30, 50)
        number_of_lesson_obj.setMinimum(1)
        maximum = getattr(self.current_user, f'{type_of_checking}_save', __default=1)
        number_of_lesson_obj.setMaximum(maximum)
        past_test_button = QPushButton('Пройти тест по предыдущим урокам', self)
        past_test_button.setGeometry(100, 140, 500, 50)
        past_test_button.clicked.connect(lambda: get_lesson(number_of_lesson_obj, test, NUMERABLE))
        hard_test_button = QPushButton('Начать тест по всему изученному в данном разделе', self)
        hard_test_button.setGeometry(100, 240, 500, 50)
        hard_test_button.clicked.connect(lambda: test(HARD))
        view_learned_words = QPushButton('Посмотреть изученное', self)
        view_learned_words.setGeometry(100, 340, 500, 50)
        ui = [continue_test_button, past_test_button, hard_test_button,
              number_of_lesson_obj, view_learned_words]
        view_learned_words.clicked.connect(lambda: self.view_learned(type_of_checking, ui))

        self.enable_ui(ui)
        self.ui_list.extend(ui)

    def start_checking_by_type(self, type_of_continue, type_of_checking, num_of_lesson=1):
        """Метод передаёт необходимые параметры в процесс тестирования
        (возможно этот метод не нужен)"""
        if type_of_continue == HARD or type_of_continue == CONTINUE:
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        test_elements = self.get_lesson_elements_by_type(type_of_checking, num_of_lesson)
        self.test_of_learned_elements(type_of_checking, test_elements, is_upgrading_test)

    def checking_hiragana(self, type_of_continue, num_of_lesson=None):
        if type_of_continue == HARD or type_of_continue == CONTINUE:
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        kana_symbols = self.get_kana(HIRAGANA, type_of_continue, num_of_lesson)
        self.test_of_learned_elements(HIRAGANA, kana_symbols, is_upgrading_test)

    def checking_katakana(self, type_of_continue, num_of_lesson=None):
        if type_of_continue == HARD or type_of_continue == CONTINUE:
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        kana_symbols = self.get_kana(KATAKANA, type_of_continue, num_of_lesson)
        self.test_of_learned_elements(KATAKANA, kana_symbols, is_upgrading_test)

    def checking_kanji(self, type_of_continue, num_of_lesson=None):
        if type_of_continue == HARD or type_of_continue == CONTINUE:
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        kanji = self.get_kanji(type_of_continue, num_of_lesson)
        self.test_of_learned_elements(KANJI, kanji, is_upgrading_test)

    def checking_words(self, type_of_continue, num_of_lesson=None):
        if type_of_continue == HARD or type_of_continue == CONTINUE:
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        words = self.get_words(type_of_continue, num_of_lesson)
        self.test_of_learned_elements(WORDS, words, is_upgrading_test)

    def save_images_or_sounds(self, writing, way, type_symb, file_type):
        """
        Данная функция сохраняет файл по указанном пути
        return save_images_or_sounds('学校', 'C:\\images\\image_1.png', KANJI, IMAGE)
        == 'C:\\Programs\\Nihongo\\images_and_sounds\\Kanji\\学校\\image.png'
        Путь для использования данной программой, исходный файл сохраняется
        """
        if not os.path.isdir(f'{self.path}\\images_and_sounds\\{type_symb}\\{writing}'):
            os.makedirs(f'{self.path}\\images_and_sounds\\{type_symb}\\{writing}')
        file_format = way.split('\\')[-1].split('.')[-1]
        if file_type == IMAGE:
            new_image_way = f'images_and_sounds\\{type_symb}\\{writing}\\image.{file_format}'
            self.copy_image_or_sound_to_program_folder(way, new_image_way)
            return new_image_way
        else:
            new_sound_way = f'images_and_sounds\\{type_symb}\\{writing}\\sound.{file_format}'
            self.copy_image_or_sound_to_program_folder(way, new_sound_way)
            return new_sound_way

    def save_new_kanji(self):
        writing = self.line_edit_of_writing.text()
        onyomi_reading = self.line_edit_of_onyomi_reading.text()
        kunyomi_reading = self.line_edit_of_kunyomi_reading.text()
        meaning = self.line_edit_of_meaning.text()
        path_to_image = self.temporary_files.get('image', default='')
        path_to_sound = self.temporary_files.get('sound', default='')
        if path_to_image:
            path_to_image = self.save_images_or_sounds(writing, path_to_image, KANJI, IMAGE)
        if path_to_sound:
            path_to_sound = self.save_images_or_sounds(writing, path_to_sound, KANJI, SOUND)
        session = db_session.create_session()
        kanji = session.query(Kanji).filter(Kanji.writing == writing, Kanji.meaning == meaning).first()
        if not kanji:
            kanji = Kanji(
                writing=writing,
                onyomi_reading=onyomi_reading,
                kunyomi_reading=kunyomi_reading,
                meaning=meaning,
                path_to_image=path_to_image,
                path_to_sound=path_to_sound
            )
            session.add(kanji)
            session.commit()
            self.line_edit_of_writing.setText('Добавлено!')
        else:
            self.line_edit_of_writing.setText(
                'Такой кандзи уже существует, пожалуйста, воспользуйтесь редактированием!'
            )
        self.disable_ui()
        self.open_setup_menu()

    def add_kanji(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        info_label_about_kanji_writing = QLabel('Введите написание иероглифа', self)
        info_label_about_kanji_writing.setGeometry(10, 20, 400, 30)
        self.line_edit_of_writing = QLineEdit(self)
        self.line_edit_of_writing.setGeometry(10, 60, 400, 40)
        info_label_about_kanji_onyomi_reading = QLabel('Введите онное чтение кандзи', self)
        info_label_about_kanji_onyomi_reading.setGeometry(10, 110, 400, 30)
        self.line_edit_of_onyomi_reading = QLineEdit(self)
        self.line_edit_of_onyomi_reading.setGeometry(10, 150, 400, 40)
        info_label_about_kanji_kunyomi_reading = QLabel('Введите кунное чтение кандзи', self)
        info_label_about_kanji_kunyomi_reading.setGeometry(10, 200, 400, 30)
        self.line_edit_of_kunyomi_reading = QLineEdit(self)
        self.line_edit_of_kunyomi_reading.setGeometry(10, 240, 400, 40)
        info_label_about_kanji_meaning = QLabel('Введите значение', self)
        info_label_about_kanji_meaning.setGeometry(10, 290, 400, 30)
        self.line_edit_of_meaning = QLineEdit(self)
        self.line_edit_of_meaning.setGeometry(10, 330, 400, 40)

        image_label = QLabel('', self)
        image_label.setGeometry(430, 60, 240, 240)
        image_button = QPushButton('Добавить изображение', self)
        image_button.setGeometry(460, 20, 180, 30)
        image_button.clicked.connect(lambda: self.add_image(image_label))

        sound_label = QLabel('', self)
        sound_label.setGeometry(460, 350, 180, 30)
        sound_button = QPushButton('Добавить звук', self)
        sound_button.setGeometry(460, 310, 180, 30)
        sound_button.clicked.connect(lambda: self.add_sound(sound_label))

        confirm_button = QPushButton('Добавить кандзи', self)
        confirm_button.setGeometry(50, 380, 600, 40)
        confirm_button.clicked.connect(self.save_new_kanji)
        ui = [info_label_about_kanji_writing, info_label_about_kanji_meaning,
              info_label_about_kanji_kunyomi_reading, info_label_about_kanji_onyomi_reading,
              self.line_edit_of_meaning, self.line_edit_of_onyomi_reading,
              self.line_edit_of_writing, image_button, sound_button,
              confirm_button, image_label, sound_label, self.line_edit_of_kunyomi_reading]
        self.ui_list.extend(ui)
        self.enable_ui(ui)

    def learn_hirigana(self, type_of_continue, num_of_lesson=None):
        hiragana_symbols = self.get_kana(HIRAGANA, type_of_continue, num_of_lesson)
        self.temporary_hiragana_symbols = iter(hiragana_symbols)
        self.create_kana_info(HIRAGANA)

    def learn_katakana(self, type_of_continue, num_of_lesson=None):
        katakana_symbols = self.get_kana(KATAKANA, type_of_continue, num_of_lesson)
        self.temporary_katakana_symbols = iter(katakana_symbols)
        self.create_kana_info(KATAKANA)

    def learn_kanji(self, type_of_continue, num_of_lesson=None):
        kanji = self.get_kanji(type_of_continue, num_of_lesson)
        self.temporary_kanji = iter(kanji)
        self.create_kanji_info()

    def learn_words(self, type_of_continue, num_of_lesson=None):
        words = self.get_words(type_of_continue, num_of_lesson)
        self.temporary_words = iter(words)
        self.create_word_info()

    def open_setup_menu(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        add_word_button = QPushButton('Добавить новое слово в программу', self)
        add_kanji_button = QPushButton('Добавить новый кандзи в программу', self)
        add_word_button.setGeometry(50, 50, 600, 40)
        add_kanji_button.setGeometry(50, 150, 600, 40)
        self.ui_list.append(add_kanji_button)
        self.ui_list.append(add_word_button)
        add_word_button.clicked.connect(self.add_word)
        add_kanji_button.clicked.connect(self.add_kanji)
        self.enable_ui([add_word_button, add_kanji_button])

    def copy_image_or_sound_to_program_folder(self, file_name, new_file_name):
        source = open(file_name, 'rb')
        current_file = open(new_file_name, 'wb')
        current_file.write(source.read())
        source.close()
        current_file.close()

    def add_image(self, image_label):
        file_name, pressed = QFileDialog.getOpenFileName(self, 'Выберите изображение', '')
        if pressed:
            self.temporary_files['image'] = file_name
            image = Image.open(file_name)
            image = image.resize((240, 240), Image.LANCZOS)
            image.save(file_name)
            pixmap = QPixmap(file_name)
            image_label.setPixmap(pixmap)

    def add_sound(self, sound_label):
        file_name, pressed = QFileDialog.getOpenFileName(self, 'Выберите звуковой файл', '')
        if pressed:
            self.temporary_files['sound'] = file_name
            sound_label.setText('Звук добавлен')
            sound_label.setFont(self.font_14)

    def listen(self, way_to_sound):
        webbrowser.open(way_to_sound)

    def save_new_word(self):
        writing = self.line_edit_of_writing.text()
        reading = self.line_edit_of_reading.text()
        meaning = self.line_edit_of_meaning.text()
        image_way = '' if None else self.temporary_files['image']
        sound_way = '' if None else self.temporary_files['sound']
        if sound_way:
            sound_way = self.save_images_or_sounds(writing, sound_way, KANJI, SOUND)
        if image_way:
            image_way = self.save_images_or_sounds(writing, image_way, KANJI, IMAGE)
        cursor = self.database.cursor()
        find = cursor.execute(f"""SELECT id FROM Words
        WHERE writing = '{writing}' AND reading = '{reading}' AND meaning = '{meaning}'""").fetchall()
        if find:
            if image_way:
                self.update_images_and_sounds(find, image_way, WORDS, IMAGE)
            if sound_way:
                self.update_images_and_sounds(find, sound_way, WORDS, SOUND)
        else:
            cursor = self.database.cursor()
            if image_way and sound_way:
                cursor.execute(f"""INSERT INTO Words(writing, reading, meaning, way_to_image, way_to_sound)
                VALUES('{writing}', '{reading}', '{meaning}', '{image_way}', '{sound_way}')""")
            elif image_way:
                cursor.execute(f"""INSERT INTO Words(writing, reading, meaning, way_to_image)
                            VALUES('{writing}', '{reading}', '{meaning}', '{image_way}')""")
            elif sound_way:
                cursor.execute(f"""INSERT INTO Words(writing, reading, meaning, way_to_sound)
                            VALUES('{writing}', '{reading}', '{meaning}', '{sound_way}')""")
            else:
                cursor.execute(f"""INSERT INTO Words(writing, reading, meaning)
                            VALUES('{writing}', '{reading}', '{meaning}')""")
        self.database.commit()
        self.disable_ui()
        self.open_setup_menu()

    def add_word(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        info_label_about_word_writing = QLabel('Введите написание слова', self)
        info_label_about_word_writing.setGeometry(10, 50, 400, 40)
        self.line_edit_of_writing = QLineEdit(self)
        self.line_edit_of_writing.setGeometry(10, 100, 400, 50)
        info_label_about_word_reading = QLabel('Введите написание слова каной (чтение)', self)
        info_label_about_word_reading.setGeometry(10, 160, 400, 40)
        self.line_edit_of_reading = QLineEdit(self)
        self.line_edit_of_reading.setGeometry(10, 210, 400, 50)
        info_label_about_word_meaning = QLabel('Введите значние слова', self)
        info_label_about_word_meaning.setGeometry(10, 260, 400, 40)
        self.line_edit_of_meaning = QLineEdit(self)
        self.line_edit_of_meaning.setGeometry(10, 310, 400, 50)

        image_label = QLabel('', self)
        image_label.setGeometry(430, 60, 240, 240)
        image_button = QPushButton('Добавить изображение', self)
        image_button.setGeometry(460, 20, 180, 30)
        image_button.clicked.connect(lambda: self.add_image(image_label))

        sound_label = QLabel('', self)
        sound_label.setGeometry(460, 350, 180, 30)
        sound_button = QPushButton('Добавить звук', self)
        sound_button.setGeometry(460, 310, 180, 30)
        sound_button.clicked.connect(lambda: self.add_sound(sound_label))

        confirm_button = QPushButton('Добавить слово', self)
        confirm_button.setGeometry(50, 380, 600, 40)
        confirm_button.clicked.connect(self.save_new_word)
        temporary_ui = [info_label_about_word_writing, info_label_about_word_meaning,
                        info_label_about_word_reading, self.line_edit_of_meaning,
                        self.line_edit_of_reading, self.line_edit_of_writing, image_button,
                        sound_button, confirm_button, image_label, sound_label]
        self.ui_list.extend(temporary_ui)
        self.enable_ui(temporary_ui)

    def check_answer(self, correct_answer, buttons, mistakes_left_label):
        if not self.checked and self.can_click:
            if self.sender().text() == correct_answer:
                self.sender().setStyleSheet('QPushButton {background-color: rgb(0, 255, 0);}')
            else:
                self.permissible_mistakes -= 1
                mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')
                for button in buttons:
                    if button.text() == correct_answer:
                        button.setStyleSheet('QPushButton {background-color: rgb(0, 255, 0);}')
                    else:
                        button.setStyleSheet('QPushButton {background-color: rgb(255, 0, 0);}')
            self.checked = True

    def check_answer_of_kanji(self, correct_answers, buttons, mistakes_left_label):
        for step in range(3):
            if not self.checked[step] and self.can_click and self.sender() in buttons[step]:
                if self.sender().text() == correct_answers[step]:
                    self.sender().setStyleSheet('QPushButton {background-color: rgb(0, 255, 0);}')
                else:
                    self.kanji_mistakes += 1
                    for button in buttons[step]:
                        if button.text() == correct_answers[step]:
                            button.setStyleSheet('QPushButton {background-color: rgb(0, 255, 0);}')
                        else:
                            button.setStyleSheet('QPushButton {background-color: rgb(255, 0, 0);}')
                self.checked[step] = True
        if self.kanji_mistakes and self.checked[0] and self.checked[1] and self.checked[2]:
            self.permissible_mistakes -= 1
            mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')

    def update_progress(self, type_of_learning):
        cursor = self.database.cursor()
        cursor.execute(f"""UPDATE Saves
        SET value = value + 1
        WHERE title_of_save = '{type_of_learning}'""").fetchall()
        self.database.commit()

    def test_of_learned_elements(self, type_of_elements, elements, is_upgrading_test=False):
        self.disable_ui()
        shuffle(elements)

        random_elements = deepcopy(elements)
        if not isinstance(elements, list):
            elements = [elements]
        if type_of_elements == WORDS:
            random_elements = [element[2] for element in random_elements]
            time_to_one_element = TIME_TO_TEST_FOR_ONE_WORD
        elif type_of_elements == HIRAGANA or type_of_elements == KATAKANA:
            random_elements = [element[1] for element in random_elements]
            time_to_one_element = TIME_TO_TEST_FOR_ONE_KANA_SYMBOL
        elif type_of_elements == KANJI:
            random_elements = [[element[1] for element in random_elements],
                               [element[2] for element in random_elements],
                               [element[3] for element in random_elements]]
            time_to_one_element = TIME_TO_TEST_FOR_ONE_KANJI
        all_time_to_test = time_to_one_element * len(elements)
        self.permissible_mistakes = int(len(elements) // 100)
        info_of_mistake_label = QLabel(f'Прав на ошибку осталось {self.permissible_mistakes}', self)
        info_of_mistake_label.setGeometry(390, 0, 300, 30)
        info_of_mistake_label.setFont(self.font_14)
        info = f'Вам необходимо пройти тест за {all_time_to_test} секунд или быстрее'
        info_label = QLabel(info, self)
        info_label.setGeometry(50, 30, 600, 30)
        info_label.setFont(self.font_14)
        label_of_element = QLabel('', self)
        label_of_element.setGeometry(50, 70, 600, 40)
        label_of_element.setAlignment(Qt.AlignHCenter)
        label_of_reading = QLabel('', self)
        label_of_reading.setGeometry(50, 100, 600, 40)
        label_of_reading.setAlignment(Qt.AlignHCenter)

        lcd_timer = QLCDNumber(self)
        lcd_timer.setGeometry(325, 0, 50, 30)

        class Timer(Thread):
            def __init__(self, duration, lcd_object, end_function):
                super().__init__()
                self.duration = duration
                self.lcd_object = lcd_object
                self.seconds = 0
                self.is_test_alive = True
                self.end_function = end_function

            def run(self):
                while self.duration - self.seconds > 0 and self.is_test_alive:
                    sleep(1)
                    self.seconds += 1
                    seconds_left = self.duration - self.seconds
                    mintes, seconds = seconds_left // 60, seconds_left % 60
                    self.lcd_object.display(f'{mintes}:{seconds}')
                if self.is_test_alive:
                    self.end_function()

        def end_time_function():
            self.can_click = False
            info_label.setText('Время вышло')

        timer = Timer(all_time_to_test, lcd_timer, end_time_function)
        timer.start()
        self.can_click = True

        def create_new_random_elements(elements_list, current_element):
            new_elements_list = deepcopy(elements_list)
            shuffle(new_elements_list)
            current_random_elements = set(new_elements_list)
            current_random_elements.discard(current_element)
            current_random_elements = list(current_random_elements)
            shuffle(current_random_elements)
            current_random_elements = current_random_elements[:3]
            current_random_elements.append(current_element)
            shuffle(current_random_elements)
            return current_random_elements

        def create_check_question(element):
            if type_of_elements == WORDS:
                random_elements_with_current_element = create_new_random_elements(random_elements, element[2])
                correct_element = element[2]
            elif type_of_elements == KATAKANA or type_of_elements == HIRAGANA:
                random_elements_with_current_element = create_new_random_elements(random_elements, element[1])
                correct_element = element[1]
            else:
                random_elements_with_current_element = [create_new_random_elements(random_elements[0], element[1]),
                                                        create_new_random_elements(random_elements[1], element[2]),
                                                        create_new_random_elements(random_elements[2], element[3])]
                correct_element = [element[1], element[2], element[3]]
            label_of_element.setText(element[0])
            if type_of_elements == WORDS:
                label_of_reading.setText(element[1])
            if type_of_elements != KANJI:
                self.checked = False
                first_button = QPushButton('', self)
                first_button.setGeometry(0, 150, 700, 50)
                second_button = QPushButton('', self)
                second_button.setGeometry(0, 210, 700, 50)
                third_button = QPushButton('', self)
                third_button.setGeometry(0, 270, 700, 50)
                fourth_button = QPushButton('', self)
                fourth_button.setGeometry(0, 330, 700, 50)
                ui = [first_button, second_button, third_button, fourth_button]
                self.ui_list.extend(ui)
                self.enable_ui(ui)
                first_button.setText(random_elements_with_current_element[0])
                second_button.setText(random_elements_with_current_element[1])
                third_button.setText(random_elements_with_current_element[2])
                fourth_button.setText(random_elements_with_current_element[3])
                buttons = [first_button, second_button, third_button, fourth_button]
                for button in buttons:
                    button.clicked.connect(lambda: self.check_answer(correct_element, buttons, info_of_mistake_label))
                    button.setFont(self.font_20)
            else:
                self.kanji_mistakes = 0
                self.checked = [False, False, False]
                first_button = QPushButton('', self)
                first_button.setGeometry(0, 150, 233, 50)
                second_button = QPushButton('', self)
                second_button.setGeometry(0, 210, 233, 50)
                third_button = QPushButton('', self)
                third_button.setGeometry(0, 270, 233, 50)
                fourth_button = QPushButton('', self)
                fourth_button.setGeometry(0, 330, 233, 50)
                fifth_button = QPushButton('', self)
                fifth_button.setGeometry(233, 150, 233, 50)
                sixth_button = QPushButton('', self)
                sixth_button.setGeometry(233, 210, 233, 50)
                seventh_button = QPushButton('', self)
                seventh_button.setGeometry(233, 270, 233, 50)
                eighth_button = QPushButton('', self)
                eighth_button.setGeometry(233, 330, 233, 50)
                nineth_button = QPushButton('', self)
                nineth_button.setGeometry(466, 150, 233, 50)
                tenth_button = QPushButton('', self)
                tenth_button.setGeometry(466, 210, 233, 50)
                eleventh_button = QPushButton('', self)
                eleventh_button.setGeometry(466, 270, 233, 50)
                twelveth_button = QPushButton('', self)
                twelveth_button.setGeometry(466, 330, 233, 50)
                ui = [first_button, second_button, third_button, fourth_button,
                      fifth_button, sixth_button, seventh_button, eighth_button,
                      nineth_button, tenth_button, eleventh_button, twelveth_button]
                self.ui_list.extend(ui)
                self.enable_ui(ui)

                first_button.setText(random_elements_with_current_element[0][0])
                second_button.setText(random_elements_with_current_element[0][1])
                third_button.setText(random_elements_with_current_element[0][2])
                fourth_button.setText(random_elements_with_current_element[0][3])
                fifth_button.setText(random_elements_with_current_element[1][0])
                sixth_button.setText(random_elements_with_current_element[1][1])
                seventh_button.setText(random_elements_with_current_element[1][2])
                eighth_button.setText(random_elements_with_current_element[1][3])
                nineth_button.setText(random_elements_with_current_element[2][0])
                tenth_button.setText(random_elements_with_current_element[2][1])
                eleventh_button.setText(random_elements_with_current_element[2][2])
                twelveth_button.setText(random_elements_with_current_element[2][3])
                buttons_group_one = ui[:4]
                buttons_group_two = ui[4:8]
                buttons_group_three = ui[8:]
                buttons = [buttons_group_one, buttons_group_two, buttons_group_three]
                for button in buttons_group_one:
                    button.clicked.connect(
                        lambda: self.check_answer_of_kanji(correct_element, buttons, info_of_mistake_label))
                    button.setFont(self.font_20)
                for button in buttons_group_two:
                    button.clicked.connect(
                        lambda: self.check_answer_of_kanji(correct_element, buttons, info_of_mistake_label))
                    button.setFont(self.font_20)
                for button in buttons_group_three:
                    button.clicked.connect(
                        lambda: self.check_answer_of_kanji(correct_element, buttons, info_of_mistake_label))
                    button.setFont(self.font_20)

        def stop_check():
            self.disable_ui()
            timer.is_test_alive = False
            self.create_normal_main_menu_button()
            result_label = QLabel('', self)
            result_label.setGeometry(50, 50, 600, 40)
            result_label.setFont(self.font_20)
            if self.permissible_mistakes >= 0:
                if is_upgrading_test:
                    self.update_progress(type_of_elements)
                    result_label.setText('Вы прошли тест и открыли новый урок')
                else:
                    result_label.setText('Вы прошли тест')
                continue_learning_button = QPushButton('Начать новый урок', self)
                continue_learning_button.setFont(self.font_20)
                continue_learning_button.setGeometry(50, 200, 600, 40)
                if type_of_elements == HIRAGANA:
                    learn = self.learn_hirigana
                elif type_of_elements == KATAKANA:
                    learn = self.learn_katakana
                elif type_of_elements == KANJI:
                    learn = self.learn_kanji
                else:
                    learn = self.learn_words
                continue_learning_button.clicked.connect(lambda: learn(CONTINUE))
                self.enable_ui([continue_learning_button, result_label])
                self.ui_list.extend([continue_learning_button, result_label])

            else:
                retest_button = QPushButton('Пройти тест заново', self)
                retest_button.setFont(self.font_20)
                retest_button.setGeometry(50, 200, 600, 40)
                words = self.get_words(CONTINUE)
                retest_button.clicked.connect(
                    lambda: self.test_of_learned_elements(type_of_elements, elements, is_upgrading_test))
                self.enable_ui([retest_button, result_label])
                self.ui_list.extend([retest_button, result_label])
                result_label.setText('Вы не прошли тест')

        def continue_check():
            try:
                current_element = next(element)
                if type_of_elements != KANJI:
                    if not self.checked:
                        self.permissible_mistakes -= 1
                else:
                    if not self.checked[0] or not self.checked[1] or not self.checked[2]:
                        self.permissible_mistakes -= 1
                info_of_mistake_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')
                create_check_question(current_element)
            except Exception:
                stop_check()

        continue_button = QPushButton('Продолжить', self)
        continue_button.setGeometry(0, 390, 700, 50)
        continue_button.clicked.connect(continue_check)
        ui = [label_of_element, label_of_reading, continue_button,
              lcd_timer, info_label, info_of_mistake_label]
        for ui_element in ui[:5]:
            ui_element.setFont(self.font_20)
        self.ui_list.extend(ui)
        self.enable_ui(ui)
        element = iter(elements)
        current_element = next(element)
        create_check_question(current_element)

    def create_kana_info(self, type_of_kana):
        self.disable_ui()
        self.create_small_main_menu_button()

        kana_label = QLabel(self)
        kana_label.setGeometry(0, 50, 440, 60)
        kana_label.setFont(self.font_20)
        kana_label.setAlignment(QtCore.Qt.AlignCenter)

        transliteration_reading_label = QLabel(self)
        transliteration_reading_label.setGeometry(0, 160, 440, 60)
        transliteration_reading_label.setFont(self.font_20)
        transliteration_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_kana = QLabel(self)
        info_label_about_kana.setGeometry(0, 10, 440, 30)
        info_label_about_kana.setFont(self.font_14)
        info_label_about_kana.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_kana.setText('Иероглиф')

        info_label_about_read = QLabel(self)
        info_label_about_read.setGeometry(QtCore.QRect(0, 120, 440, 30))
        info_label_about_read.setFont(self.font_14)
        info_label_about_read.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read.setText('Чтение (транслитерация на русский)')

        kana_next_button = QPushButton('Следующий иероглиф', self)
        kana_next_button.clicked.connect(lambda: self.create_kana_info(type_of_kana))
        kana_next_button.setFont(self.font_14)
        kana_next_button.setGeometry(50, 400, 600, 30)

        ui = [kana_label, kana_next_button, info_label_about_kana,
              info_label_about_read, transliteration_reading_label]
        self.ui_list.extend(ui)
        self.enable_ui(ui)
        try:
            if type_of_kana == KATAKANA:
                symbol = next(self.temporary_katakana_symbols)
            else:
                symbol = next(self.temporary_hiragana_symbols)
            writing, reading = symbol
            kana_label.setText(writing)
            transliteration_reading_label.setText(reading)

        except StopIteration:
            self.disable_ui()

            kana_symbols = self.get_kana(type_of_kana, CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(self.font_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(type_of_kana, kana_symbols, True))
            checking_button.setFont(self.font_20)
            ui = [checking_button, return_to_menu_button]
            self.enable_ui(ui)
            self.ui_list.extend(ui)

    def create_kanji_info(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        kanji_label = QLabel(self)
        kanji_label.setGeometry(0, 20, 420, 60)
        kanji_label.setFont(self.font_20)
        kanji_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_image_label = QLabel(self)
        kanji_image_label.setGeometry(441, 50, 240, 240)

        kanji_onyomi_reading_label = QLabel(self)
        kanji_onyomi_reading_label.setGeometry(0, 110, 440, 40)
        kanji_onyomi_reading_label.setFont(self.font_20)
        kanji_onyomi_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_kunyomi_reading_label = QLabel(self)
        kanji_kunyomi_reading_label.setGeometry(0, 180, 440, 40)
        kanji_kunyomi_reading_label.setFont(self.font_20)
        kanji_kunyomi_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_meaning_label = QLabel(self)
        kanji_meaning_label.setGeometry(0, 270, 500, 60)
        kanji_meaning_label.setFont(self.font_20)
        kanji_meaning_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_kanji = QLabel(self)
        info_label_about_kanji.setGeometry(0, 0, 440, 18)
        info_label_about_kanji.setFont(self.font_14)
        info_label_about_kanji.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_kanji.setText('Слово')

        info_label_about_read_onyomi = QLabel(self)
        info_label_about_read_onyomi.setGeometry(QtCore.QRect(0, 90, 440, 18))
        info_label_about_read_onyomi.setFont(self.font_14)
        info_label_about_read_onyomi.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read_onyomi.setText('Чтение (онъёми)')

        info_label_about_read_kunyomi = QLabel(self)
        info_label_about_read_kunyomi.setGeometry(QtCore.QRect(0, 160, 440, 18))
        info_label_about_read_kunyomi.setFont(self.font_14)
        info_label_about_read_kunyomi.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read_kunyomi.setText('Чтение (куннъёми)')

        info_label_about_meaning = QLabel(self)
        info_label_about_meaning.setGeometry(0, 230, 440, 30)
        info_label_about_meaning.setFont(self.font_14)
        info_label_about_meaning.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_meaning.setText('Значение')

        kanji_reading_button = QPushButton(self)
        kanji_reading_button.setGeometry(441, 280, 240, 40)
        kanji_reading_button.setFont(self.font_14)
        kanji_reading_button.setText('Прослушать')

        kanji_next_button = QPushButton('Следующий кандзи', self)
        kanji_next_button.clicked.connect(self.create_kanji_info)
        kanji_next_button.setFont(self.font_14)
        kanji_next_button.setGeometry(50, 400, 600, 30)

        kanji_use_examples_list = QListWidget(self)
        kanji_use_examples_list.setGeometry(50, 330, 600, 60)

        ui = [kanji_use_examples_list, kanji_image_label, kanji_kunyomi_reading_label,
              kanji_onyomi_reading_label, kanji_reading_button, kanji_next_button,
              kanji_label, kanji_meaning_label, info_label_about_kanji,
              info_label_about_meaning, info_label_about_read_onyomi,
              info_label_about_read_kunyomi]
        self.ui_list.extend(ui)
        self.enable_ui(ui)
        try:
            kanji = next(self.temporary_kanji)
            writing, onyomi_reading, kunyomi_reading, meaning, examples, way_to_image, way_to_sound = kanji
            if way_to_image:
                pixmap = QPixmap(way_to_image)
                kanji_image_label.setPixmap(pixmap)
            if way_to_sound:
                kanji_reading_button.clicked.connect(lambda: self.listen(way_to_sound))
            else:
                kanji_reading_button.setText('Нет звукового файла')
            if examples:
                try:
                    for example in examples.split(','):
                        kanji_use_examples_list.addItem(QListWidgetItem(f'{example}'))
                except Exception:
                    pass
            kanji_label.setText(writing)
            kanji_onyomi_reading_label.setText(onyomi_reading)
            kanji_kunyomi_reading_label.setText(kunyomi_reading)
            kanji_meaning_label.setText(meaning)

        except StopIteration:
            self.disable_ui()

            kanji = self.get_kanji(CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(self.font_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(KANJI, kanji, True))
            checking_button.setFont(self.font_20)
            ui = [checking_button, return_to_menu_button]
            self.enable_ui(ui)
            self.ui_list.extend(ui)

    def create_word_info(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        word_label = QLabel(self)
        word_label.setGeometry(0, 50, 420, 60)
        word_label.setFont(self.font_20)
        word_label.setAlignment(QtCore.Qt.AlignCenter)

        word_image_label = QLabel(self)
        word_image_label.setGeometry(441, 50, 240, 240)

        word_hiragana_reading_label = QLabel(self)
        word_hiragana_reading_label.setGeometry(0, 160, 440, 60)
        word_hiragana_reading_label.setFont(self.font_20)
        word_hiragana_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        word_meaning_label = QLabel(self)
        word_meaning_label.setGeometry(20, 270, 660, 60)
        word_meaning_label.setFont(self.font_20)
        word_meaning_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_word = QLabel(self)
        info_label_about_word.setGeometry(0, 10, 440, 30)
        info_label_about_word.setFont(self.font_14)
        info_label_about_word.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_word.setText('Слово')

        info_label_about_read = QLabel(self)
        info_label_about_read.setGeometry(QtCore.QRect(0, 120, 440, 30))
        info_label_about_read.setFont(self.font_14)
        info_label_about_read.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read.setText('Чтение (кана)')

        info_label_about_meaning = QLabel(self)
        info_label_about_meaning.setGeometry(0, 230, 440, 30)
        info_label_about_meaning.setFont(self.font_14)
        info_label_about_meaning.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_meaning.setText('Значение')

        word_reading_button = QPushButton(self)
        word_reading_button.setGeometry(441, 340, 240, 40)
        word_reading_button.setFont(self.font_14)
        word_reading_button.setText('Прослушать')

        word_next_button = QPushButton('Следующее слово', self)
        word_next_button.clicked.connect(self.create_word_info)
        word_next_button.setFont(self.font_14)
        word_next_button.setGeometry(50, 400, 600, 30)

        ui = [word_image_label, word_reading_button,
              word_label, word_hiragana_reading_label,
              word_meaning_label, info_label_about_meaning,
              info_label_about_read, info_label_about_word,
              word_next_button]
        self.ui_list.extend(ui)
        self.enable_ui(ui)
        try:
            word = next(self.temporary_words)
            writing, reading, meaning, way_to_image, way_to_sound = word
            if way_to_image:
                pixmap = QPixmap(way_to_image)
                word_image_label.setPixmap(pixmap)
            if way_to_sound:
                word_reading_button.clicked.connect(lambda: self.listen(way_to_sound))
            else:
                word_reading_button.setText('Нет звукового файла')
            word_label.setText(writing)
            word_hiragana_reading_label.setText(reading)
            word_meaning_label.setText(meaning)

        except StopIteration:
            self.disable_ui()

            words = self.get_words(CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(self.font_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(WORDS, words, True))
            checking_button.setFont(self.font_20)
            ui = [checking_button, return_to_menu_button]
            self.enable_ui(ui)
            self.ui_list.extend(ui)

    def view_learned(self, type_of_learned, ui_list):
        self.disable_ui()
        self.create_small_main_menu_button()

        cursor = self.database.cursor()
        max_lesson_number = cursor.execute(f"""SELECT value FROM Saves
        WHERE title_of_save = '{type_of_learned}'""").fetchall()[0][0]
        end_id = COUNT_OF_LEARNING * (max_lesson_number - 1)
        cursor = self.database.cursor()
        elements = cursor.execute(f"""SELECT writing FROM {type_of_learned}
        WHERE id <= {end_id}""").fetchall()
        list_widget = QListWidget(self)
        list_widget.setGeometry(0, 0, 700, 380)
        for element in elements:
            list_widget.addItem(QListWidgetItem(f'{element[0]}'))
        return_button = QPushButton('Вернуться к выбору', self)
        self.ui_list.extend([return_button, list_widget])

        def return_to_learn_menu(ui_list):
            self.disable_ui()
            self.enable_ui(ui_list)

        return_button.setGeometry(50, 400, 600, 50)
        return_button.setFont(self.font_14)
        return_button.clicked.connect(lambda: return_to_learn_menu(ui_list))
        self.enable_ui([return_button, list_widget])

    def learn_menu(self, type_learn):
        self.disable_ui()
        self.create_small_main_menu_button()

        if type_learn == HIRAGANA:
            learn = self.learn_hirigana
        elif type_learn == KATAKANA:
            learn = self.learn_katakana
        elif type_learn == KANJI:
            learn = self.learn_kanji
        else:
            learn = self.learn_words
        continue_learn_button = QPushButton('Продолжить', self)
        continue_learn_button.setGeometry(100, 40, 500, 50)
        continue_learn_button.clicked.connect(lambda: learn(CONTINUE))

        def get_lesson(number_of_lesson_obj, function_of_learn, type_of_learn):
            number_of_lesson = number_of_lesson_obj.value()
            function_of_learn(type_of_learn, number_of_lesson)

        number_of_lesson_obj = QSpinBox(self)
        number_of_lesson_obj.setGeometry(610, 140, 30, 50)
        number_of_lesson_obj.setMinimum(1)
        cursor = self.database.cursor()
        maximum = cursor.execute(f"""SELECT value FROM Saves
        WHERE title_of_save = '{type_learn}'""").fetchall()[0][0]
        number_of_lesson_obj.setMaximum(maximum)
        past_learn_button = QPushButton('Повторить предыдущую часть', self)
        past_learn_button.setGeometry(100, 140, 500, 50)
        past_learn_button.clicked.connect(lambda: get_lesson(number_of_lesson_obj, learn, NUMERABLE))
        new_learn_button = QPushButton('Начать сначала (сбросит все сохраненные данные в этом разделе)', self)
        new_learn_button.setGeometry(100, 240, 500, 50)
        new_learn_button.clicked.connect(lambda: learn(NEW))
        view_learned_words = QPushButton('Посмотреть изученное', self)
        view_learned_words.setGeometry(100, 340, 500, 50)
        ui = [continue_learn_button, past_learn_button, new_learn_button,
              number_of_lesson_obj, view_learned_words]
        view_learned_words.clicked.connect(lambda: self.view_learned(type_learn, ui))

        self.enable_ui(ui)
        self.ui_list.extend(ui)

    def create_main_types_of_learning_button_with_function(self, function):
        hiragana_button = QPushButton('Хирагана', self)
        hiragana_button.setGeometry(50, 50, 600, 40)
        hiragana_button.clicked.connect(lambda: function(HIRAGANA))
        katakana_button = QPushButton('Катакана', self)
        katakana_button.setGeometry(50, 130, 600, 40)
        katakana_button.clicked.connect(lambda: function(KATAKANA))
        kanji_button = QPushButton('Кандзи', self)
        kanji_button.setGeometry(50, 210, 600, 40)
        kanji_button.clicked.connect(lambda: function(KANJI))
        words_button = QPushButton('Слова', self)
        words_button.setGeometry(50, 290, 600, 40)
        words_button.clicked.connect(lambda: function(WORDS))
        ui = [hiragana_button, katakana_button,
              kanji_button, words_button]
        self.ui_list.extend(ui)
        self.enable_ui(ui)

    def start_learn(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        self.create_main_types_of_learning_button_with_function(self.learn_menu)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProgramLearnJapaneseLanguage()
    ex.show()
    sys.exit(app.exec_())
