from PyQt5.QtGui import QFont

FONT_14 = QFont()
FONT_14.setPointSize(14)
FONT_20 = QFont()
FONT_20.setPointSize(20)
MAIN_COLORS = {
    'red': [255, 0, 0],
    'green': [0, 255, 0],
    'main_button': [120, 120, 255],
    'menu': [70, 70, 200]
}

def mark_correct_button(ui_element, is_correct):
    if is_correct:
        set_color(ui_element, MAIN_COLORS['green'])
    else:
        set_color(ui_element, MAIN_COLORS['red'])


def set_color(ui_element, color):
    """color == [0..255,0..255,0..255] or
       color == (0..255,0..255,0..255)"""
    red, green, blue = color
    style = f'background-color: rgb({red}, {green}, {blue})'
    ui_element.setStyleSheet(style)
