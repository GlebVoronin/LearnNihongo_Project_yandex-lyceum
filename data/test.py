from random import shuffle, choices

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLCDNumber, QMainWindow, QPushButton, QLabel)

import Nihongo
from data.timer import Timer


class Test(QMainWindow):
    def __init__(self, element_type, elements, is_upgrading, user, parent):
        super().__init__(parent, Qt.Window)
        shuffle(elements)
        self.element_type = element_type
        self.elements = elements
        self.parent_widget = parent
        self.current_user = user
        self.one_element_time = Nihongo.TIME_FOR_ONE_ELEMENT[element_type]
        self.all_time = self.one_element_time * len(elements)
        self.upgrade = is_upgrading
        # количество допустимых ошибок = кол-во элементов * 1 % * число процентов
        self.permissible_mistakes = int(len(elements) * 0.01 * Nihongo.ERROR_PERCENT_FOR_TEST)
        self.can_click = True
        self.checked = False if element_type != Nihongo.KANJI else [False, False, False]
        if element_type == Nihongo.KANJI:
            self.kanji_mistakes = 0
        self.buttons = []
        self.elements_iterator = iter(self.elements)
        lcd_timer = QLCDNumber(self)
        lcd_timer.setGeometry(325, 0, 50, 30)
        self.timer = Timer(self.all_time, lcd_timer, self)
        self.timer.start()
        self.setupUi()
        self.start_test()

    def setupUi(self):
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.resize(700, 450)
        Nihongo.set_style(self)

        self.mistakes_left_label = QLabel(f'Прав на ошибку осталось {self.permissible_mistakes}', self)
        self.mistakes_left_label.setGeometry(390, 0, 300, 30)
        self.mistakes_left_label.setFont(Nihongo.FONT_14)
        info = f'Вам необходимо пройти тест не более чем за {self.all_time} секунд'
        self.info_label = QLabel(info, self)
        self.info_label.setGeometry(50, 30, 600, 30)
        self.info_label.setFont(Nihongo.FONT_14)
        self.label_of_element = QLabel('', self)
        self.label_of_element.setGeometry(50, 70, 600, 40)
        self.label_of_element.setAlignment(Qt.AlignHCenter)
        self.label_of_element.setFont(Nihongo.FONT_20)
        self.label_of_reading = QLabel('', self)
        self.label_of_reading.setGeometry(50, 100, 600, 40)
        self.label_of_reading.setAlignment(Qt.AlignHCenter)
        self.label_of_reading.setFont(Nihongo.FONT_20)

    def create_buttons(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []
        if self.element_type != Nihongo.KANJI:
            x = 150
            for index in range(4):
                button = QPushButton('', self)
                button.setGeometry(0, x, 700, 50)
                button.setFont(Nihongo.FONT_20)
                x += 60
                self.buttons.append(button)
        else:
            x = 150
            y = 0
            for index in range(12):
                button = QPushButton('', self)
                button.setGeometry(y, x, 233, 50)
                button.setFont(Nihongo.FONT_20)
                x += 60
                self.buttons.append(button)
                if index % 4 == 0:
                    y += 233
        Nihongo.enable_ui(self.buttons)

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
        wrong_elements = choices(temporary, k=3)
        result = (wrong_elements + [current_element])
        shuffle(result)
        return result

    def create_question(self, current_element):
        self.create_buttons()
        self.checked = False if self.element_type != Nihongo.KANJI else [False, False, False]
        self.label_of_element.setText(current_element.title)
        if self.element_type == Nihongo.WORD:
            self.label_of_reading.setText(current_element.reading)

        question_elements = self.select_elements_for_question(self.elements, current_element)
        if self.element_type != Nihongo.KANJI:
            for index, button in enumerate(self.buttons):
                Nihongo.set_style(button)
                if self.element_type == Nihongo.WORD:
                    button.setText(question_elements[index].meaning)
                else:
                    button.setText(question_elements[index].reading)
                button.clicked.connect(
                    lambda: self.check_answer(current_element, self.buttons))
        else:
            self.kanji_mistakes = 0
            for index, button in enumerate(self.buttons):
                Nihongo.set_style(button)
                if index < 4:  # кнопки с 0 по 3
                    button.setText(question_elements[index].onyomi_reading)
                elif index < 8:
                    button.setText(question_elements[index].kunyomi_reading)
                else:
                    button.setText(question_elements[index].meaning)
                button.clicked.connect(
                    lambda: self.check_answer_of_kanji(current_element, self.buttons))

    def start_test(self):
        continue_button = QPushButton('Продолжить', self)
        continue_button.setGeometry(0, 390, 700, 50)
        continue_button.clicked.connect(self.continue_test)
        current_element = next(self.elements_iterator)
        self.create_question(current_element)

    def stop_test(self, timer=False):
        [button.setEnabled(False) for button in self.buttons]
        [button.setVisible(False) for button in self.buttons]
        result_label = QLabel('', self)
        result_label.setGeometry(50, 50, 600, 40)
        result_label.setFont(Nihongo.FONT_20)
        if self.permissible_mistakes >= 0 and not timer:
            if self.upgrade:
                Nihongo.update_progress(self.element_type, self.user)
                result_label.setText('Вы прошли тест и открыли новый урок')
            else:
                result_label.setText('Вы прошли тест')
        else:
            retest_button = QPushButton('Пройти тест заново', self)
            retest_button.setFont(Nihongo.FONT_20)
            retest_button.setGeometry(50, 200, 600, 40)
            retest_button.clicked.connect(
                lambda: self.reset())
            result_label.setText('Вы не прошли тест')
            Nihongo.enable_ui([result_label])
        continue_button = QPushButton('Продолжить', self)
        continue_button.setFont(Nihongo.FONT_20)
        continue_button.setGeometry(50, 400, 600, 40)
        continue_button.clicked.connect(
            lambda: self.destroy())
        Nihongo.enable_ui([continue_button])

    def reset(self):
        self.__init__(self.element_type, self.elements,
                      self.is_upgrading_test, self.user, self.parent_widget)

    def continue_test(self):
        if self.element_type != Nihongo.KANJI:
            if not self.checked:
                self.permissible_mistakes -= 1
        else:
            if not all(self.checked):
                self.permissible_mistakes -= 1
        try:
            current_element = next(self.elements_iterator)
            info_text = f'Прав на ошибку осталось {self.permissible_mistakes}'
            self.mistakes_left_label.setText(info_text)
            self.create_question(current_element)
        except StopIteration:
            self.stop_test()

    def check_answer(self, correct_element, buttons):
        if isinstance(correct_element, Nihongo.Word):
            correct_answer = correct_element.meaning
        else:
            correct_answer = correct_element.reading
        if not self.checked and self.can_click:
            button = self.sender()
            if button.text() == correct_answer:
                Nihongo.set_style(button, correct_check=True, correct=True)
            else:
                self.permissible_mistakes -= 1
                self.mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')
                for button in buttons:
                    if button.text() == correct_answer:
                        Nihongo.set_style(button, correct_check=True, correct=True)
                    else:
                        Nihongo.set_style(button, correct_check=True, correct=False)
            self.checked = True

    def check_answer_of_kanji(self, correct_element, buttons):
        for index in range(3):
            correct_answers = {0: correct_element.onyomi_reading,
                               1: correct_element.kunyomi_reading,
                               2: correct_element.meaning}
            if not self.checked[index] and self.can_click:
                button = self.sender()
                if button.text() == correct_answers[index]:
                    Nihongo.set_style(button, correct_check=True, correct=True)
                else:
                    self.kanji_mistakes += 1
                    for button in buttons[index]:
                        if button.text() == correct_answers[index]:
                            Nihongo.set_style(button, correct_check=True, correct=True)
                        else:
                            Nihongo.set_style(button, correct_check=True, correct=False)
                self.checked[index] = True
        if self.kanji_mistakes and all(self.checked):
            self.permissible_mistakes -= 1
            self.mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')
