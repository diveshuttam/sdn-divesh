from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from threading import Thread, Lock
from collections import deque

class LivePlot(object):
    """
    Initialize the plot
    @param wmaxt is windows maxt
    """
    def __init__(self, interval=1000,bucketrange=20):
        self.interval=interval
        self.bucketrange=bucketrange
        self.fig, self.ax = plt.subplots()
        self.maxt = 0
        self.tdata = deque([])
        self.ydata = deque([])
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(0, 0)
        self.ax.set_xlim(0, 0)
        self.datalock = Lock()
        Thread(target=self.start).start()

    def start(self):
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=self.interval,
                                            blit=True)
        plt.show()

    def update(self, y):
        print(f"called update with {y}")
        self.ax.figure.canvas.draw()
        with self.datalock:
            tdata = self.tdata
            ydata = self.ydata
        try:
            minx=min(tdata)
            miny=min(ydata)
            maxx=max(tdata)
            maxy=max(ydata)
            self.ax.set_ylim(miny,maxy)
            self.ax.set_xlim(minx,maxx)
        except:
            pass
        self.line.set_data(tdata, ydata)
        return self.line,
    
    def nextpoint(self,x,y):
        print(f"called nextpoint with {(x,y)}")
        with self.datalock:
            self.tdata.append(x)
            self.ydata.append(y)
            if(len(self.tdata)>self.bucketrange):
                self.tdata.popleft()
                self.ydata.popleft()

if __name__ == '__main__':
    plot = LivePlot(interval=1000,bucketrange=200)
    from capture import BucketCapture
    import logging
    format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    capture = BucketCapture("enp0s3",0.1,20)
    def update_hook(buckets):
        print("called update hook")
        for bucket in buckets:
            plot.nextpoint(bucket._starttime.timestamp(), bucket._bytes)
    capture.register(update_hook)
    capture.start()
    capture.join()