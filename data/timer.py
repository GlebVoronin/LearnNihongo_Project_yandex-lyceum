from threading import Thread
from time import sleep


class Timer(Thread):
    def __init__(self, duration, lcd_object, end_function):
        super().__init__()
        self.duration = duration
        self.lcd_object = lcd_object
        self.seconds = 0
        self.is_test_alive = True
        self.end_function = end_function

    def run(self):
        while self.duration - self.seconds > 0 and self.is_test_alive:
            sleep(1)
            self.seconds += 1
            seconds_left = self.duration - self.seconds
            minutes, seconds = seconds_left // 60, seconds_left % 60
            self.lcd_object.display(f'{minutes}:{seconds}')
        if not self.is_test_alive:
            self.end_function()
