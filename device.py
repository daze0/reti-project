#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM, timeout
import time
import os
import measurement
from packet import Packet, PacketBuilder
import pickle

# CONSTANTS 
SEP = " "
PERIOD = 25 # secs
BUFSIZE = 4096
TIMEOUT = 1440 # secs

class Device:
    def __init__(self, filename, device_ip, device_mac, gateway_addr, router_mac, target_ip): 
        # Socket used to connect to the GATEWAY
        self._sock = socket(AF_INET, SOCK_DGRAM)
        # Arg type validity check
        try:
            self._address = tuple(gateway_addr)
        except TypeError as info:
            print(info)
        # This is the filename of the file that contains 24h worth of data 
        self._filename = filename
        # Device IP as file header
        self._ip = device_ip
        # Device MAC address
        self._mac = device_mac
        # Router MAC address
        self._router_mac = router_mac
        # pkt headers setup
        self._pkt = PacketBuilder()\
            .ethernet_header(self._mac+self._router_mac)\
            .IP_header(self._ip+target_ip)\
            .build()
        # Periodically send data to GATEWAY
        self._sock.settimeout(TIMEOUT)
        try:
            while True:
                self._get_random_data()
        except timeout:
            self._send()
            os.remove(self._filename)
                
    # Get a measurement from the user
    # Write it on data file
    def _get_data(self):
        print("\nNew measurement('q' to quit): ") 
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        temperature = str(input("\nTemperature(°C): "))
        humidity = str(input("Humidity(%): "))
        if temperature == "q" and humidity == "q": 
            return False
        else:
            with open(self._filename, "a") as f:
                f.write(current_time+SEP+temperature+SEP+humidity+"\n")
            return True
        
    # Get a random measurement
    # Write it on data file
    def _get_random_data(self):
        print("\nNew measurement: ")
        measure = measurement.Measurement()
        time = measure.get_time()
        temperature = measure.get_temperature()
        humidity = measure.get_humidity()
        with open(self._filename, "a") as f:
            f.write(time+SEP+temperature+SEP+humidity+"\n")
        print("Time: "+time)
        print("Temperature: "+temperature)
        print("Humidity: "+humidity)
        return True
        
    # Send data file to GATEWAY
    def _send(self):
        with open(self._filename, "rb") as file:
            while True:
                r = file.read(BUFSIZE)
                if not r:
                    break
                else:
                    try:
                        self._pkt.set_epoch_time()
                        self._pkt.set_payload(r.decode())
                        serialized_pkt = pickle.dumps(self._pkt)
                        self._sock.sendto(serialized_pkt, self._address) 
                    except Exception as info:
                        print(info)
                        
    # Close device socket
    def _close_sock(self):
        print ('closing socket')
        self._sock.close()
    