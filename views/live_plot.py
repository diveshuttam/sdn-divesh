import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime


class LivePlot(object):
    """
    Initialize the plot
    @param wmaxt is windows maxt
    """
    def __init__(self, interval=0.001, wmaxt=2):
        self.interval=interval
        self.fig, self.ax = plt.subplots()
        self.wmaxt = wmaxt
        self.maxt = 0
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(-.1, 1.1)
        self.ax.set_xlim(0, self.wmaxt)
    
    def start(self):
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=self.interval,
                                    blit=True)
        plt.show()

    def update(self, y):
        if self.maxt > self.tdata[0] + self.wmaxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.wmaxt)
            self.ax.figure.canvas.draw()
        self.line.set_data(self.tdata, self.ydata)
        return self.line,
    
    def nextpoint(self,y):
        self.tdata.append(datetime.now())
        self.ydata.append(y)
        self.maxt=max(self.maxt,y)

if __name__ == '__main__':
    plot = LivePlot()
    import random
    for i in range(20):
        plot.nextpoint(random.randint(0,10))