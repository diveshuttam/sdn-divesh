import pyshark
import socket
import struct
from threading import Thread
from time import sleep
from datetime import datetime
from datetime import timedelta
from math import ceil

HOST = '192.168.1.3' # The server's IP address
PORT = 4747 # The port used by the server

initialPollingFreq = 10 # expressed in no of times to poll per time_partition
timePartition = 10 # expressed in seconds
granularity = 500 # This is the bucket size expressed in milliseconds.
alpha = 0.1 # weight given to current reading of delta. 1 - alpha weight given to prev reading
maxPollingFreq = int(timePartition * 1000 / granularity)
minPollingFreq = 4
beta = 0.1 # used for history (exponential average)
prevPollingFreq = 10

class CurrentBucket(Thread):
    firstTimePartition = True
    prevByteCount = None
    bucketSize = timedelta(milliseconds=granularity) # bucket size expressed as timedelta object

    currByteCount = 0

    bucketNumber = 0 # keeps track of bucket Number in current time partition
    sampleCount = 0
    averageDelta = 0
    deltaSamples = 0
    delta = 30 # difference % to consider between two reading to consider it as a sample

    def __init__(self, s):
        Thread.__init__(self)
        self.s = s

    def run(self):
        while True:
            sleep(self.bucketSize.total_seconds()) # wait for granularity time
            #after wake

            self.bucketNumber += 1

            if self.prevByteCount != None: # will be satisfied everytime after the first iteration.

                if self.prevByteCount == 0 and self.currByteCount > 0 or self.prevByteCount > 0 and self.currByteCount == 0:
                    self.sampleCount += 1
                elif self.prevByteCount != 0 and self.currByteCount != 0 and abs(self.currByteCount - self.prevByteCount) / self.prevByteCount * 100 >= self.delta:
                    #consider current reading as a sample and increase sample count
                    self.sampleCount += 1

                if self.prevByteCount != 0: # if we have data to calculate the delta, then calculate it
                    self.averageDelta += abs(self.currByteCount - self.prevByteCount) / self.prevByteCount * 100
                    self.deltaSamples += 1

            self.prevByteCount = self.currByteCount

            if self.bucketNumber == int(timePartition * 1000 / granularity): #this condition will be true after every time partition
                # All buckets are covered in current time partition

                if self.deltaSamples != 0:
                    self.averageDelta /= self.deltaSamples
                    self.delta = alpha * self.averageDelta + (1 - alpha) * self.delta

                print('average delta in prev TP:', self.averageDelta)
                print('delta', self.delta)

                global prevPollingFreq

                pollingFreq = 2 * self.sampleCount

                #if you want to take history to decide polling frequency then use next line otherwise comment it out
                pollingFreq = ceil((1 - beta) * prevPollingFreq + beta * pollingFreq) #take history into account
                
                pollingFreq = max(minPollingFreq, min(maxPollingFreq, pollingFreq))

                prevPollingFreq = pollingFreq

                # now send polling frequency to server
                self.s.sendall(struct.pack('!Q', pollingFreq))

                self.bucketNumber = 0
                self.sampleCount = 0
                self.averageDelta = 0
                self.deltaSamples = 0

            self.currByteCount = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT)) # connect to the server

    capture = pyshark.LiveCapture(interface=['h1-eth1', 'h1-eth2'])
    currBucket = CurrentBucket(s)
    currBucket.start()

    s.sendall(struct.pack('!Q', initialPollingFreq)) #sending initial frequency to server. (struct '!Q' used for sending int)

    for packet in capture.sniff_continuously(): #data coming from mirror port. Run continously on main thread
        currBucket.currByteCount += int(packet.length) #packet length is the size of packet
