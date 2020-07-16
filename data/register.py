from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QLabel, QLineEdit)
from werkzeug.security import check_password_hash, generate_password_hash

import Nihongo
from data import db_session
from data.style import FONT_20, FONT_14
from data.models.users import User
##############################################доделать

class LoginRegisterMenu(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent, Qt.Window)
        db_session.global_init(f'db/{Nihongo.DB_FILE_NAME}')
        self.login_menu()

    def login(self, ui, register=False):
        session = db_session.create_session()
        login = ui['login_line'].text()
        password = ui['password_line'].text()
        if not register:
            user = session.query(User).filter(
                User.login == login,
                check_password_hash(User.password_hash, password)
            ).first()
            if user:
                self.current_user = user
                self.start_learn()
            else:
                ui['info'].setText('Неверный логин или пароль!')
        else:
            user = User(
                login=login,
                password_hash=generate_password_hash(password)
            )
            session.add(user)
            session.commit()
            self.current_user = user
            self.start_learn()

    def login_menu(self, register=False):
        info_label = QLabel('Введите свой логин и пароль', self)
        info_label.setGeometry(50, 40, 600, 40)
        info_label.setFont(FONT_14)
        info_label.setAlignment(Qt.AlignCenter)
        info_login_label = QLabel('Логин: ', self)
        info_login_label.setGeometry(10, 100, 80, 60)
        info_login_label.setFont(FONT_14)
        info_password_label = QLabel('Пароль: ', self)
        info_password_label.setGeometry(10, 210, 80, 60)
        info_password_label.setFont(FONT_14)
        login_line = QLineEdit(self)
        login_line.setGeometry(100, 100, 500, 60)
        password_line = QLineEdit(self)
        password_line.setGeometry(100, 210, 500, 60)
        confirm_button = QPushButton('Подтвердить', self)
        confirm_button.setGeometry(50, 300, 600, 60)
        confirm_button.setFont(FONT_20)
        ui = {'info': info_label,
              'login_label': info_login_label,
              'password_label': info_password_label,
              'login_line': login_line,
              'password_line': password_line,
              'confirm': confirm_button}
        if not register:
            register_button = QPushButton('Зарегистрироваться', self)
            register_button.setGeometry(50, 380, 600, 60)
            register_button.setFont(FONT_20)
            register_button.clicked.connect(lambda: self.login_menu(register=True))
            ui['register'] = register_button
        self.disable_ui(without=ui.values())
        self.ui_list.extend(ui.values())
        if not register:
            confirm_button.clicked.connect(lambda: self.login(ui))
        else:
            confirm_button.clicked.connect(lambda: self.login(ui, register=True))
