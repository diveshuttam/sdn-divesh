from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from threading import Thread
from threading import Condition
from time import sleep
import datetime
from collections import deque
from statistics import mean
from statistics import stdev
from math import ceil

class PollingEvent(Thread):

    window = deque()
    window_min_size = 3

    min_poll_time = 1
    max_poll_time = 5
    poll_after = 1

    polled_reading = 0
    prev_traffic = 0

    def __init__(self, condition, datapaths):
        Thread.__init__(self)
        self.condition = condition
        self.datapaths = datapaths

    def run(self):
        while True:
            sleep(self.poll_after)

            #poll
            for dp in self.datapaths.values():
                self.request_stats(dp)

            with self.condition:
                #wait for the polling results
                self.condition.wait()

                #polling results now available!
                #polled_reading is updated
                #poll_after is updated

    def request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Request port stats
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


class SimpleMonitor13(simple_switch_13.SimpleSwitch13):

    condition = Condition()
    monitored_data = {}

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}

        # New thread for polling
        self.pollingEvent = PollingEvent(self.condition, self.datapaths)
        self.pollingEvent.start()


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


    #reply handler
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        traffic = 0

        # traffic is the total number of bytes from the start (sum of all the
        # port counters)
        for stat in sorted(body, key=attrgetter('port_no')):
            traffic += (stat.rx_bytes + stat.tx_bytes)

        # divide by 2 because every packet is counted twice. Once when sent,
        # and second when received
        traffic /= 2


        self.pollingEvent.polled_reading = traffic - self.pollingEvent.prev_traffic
        self.pollingEvent.prev_traffic = traffic

        self.monitored_data[datetime.datetime.now()] = self.pollingEvent.polled_reading

        # initial window filling
        # Initially the window is empty and needs to be filled for deciding further pooling time
        # Until the length of window is less than window_min_size, poll every 1 sec to fill the window
        if len(self.pollingEvent.window) < self.pollingEvent.window_min_size:
            self.pollingEvent.window.append(self.pollingEvent.polled_reading)
            self.pollingEvent.poll_after = 1
        else:
            # find delta (refer CeMon Paper)
            windowMean = mean(self.pollingEvent.window)
            windowStddev = stdev(self.pollingEvent.window)

            upperDelta =  windowMean + 2 * windowStddev
            lowerDelta = windowMean - 2 * windowStddev

            #print("delta :", delta)

            if (self.pollingEvent.polled_reading > upperDelta) or (self.pollingEvent.polled_reading < lowerDelta):
                self.pollingEvent.poll_after = max(self.pollingEvent.min_poll_time, self.pollingEvent.poll_after / 2)
                newWs = min(self.pollingEvent.window_min_size, ceil(len(self.pollingEvent.window) / 2))

                while len(self.pollingEvent.window) >= newWs:
                    self.pollingEvent.window.popleft()

            else:
                self.pollingEvent.poll_after = min(self.pollingEvent.max_poll_time, self.pollingEvent.poll_after * 2)

            self.pollingEvent.window.append(self.pollingEvent.polled_reading)

        # notify that values are updated
        with self.condition:
            self.condition.notify()

        print("___Polling Results___")
        print("Polled Traffic Reading :", self.pollingEvent.polled_reading)
        print("Next Polling after :", self.pollingEvent.poll_after, "s")
        print("Window contents :", self.pollingEvent.window)
        print()
        #print("Monitored Data :", self.monitored_data)
