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

class TestDevices:
    
    def __init__(self):
        self._subprocesses_list = []
        self._running = True
            
    def _execute(self, target):
        return Popen(["python", target + ".py"])
    
    def test(self):
        print("Device 1")
        dev1 = self._execute("test_dev1")
        self._subprocesses_list.append(dev1)
        
        print("Device 2")
        dev2 = self._execute("test_dev2")
        self._subprocesses_list.append(dev2)
        
        print("Device 3")
        dev3 = self._execute("test_dev3")
        self._subprocesses_list.append(dev3)
    
        print("Device 4")
        dev4 = self._execute("test_dev4")
        self._subprocesses_list.append(dev4)
        
        print("Press CTRL+C to kill each device execution")
        # CTRL+C signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        while self._running:
            continue
        
    def _signal_handler(self, signal, frame):
        try:
            self._running = False
            # SIGINT propagation
            for sub in self._subprocesses_list:
                sub.send_signal(signal.SIGINT)
        finally:
            print('Ctrl+c pressed: all subprocesses have been killed..')
            sys.exit(0)
    
if __name__ == "__main__":
    t = TestDevices()
    t.test()

