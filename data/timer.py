from threading import Thread
from time import sleep


class Timer(Thread):
    def __init__(self, duration, display_object, main_object):
        super().__init__()
        self.duration = duration
        self.display_object = display_object
        self.seconds = 0
        self.stop = False
        self.main_object = main_object

    def end(self):
        self.stop = True

    def run(self):
        while self.duration - self.seconds > 0 and not self.stop:
            sleep(1)
            self.seconds += 1
            seconds_left = self.duration - self.seconds
            minutes, seconds = seconds_left // 60, seconds_left % 60
            self.display_object.display(f'{minutes}:{seconds}')
        if not self.stop:
            self.main_object.stop_test(timer=True)
