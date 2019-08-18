from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from threading import Thread
from threading import Condition
from time import sleep
from time import time
from datetime import datetime
import datetime
from collections import deque
from statistics import mean
from statistics import stdev
from math import ceil
import socket
import struct
import queue

HOST = '192.168.1.3'
PORT = 4747        # Port to listen on (non-privileged ports are > 1023)
timePartition = 10 # expressed in seconds
granularity = 500 # This is the bucket size expressed in milliseconds.
startPolling = False


class PollingEventOurApproach(Thread):

    timePartitionEndTime = None
    pollingTimes = None

    def __init__(self, pollingQueue, datapaths, actualData):
        Thread.__init__(self)
        self.pollingQueue = pollingQueue
        self.datapaths = datapaths
        self.actualData = actualData
        self.poll = lambda m, n: [i*n//m + n//(2*m) for i in range(m)] #m -> no of times to poll, n is the time partition

    def run(self):
        while True:
            if self.timePartitionEndTime == None or datetime.datetime.now() > self.timePartitionEndTime: #will match every 10 seconds
                pollingFreq = self.pollingQueue.get()
                self.timePartitionEndTime = datetime.datetime.now() + datetime.timedelta(seconds=timePartition)
                self.pollingTimes = self.poll(pollingFreq, int(timePartition * 1000 / granularity))
                for i in range(len(self.pollingTimes)-1, 0, -1): #instead of absolute time, delay should be put into the list
                    self.pollingTimes[i] -= self.pollingTimes[i - 1] #delay is the difference between current absolute time - prev absolute time
                #delay is time to wait before polling.
            else: #otherwise this will match
                if len(self.pollingTimes) > 0:
                    pollAfter = datetime.timedelta(milliseconds = granularity * self.pollingTimes[0]).total_seconds()
                    del self.pollingTimes[0]
                    sleep(pollAfter)

                    #poll
                    with open("polledData.txt", 'a') as f:
                        print('p,1', self.actualData[1][-1], time(), sep=',', file=f)
                        print('p,2', self.actualData[2][-1], time(), sep=',', file=f)
                        print('p,3', self.actualData[3][-1], time(), sep=',', file=f)
                    # for dp in self.datapaths.values():
                    #     self.request_stats(dp)

    def request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Request port stats
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

class PollingEventCeMon(Thread):

    window = deque()
    window_min_size = 3

    min_poll_time = 0.5
    max_poll_time = 2.5
    poll_after = 0.5

    def __init__(self, actualData, switchNumber):
        Thread.__init__(self)
        self.actualData = actualData
        self.switchNumber = switchNumber

    def run(self):
        while True:
            sleep(self.poll_after)
            if not startPolling:
                continue

            #pollactualData
            polledReading = self.actualData[self.switchNumber][-1]

            with open("polledData.txt", 'a') as f:
                print('c', self.switchNumber, polledReading, time(), sep=',', file=f)

            #initial window filling
            if len(self.window) < self.window_min_size:
                self.window.append(polledReading)
                self.poll_after = 0.5
            else:
                delta = mean(self.window) + 2 * stdev(self.window)

                if polledReading > delta:
                    self.poll_after = max(self.min_poll_time, self.poll_after / 2)
                    newWs = min(self.window_min_size, ceil(len(self.window) / 2))

                    while len(self.window) > newWs:
                        self.window.popleft()

                    self.window.popleft()
                else:
                    self.poll_after = min(self.max_poll_time, self.poll_after * 2)

                self.window.append(polledReading)


class PollingServer(Thread):

    def __init__(self, pollingQueue):
        Thread.__init__(self)
        self.pollingQueue = pollingQueue

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by Mirrored Host', addr)
                global startPolling
                startPolling = True
                unpacker = struct.Struct('!Q')

                while True:
                    pollingFreq = unpacker.unpack(conn.recv(unpacker.size))[0]
                    print('Polling Freq :', pollingFreq)
                    self.pollingQueue.put(pollingFreq)

class ActualPoller(Thread):

    def __init__(self, datapaths):
        Thread.__init__(self)
        self.datapaths = datapaths

    def run(self):
        while True:
            sleep(0.1)
            for dp in self.datapaths.values():
                self.request_stats(dp)

    def request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Request port stats
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

class ControllerMonitoringServer(simple_switch_13.SimpleSwitch13):

    pollingQueue = queue.Queue()
    actualData = {1: [], 2: [], 3: []}
    lastReading = [0,0,0]


    def __init__(self, *args, **kwargs):
        super(ControllerMonitoringServer, self).__init__(*args, **kwargs)
        self.datapaths = {}
        #self.monitor_thread = hub.spawn(self._monitor)
        self.pollingEventOurApproach = PollingEventOurApproach(self.pollingQueue, self.datapaths, self.actualData)
        self.pollingEventCeMons1 = PollingEventCeMon(self.actualData, 1) #for every switch. 1,2 and 3 we need this because window is different for all switches and hence the polling time will differ for every switch
        self.pollingEventCeMons2 = PollingEventCeMon(self.actualData, 2)
        self.pollingEventCeMons3 = PollingEventCeMon(self.actualData, 3)
        self.pollingServer = PollingServer(self.pollingQueue)
        self.actualPoller = ActualPoller(self.datapaths)

        self.pollingServer.start()
        self.actualPoller.start()
        self.pollingEventOurApproach.start()
        self.pollingEventCeMons1.start()
        self.pollingEventCeMons2.start()
        self.pollingEventCeMons3.start()

        with open("polledData.txt", "w") as f:
            pass


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
        datapathId = ev.msg.datapath.id

        traffic = 0

        for stat in sorted(body, key=attrgetter('port_no')):
            traffic += (stat.rx_bytes + stat.tx_bytes)

        # divide by 2 because every packet is counted twice. Once when sent,
        # and second when received
        traffic /= 2

        reading = traffic - self.lastReading[datapathId - 1]

        self.actualData[datapathId].append(reading)

        with open("polledData.txt", "a") as f:
            print('o', datapathId , reading ,time(), sep=',', file=f)

        self.lastReading[datapathId - 1] = traffic

        print("Polled Reading :", traffic)
