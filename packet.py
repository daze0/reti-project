#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 22:13:12 2021

@author: daze
"""

import time

class Packet:
    #Constructor
    def __init__(self, ethernet_header, IP_header, payload):
        self._ethernet_header = ethernet_header
        self._IP_header = IP_header
        self._epoch_t = time.time()
        self._payload = payload
        
    # Builder pattern methods
    def IP_header(self, src, dst):
        self._IP_header = src+dst
        return self
    
    def ethernet_header(self, src, dst):
        self._ethernet_header = src+dst
        return self    
    
    def epoch_time(self):
        self._epoch_t = time.time()
        return self
    
    def payload(self, payload):
        self._payload = payload
        return self
    
    # Getters methods section
    def get_src_ip(self):
        return self._ethernet_header[0:12]
    
    def get_dst_ip(self):
        return self._ethernet_header[12:]#22
    
    def get_src_mac(self):
        return self._IP_header[0:17]
    
    def get_dst_mac(self):
        return self._IP_header[17:]#19
    
    def get_epoch_time(self):
        return self._epoch_t
    
    def get_headers(self):
        return self._IP_header+self._ethernet_header+str(self._epoch_t)
    
    def get_payload(self):
        return self._payload