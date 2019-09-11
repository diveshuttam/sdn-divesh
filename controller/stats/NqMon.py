class NqMon():
    """
    @param 
    """
    def __init__(self, tmin, tmax):
        # interval is in seconds
        self.interval = tmin
        self.tmin = tmin
        self.tmax = tmax

    def get_next_wait_time(self):
        return self.interval
    
    def update_interval(self,frequency_count):
        if(frequency_count==0):
            self.interval = self.tmax
        if(frequency_count>0):
            self.interval=10/frequency_count
            self.interval=max(self.interval, self.tmin)
            self.interval=min(self.interval, self.tmax)
        print(f'new interval for nqmon is {self.interval}')