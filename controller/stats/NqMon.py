from .server import Server
class NqMon():
    """
    @param inital_interval is in seconds
    """
    def __init__(self, initial_interval):
        self.server = Server('0.0.0.0',4747)
        # interval is in seconds
        self.interval = initial_interval
        self.server.register(self.update_interval)
        self.server.start()

    def get_next_wait_time(self):
        return 10
        return self.interval
    
    def update_interval(self,new_interval):
        self.interval=new_interval