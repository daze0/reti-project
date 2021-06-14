#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 18:31:13 2021

@author: daze
"""

from device import Device
from gateway import Gateway
from cloud import Cloud

DEFAULT_UDP_PORT = 10000
DEFAULT_TCP_PORT = 45000

class DeviceFactory:
    # Creates and returns an active customized device
    def custom_device(filename, device_ip, device_mac, gateway_addr, router_mac, target_ip):
        return Device(filename, device_ip, device_mac, gateway_addr, router_mac, target_ip)
    # Creates and returns default device 1
    def default_device_1(self):
        return Device("data_dev1.txt", "192.168.1.10", "36:DF:28:FC:D1:67", ('localhost', DEFAULT_UDP_PORT), '7A:D8:DD:50:8B:42', '10.10.10.2')
    # Creates and returns default device 2
    def default_device_2(self):
        return Device("data_dev2.txt", "192.168.1.15", "04:EA:56:E2:2D:63", ('localhost', DEFAULT_UDP_PORT), '7A:D8:DD:50:8B:42', '10.10.10.2')
    # Creates and returns default device 3
    def default_device_3(self):
        return Device("data_dev3.txt", "192.168.1.20", "6A:6C:39:F0:66:7A", ('localhost', DEFAULT_UDP_PORT), '7A:D8:DD:50:8B:42', '10.10.10.2')
    # Creates and returns default device 4
    def default_device_4(self):
        return Device("data_dev4.txt", "192.168.1.25", "96:34:75:51:CC:73", ('localhost', DEFAULT_UDP_PORT), '7A:D8:DD:50:8B:42', '10.10.10.2')
    
class GatewayFactory:
    # Creates and returns a customized and completely active gateway 
    # Active means it's already working on both ends, the devices' and the cloud ones
    def custom_gateway(ip_port_UDP, ip_port_TCP, ip_devnet, ip_cloudnet, mac_addr, cloud_addr):
        return Gateway(ip_port_UDP, ip_port_TCP, ip_devnet, ip_cloudnet, mac_addr, cloud_addr)
    # Creates and returns default gateway
    def default_gateway(self):
        return Gateway(('localhost', DEFAULT_UDP_PORT), ('localhost', DEFAULT_TCP_PORT), 
                      '192.168.1.1', '10.10.10.1', '7A:D8:DD:50:8B:42',
                      ('10.10.10.2', 'FE:D7:0B:E6:43:C5'))
    
class CloudFactory:
    #Creates and returns a customized cloud server
    def custom_cloud(ip_n_port, ip, mac_addr):
        return Cloud(ip_n_port, ip, mac_addr)
    #Creates and returns default cloud server
    def default_cloud(self):
        return Cloud(('localhost', DEFAULT_TCP_PORT), '10.10.10.2', 'FE:D7:0B:E6:43:C5')