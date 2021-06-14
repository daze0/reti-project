#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 26 16:42:30 2021
@author: fedebruno
"""
import time, random

MIN_TEMP = -99
MAX_TEMP = 99

MIN_HUMIDITY = 0
MAX_HUMIDITY = 100

class Measurement:      
    def get_time(self):
        t = time.localtime()
        return time.strftime("%H:%M:%S", t)
    
    def get_temperature(self):
        return str(random.randrange(MIN_TEMP, MAX_TEMP))
    
    def get_humidity(self):
        return str(random.randrange(MIN_HUMIDITY, MAX_HUMIDITY))