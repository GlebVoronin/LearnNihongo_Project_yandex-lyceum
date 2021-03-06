import logging
import os
from shutil import copy2
import winsound

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from werkzeug.security import check_password_hash

import data.register
import data.test
from data import db_session
from data.consts import *
from data.models.users import User
from data.style import *


class ProgramLearnJapaneseLanguage(QMainWindow):
    def __init__(self):
        super().__init__()
        db_session.global_init(f'db/{DB_FILE_NAME}')
        self.temporary_files = {'sound': None, 'image': None}
        self.current_user = None
        self.path = os.getcwd()  # Путь к текущей папке программы
        self.ui_list = []
        self.setupUi()
        self.login_menu()
        self.set_style_and_show_all()

    def setupUi(self):
        self.resize(700, 450)
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        start_learn_button = QPushButton("Обучение", self)
        start_learn_button.setGeometry(25, 58, 650, 40)
        start_learn_button.setFont(FONT_14)
        start_learn_button.clicked.connect(self.start_learn)
        start_checking_button = QPushButton("Тест", self)
        start_checking_button.setGeometry(25, 156, 650, 40)
        start_checking_button.setFont(FONT_14)
        start_checking_button.clicked.connect(self.checking)
        setup_button = QPushButton("Настройка", self)
        setup_button.setGeometry(25, 254, 650, 40)
        setup_button.setFont(FONT_14)
        setup_button.clicked.connect(self.open_setup_menu)
        answer_button = QPushButton("Справка", self)
        answer_button.setGeometry(25, 352, 650, 40)
        answer_button.setFont(FONT_14)
        answer_button.clicked.connect(self.answer_of_users_questions)
        self.ui_list.extend(
            [start_checking_button, start_learn_button, answer_button, setup_button]
        )

    def get_lesson_elements_by_type(self, elements_type, lesson_type=CONTINUE, lesson_number=1):
        """
        Данная функция принимает в качестве аргументов: тип элемента и
        продолжение обучения
        Если тип обучения не был указан, то будет выбран 1 урок.
        Функция возвращат список объектов модели указанного элемента
        Например:
        result = get_lesson_elements_by_type(HIRAGANA, CONTINUE)
        result == [Hiragana, Hiragana ...Hiragana]
        result[0] == Hiragana(id=1, title='あ', reading='А')
        result[7] == Hiragana(id=7, title='ま', reading='Ма')
        """

        # получение номера последнего урока, 1-й урок по умолчанию
        last_lesson = getattr(self.current_user, f'{elements_type}_save', 1)
        if lesson_type == CONTINUE:  # продолжить с последнего
            start_id = COUNT_OF_LEARNING * (last_lesson - 1) + 1
        elif lesson_type == NUMERABLE:  # выбранный урок
            start_id = COUNT_OF_LEARNING * (lesson_number - 1) + 1
        else:  # все уроки, с самого начала
            start_id = 1
        if lesson_type == CONTINUE:  # текущий конец
            end_id = COUNT_OF_LEARNING * last_lesson
        elif lesson_type == NUMERABLE:  # конец в выбранном уроке
            end_id = COUNT_OF_LEARNING * lesson_number
        else:  # lesson_type == HARD  все уроки
            end_id = float('inf')
        class_of_element = CLASSES_BY_TYPES_OF_ELEMENTS.get(elements_type, None)
        if not class_of_element:
            return logging.error('Type of element not found in classes list')
        session = db_session.create_session()
        elements = session.query(class_of_element).filter(
            class_of_element.id >= start_id, class_of_element.id <= end_id).all()
        if not isinstance(elements, list):
            elements = [elements]  # type(elements) == 'list'
        return elements

    def create_small_main_menu_button(self):
        return_button = QPushButton('Меню', self)
        return_button.setGeometry(660, 0, 40, 40)
        return_button.clicked.connect(self.return_to_start_menu)
        self.ui_list.append(return_button)

    def return_to_start_menu(self):
        self.disable_ui()
        self.setupUi()
        self.set_style_and_show_all()

    def disable_ui(self):
        for ui_item in self.ui_list:
            ui_item.setParent(None)
            del ui_item

    def set_style_and_show_all(self):
        for ui_object in self.children():
            if hasattr(ui_object, 'setStyleSheet'):
                if isinstance(ui_object, QPushButton):
                    set_color(ui_object, MAIN_COLORS['main_button'])
                else:
                    set_color(ui_object, MAIN_COLORS['menu'])
            if hasattr(ui_object, 'show'):
                ui_object.show()

    def answer_of_users_questions(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        answer_label = QLabel(self)
        answer_label.setAlignment(Qt.AlignTop)
        answer_label.setGeometry(25, 25, 630, 430)
        # добавить пункт о регистрации!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
        self.set_style_and_show_all()

    def login_menu(self):
        self.hide()
        register = data.register.LoginRegisterMenu(self)
        register.show()
        self.show()

    def checking(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        self.create_main_types_of_learning_button_with_function(self.menu_of_checking)
        self.set_style_and_show_all()

    def menu_of_checking(self, type_of_checking):
        self.disable_ui()
        self.create_small_main_menu_button()
        continue_test_button = QPushButton('Пройти тест по последнему уроку', self)
        continue_test_button.setGeometry(100, 40, 500, 50)
        continue_test_button.clicked.connect(
            lambda: self.start_test_by_type(type_of_checking, CONTINUE)
        )
        number_of_lesson_obj = QSpinBox(self)
        number_of_lesson_obj.setGeometry(610, 140, 30, 50)
        number_of_lesson_obj.setMinimum(1)
        maximum = getattr(self.current_user, f'{type_of_checking}_save', 1)
        number_of_lesson_obj.setMaximum(maximum)

        past_test_button = QPushButton('Пройти тест по предыдущим урокам', self)
        past_test_button.setGeometry(100, 140, 500, 50)
        past_test_button.clicked.connect(
            lambda: self.start_test_by_type(type_of_checking, number_of_lesson_obj.value(), NUMERABLE)
        )
        hard_test_button = QPushButton('Начать тест по всему изученному в данном разделе', self)
        hard_test_button.setGeometry(100, 240, 500, 50)
        hard_test_button.clicked.connect(
            lambda: self.start_test_by_type(type_of_checking, HARD))
        view_learned_words = QPushButton('Посмотреть изученное', self)
        view_learned_words.setGeometry(100, 340, 500, 50)
        ui = [continue_test_button, past_test_button, hard_test_button,
              number_of_lesson_obj, view_learned_words]
        view_learned_words.clicked.connect(
            lambda: self.view_learned(type_of_checking))
        self.ui_list.extend(ui)
        self.set_style_and_show_all()

    def start_test_by_type(self, checking_type, lesson_type, lesson_number=1):
        """Метод передаёт необходимые параметры в процесс тестирования
        (возможно этот метод не нужен)"""
        if self.current_user and (checking_type == HARD or checking_type == CONTINUE):
            is_upgrading_test = True
        else:
            is_upgrading_test = False
        test_elements = self.get_lesson_elements_by_type(checking_type, lesson_type, lesson_number)
        self.test_of_learned_elements(checking_type, test_elements, is_upgrading_test)

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
            copy2(way, new_image_way)  # копирование без удаления исходного файла
            return new_image_way
        else:
            new_sound_way = f'images_and_sounds\\{type_symb}\\{writing}\\sound.{file_format}'
            copy2(way, new_sound_way)  # копирование без удаления исходного файла
            return new_sound_way

    def save_new_kanji(self):
        writing = self.line_edit_of_writing.text()
        onyomi_reading = self.line_edit_of_onyomi_reading.text()
        kunyomi_reading = self.line_edit_of_kunyomi_reading.text()
        meaning = self.line_edit_of_meaning.text()
        path_to_image = self.temporary_files.get('image', '')
        path_to_sound = self.temporary_files.get('sound', '')
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
        self.set_style_and_show_all()

    def learn(self, element_type, lesson_type, lesson_number=1):
        info_methods = {
            HIRAGANA: lambda: self.create_kana_info(HIRAGANA),
            KATAKANA: lambda: self.create_kana_info(KATAKANA),
            KANJI: lambda: self.create_kanji_info(),
            WORD: lambda: self.create_word_info()
        }
        elements = self.get_lesson_elements_by_type(element_type, lesson_type, lesson_number)
        self.temporary_elements_for_learn = iter(elements)
        learning_method = info_methods.get(element_type)
        learning_method()

    def open_setup_menu(self):
        """Доработать!!!!!!!!!!!!!"""
        self.disable_ui()
        self.create_small_main_menu_button()

        add_word_button = QPushButton('Добавить новое слово в программу', self)
        add_word_button.setGeometry(50, 50, 600, 40)
        add_word_button.clicked.connect(self.add_word)
        add_kanji_button = QPushButton('Добавить новый кандзи в программу', self)
        add_kanji_button.setGeometry(50, 150, 600, 40)
        add_kanji_button.clicked.connect(self.add_kanji)
        self.ui_list.extend([add_kanji_button, add_word_button])
        self.set_style_and_show_all()

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
            sound_label.setFont(FONT_14)

    def listen(self, way_to_sound):
        """возможно не работает//////////////////////"""
        winsound.PlaySound(way_to_sound, winsound.SND_FILENAME)

    def save_new_word(self):
        writing = self.line_edit_of_writing.text()
        reading = self.line_edit_of_reading.text()
        meaning = self.line_edit_of_meaning.text()
        path_to_image = self.temporary_files.get('image', '')
        path_to_sound = self.temporary_files.get('sound', '')
        if path_to_image:
            path_to_image = self.save_images_or_sounds(writing, path_to_image, WORD, IMAGE)
        if path_to_sound:
            path_to_sound = self.save_images_or_sounds(writing, path_to_sound, WORD, SOUND)
        session = db_session.create_session()
        word = Word(
            writing=writing,
            reading=reading,
            meaning=meaning,
            path_to_image=path_to_image,
            path_to_sound=path_to_sound
        )
        session.add(word)
        session.commit()
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
        self.set_style_and_show_all()

    def load_user(self, login, password, hashed=False):
        session = db_session.create_session()
        if not hashed:
            user = session.query(User).filter(
                User.login == login,
                check_password_hash(User.password_hash, password)).first()
        else:
            user = session.query(User).filter(
                User.login == login,
                User.password_hash == password).first()
        self.current_user = user

    def test_of_learned_elements(self, element_type, elements, is_upgrading_test=False):
        self.hide()
        user = self.current_user
        test = data.test.Test(element_type, elements, is_upgrading_test, user, self)
        test.show()
        self.show()

    def create_kana_info(self, type_of_kana):
        self.disable_ui()
        self.create_small_main_menu_button()

        kana_label = QLabel(self)
        kana_label.setGeometry(0, 50, 440, 60)
        kana_label.setFont(FONT_20)
        kana_label.setAlignment(QtCore.Qt.AlignCenter)

        transliteration_reading_label = QLabel(self)
        transliteration_reading_label.setGeometry(0, 160, 440, 60)
        transliteration_reading_label.setFont(FONT_20)
        transliteration_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_kana = QLabel(self)
        info_label_about_kana.setGeometry(0, 10, 440, 30)
        info_label_about_kana.setFont(FONT_14)
        info_label_about_kana.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_kana.setText('Иероглиф')

        info_label_about_read = QLabel(self)
        info_label_about_read.setGeometry(QtCore.QRect(0, 120, 440, 30))
        info_label_about_read.setFont(FONT_14)
        info_label_about_read.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read.setText('Чтение (транслитерация на русский)')

        kana_next_button = QPushButton('Следующий иероглиф', self)
        kana_next_button.clicked.connect(lambda: self.create_kana_info(type_of_kana))
        kana_next_button.setFont(FONT_14)
        kana_next_button.setGeometry(50, 400, 600, 30)

        ui = [kana_label, kana_next_button, info_label_about_kana,
              info_label_about_read, transliteration_reading_label]
        self.ui_list.extend(ui)
        self.set_style_and_show_all()
        try:
            symbol = next(self.temporary_elements_for_learn)
            kana_label.setText(symbol.title)
            transliteration_reading_label.setText(symbol.reading)

        except StopIteration:
            self.disable_ui()

            kana_symbols = self.get_lesson_elements_by_type(type_of_kana, CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(FONT_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(type_of_kana, kana_symbols, True))
            checking_button.setFont(FONT_20)
            ui = [checking_button, return_to_menu_button]
            self.ui_list.extend(ui)
            self.set_style_and_show_all()

    def create_kanji_info(self):
        self.disable_ui()
        self.create_small_main_menu_button()

        kanji_label = QLabel(self)
        kanji_label.setGeometry(0, 20, 420, 60)
        kanji_label.setFont(FONT_20)
        kanji_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_image_label = QLabel(self)
        kanji_image_label.setGeometry(441, 50, 240, 240)

        kanji_onyomi_reading_label = QLabel(self)
        kanji_onyomi_reading_label.setGeometry(0, 110, 440, 40)
        kanji_onyomi_reading_label.setFont(FONT_20)
        kanji_onyomi_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_kunyomi_reading_label = QLabel(self)
        kanji_kunyomi_reading_label.setGeometry(0, 180, 440, 40)
        kanji_kunyomi_reading_label.setFont(FONT_20)
        kanji_kunyomi_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        kanji_meaning_label = QLabel(self)
        kanji_meaning_label.setGeometry(0, 270, 500, 60)
        kanji_meaning_label.setFont(FONT_20)
        kanji_meaning_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_kanji = QLabel(self)
        info_label_about_kanji.setGeometry(0, 0, 440, 18)
        info_label_about_kanji.setFont(FONT_14)
        info_label_about_kanji.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_kanji.setText('Слово')

        info_label_about_read_onyomi = QLabel(self)
        info_label_about_read_onyomi.setGeometry(QtCore.QRect(0, 90, 440, 18))
        info_label_about_read_onyomi.setFont(FONT_14)
        info_label_about_read_onyomi.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read_onyomi.setText('Чтение (онъёми)')

        info_label_about_read_kunyomi = QLabel(self)
        info_label_about_read_kunyomi.setGeometry(QtCore.QRect(0, 160, 440, 18))
        info_label_about_read_kunyomi.setFont(FONT_14)
        info_label_about_read_kunyomi.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read_kunyomi.setText('Чтение (куннъёми)')

        info_label_about_meaning = QLabel(self)
        info_label_about_meaning.setGeometry(0, 230, 440, 30)
        info_label_about_meaning.setFont(FONT_14)
        info_label_about_meaning.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_meaning.setText('Значение')

        kanji_reading_button = QPushButton(self)
        kanji_reading_button.setGeometry(441, 280, 240, 40)
        kanji_reading_button.setFont(FONT_14)
        kanji_reading_button.setText('Прослушать')

        kanji_next_button = QPushButton('Следующий кандзи', self)
        kanji_next_button.clicked.connect(self.create_kanji_info)
        kanji_next_button.setFont(FONT_14)
        kanji_next_button.setGeometry(50, 400, 600, 30)

        kanji_use_examples_list = QListWidget(self)
        kanji_use_examples_list.setGeometry(50, 330, 600, 60)

        ui = [kanji_use_examples_list, kanji_image_label, kanji_kunyomi_reading_label,
              kanji_onyomi_reading_label, kanji_reading_button, kanji_next_button,
              kanji_label, kanji_meaning_label, info_label_about_kanji,
              info_label_about_meaning, info_label_about_read_onyomi,
              info_label_about_read_kunyomi]
        self.ui_list.extend(ui)
        self.set_style_and_show_all()
        try:
            kanji = next(self.temporary_elements_for_learn)
            if kanji.path_to_image:
                pixmap = QPixmap(kanji.path_to_image)
                kanji_image_label.setPixmap(pixmap)
            if kanji.path_to_sound:
                kanji_reading_button.clicked.connect(lambda: self.listen(kanji.path_to_sound))
            else:
                kanji_reading_button.setText('Нет звукового файла')
            if kanji.examples:
                try:
                    for example in kanji.examples.split(','):
                        kanji_use_examples_list.addItem(QListWidgetItem(f'{example}'))
                except Exception:
                    pass
            kanji_label.setText(kanji.title)
            kanji_onyomi_reading_label.setText(kanji.onyomi_reading)
            kanji_kunyomi_reading_label.setText(kanji.kunyomi_reading)
            kanji_meaning_label.setText(kanji.meaning)
        except StopIteration:
            self.disable_ui()

            kanji = self.get_lesson_elements_by_type(KANJI, CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(FONT_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(KANJI, kanji, True))
            checking_button.setFont(FONT_20)
            ui = [checking_button, return_to_menu_button]
            self.ui_list.extend(ui)
            self.set_style_and_show_all()

    def create_word_info(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        word_label = QLabel(self)
        word_label.setGeometry(0, 50, 420, 60)
        word_label.setFont(FONT_20)
        word_label.setAlignment(QtCore.Qt.AlignCenter)

        word_image_label = QLabel(self)
        word_image_label.setGeometry(441, 50, 240, 240)

        word_hiragana_reading_label = QLabel(self)
        word_hiragana_reading_label.setGeometry(0, 160, 440, 60)
        word_hiragana_reading_label.setFont(FONT_20)
        word_hiragana_reading_label.setAlignment(QtCore.Qt.AlignCenter)

        word_meaning_label = QLabel(self)
        word_meaning_label.setGeometry(20, 270, 660, 60)
        word_meaning_label.setFont(FONT_20)
        word_meaning_label.setAlignment(QtCore.Qt.AlignCenter)

        info_label_about_word = QLabel(self)
        info_label_about_word.setGeometry(0, 10, 440, 30)
        info_label_about_word.setFont(FONT_14)
        info_label_about_word.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_word.setText('Слово')

        info_label_about_read = QLabel(self)
        info_label_about_read.setGeometry(QtCore.QRect(0, 120, 440, 30))
        info_label_about_read.setFont(FONT_14)
        info_label_about_read.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_read.setText('Чтение (кана)')

        info_label_about_meaning = QLabel(self)
        info_label_about_meaning.setGeometry(0, 230, 440, 30)
        info_label_about_meaning.setFont(FONT_14)
        info_label_about_meaning.setAlignment(QtCore.Qt.AlignCenter)
        info_label_about_meaning.setText('Значение')

        word_reading_button = QPushButton(self)
        word_reading_button.setGeometry(441, 340, 240, 40)
        word_reading_button.setFont(FONT_14)
        word_reading_button.setText('Прослушать')

        word_next_button = QPushButton('Следующее слово', self)
        word_next_button.clicked.connect(self.create_word_info)
        word_next_button.setFont(FONT_14)
        word_next_button.setGeometry(50, 400, 600, 30)

        ui = [word_image_label, word_reading_button,
              word_label, word_hiragana_reading_label,
              word_meaning_label, info_label_about_meaning,
              info_label_about_read, info_label_about_word,
              word_next_button]
        self.ui_list.extend(ui)
        self.set_style_and_show_all()
        try:
            word = next(self.temporary_elements_for_learn)
            if word.path_to_image:
                pixmap = QPixmap(word.path_to_image)
                word_image_label.setPixmap(pixmap)
            if word.path_to_sound:
                word_reading_button.clicked.connect(lambda: self.listen(word.path_to_sound))
            else:
                word_reading_button.setText('Нет звукового файла')
            word_label.setText(word.title)
            word_hiragana_reading_label.setText(word.reading)
            word_meaning_label.setText(word.meaning)

        except StopIteration:
            self.disable_ui()

            words = self.get_lesson_elements_by_type(WORD, CONTINUE)
            return_to_menu_button = QPushButton('Вернуться в исходное меню', self)
            return_to_menu_button.setGeometry(50, 100, 600, 50)
            return_to_menu_button.clicked.connect(self.return_to_start_menu)
            return_to_menu_button.setFont(FONT_20)

            checking_button = QPushButton('Пройти тест', self)
            checking_button.setGeometry(50, 100, 600, 50)
            checking_button.clicked.connect(lambda: self.test_of_learned_elements(WORD, words, True))
            checking_button.setFont(FONT_20)
            ui = [checking_button, return_to_menu_button]
            self.ui_list.extend(ui)
            self.set_style_and_show_all()

    def view_learned(self, learn_type):
        self.disable_ui()
        self.create_small_main_menu_button()

        elements = self.get_lesson_elements_by_type(learn_type, lesson_type=HARD)
        list_widget = QListWidget(self)
        list_widget.setGeometry(0, 0, 700, 380)
        for element in elements:
            list_widget.addItem(QListWidgetItem(f'{element.title}'))
        return_button = QPushButton('Вернуться к выбору', self)
        return_button.setGeometry(50, 400, 600, 50)
        return_button.setFont(FONT_14)
        return_button.clicked.connect(lambda: self.learn_menu(learn_type))
        self.ui_list.extend([return_button, list_widget])
        self.set_style_and_show_all()

    def learn_menu(self, learn_type):
        self.disable_ui()
        self.create_small_main_menu_button()
        continue_learn_button = QPushButton('Продолжить', self)
        continue_learn_button.setGeometry(100, 40, 500, 50)
        continue_learn_button.clicked.connect(lambda: self.learn(learn_type, CONTINUE))
        number_of_lesson_obj = QSpinBox(self)
        number_of_lesson_obj.setGeometry(610, 140, 30, 50)
        number_of_lesson_obj.setMinimum(1)
        maximum = getattr(self.current_user, f'{learn_type}_save', 1)
        number_of_lesson_obj.setMaximum(maximum)
        past_learn_button = QPushButton('Повторить предыдущую часть', self)
        past_learn_button.setGeometry(100, 140, 500, 50)
        past_learn_button.clicked.connect(
            lambda: self.learn(learn_type, NUMERABLE, number_of_lesson_obj.value())
        )
        view_learned_words = QPushButton('Посмотреть изученное', self)
        view_learned_words.setGeometry(100, 340, 500, 50)
        ui = [continue_learn_button, past_learn_button,
              number_of_lesson_obj, view_learned_words]
        view_learned_words.clicked.connect(lambda: self.view_learned(learn_type))
        self.ui_list.extend(ui)
        self.set_style_and_show_all()

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
        words_button.clicked.connect(lambda: function(WORD))
        ui = [hiragana_button, katakana_button,
              kanji_button, words_button]
        self.ui_list.extend(ui)

    def start_learn(self):
        self.disable_ui()
        self.create_small_main_menu_button()
        self.create_main_types_of_learning_button_with_function(self.learn_menu)
        self.set_style_and_show_all()
