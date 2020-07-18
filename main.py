import logging
import sys

from PyQt5.QtWidgets import *

from data import db_session
from data.Nihongo import ProgramLearnJapaneseLanguage
from data.consts import LOG_FILE
from data.models.users import User

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
