from operator import attrgetter
import time
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from stats import CEMon, NqMon, Server
from viewer import test_plotly as plotly
from datetime import datetime
from random import randint
from threading import Thread,Lock
import multiprocessing
import requests

URL='http://localhost:8050/update'
class SimpleMonitor13(simple_switch_13.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.logger.debug('called init')
        self.datapaths = {}
        self.waiting=0
        self.initial_wait=1
        self.bytes_lock = Lock()
        # self.bytes_=0
        self.actual_polling=1
        self.cemon = CEMon.CEMon(5,5.0)
        self.nqmon = NqMon.NqMon(5)
        self.nqmon_server = Server.Server('0.0.0.0',8080)
        self.nqmon_server.register(self.nqmon.update_interval)
        self.cemon_thread = Thread(target=self._cemon_monitor, name='cemon thread')
        self.nqmon_thread = Thread(target=self._nqmon_monitor, name='nqmon thread')
        self.plotly_process = multiprocessing.Process(target=self._plotly_process)
        self.actual_thread = Thread(target=self._actual_thread, name='actual thread')
        self.cemon_thread.start()
        self.nqmon_thread.start()
        self.plotly_process.start()
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
            bytes_=self._request_bytes()
            try:
                bytes_diff = bytes_-self.cemon_bytes_
                self.cemon.add_new_window(bytes_diff)
            except AttributeError:
                pass
            self.cemon_bytes_=bytes_
            self.logger.debug(f'cemon bytes {self.cemon_bytes_}')
            requests.post(URL,json={'time':datetime.now().timestamp(),'val':self.cemon_bytes_, 'type':'cemon'})
            t=self.cemon.get_next_wait_time()
            self.logger.debug(f'cemon going to sleep for {t}s')
            time.sleep(t)

    def _nqmon_monitor(self):
        time.sleep(self.initial_wait)
        self.logger.debug('waiting for nqmon collector connection')
        self.nqmon_server.start()
        while True:
            self.logger.debug("nqmon")
            self.nqmon_bytes_=self._request_bytes()
            self.logger.debug(f'nqmon bytes {self.nqmon_bytes_}')
            requests.post(URL,json={'time':datetime.now().timestamp(),'val':self.nqmon_bytes_, 'type':'nqmon'})
            t=self.nqmon.get_next_wait_time()
            self.logger.debug(f'nqmon going to sleep for {t}s')
            time.sleep(t)
    
    def _actual_thread(self):
        time.sleep(self.initial_wait)
        while True:
            self.actual_bytes_=self._request_bytes()
            requests.post(URL,json={'time':datetime.now().timestamp(),'val':self.actual_bytes_, 'type':'actual'})
            time.sleep(self.actual_polling)
 
    def _plotly_process(self):
        plotly.app.run_server(debug=True,threaded=False,processes=1)


    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        # req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        # datapath.send_msg(req)

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
            bytes_=self.bytes_
        return bytes_
        

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        # self.logger.info('datapath         '
        #                  'in-port  eth-dst           '
        #                  'out-port packets  bytes')
        # self.logger.info('---------------- '
        #                  '-------- ----------------- '
        #                  '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
            self.bytes_=stat.byte_count
        self.waiting-=1
