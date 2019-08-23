"""
This runs on the collector and sends final polling frequency to the controller
"""
import requests


ip = '192.168.1.1'
port = 4747


def post(buckets):
    requests.post(ip, calculate_frequency(buckets))