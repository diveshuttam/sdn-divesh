from collections import deque
import time
from math import ceil, sqrt
import numpy as np
from threading import Thread

class window(deque):
    @property
    def mean(self):
        try:
            return sum(self)/len(self)
        except:
            return 0

    @property
    def stdev(self):
        try:
            return np.std(self)
        except:
            return 0

    @property
    def length(self):
        return len(self)

class NqMon():
    def __init__(self,tmin,tmax):
        self.current_time = None
        self.τ = 1.0
        self.τ_max = 5.0
        self.τ_min = 0.5
        self.last_reading = 0
        self.win_bytes = window([])
        self.dwin_bytes = window([])
        self.ddwin_bytes = window([])
        self.t_window = window([])
        self.ws = 3
        self.previous= False

    def get_next_wait_time(self,bytes_=None):
        if(bytes_ is not None):
            self.add_new_window(bytes_)
        return self.τ
    
    def add_new_window(self,bytes_,flow_time):
        self.current_reading = bytes_
        self.current_time = flow_time
        self.t_window.append(self.current_time)
        # print(f"appending {self.current_time}, {self.current_reading}, τ = {τ}")
        # var = current_reading-last_reading
        self.last_reading=self.current_reading
        if(self.win_bytes.length==0):
            self.win_bytes.append(self.current_reading)
            return
        elif(self.win_bytes.length==1):
            self.win_bytes.append(self.current_reading)
            self.dwin_bytes.append((self.win_bytes[-1]-self.win_bytes[-2])/self.τ)
            return
        self.win_bytes.append(self.current_reading)
        self.dwin_bytes.append((self.win_bytes[-1]-self.win_bytes[-2])/self.τ)
        tdiff = self.t_window[-1]-self.t_window[-3]
        self.ddwin_bytes.append((self.win_bytes[-1]-self.win_bytes[-3])/(tdiff))
        #instantaneous curvature
        # print(abs(self.ddwin_bytes[-1]-(self.dwin_bytes[-2]+self.dwin_bytes[-1])/2.0))
        # input()
        if(abs(self.ddwin_bytes[-1]-(self.dwin_bytes[-2]+self.dwin_bytes[-1])/2.0)>500):
            if(self.previous==False):
                self.τ = max(self.τ_min,self.τ/3.0)
                self.ws = max(3,ceil(self.ws))
                self.previous=True
        else:
            self.τ = min(self.τ_max,self.τ*2)
            self.ws = self.ws + 1
            self.previous=False

        while self.win_bytes.length>self.ws:
            self.win_bytes.popleft()
            self.ddwin_bytes.popleft()
            self.dwin_bytes.popleft()
            self.t_window.popleft()
        # print(f'cemon window ... {list(self.window)[-10:]}, mean:{self.mean}, stdev:{self.stdev}, time:{self.time}')
    
    def reset(self):
        self.current_time = None
        self.τ = 1.0
        self.τ_max = 5.0
        self.τ_min = 0.5
        self.last_reading = 0
        self.win_bytes = window([])
        self.dwin_bytes = window([])
        self.ddwin_bytes = window([])
        self.t_window = window([])
        self.ws = 3
        self.previous= False