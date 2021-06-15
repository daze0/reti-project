#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 22:55:07 2021

@author: daze
"""

from threading import Thread
import time as t

class Timer(Thread):
    def __init__(self, limit):
        Thread.__init__(self)
        self._limit = limit
        self._elapsed_time = 0.0 # secs
        self._is_running = True
        self._time_zero = t.time()
        self._just_started = True
    
    def run(self):
        while self._is_running:
            if self._just_started:
                before = self._time_zero
                self._just_started = False
            now = t.time()
            self._elapsed_time += now - before
            before = now
            t.sleep(1)
    
    def limit_reached(self):
        if self._elapsed_time >= self._limit:
            return True
        else:
            return False
    
    def reset(self):
        self._elapsed_time = 0
        self._time_zero = t.time()
        self._just_started = True
    
    def stop(self):
        self._is_running = False
        