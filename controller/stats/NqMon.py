class NqMon():
    """
    @param inital_interval is in miliseconds
    """
    def __init__(self, initial_interval=500):
        # interval is in seconds
        self.interval = initial_interval

    def get_next_wait_time(self):
        return self.interval
    
    def update_interval(self,new_interval):
        self.interval=new_interval