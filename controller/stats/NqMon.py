from .server import Server
class NqMon():
    """
    @param inital_interval is in miliseconds
    """
    def __init__(self, initial_interval=500):
        self.server = Server('0.0.0.0',4747)
        # interval is in seconds
        self.interval = initial_interval
        # register update interval hook to the collector
        self.server.register(self.update_interval)
        self.server.start()

    def get_next_wait_time(self):
        return self.interval
    
    def update_interval(self,new_interval):
        self.interval=new_interval