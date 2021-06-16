#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 11:21:51 2021

@author: fedebruno
"""

class NetworkInterface:
    def __init__(self, ip_addr, mac_addr):
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
    
    def set_ip_address(self, ip):
        self.ip_addr = ip
        
    def set_mac_address(self, mac):
        self.mac_addr = mac
        
    def get_ip_address(self):
        return self.ip_interface_addr
    
    def get_mac_address(self):
        return self.mac_addr