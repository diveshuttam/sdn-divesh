import socket
from struct import *
import datetime
import pcapy
import sys, csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

hashmap = {}
samples = []
s = {}

def main(argv):
        devices = pcapy.findalldevs()
        print (devices)

        print ("Available devices are:")
        for d in devices:
                print (d)

        #dev = str(input("Enter device name to sniff: "))
        dev = 'any'
        print ("Sniffing device " + dev)

        cap = pcapy.open_live(dev, 65536, 1, 1000) #open_live(device, max bytes to capture, promisc (ignored for any), to_ms read timeout)
        #change = str(input("Enter the percentage change you want to measure: "))
        timeout = 0
        prevkey = ''
        global hashmap
        sampledata = open('sampletimes.txt', 'w')
        bucketdata = open('bucket.txt', 'w')
        while(1):
                #print ("Hashmap: " + str(hashmap))
                try:
                        (header, packet) = cap.next() # (packet header, string data)
                        timeout = 0
                        #print ('%s: captured %d bytes' %(datetime.datetime.now(), header.getlen()))
                        key = str(datetime.datetime.now().replace(microsecond=0))
                        headerlen = header.getlen()

                        if (key in hashmap.keys()):
                                hashmap[key] += headerlen
                                prevkey = key
                        else:
                                if (len(hashmap.keys()) is not 0):
                                        bucketstring = prevkey  + ',' + str(hashmap[prevkey])

                                        bucketdata.write(bucketstring + '\n')
                                        bucketdata.flush()
                                hashmap[key] = headerlen
                                if len(samples) == 0:
                                        samples.append(key)
                                else:
                                        delta = (abs(hashmap[samples[-1]] - hashmap[prevkey] )/hashmap[samples[-1]]) * 100
                                        print ("------------delta----------------- = " + str(delta))
                                        if delta > 40:
                                                samples.append(prevkey)
                                                sampledata.write(prevkey + '\n')
                                                sampledata.flush()
                                                print('11\n')
                                        else:
                                                print("Not appending in samples")
                                        print ("hashmap length: " + str(len(hashmap.keys())))
                                        print ("Hashmap: " + str(OrderedDict(sorted(hashmap.iterkeys()))))
                                        print ("samples length: " + str(len(samples)))
                                        print ("***samples***: " + str(samples))

                except KeyboardInterrupt:
                        print ("Hashmap: " + str(hashmap))
                        print ("hashmap length: " + str(len(hashmap.keys())))
                        print ("samples:" + str(samples))
                        print ("samples length: " + str(len(samples)))
                        sampledata.close()
                        bucketdata.close()
                        break
                except:
                        print ("no packets")
                #finally:

                #       print ("Hashmap: " + str(hashmap))
                #       print ("***samples***: " + str(samples))
        #print (hashmap)

        for item in samples:
                s[item] = hashmap[item]
        plt.ion()
        lists = sorted(hashmap.items()) # sorted by key, return a list of tuples
        print ('Plotting..')
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        plt.xticks(rotation=90)
        plt.plot(x, y)

        list1 = sorted(s.items()) # sorted by key, return a list of tuples
        print ('Plotting..')
        x1, y1 = zip(*list1)
        #plt.xticks(rotation=90)
        plt.plot(x1, y1, linestyle = ':')


        plt.show(block=True)


if __name__ == "__main__":
        main(sys.argv)
