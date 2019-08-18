#!/bin/bash

ryu-manager controller.py 
mn -v debug --custom sdn.py  --mac --controller ryu  --topo sdntopo
