from random import shuffle, choices

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLCDNumber, QMainWindow, QPushButton, QLabel)

import Nihongo
from data.timer import Timer


class Test(QMainWindow):
    def __init__(self, element_type, elements, is_upgrading):
        super().__init__()
        shuffle(elements)
        self.element_type = element_type
        self.elements = elements
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
        self.setupUi()
        self.start_test()

    def setupUi(self):
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.resize(700, 450)
        Nihongo.set_style(self)

        self.info_of_mistake_label = QLabel(f'Прав на ошибку осталось {self.permissible_mistakes}', self)
        self.info_of_mistake_label.setGeometry(390, 0, 300, 30)
        self.info_of_mistake_label.setFont(self.font_14)
        info = f'Вам необходимо пройти тест не более чем за {self.all_time} секунд'
        self.info_label = QLabel(info, self)
        self.info_label.setGeometry(50, 30, 600, 30)
        self.info_label.setFont(self.font_14)
        self.label_of_element = QLabel('', self)
        self.label_of_element.setGeometry(50, 70, 600, 40)
        self.label_of_element.setAlignment(Qt.AlignHCenter)
        self.label_of_reading = QLabel('', self)
        self.label_of_reading.setGeometry(50, 100, 600, 40)
        self.label_of_reading.setAlignment(Qt.AlignHCenter)

        # создание кнопок для ответов пользователя
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
        result = (wrong_elements + current_element)
        shuffle(result)
        return result

    def create_question(self, current_element):
        self.checked = False if self.element_type != Nihongo.KANJI else [False, False, False]
        self.label_of_element.setText(current_element.title)
        if self.element_type == Nihongo.WORD:
            self.label_of_reading.setText(current_element.reading)

        question_elements = self.select_elements_for_question(self.elements, current_element)

        if self.element_type != Nihongo.KANJI:
            for index, button in enumerate(self.buttons):
                button.setText(question_elements[index].meaning)
                button.clicked.connect(
                    lambda: self.check_answer(current_element, self.buttons))
        else:
            self.kanji_mistakes = 0
            for index, button in enumerate(self.buttons):
                if index < 4:
                    button.setText(question_elements[index].onyomi_reading)
                elif index < 8:
                    button.setText(question_elements[index].kunyomi_reading)
                else:
                    button.setText(question_elements[index].meaning)




    def start_test(self):
        lcd_timer = QLCDNumber(self)
        lcd_timer.setGeometry(325, 0, 50, 30)
        timer = Timer(self.all_time, lcd_timer, self)
        timer.start()



        def stop_check():
            self.disable_ui()
            timer.is_test_alive = False
            self.create_normal_main_menu_button()
            result_label = QLabel('', self)
            result_label.setGeometry(50, 50, 600, 40)
            result_label.setFont(self.font_20)
            if self.permissible_mistakes >= 0:
                if is_upgrading_test:
                    self.update_progress(element_type)
                    result_label.setText('Вы прошли тест и открыли новый урок')
                else:
                    result_label.setText('Вы прошли тест')
                continue_learning_button = QPushButton('Начать новый урок', self)
                continue_learning_button.setFont(self.font_20)
                continue_learning_button.setGeometry(50, 200, 600, 40)
                if element_type == Nihongo.HIRAGANA:
                    learn = self.learn_hirigana
                elif element_type == Nihongo.KATAKANA:
                    learn = self.learn_katakana
                elif element_type == Nihongo.KANJI:
                    learn = self.learn_kanji
                else:
                    learn = self.learn_words
                continue_learning_button.clicked.connect(lambda: learn(Nihongo.CONTINUE))
                self.enable_ui([continue_learning_button, result_label])
                self.ui_list.extend([continue_learning_button, result_label])
            else:
                retest_button = QPushButton('Пройти тест заново', self)
                retest_button.setFont(self.font_20)
                retest_button.setGeometry(50, 200, 600, 40)
                retest_button.clicked.connect(
                    lambda: self.test_of_learned_elements(element_type, elements, is_upgrading_test))
                self.enable_ui([retest_button, result_label])
                self.ui_list.extend([retest_button, result_label])
                result_label.setText('Вы не прошли тест')

        def continue_check():
            try:
                current_element = next(element)
                if element_type != Nihongo.KANJI:
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
              lcd_timer, self.info_label, info_of_mistake_label]
        for ui_element in ui[:5]:
            ui_element.setFont(self.font_20)
        self.ui_list.extend(ui)
        self.enable_ui(ui)
        element = iter(elements)
        current_element = next(element)
        create_check_question(current_element)

    def stop_test(self):
        pass

    def continue_test(self):
        pass
    def check_answer(self, correct_answer, buttons):
        if not self.checked and self.can_click:
            button = self.sender()
            if button.text() == correct_answer:
                set_style(button, correct_check=True, correct=True)
            else:
                self.permissible_mistakes -= 1
                self.mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')
                for button in buttons:
                    if button.text() == correct_answer:
                        set_style(button, correct_check=True, correct=True)
                    else:
                        set_style(button, correct_check=True, correct=False)
            self.checked = True

    def check_answer_of_kanji(self, correct_answers, buttons, mistakes_left_label):
        for step in range(3):
            if not self.checked[step] and self.can_click and self.sender() in buttons[step]:
                button = self.sender()
                if button.text() == correct_answers[step]:
                    set_style(button, correct_check=True, correct=True)
                else:
                    self.kanji_mistakes += 1
                    for button in buttons[step]:
                        if button.text() == correct_answers[step]:
                            set_style(button, correct_check=True, correct=True)
                        else:
                            set_style(button, correct_check=True, correct=False)
                self.checked[step] = True
        if self.kanji_mistakes and all(self.checked):
            self.permissible_mistakes -= 1
            mistakes_left_label.setText(f'Прав на ошибку осталось {self.permissible_mistakes}')