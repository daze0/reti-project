#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 22:13:12 2021

@author: daze
"""

import time

ETHNET_INDEX = 17
MAX_SRC_IP_LEN = 12

class Packet:
    # Constructor
    def __init__(self, ethernet_header='', IP_header='', payload='', special=False):
        self._ethernet_header = ethernet_header
        self._IP_header = IP_header
        self._epoch_t = time.time()
        self._payload = payload
        # Special Packets differentiates from normal ones
        # because their payload is encoded
        self._is_special_pkt = special 
    
    # Setters methods section
    def set_IP_header(self, src, dst):
        if len(src) < MAX_SRC_IP_LEN:
            src += "*"
            while len(src) < MAX_SRC_IP_LEN:
                src += "*"
        self._IP_header = src+dst
        return self
    
    def set_ethernet_header(self, src, dst):
        self._ethernet_header = src+dst
        return self    
    
    def set_epoch_time(self):
        self._epoch_t = time.time()
        return self
    
    def set_payload(self, payload):
        if isinstance(payload, bytes):
            self._payload = payload.decode()
        else:
            self._payload = payload
        return self
  
    # Getters methods section
    def get_src_mac(self):
        return self._ethernet_header[0:ETHNET_INDEX]
    
    def get_dst_mac(self):
        return self._ethernet_header[ETHNET_INDEX:]
    
    def get_src_ip(self):
        src_ip = self._IP_header[0:MAX_SRC_IP_LEN]
        return src_ip.strip('*')
    
    def get_dst_ip(self):
        return self._IP_header[MAX_SRC_IP_LEN:]
    
    def get_epoch_time(self):
        return self._epoch_t
    
    def get_headers(self):
        return self._ethernet_header+self._IP_header+str(self._epoch_t)
    
    def get_payload(self):
        if self._is_special_pkt:
            return bytes(self._payload.encode())
        return self._payload
    
    def __str__(self):
        return "HEADERS\nethernet: {eth_src} | {eth_dst}\nip: {ip_src} | {ip_dst}\nepoch time: {epoch_time}\n".format(eth_src=self.get_src_mac(), eth_dst=self.get_dst_mac(), ip_src=self.get_src_ip(), ip_dst=self.get_dst_ip(), epoch_time=self._epoch_t)\
            + "PAYLOAD\n{payload}".format(payload=str(self._payload))
    
    
class PacketBuilder:
    def __init__(self, special_pkt=False):
        self._pkt = Packet(special=special_pkt)
        
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