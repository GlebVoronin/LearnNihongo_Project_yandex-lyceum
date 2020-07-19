from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QLabel, QLineEdit)
from werkzeug.security import check_password_hash, generate_password_hash

from data import db_session
from data.consts import *
from data.models.users import User
from data.style import *


class LoginRegisterMenu(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent, Qt.Window)
        self.resize(700, 450)
        self.setWindowTitle("Программа для помощи в изучении японского языка")
        db_session.global_init(f'db/{DB_FILE_NAME}')
        self.ui_list = []
        self.login_menu()

    def disable_ui(self):
        for ui_item in self.ui_list:
            ui_item.setParent(None)
            del ui_item

    def create_pass_button(self):
        pass_button = QPushButton('Пропустить', self)
        pass_button.setGeometry(600, 0, 100, 60)
        pass_button.setFont(FONT_14)
        pass_button.clicked.connect(self.destroy)
        return pass_button

    def create_back_button(self, onclick_function):
        back_button = QPushButton('Назад', self)
        back_button.setGeometry(0, 0, 100, 60)
        back_button.setFont(FONT_14)
        back_button.clicked.connect(onclick_function)
        return back_button

    def set_style_and_show_all(self):
        for ui_object in self.children():
            if hasattr(ui_object, 'setStyleSheet'):
                if isinstance(ui_object, QPushButton):
                    set_color(ui_object, MAIN_COLORS['main_button'])
                else:
                    set_color(ui_object, MAIN_COLORS['menu'])
            if hasattr(ui_object, 'show'):
                ui_object.show()

    def register(self, ui):
        login = ui['login'].text()
        password = ui['password'].text()
        repeat_password = ui['repeat'].text()
        if password != repeat_password:
            ui['info'].setText('Пароли должны совпадать!')
        elif not login or not password:
            ui['info'].setText('Неверный логин или пароль!')
        else:
            session = db_session.create_session()
            user = User(
                login=login,
                password_hash=generate_password_hash(password)
            )
            session.add(user)
            session.commit()
            self.parent().current_user = user
            self.setParent(None)

    def login(self, ui):
        login = ui['login'].text()
        password = ui['password'].text()
        if not login or not password:
            ui['info'].setText('Неверный логин или пароль!')
        else:
            session = db_session.create_session()
            users = session.query(User).all()
            found = False
            user = None
            for user in users:
                if check_password_hash(user.password_hash, password) and user.login == login:
                    found = True
                    break
            if found:
                self.parent().current_user = user
                self.setParent(None)
            else:
                ui['info'].setText('Неверный логин или пароль!')

    def register_menu(self):
        self.disable_ui()
        pass_button = self.create_pass_button()
        back_button = self.create_back_button(self.login_menu)
        info_label = QLabel('Введите свой логин и пароль', self)
        info_label.setGeometry(100, 40, 500, 40)
        info_label.setFont(FONT_14)
        info_label.setAlignment(Qt.AlignCenter)

        info_login_label = QLabel('Логин: ', self)
        info_login_label.setGeometry(10, 100, 130, 60)
        info_login_label.setFont(FONT_14)
        login_line = QLineEdit(self)
        login_line.setGeometry(150, 100, 500, 60)

        info_password_label = QLabel('Пароль: ', self)
        info_password_label.setGeometry(10, 190, 130, 60)
        info_password_label.setFont(FONT_14)
        password_line = QLineEdit(self)
        password_line.setGeometry(150, 190, 500, 60)

        info_repeat_password_label = QLabel('Повторите\nпароль: ', self)
        info_repeat_password_label.setGeometry(10, 280, 130, 60)
        info_repeat_password_label.setFont(FONT_14)
        repeat_password_line = QLineEdit(self)
        repeat_password_line.setGeometry(150, 280, 500, 60)

        confirm_button = QPushButton('Подтвердить', self)
        confirm_button.setGeometry(50, 380, 600, 60)
        confirm_button.setFont(FONT_20)
        ui = {'login': login_line,
              'password': password_line,
              'repeat': repeat_password_line,
              'info': info_label}
        confirm_button.clicked.connect(lambda: self.register(ui))
        self.ui_list.extend(ui.values())
        self.ui_list.extend([info_login_label, info_password_label, pass_button,
                             info_repeat_password_label, confirm_button, back_button])
        self.set_style_and_show_all()

    def login_menu(self):
        self.disable_ui()
        pass_button = self.create_pass_button()
        back_button = self.create_back_button(self.register_menu)
        info_label = QLabel('Введите свой логин и пароль', self)
        info_label.setGeometry(100, 40, 500, 40)
        info_label.setFont(FONT_14)
        info_label.setAlignment(Qt.AlignCenter)
        info_login_label = QLabel('Логин: ', self)
        info_login_label.setGeometry(10, 100, 130, 60)
        info_login_label.setFont(FONT_14)
        info_password_label = QLabel('Пароль: ', self)
        info_password_label.setGeometry(10, 210, 130, 60)
        info_password_label.setFont(FONT_14)
        login_line = QLineEdit(self)
        login_line.setGeometry(150, 100, 500, 60)
        password_line = QLineEdit(self)
        password_line.setGeometry(150, 210, 500, 60)
        confirm_button = QPushButton('Подтвердить', self)
        confirm_button.setGeometry(50, 300, 600, 60)
        confirm_button.setFont(FONT_20)
        register_button = QPushButton('Зарегистрироваться', self)
        register_button.setGeometry(50, 380, 600, 60)
        register_button.setFont(FONT_20)
        register_button.clicked.connect(self.register_menu)
        ui = {'login': login_line,
              'password': password_line,
              'info': info_label}
        confirm_button.clicked.connect(lambda: self.login(ui))
        self.ui_list.extend(ui.values())
        self.ui_list.extend([info_login_label, info_password_label, pass_button,
                             register_button, confirm_button, back_button])
        self.set_style_and_show_all()
