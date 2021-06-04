#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 26 16:42:30 2021

@author: fedebruno
"""
import time, random

class Measurement:
    def __init__(self):
        self.t = time.localtime()
        self.current_time = time.strftime("%H:%M:%S", self.t)
        self.temperature = str(random.randrange(-99, 99))
        self.humidity = str(random.randrange(0, 100))
       
    def get_time(self):
        return self.current_time
    
    def get_temperature(self):
        return self.temperature
    
    def get_humidity(self):
        return self.humidity