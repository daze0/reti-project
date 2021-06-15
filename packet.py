#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 22:13:12 2021

@author: daze
"""

import time
    
class Packet:
    # Constructor
    def __init__(self, ethernet_header='', IP_header='', payload=''):
        self._ethernet_header = ethernet_header
        self._IP_header = IP_header
        self._epoch_t = time.time()
        self._payload = payload
    
    # Setters methods section
    def set_IP_header(self, src, dst):
        self._IP_header = src+dst
        return self
    
    def set_ethernet_header(self, src, dst):
        self._ethernet_header = src+dst
        return self    
    
    def set_epoch_time(self):
        self._epoch_t = time.time()
        return self
    
    def set_payload(self, payload):
        self._payload = payload
        return self
  
    # Getters methods section
    def get_src_mac(self):
        return self._ethernet_header[0:17]
    
    def get_dst_mac(self):
        return self._ethernet_header[17:]
    
    def get_src_ip(self):
        return self._IP_header[0:12]
    
    def get_dst_ip(self):
        return self._IP_header[12:]
    
    def get_epoch_time(self):
        return self._epoch_t
    
    def get_headers(self):
        return self._ethernet_header+self._IP_header+str(self._epoch_t)
    
    def get_payload(self):
        return self._payload
    
    def __str__(self):
        return "HEADERS\nethernet: {eth_header}\nip: {ip_header}\nepoch time: {epoch_time}\n".format(eth_header=self._ethernet_header, ip_header=self._IP_header, epoch_time=self._epoch_t)\
            + "PAYLOAD\n{payload}".format(payload=self._payload)
    
    
class PacketBuilder:
    def __init__(self):
        self._pkt = Packet()
        
    def IP_header(self, src, dst):
        self._pkt.set_IP_header(src, dst)
        return self
    
    def ethernet_header(self, src, dst):
        self._pkt.set_ethernet_header(src, dst)
        return self    
    
    def epoch_time(self):
        self._pkt.set_epoch_time()
        return self
    
    def payload(self, payload):
        self._pkt.set_payload(payload)
        return self
    
    def build(self):
        return self._pkt