from threading import Thread
from time import sleep


class Timer(Thread):
    def __init__(self, duration, display_object, main_object):
        super().__init__()
        self.duration = duration
        self.display_object = display_object
        self.seconds = 0
        self.is_test_alive = True
        self.main_object = main_object

    def run(self):
        while self.duration - self.seconds > 0 and self.is_test_alive:
            sleep(1)
            self.seconds += 1
            seconds_left = self.duration - self.seconds
            minutes, seconds = seconds_left // 60, seconds_left % 60
            self.display_object.display(f'{minutes}:{seconds}')
        if not self.is_test_alive:
            self.end_function()

    def end_function(self):
        self.main_object.can_click = False
        self.main_object.info_label.setText('Время вышло')
