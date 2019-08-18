import pyshark
from threading import Thread
from time import sleep
from datetime import datetime
from datetime import timedelta

buckets = []

class Bucket:
    def __init__(self, time, packetCount, byteCount):
        self.time = time
        self.packetCount = packetCount
        self.byteCount = byteCount

class CurrentBucket(Thread):
    bucketSize = timedelta(milliseconds=500) # bucket size expressed as timedelta object
    time = datetime.now() + bucketSize # All packets with their time <= self.time belongs to currentBucket
    packetCount = 0
    byteCount = 0

    def run(self):
        while True:
            global buckets
            sleep(self.bucketSize.total_seconds())
            buckets.append(Bucket(self.time, self.packetCount, self.byteCount))
            self.time += self.bucketSize
            self.packetCount = 0
            self.byteCount = 0


capture = pyshark.LiveCapture(interface='h3-eth0')
currBucket = CurrentBucket()
currBucket.start()

try:
    for packet in capture.sniff_continuously():
        currBucket.packetCount += 1
        currBucket.byteCount += int(packet.length)
except KeyboardInterrupt:
    pc = 0
    bc = 0
    for bucket in buckets:
        pc += bucket.packetCount
        bc += bucket.byteCount
        print("Packet Count :", bucket.packetCount, ", Byte Count :", bucket.byteCount)
    print()
    print("PC:", pc, " BC:", bc)
    i = 1
    f = open("traffic.dat", "w")
    for bucket in buckets:
        if bucket.packetCount == 0 and i == 1:
            continue
        print(i, bucket.packetCount, bucket.byteCount, file=f)
        i += 1
    f.close()
    exit()
