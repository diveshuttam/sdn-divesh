import matplotlib.pyplot as plt
from statistics import mean
from statistics import stdev
from math import ceil
from collections import deque
import numpy as np

# All time is in units unless explicitly stated

bucketTime = 500 # expressed in ms. 1 unit of time is equal to bucketTime

time = list()
packetCount = list()
byteCount = list()

fig, ax = plt.subplots()
ax.set_title('Results of polling algorithms - Nyquist vs CeMon')
lines = list()

for line in open('traffic.txt', 'r').readlines():
    (t, pkCnt, byteCnt) = line.split()
    time.append(int(t))
    packetCount.append(int(pkCnt))
    byteCount.append(int(byteCnt))

def plotActualTraffic(time, traffic):
    line1, = ax.plot(time, traffic, label='Actual traffic')
    lines.append(line1)

def plotUsingCeMon(time, traffic):
    sampledData = [None] * len(traffic)

    totalPolls = 0
    window = deque()
    window_min_size = 3

    min_poll_time = 1
    max_poll_time = 5
    poll_after = 1

    print("Using CeMon approach (Sliding Window)")
    print("Window min size is", window_min_size)
    print("Minimum polling time is :", min_poll_time)
    print("Maximum polling time is :", max_poll_time)

    i = 0
    while i < len(traffic):

        sampledData[i] = traffic[i]
        totalPolls += 1

        # initial window filling
        if len(window) < window_min_size:
            window.append(traffic[i]) # fill window
            i += 1 # next
        else:
            windowMean = mean(window)
            windowStddev = stdev(window)

            upperDelta =  windowMean + 2 * windowStddev
            lowerDelta = windowMean - 2 * windowStddev

            if (traffic[i] > upperDelta) or (traffic[i] < lowerDelta):
                poll_after = max(min_poll_time, poll_after // 2)
                newWs = min(window_min_size, ceil(len(window) / 2))

                while len(window) >= newWs:
                    window.popleft()

            else:
                poll_after = min(max_poll_time, poll_after * 2)

            window.append(traffic[i])
            i += poll_after

    sampledData[0] = traffic[0]
    sampledData[-1] = traffic[-1]

    #fill missing values in sample data by linear interpolation
    lastNone = 0
    i = 1
    while i < len(sampledData):
        if sampledData[i] != None:
            # fill all None values between current i and lastNone
            for j in range(lastNone + 1, i):
                sampledData[j] = np.interp(j, [lastNone, i], [sampledData[lastNone], sampledData[i]])

            lastNone = i
        i += 1

    errorList = []

    for i in range(0, len(sampledData)):
        if (sampledData[i] != None):
            diff = abs(traffic[i] - sampledData[i]) / traffic[i] * 100
            errorList.append(diff)

    print("Total Polls :", totalPolls, "out of :", len(traffic))
    print("error% = ", round(sum(errorList)/len(errorList), 2), "%",sep='')
    line3, = ax.plot(time, sampledData, label='CeMon approach')
    lines.append(line3)

def plotUsingNyquist(time, traffic):
    pollingFreq = 10 # no of times to poll in given partition time
    partitionTime = 20 # units of time partition
    lastPolled = 0
    totalPolls = 0
    diff = 35 # difference % to be considered

    sdelta = diff
    deltaVar = diff / 2

    print("Using our approach (Using Nyquist Theorem)")
    print("Initial polling frequency is", pollingFreq)
    print("Initial delta is ", diff, "%", sep='')
    print("Total time (in units) :", len(traffic))
    print("Partition time (in units) :", partitionTime)

    actualTraffic = traffic
    sampledData = [None] * len(actualTraffic)

    totalPartitions = len(actualTraffic) // partitionTime
    print("Total partitions :", totalPartitions)

    for i in range(0, totalPartitions):
        pollingFreq = min(max(pollingFreq, 2), partitionTime)

        #start and end index of current partition
        start = partitionTime * i
        end = partitionTime * (i + 1) - 1

        poll = lambda m, n: [i*n//m + n//(2*m) + start for i in range(m)]
        poll = poll(pollingFreq, partitionTime)
        for j in poll:
            sampledData[j] = actualTraffic[j]
        totalPolls += len(poll)

        newPollingFreq = 0
        currDelAv = 0
        for j in range(start, end + 1):
            if j > 0:
                percentageDiff = abs(actualTraffic[j] - actualTraffic[j - 1]) / actualTraffic[j] * 100
                currDelAv += percentageDiff
                if percentageDiff > diff:
                    newPollingFreq += 1

        if start == 0:
            currDelAv = currDelAv / (partitionTime - 1)
        else:
            currDelAv = currDelAv / partitionTime



        # Moving exponential approach to make delta adaptive
        alpha = 0.1
        diff = (1 - alpha) * diff + alpha * currDelAv

        # SRTT approach
        # alpha = 0.125
        # beta = 0.25
        # deltaVar = (1 - beta) * deltaVar + beta * abs(sdelta - currDelAv)
        # sdelta = (1 - alpha) * sdelta + alpha * currDelAv
        # diff = sdelta + 4 * deltaVar
        # print("delta :", round(diff, 2), "sdelta :", round(sdelta, 2), "deltaVar :", round(deltaVar, 2))

        #Nyquist theorem
        newPollingFreq *= 2

        pollingFreq = newPollingFreq


    #linear interpolation
    if sampledData[0] == None:
        sampledData[0] = actualTraffic[0]
        totalPolls += 1

    lastNone = 0
    i = 1
    while i < len(sampledData):
        if sampledData[i] != None:
            # fill all None values between current i and lastNone
            for j in range(lastNone + 1, i):
                sampledData[j] = np.interp(j, [lastNone, i], [sampledData[lastNone], sampledData[i]])
            lastNone = i
        i += 1

    # error calculation
    errorList = []
    for i in range(0, len(sampledData)):
        if (sampledData[i] != None):
            diff = abs(actualTraffic[i] - sampledData[i]) / actualTraffic[i] * 100
            errorList.append(diff)

    print("Total Polls :", totalPolls, "out of :", len(traffic))
    print("error% = ", round(sum(errorList)/len(errorList), 2), "%",sep='')
    line2, = ax.plot(time, sampledData, label='Our approach')
    lines.append(line2)

new = []
for i in range(len(byteCount)):
    new.append(byteCount[i]/packetCount[i])
plotActualTraffic(time, byteCount)
plotUsingNyquist(time, byteCount)
print()
print()
plotUsingCeMon(time, byteCount)

leg = ax.legend(loc='upper left', fancybox=True, shadow=True)
leg.get_frame().set_alpha(0.4)

# we will set up a dict mapping legend line to orig line, and enable
# picking on the legend line
lined = dict()
for legline, origline in zip(leg.get_lines(), lines):
    legline.set_picker(5)  # 5 pts tolerance
    lined[legline] = origline

plt.gca().set_xlabel("time")
plt.gca().set_ylabel("bytes")
#plt.legend(loc='upper right')

def onpick(event):
    # on the pick event, find the orig line corresponding to the
    # legend proxy line, and toggle the visibility
    legline = event.artist
    origline = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)
    fig.canvas.draw()

fig.canvas.mpl_connect('pick_event', onpick)

plt.show()
