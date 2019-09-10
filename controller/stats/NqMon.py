class NqMon():
    """
    @param 
    """
    def __init__(self, tmin=0.5,tmax=5):
        # interval is in seconds
        self.interval = tmin

    def get_next_wait_time(self):
        return self.interval
    
    def update_interval(self,new_interval):
        self.interval=new_interval