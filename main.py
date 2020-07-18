import logging
import sys

from PyQt5.QtWidgets import *

from data.Nihongo import ProgramLearnJapaneseLanguage
from data.consts import LOG_FILE

logging.basicConfig(
    level=logging.ERROR,
    filename=LOG_FILE,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ProgramLearnJapaneseLanguage()
    main.show()
    sys.exit(app.exec_())
