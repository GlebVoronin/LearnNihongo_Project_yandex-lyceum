from copy import deepcopy
from random import shuffle

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLCDNumber, QMainWindow, QPushButton, QLabel)

import Nihongo
from data.timer import Timer


class Test(QMainWindow):
    def __init__(self, element_type, elements, is_upgrading):
        super().__init__()
        self.element_type = element_type
        self.elements = elements
        self.upgrade = is_upgrading
        self.setupUi()
        self.start_test()

    def setupUi(self):
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        self.resize(700, 450)
        Nihongo.set_style(self)

    def start_test(self):
        shuffle(self.elements)
        random_elements = deepcopy(elements)
        time_to_one_element = Nihongo.TIME_FOR_ONE_ELEMENT[element_type]
        if element_type != Nihongo.KANJI:
            random_elements = [element.title for element in random_elements]
        else:
            random_elements = [[], [], []]
            for element in elements:
                random_elements[0].append(element.title)
                random_elements[1].append(element.onyomi_reading)
                random_elements[2].append(element.kunyomi_reading)
        all_time_to_test = time_to_one_element * len(elements)
        # количество допустимых ошибок = кол-во элементов * 1 % * число процентов
        self.permissible_mistakes = int(len(elements) * 0.01 * Nihongo.ERROR_PERCENT_FOR_TEST)
        info_of_mistake_label = QLabel(f'Прав на ошибку осталось {self.permissible_mistakes}', self)
        info_of_mistake_label.setGeometry(390, 0, 300, 30)
        info_of_mistake_label.setFont(self.font_14)
        info = f'Вам необходимо пройти тест не более чем за {all_time_to_test} секунд'
        self.info_label = QLabel(info, self)
        self.info_label.setGeometry(50, 30, 600, 30)
        self.info_label.setFont(self.font_14)
        label_of_element = QLabel('', self)
        label_of_element.setGeometry(50, 70, 600, 40)
        label_of_element.setAlignment(Qt.AlignHCenter)
        label_of_reading = QLabel('', self)
        label_of_reading.setGeometry(50, 100, 600, 40)
        label_of_reading.setAlignment(Qt.AlignHCenter)
        lcd_timer = QLCDNumber(self)
        lcd_timer.setGeometry(325, 0, 50, 30)
        timer = Timer(all_time_to_test, lcd_timer, self)
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
            if element_type == Nihongo.WORD:
                random_elements_with_current_element = create_new_random_elements(random_elements, element[2])
                correct_element = element[2]
            elif element_type == Nihongo.KATAKANA or element_type == Nihongo.HIRAGANA:
                random_elements_with_current_element = create_new_random_elements(random_elements, element[1])
                correct_element = element[1]
            else:
                random_elements_with_current_element = [create_new_random_elements(random_elements[0], element[1]),
                                                        create_new_random_elements(random_elements[1], element[2]),
                                                        create_new_random_elements(random_elements[2], element[3])]
                correct_element = [element[1], element[2], element[3]]
            label_of_element.setText(element[0])
            if element_type == Nihongo.WORD:
                label_of_reading.setText(element[1])
            if element_type != Nihongo.KANJI:
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
                    button.clicked.connect(
                        lambda: self.check_answer(correct_element, buttons, info_of_mistake_label))
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


