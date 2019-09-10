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
        self.initial_wait=0
        self.bytes_lock = Lock()
        self.flow_dict={}
        self.flow_dict_lock=Lock()
        self.interesting_flow = ('10.0.0.1', '10.0.0.2')
        self.actual_polling=5 # freqency for actual polling
        self.cemon = CEMon.CEMon(0.5,5.0)
        self.nqmon = NqMon.NqMon(0.5,5.0)
        self.nqmon_server = Server.Server('0.0.0.0',8080)
        # self.nqmon_server.register(self.nqmon.update_interval)
        self.cemon_thread = Thread(target=self._cemon_monitor, name='cemon thread')
        self.nqmon_thread = Thread(target=self._nqmon_monitor, name='nqmon thread')
        self.actual_thread = Thread(target=self._actual_thread, name='actual thread')
        # self.cemon_thread.start()
        # self.nqmon_thread.start()
        self.actual_thread.start()
        
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
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
            bytes_,time_=self._request_bytes()
            try:
                bytes_diff = bytes_-self.cemon_bytes_
                time_diff = time_-self.cemon_time_
                requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'cemon'})
                self.logger.debug(f'cemon bytes {self.cemon_bytes_}')
                self.cemon.add_new_window(bytes_diff/time_diff)
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass 
            self.cemon_bytes_=bytes_
            self.cemon_time_=time_
            t=self.cemon.get_next_wait_time()
            self.logger.debug(f'cemon going to sleep for {t}s ws:{self.cemon.ws}, mean:{self.cemon.mean}, stdev:{self.cemon.stdev}')
            time.sleep(t)

    def _nqmon_monitor(self):
        time.sleep(self.initial_wait)
        self.logger.debug('waiting for nqmon collector connection')
        self.nqmon_server.start()
        while True:
            self.logger.debug("nqmon")
            try:
                bytes_,time_=self._request_bytes()
                bytes_diff = bytes_-self.nqmon_bytes_
                time_diff = time_-self.nqmon_time_
                requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'nqmon'})
                self.logger.debug(f'nqmon bytes {self.nqmon_bytes_}')
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass
            self.nqmon_bytes_=bytes_
            self.nqmon_time_ = time_
            t=self.nqmon.get_next_wait_time()
            self.logger.debug(f'nqmon going to sleep for {t}s')
            time.sleep(t)
    
    def _actual_thread(self):
        time.sleep(self.initial_wait)
        while True:
            try:
                bytes_,time_=self._request_bytes()
                bytes_diff=bytes_-self.actual_bytes_
                time_diff=time_-self.actual_time_
                # requests.post(URL,json={'time':datetime.now().timestamp(),'val1':bytes_,'val':bytes_diff/time_diff, 'type':'actual'})
            except (AttributeError,requests.ConnectionError) as e:
                print(e)
                pass
            # self.actual_bytes_=bytes_
            # self.actual_time_=time_
            time.sleep(self.actual_polling)
 
    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    def _request_bytes(self):
        with self.bytes_lock:
            while len(list(self.datapaths.values()))==0:
                time.sleep(0.05)
            for dp in self.datapaths.values():
                self.waiting+=1
                self._request_stats(dp)
            while self.waiting!=0:
                self.logger.debug(f'waiting {self.waiting}')
                time.sleep(0.05)
            bytes_, time_ = 0,0
            return bytes_, time_

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        time=datetime.now()
        body = ev.msg.body
        flag = False
        with self.flow_dict_lock:
            count = 0
            for stat in body:
                f= ('table_id=%s '
                        'duration_sec=%d duration_nsec=%d '
                        'priority=%d '
                        'idle_timeout=%d hard_timeout=%d flags=0x%04x '
                        'cookie=%d packet_count=%d byte_count=%d '
                        'match=%s instructions=%s' %
                        (stat.table_id,
                        stat.duration_sec, stat.duration_nsec,
                        stat.priority,
                        stat.idle_timeout, stat.hard_timeout, stat.flags,
                        stat.cookie, stat.packet_count, stat.byte_count,
                        stat.match, stat.instructions))
                self.logger.debug('FlowStats: %s', f)

                try:
                    flow_id=(stat.match['ipv4_src'],stat.match['ipv4_dst'])
                    if flow_id not in self.flow_dict:
                        self.flow_dict[flow_id]=deque([(stat.byte_count,time)],maxlen=30)
                    else:
                        self.flow_dict[flow_id].append((stat.byte_count,time))
                    count+=1
                except BaseException as e:
                    print(e)
        if(count==0):
            print('count is 0')
        else:
            print('count is not 0')
        self.waiting-=1