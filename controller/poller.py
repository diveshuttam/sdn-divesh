from threading import Thread
from threading import Lock
import time

class Poller():
    def __init__(self, initial_polling_frequency,get_stats_function, time = 10):
        self.polling_frequency = initial_polling_frequency
        self.frequency_lock = Lock()
        self.time = time
        self.hooks = []
        def polling(self):
            stats=get_stats_function()
            for hook in self.hooks:
                Thread(target=hook,args=(stats,)).start()
            with self.frequency_lock:
                freq = self.polling_frequency
            time.sleep(time/freq)
        self.thread = Thread(target = polling, args = (self,))

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def update_frequency(self, new_frequency):
        with self.frequency_lock:
            self.polling_frequency = new_frequency

    def register(self, hook):
        self.hooks.append(hook)