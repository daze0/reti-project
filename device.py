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
BUFSIZE = 1024
PERIOD = 60 # secs

class Device:
    def __init__(self, device_label, filename, device_ip, device_mac, gateway_addr, router_mac, target_ip): 
        self._label = device_label
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
            time.sleep(5)
            
    def get_label(self):
        return self._label

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
    
    # Waits for an ACKnowledge from the gateway regarding last data dump
    def _wait_ack(self):
        print("Waiting for ACK")
        while True:
            data, addr = self._sock.recvfrom(BUFSIZE)
            if self._ack_received(data):
                break
    
    # Serializes received data and checks if it is an ack
    def _ack_received(self, data):
        possible_ack = pickle.loads(data)
        print("\nACK received in: {elapsed_time}".format(elapsed_time=time.time()-possible_ack.get_epoch_time()))
        print(possible_ack)
        if possible_ack.get_payload() == bytes(1): 
            return True  # ACK is a byte = 1
        return False

    def _signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            print ('closing socket')
            self._sock.close()
            os.remove(self._filename)
            self._timer.stop()
        finally:
            sys.exit(0)
    