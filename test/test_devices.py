#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 12:19:14 2021

@author: daze
"""

from subprocess import Popen
import sys
sys.path.append('../')
import factories as f
import signal

def _signal_handler(self, signal, frame, subprocesses_list):
        try:
            for popen in subprocesses_list:
                popen.kill()
        finally:
            print('Ctrl+c pressed: all subprocesses have been killed..')
            sys.exit(0)
            
def execute(target):
    return Popen(["python", target + ".py"])
    
def test():
    print("Device 1")
    dev1 = execute("test_dev1")
    
    print("Device 2")
    dev2 = execute("test_dev2")
    
    print("Device 3")
    dev3 = execute("test_dev3")
    
    print("Device 4")
    dev4 = execute("test_dev4")
    
    print("Press CTRL+C to kill each device execution")
    # CTRL+C signal handler
    signal.signal(signal.SIGINT, self._signal_handler, list(dev1, dev2, dev3, dev4))
    running = True
    while running:
        continue
    
if __name__ == "__main__":
    test()

