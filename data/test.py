from random import shuffle, sample

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from data import db_session
from data.consts import *
from data.models.users import User
from data.style import *
from data.timer import Timer


class Test(QMainWindow):
    def __init__(self, element_type, elements, is_upgrading, user, parent):
        super().__init__(parent, Qt.Window)
        shuffle(elements)
        self.element_type = element_type
        self.elements = elements
        self.question_index = -1
        self.parent_widget = parent
        self.user = user
        self.one_element_time = TIME_FOR_ONE_ELEMENT[element_type]
        self.all_time = self.one_element_time * len(self.elements)
        self.upgrade = is_upgrading
        # количество допустимых ошибок = кол-во элементов * 1 % * число процентов
        self.permissible_mistakes = int(len(elements) * 0.01 * ERROR_PERCENT_FOR_TEST)
        self.can_click = True
        self.checked = False if element_type != KANJI else [False, False, False]
        if element_type == KANJI:
            self.kanji_mistakes = 0
        self.buttons = []
        self.ui_list = []
        self.setupUi()
        self.continue_test()  # запуск теста

    def disable_ui(self):
        for ui_item in self.ui_list:
            ui_item.setParent(None)
        self.ui_list = []
        for button in self.buttons:
            button.setParent(None)
        self.buttons = []

    def set_style_and_show_all(self):
        for ui_object in self.children():
            if hasattr(ui_object, 'setStyleSheet'):
                if isinstance(ui_object, QPushButton):
                    set_color(ui_object, MAIN_COLORS['main_button'])
                else:
                    set_color(ui_object, MAIN_COLORS['menu'])
            if hasattr(ui_object, 'show'):
                ui_object.show()

    def setupUi(self):
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.resize(700, 450)
        self.mistakes_left_label = QLabel(f'Прав на ошибку осталось: {self.permissible_mistakes}', self)
        self.mistakes_left_label.setGeometry(390, 0, 300, 30)
        self.mistakes_left_label.setFont(FONT_14)
        self.questions_left_label = QLabel(f'Вопросов осталось: {len(self.elements) - self.question_index}', self)
        self.questions_left_label.setGeometry(0, 0, 300, 30)
        self.questions_left_label.setFont(FONT_14)
        info = f'Вам необходимо пройти тест не более чем за {self.all_time} секунд'
        self.info_label = QLabel(info, self)
        self.info_label.setGeometry(50, 30, 600, 30)
        self.info_label.setFont(FONT_14)
        self.menu_button = QPushButton('Меню', self)
        self.menu_button.setGeometry(660, 0, 40, 40)
        self.menu_button.clicked.connect(lambda: self.stop_test(prematurely=True))
        self.label_of_element = QLabel('', self)
        self.label_of_element.setGeometry(50, 70, 600, 40)
        self.label_of_element.setAlignment(Qt.AlignHCenter)
        self.label_of_element.setFont(FONT_20)
        self.label_of_reading = QLabel('', self)
        self.label_of_reading.setGeometry(50, 100, 600, 40)
        self.label_of_reading.setAlignment(Qt.AlignHCenter)
        self.label_of_reading.setFont(FONT_20)
        self.continue_button = QPushButton('Продолжить', self)
        self.continue_button.setGeometry(0, 390, 700, 50)
        self.continue_button.clicked.connect(self.continue_test)
        lcd_timer = QLCDNumber(self)
        lcd_timer.setGeometry(325, 0, 50, 30)
        self.timer = Timer(self.all_time, lcd_timer, self)
        self.timer.start()
        self.ui_list.extend([self.mistakes_left_label, self.info_label,
                             self.label_of_reading, self.label_of_element,
                             self.continue_button, self.menu_button,
                             self.questions_left_label, lcd_timer])

    def create_buttons(self):
        for button in self.buttons:
            button.setParent(None)
        self.buttons = []
        if self.element_type != KANJI:
            y = 150
            for index in range(4):
                button = QPushButton('', self)
                button.setGeometry(0, y, 700, 50)
                button.setFont(FONT_17)
                y += 60
                self.buttons.append(button)
        else:
            y = 150
            x = 0
            for index in range(12):
                button = QPushButton('', self)
                button.setGeometry(x, y, 232, 50)
                button.setFont(FONT_17)
                button.level = index // 4
                y += 60
                self.buttons.append(button)
                if index % 4 == 3:
                    x += 233
                    y = 150

    @staticmethod
    def select_elements_for_question(elements, current_element):
        """
        elements: list
        current_element: (Hiragana, Katakana, Kanji или Word
        Возвращает список (list) из 4-х элементов, включая current_element,
        являющимся правильным ответом на тест
        """
        temporary = set(elements)
        temporary.discard(current_element)
        temporary = list(temporary)
        wrong_elements = sample(temporary, 3)
        result = (wrong_elements + [current_element])
        shuffle(result)
        return result

    def create_question(self, current_element):
        self.create_buttons()
        self.checked = False if self.element_type != KANJI else [False, False, False]
        self.label_of_element.setText(current_element.title)
        if self.element_type == WORD:
            self.label_of_reading.setText(current_element.reading)

        question_elements = self.select_elements_for_question(self.elements, current_element)
        if self.element_type != KANJI:
            for index, button in enumerate(self.buttons):
                if self.element_type == WORD:
                    button.setText(question_elements[index].meaning)
                else:
                    button.setText(question_elements[index].reading)
                button.clicked.connect(
                    lambda: self.check_answer(current_element, self.buttons))
        else:
            self.kanji_mistakes = 0
            onyomi_readings = set(kanji.onyomi_reading for kanji in question_elements)
            kunyomi_readings = set(kanji.kunyomi_reading for kanji in question_elements)
            meanings = set(kanji.meaning for kanji in question_elements)
            for index, button in enumerate(self.buttons):
                if index < 4:
                    button.setText(onyomi_readings.pop())
                elif index < 8:
                    button.setText(kunyomi_readings.pop())
                else:
                    button.setText(meanings.pop())
                button.clicked.connect(
                    lambda: self.check_answer_of_kanji(current_element, self.buttons))

    def stop_test(self, timer=False, prematurely=False):
        if prematurely:
            self.setParent(None)
        self.timer.end()
        self.disable_ui()
        result_label = QLabel('', self)
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setGeometry(50, 50, 600, 40)
        result_label.setFont(FONT_20)
        if self.permissible_mistakes >= 0 and not timer:
            if self.upgrade:
                self.update_progress(self.element_type, self.user)
                result_label.setText('Вы прошли тест и открыли новый урок')
            else:
                result_label.setText('Вы прошли тест')
        elif timer:
            result_label.setText('Ваше время истекло')
        else:
            retest_button = QPushButton('Пройти тест заново', self)
            retest_button.setFont(FONT_20)
            retest_button.setGeometry(50, 200, 600, 40)
            retest_button.clicked.connect(self.reset)
            result_label.setText('Вы не прошли тест')
        continue_button = QPushButton('Продолжить', self)
        continue_button.setFont(FONT_20)
        continue_button.setGeometry(50, 400, 600, 40)
        continue_button.clicked.connect(self.destroy)
        self.set_style_and_show_all()

    def reset(self):
        self.__init__(self.element_type, self.elements,
                      self.upgrade, self.user, self.parent_widget)

    def continue_test(self):
        if self.question_index != -1:  # индекс -1 - тест только инициализируется
            if self.element_type != KANJI:
                if not self.checked:
                    self.permissible_mistakes -= 1
            else:
                if not all(self.checked):
                    self.permissible_mistakes -= 1
        self.question_index += 1
        if self.question_index == len(self.elements):
            self.stop_test()
        else:
            current_element = self.elements[self.question_index]
            info_text = f'Прав на ошибку осталось: {self.permissible_mistakes}'
            self.mistakes_left_label.setText(info_text)
            self.questions_left_label.setText(f'Вопросов осталось: {len(self.elements) - self.question_index}')
            self.create_question(current_element)
            self.set_style_and_show_all()

    def check_answer(self, correct_element, buttons):
        if isinstance(correct_element, Word):
            correct_answer = correct_element.meaning
        else:
            correct_answer = correct_element.reading
        if not self.checked and self.can_click:
            button = self.sender()
            if button.text() == correct_answer:
                mark_correct_button(button, is_correct=True)
            else:
                self.permissible_mistakes -= 1
                self.mistakes_left_label.setText(f'Прав на ошибку осталось: {self.permissible_mistakes}')
                for button in buttons:
                    if button.text() == correct_answer:
                        mark_correct_button(button, is_correct=True)
                    else:
                        mark_correct_button(button, is_correct=False)
            self.checked = True

    def check_answer_of_kanji(self, correct_element, buttons):
        current_level = self.sender().level
        buttons = [button for button in buttons if button.level == current_level]
        correct_answers = {0: correct_element.onyomi_reading,
                           1: correct_element.kunyomi_reading,
                           2: correct_element.meaning}
        if not self.checked[current_level] and self.can_click:
            current_button = self.sender()
            if current_button.text() == correct_answers[current_level]:
                mark_correct_button(current_button, is_correct=True)
            else:
                self.kanji_mistakes += 1
                for button in buttons:
                    if button.text() == correct_answers[current_level]:
                        mark_correct_button(button, is_correct=True)
                    else:
                        mark_correct_button(button, is_correct=False)
            self.checked[current_level] = True
        if self.kanji_mistakes and all(self.checked):
            self.permissible_mistakes -= 1
            self.mistakes_left_label.setText(f'Прав на ошибку осталось: {self.permissible_mistakes}')

    def update_progress(self, type_of_learning, user):
        if user:
            session = db_session.create_session()
            user = session.query(User).filter(User.id == user.id).first()
            current = getattr(user, f'{type_of_learning}_save', 1)
            setattr(user, f'{type_of_learning}_save', current + 1)
            session.commit()
            self.parent_widget.current_user = user
