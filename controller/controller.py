from operator import attrgetter
import time
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from stats import CEMon, NqMon, Server
# from viewer import test_plotly as plotly
from datetime import datetime
from random import randint
from threading import Thread,Lock
import multiprocessing
import requests
from collections import deque

URL='http://localhost:8050/update'
class SimpleMonitor13(simple_switch_13.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.logger.debug('called init')
        self.datapaths = {}
        self.waiting=0
        self.initial_wait=10
        self.bytes_lock = Lock()
        self.flow_dict={}
        self.flow_dict_lock=Lock()
        self.interesting_flow = ('00:00:00:00:00:02', '00:00:00:00:00:06')
        self.interesting_switch = 1
        self.actual_polling=0.5 # freqency for actual polling
        self.tmin = 0.5
        self.tmax = 5
        self.cemon = CEMon.CEMon(self.tmin,self.tmax)
        self.nqmon = NqMon.NqMon(self.tmin,self.tmax)
        self.nqmon_server = Server.Server('192.168.1.3',4747)
        self.nqmon_server.register(self.nqmon.update_interval)
        self.nqmon_server.start()
        self.cemon_thread = Thread(target=self._cemon_monitor, name='cemon thread')
        self.nqmon_thread = Thread(target=self._nqmon_monitor, name='nqmon thread')
        self.actual_thread = Thread(target=self._actual_thread, name='actual thread')
        self.cemon_thread.start()
        self.nqmon_thread.start()
        self.actual_thread.start()
        
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        print('datapath id', datapath.id)
        if(datapath.id == self.interesting_switch):
            if ev.state == MAIN_DISPATCHER:
                if datapath.id not in self.datapaths:
                    self.logger.debug('register datapath: %016x', datapath.id)
                    self.datapaths[datapath.id] = datapath
            elif ev.state == DEAD_DISPATCHER:
                if datapath.id in self.datapaths:
                    self.logger.debug('unregister datapath: %016x', datapath.id)
                    del self.datapaths[datapath.id]

    def _cemon_monitor(self):
        time.sleep(self.initial_wait)
        while True:
            self.logger.debug("cemon")
            try:
                temp=self._request_bytes()
                if(temp is None):
                    time.sleep(self.tmax)
                    continue
                bytes_,flow_time, time_=temp
                bytes_diff = bytes_-self.cemon_bytes_
                time_diff = flow_time-self.cemon_time_
                print('***timediff***', time_diff)
                requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'cemon'})
                self.logger.debug(f'cemon bytes {self.cemon_bytes_}')
                self.cemon.add_new_window(bytes_diff)
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass 
            self.cemon_bytes_=bytes_
            self.cemon_time_=flow_time
            t=self.cemon.get_next_wait_time()
            self.logger.debug(f'cemon going to sleep for {t}s with ws:{self.cemon.ws}, mean:{self.cemon.mean}, stdev:{self.cemon.stdev}')
            time.sleep(t)

    def _nqmon_monitor(self):
        time.sleep(self.initial_wait)
        self.logger.debug('waiting for nqmon collector connection')
        while True:
            self.logger.debug("nqmon")
            try:
                temp=self._request_bytes()
                if(temp is None):
                   time.sleep(self.tmax)
                   continue
                bytes_,flow_time, time_=temp
                bytes_diff = bytes_-self.nqmon_bytes_
                time_diff = flow_time-self.nqmon_time_
                requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'nqmon'})
                self.logger.debug(f'nqmon bytes {self.nqmon_bytes_}')
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass
            self.nqmon_bytes_=bytes_
            self.nqmon_time_ = flow_time
            t=self.nqmon.get_next_wait_time()
            self.logger.debug(f'nqmon going to sleep for {t}s')
            time.sleep(t)
    
    def _actual_thread(self):
        time.sleep(self.initial_wait)
        while True:
            try:
                temp=self._request_bytes()
                if(temp is None):
                    time.sleep(self.tmax)
                    continue
                bytes_,flow_time, time_=temp
                bytes_diff=bytes_-self.actual_bytes_
                time_diff=flow_time-self.actual_time_
                requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'actual'})
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass
            self.actual_bytes_=bytes_
            self.actual_time_=flow_time
            time.sleep(self.actual_polling)
 
    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_src = self.interesting_flow[0], eth_dst = self.interesting_flow[1])
        req = parser.OFPFlowStatsRequest(datapath, match = match)
        datapath.send_msg(req)

    def _request_bytes(self):
        with self.bytes_lock:
            # wait for datapaths entries to be created
            while len(list(self.datapaths.values()))==0:
                time.sleep(0.05)

            # poll the interesting switch
            for dp in self.datapaths.values():
                print(dp)
                self.waiting+=1
                self._request_stats(dp)
            
            while self.waiting!=0:
                self.logger.debug(f'waiting for switch responses {self.waiting}')
                time.sleep(0.05)
            
            try:
                bytes_, flow_time, time_ = self.bytes_, self.flow_time, self.time_
            except:
                return None
            # print(f'returning {bytes_}, {time_}')
            return bytes_, flow_time, time_

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        time=datetime.now().timestamp()
        body = ev.msg.body
        datapath = ev.msg.datapath
        ofp_match = datapath.ofproto_parser
        
        flag = False
        with self.flow_dict_lock:
            count = 0
            for stat in body:
                print('some stat found')
                count+=1

                try:
                    flow_id = (stat.match['eth_src'],stat.match['eth_dst'])
                    flow_time = stat.duration_sec + (stat.duration_nsec)/1000000000
                    if flow_id not in self.flow_dict:
                        self.flow_dict[flow_id]=deque([], maxlen=30)
                    self.flow_dict[flow_id].append((stat.byte_count,flow_time))
                    self.bytes_, self.flow_time, self.time_ = stat.byte_count, flow_time, time
                    # print(f'set {self.bytes_}, {self.time_}')
                except BaseException as e:
                    raise
                    print(e)
            # print('returning reply')
            self.waiting-=1