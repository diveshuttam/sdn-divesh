from collector.capture import BucketCapture
from collector.frequency import FrequencyCalculator
from views.live_plot import LivePlot
import logging

if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
    
    capture = BucketCapture("enp0s3",0.1,20)
    fq = FrequencyCalculator()
    plot = LivePlot(interval=1000,bucketrange=20)
    def update_hook(buckets):
        logging.debug("called update hook")
        for bucket in buckets:
            plot.nextpoint(bucket._starttime.timestamp(), bucket._bytes)
    capture.register(fq.calculate_frequency)
    capture.register(update_hook)
    
    plot.start()
    capture.start()
    capture.join()
    plot.join()