#!/usr/bin/python3
"""
This module helps in capturing buckets of data.
Need to call with 'sudo' due to packet collection
"""

from threading import Thread, Lock
from datetime import datetime
import time
import logging
import pyshark
import json
import requests

"""
Bucket class is the representation of a Data Bucket
"""
class Bucket():
    def __init__(self,starttime,endtime,bytes_):
        self._starttime=starttime
        self._endtime=endtime
        self._bytes=bytes_


"""
Bucket capture class runs threads to captures packets
from given interface and form a bucket
"""
class BucketCapture():
    """
    Initialize the data
    @param is the interval in seconds
    @maxbuckets buckets to accumulte for calculating frequency
    """
    def __init__(self,interface,interval,maxbuckets):
        self._interface = interface

        self._interval = interval
        self._interval_lock = Lock()
        
        self._maxbuckets = maxbuckets

        self._hooks = []
        self._running = False
        self._buckets = []

        self._current_bytes = 0
        self._current_bytes_lock = Lock()
        
        self._capture = None
        self._capture_thread = None
        self._bucket_thread = None
        

    """
    Starts running the Capture and Bucketization
    """
    def start(self):
        self._capture = pyshark.LiveCapture(interface=self._interface)
        
        """
        Capture function for the capture thread
        """
        def _capture_function():
            logging.debug(" capture thread starting")
            for packet in self._capture.sniff_continuously():
                with self._current_bytes_lock:
                    logging.debug("acquired current bytes lock")
                    self._current_bytes+=int(packet.length)
                    logging.debug(f"updated bytes to {self._current_bytes}")
                    logging.debug("released current bytes lock")
                    logging.debug(f"captured packet with {packet.length} bytes")

        """
        Bucket function for the bucket thread
        Calls the hooks when the maxbuckets is reached
        """
        def _bucket_function():
            while(True):
                starttime=datetime.now()
                logging.debug(starttime)

                self._interval_lock.acquire()
                interval=self._interval
                self._interval_lock.release()

                logging.debug("going to sleep")
                time.sleep(interval)
                logging.debug("wakeup")

                # Create a bucket
                with self._current_bytes_lock:
                    logging.debug("acquried current bytes lock")
                    endtime =datetime.now()
                    b = Bucket(starttime,endtime, self._current_bytes)
                    logging.debug(f"added bucket {starttime}, {endtime}, {self._current_bytes}")
                    self._current_bytes = 0
                    logging.debug("released current bytes lock")

                self._buckets.append(b)

                if(len(self._buckets)==self._maxbuckets):
                    # Call the hooks (in other thread)
                    for hook in self._hooks:
                        try:
                            Thread(target=hook,args=([self._buckets[:]])).start()
                        except:
                            pass
                    
                    logging.debug(f"-----------")
                    logging.debug(f"collected {self._maxbuckets} packets with {sum(map(lambda x:x._bytes, self._buckets))} bytes")
                    logging.debug(f"-----------")
                    self._buckets=[]

        self._bucket_thread = Thread(target=_bucket_function,name="Bucketing Thread")
        self._capture_thread = Thread(target=_capture_function,name="Capture Thread")
        self._running = True

        self._capture_thread.start()
        self._bucket_thread.start()

    """
    Stops and resets the capture
    """
    def stop(self):
        self._running = False
        self._buckets = []
        self._capture = None
        self._capture_thread._stop()
        self._capture_thread = None
        self._current_bytes = 0
        
    """
    Let the main thread join the capture and bucketing threads
    """
    def join(self):
        if(self._running==True):
            self._bucket_thread.join()
            self._capture_thread.join()

    """
    Change the interval of polling
    """
    def interval(self,new_interval,maxbuckets):
        with self._interval_lock:
            self._interval=new_interval
            self._maxbuckets=maxbuckets

    """
    Registers hooks to the maxbucket reached event
    """
    def register(self, hook):
        self._hooks.append(hook)


"""
Main to test out the module
"""
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s: %(funcName)s"
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")
    capture = BucketCapture("enp0s3",0.1,20)
    capture.start()
    capture.join()