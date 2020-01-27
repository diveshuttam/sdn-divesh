from collector.capture import BucketCapture
from collector.frequency import FrequencyCalculator
from views.live_plot import LivePlot
from controller.server import Server
from collector.client import Client
import logging
from datetime import datetime
if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    
    capture = BucketCapture("enp0s3",10/11,11)
    fq = FrequencyCalculator()
    plot = LivePlot(interval=1000,bucketrange=11)
    plot1 = LivePlot(interval=1000,bucketrange=11)
    host,port = '0.0.0.0',4747
    server = Server(host,port)
    client = Client(host,port)
    def plot_data(buckets):
        logging.debug("called update hook")
        for bucket in buckets:
            plot.nextpoint(bucket._starttime.timestamp(), bucket._bytes)
    def plot_frequency(freq):
        logging.debug("-------------\ncalled freq hook\n-----------------")
        plot1.nextpoint(datetime.now().timestamp(),freq)
    fq.register(plot_frequency)
    fq.register(client.frequency_send)
    capture.register(fq.calculate_frequency)
    capture.register(plot_data)
    
    capture.start()
    server.start()
    client.start()
    plot1.start(False)
    plot.start()
    server.join()
    client.join()
    capture.join()
    plot.join()
    plot1.join()