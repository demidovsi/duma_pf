import threading
import time


# таймер с выводом времени в заданный Label
class ClockThread(threading.Thread):
    need_close = False
    interval = 1
    label_time = None

    def __init__(self, interval, label_time):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.label_Time = label_time

    def run(self):
        while not self.need_close:
            try:
                self.label_Time.setText(time.ctime())
            except Exception:
                pass
            time.sleep(self.interval)
