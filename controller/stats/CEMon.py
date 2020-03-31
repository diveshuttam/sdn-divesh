from collections import deque
import time
from math import ceil, sqrt
from threading import Thread

class CEMon():
    def __init__(self,tmin,tmax):
        self.window=deque([])
        self.sum=0
        self.squaresum=0
        self.lastreading=0
        self.time=tmin
        self.tmin=tmin
        self.tmax=tmax
        self.mean=0
        self.stdev=0
        self.ws=3
        self.tsum=0

    def get_next_wait_time(self,bytes_=None):
        if(bytes_ is not None):
            self.add_new_window(bytes_)
        return self.time
    
    def add_new_window(self,bytes_):
        # check for abs later
        var = bytes_
        if(abs(var-self.mean)>2*self.stdev):
            # traffic changes significantly
            self.time=max(self.tmin,self.time/2)
            # change to max later
            self.ws=max(3,ceil(self.ws/2))
        else:
            self.time=min(self.tmax,self.time*2)
            self.ws+=1

        self.window.append(bytes_)
        self.sum+=bytes_
        self.squaresum+=(bytes_*bytes_)
        self.ws = min(10,self.ws)
        while len(self.window)>self.ws:
            b1=self.window[0]
            self.sum-=b1
            self.squaresum-=(b1*b1)
            self.window.popleft()
        self.mean=self.sum/len(self.window)
        # average of squaresum - (average of sum) ^ 2
        self.stdev=sqrt(self.squaresum/len(self.window)-self.mean*self.mean)
        print(f'cemon window ... {list(self.window)[-10:]}, mean:{self.mean}, stdev:{self.stdev}, time:{self.time}')
    
    def reset(self):
        self.window=deque([])
        self.sum=0
        self.squaresum=0
        self.lastreading=0
        self.time=self.tmin
        self.mean=0
        self.stdev=0
        self.ws=3
        self.tsum=0