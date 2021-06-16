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
from network_interface import NetworkInterface as ni
from timer import Timer
import signal, sys

# CONSTANTS 
SEP = " "
BUFSIZE = 4096
PERIOD = 60 # secs

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
        # Device IP and MAC addresses
        self._device_interface = ni(device_ip, device_mac)
        # Router MAC address
        self._router_mac = router_mac
        # pkt headers setup
        self._pkt = PacketBuilder()\
            .ethernet_header(self._device_interface.get_mac_address(), self._router_mac)\
            .IP_header(self._device_interface.get_ip_address(), target_ip)\
            .build()
        # CTRL+C signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        # Periodically send data to GATEWAY
        self._timer = Timer(PERIOD)
        self._timer.start()
        while True:
            if self._timer.limit_reached():
                self._send()
                self._wait_ack()
                os.remove(self._filename)
                self._timer.reset()
            self._get_random_data()
            time.sleep(20)
                
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
    
    def _wait_ack(self):
        while True:
            data, addr = self._sock.recvfrom(4096)
            possible_ack = data.decode()
            if possible_ack == "ACK":
                print("\nACK received")
                break
            
    # Close device socket
    def _close_sock(self):
        print ('closing socket')
        self._sock.close()

    def _signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self._close_sock()
            os.remove(self._filename)
            self._timer.stop()
        finally:
            sys.exit(0)
    