import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import pprint

#style.use('fivethirtyeight')

fig, ax = plt.subplots()
ax.set_title('Live Polling')
lines1 = list()
lined = dict()

start = False

#not used!!!
def getError():
    graph_data = open('polledData.txt', 'r').read()
    lines = graph_data.split('\n')
    orig = {1: {}, 2: {}, 3: {}}
    ourPoll = {1: {}, 2: {}, 3: {}}
    ceMonPoll = {1: {}, 2: {}, 3: {}}

    start_time = float(lines[0].split(',')[-1])
    
    getBucket = lambda t : int(round((float(t) - start_time)*10))
    last_bucket = 0

    for line in reversed(lines):
        if(len(line) > 1):
            t, i, a, b = line.split(',')
            if t == 'o' and int(i) == 1:
                last_bucket = getBucket(b)
                break;


    # print(start_time)
    # print(last_bucket)
    for line in lines:
        if len(line) > 1:
            _type, _id, traffic, time = line.split(',')
            if _type == 'o': #actual
                orig[int(_id)][getBucket(time)] = float(traffic)
                #ysOrig[int(id)].append(float(traffic))
            elif _type == 'p': #polled
                ourPoll[int(_id)][getBucket(time)] = float(traffic)
            elif _type == 'c': #cemoax.ln polled
                ceMonPoll[int(_id)][getBucket(time)] = float(traffic)
    
    # print(orig[2].keys())
    # print('_______________________________')
    # print(ourPoll[2].keys())
    # print('_______________________________')
    # print(ceMonPoll[2].keys())

    # for i in range(1,2):
    #     common = []
    #     for j in range(0, len(xsPoll[i])):
    #         for k in range(0, len(xsOrig[i])):
    #             if xsOrig[i][k] >= xsPoll[i][j]:
    #                 #k-1 is the required index with same value
    #                 common.append((k-1, j))
    #                 break

        # for j in range(0, len(common) - 1):
        #     start = common[j][1]
        #     end = common[j+1][1]
        #     print("d", start, end, xsOrig[i][common[j][0]], xsPoll[i][common[j][1]])
        #
        #     for k in range(common[j][0]+1, common[j+1][0]):
        #         pollInterp = np.interp(xsOrig[i][k], [xsPoll[i][start], xsPoll[i][end]], [ysPoll[i][start], ysPoll[i][end]])
        #         print(ysPoll[i][start], ysPoll[i][end], pollInterp, ysOrig[i][k])
#np.interp(j, [lastNone, i], [sampledData[lastNone], sampledData[i]])


    def error_(ttm_o, ttm_p):
        # time-traffic map original and time-traffic map polled
        def getVal(obj, t):
            if t > last_bucket:
                return -1
            if t in obj:
                return obj[t]
            return getVal(obj, t + 1)

        err = 0
        d = 0
        for key in ttm_p.keys():
            v = getVal(ttm_o, key)
            if v != -1:
                d += v          
                err += abs(ttm_p[key] - v)
        return err / d
    print("Errors:")
    print("Our Poll")
    print("switch 1: %s"% error_(orig[1], ourPoll[1]))
    print("switch 2: %s"% error_(orig[2], ourPoll[2]))
    print("switch 3: %s"% error_(orig[3], ourPoll[3]))
    print("CeMon Poll")
    print("switch 1: %s"% error_(orig[1], ceMonPoll[1]))
    print("switch 2: %s"% error_(orig[2], ceMonPoll[2]))
    print("switch 3: %s"% error_(orig[3], ceMonPoll[3]))

def animate(i):
    getError()
    graph_data = open('polledData.txt', 'r').read()
    lines = graph_data.split('\n')
    xsOrig = {1: [], 2: [], 3: []} #1,2 and 3 refers to the switches. x axis contains timestamp, y axis contains byte count
    ysOrig = {1: [], 2: [], 3: []}

    xsPoll = {1: [], 2: [], 3: []}
    ysPoll = {1: [], 2: [], 3: []}

    xsPollCeMon = {1: [], 2: [], 3: []}
    ysPollCeMon = {1: [], 2: [], 3: []}

    for line in lines:
        if len(line) > 1:
            type, id, traffic, time = line.split(',')
            if type == 'o': #actual
                xsOrig[int(id)].append(float(time))
                ysOrig[int(id)].append(float(traffic))
            elif type == 'p': #polled
                xsPoll[int(id)].append(float(time))
                ysPoll[int(id)].append(float(traffic))

            elif type == 'c': #cemon polled
                xsPollCeMon[int(id)].append(float(time))
                ysPollCeMon[int(id)].append(float(traffic))


    ax.clear()
#    l1, = ax.plot(xsOrig[1], ysOrig[1], label='S1 Actual')
    l2, = ax.plot(xsOrig[2], ysOrig[2], label='S2 Actual',color='b')
#    l3, = ax.plot(xsOrig[3], ysOrig[3], label='S3 Actual')

#    l4, = ax.plot(xsPoll[1], ysPoll[1], label='S1 Polled')
    l5, = ax.plot(xsPoll[2], ysPoll[2], label='S2 Polled',color='y')
#    l6, = ax.plot(xsPoll[3], ysPoll[3], label='S3 Polled')

#    l7, = ax.plot(xsPollCeMon[1], ysPollCeMon[1], label='S1 Polled CeMon')
    l8, = ax.plot(xsPollCeMon[2], ysPollCeMon[2], label='S2 Polled CeMon',color='r')
#    l9, = ax.plot(xsPollCeMon[3], ysPollCeMon[3], label='S3 Polled CeMon')

    ax.legend()


try:
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.gca().set_xlabel("time")
    plt.gca().set_ylabel("bytes")

    plt.show()
except KeyboardInterrupt:
    pass

