#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM
import time
import os, sys, signal
import Measurement
from packet import Packet
from network_interface import network_interface as ni
import pickle

class device:
    def __init__(self, filename, device_ip, device_mac, addr, router_mac, target_ip): 
        # Socket used to connect to the GATEWAY
        self.sock = socket(AF_INET, SOCK_DGRAM)
        # timer thread flag
        #self.socket_on = True
        # Arg type validity check
        try:
            self.address = tuple(addr)
        except TypeError as info:
            print(info)
        # Useful for sending data periodically to the server
        # Initially set at -1
        self.data_dump_timer = -1
        # This is the filename of the file that contains 24h worth of data 
        self.filename = filename
        # CONSTANTS
        self.SEP = " "
        self.PERIOD = 15 # secs
        self.BUFSIZE = 4096
        # Device IP as file header
        self.device_interface = ni(device_ip, device_mac)
        # Router MAC address
        self.router_mac = router_mac
        # Router IP address
        self.router_ip = target_ip
        # HEADERS creation
        IP_header = self.device_interface.get_ip_address() + self.router_ip
        ethernet_header = self.device_interface.get_mac_address() + self.router_mac
        # Start timer thread
        headers = ethernet_header + IP_header
        # Ctrl+C to exit
        signal.signal(signal.SIGINT, self.signal_handler)
        # Periodically send data to GATEWAY
        self.timer = time.time()
        while True:
            if time.time() - self.timer >= self.PERIOD:
                self.send(headers)
                self.timer = time.time()
                os.remove(self.filename)
            self.get_random_data()
            time.sleep(3)
            
    def update_epoch_header(self, headers):
        epoch_time = time.time()
        headers = headers + str(epoch_time)
        self.headers = headers
        return headers
                
    # Get a measurement from the user
    # Write it on data file
    def get_data(self):
        print("\nNew measurement('q' to quit): ") 
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        temperature = str(input("\nTemperature(°C): "))
        humidity = str(input("Humidity(%): "))
        if temperature == "q" and humidity == "q": 
            return False
        else:
            with open(self.filename, "a") as f:
                f.write(current_time+self.SEP+temperature+self.SEP+humidity+"\n")
            return True

    # Get a random measurement
    # Write it on data file
    def get_random_data(self):
        print("\nNew measurement: ")
        measure = Measurement.Measurement()
        with open(self.filename, "a") as f:
            time = measure.get_time()
            temperature = measure.get_temperature()
            humidity = measure.get_humidity()
            f.write(time+self.SEP+temperature+self.SEP+humidity+"\n")
        print("Time: "+time)
        print("Temperature: "+temperature)
        print("Humidity: "+humidity)
        return True
        
    # Send data file to GATEWAY
    def send(self, headers):
        with open(self.filename, "rb") as file:
            r = file.read(self.BUFSIZE)
            try:
                msg = r.decode()
                pkt = Packet(self.device_interface.get_mac_address()+self.router_mac, 
                             self.device_interface.get_ip_address()+self.router_ip,
                             msg)
                self.sock.sendto(pickle.dumps(pkt), self.address)
            except Exception as info:
                print(info)
                        
    # Close device socket
    def close_sock(self):
        print ('closing socket')
        self.sock.close()
        self.timer.do_run = False
    
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self.sock.close()
            os.remove(self.filename)
        finally:
            sys.exit(0)

dev1 = device("data.txt", "192.168.1.10", "36:DF:28:FC:D1:67", ('localhost', 10018), 
              '7A:D8:DD:50:8B:42', '10.10.10.2')