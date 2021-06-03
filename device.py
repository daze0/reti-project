#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM
import time
import os
import Measurement

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
        self.PERIOD = 25 # secs
        self.BUFSIZE = 4096
        # Device IP as file header
        self.ip = device_ip
        # Device MAC address
        self.mac = device_mac
        # Router MAC address
        self.router_mac = router_mac
        # HEADERS creation
        IP_header = self.ip + target_ip
        ethernet_header = self.mac + self.router_mac
        headers = IP_header + ethernet_header
        self.write_headers(headers)
        # Periodically send data to GATEWAY
        self.timer = time.time()
        while True:
            if time.time() - self.timer >= self.PERIOD:
                self.send()
                self.timer = time.time()
                os.remove(self.filename)
                self.write_headers(headers)
            self.get_random_data()
            time.sleep(5)
            
    def write_headers(self, headers):
        epoch_time = time.time()
        headers = headers + str(epoch_time)
        self.headers = headers
        with open(self.filename, "wt") as f:
            f.write(headers+"\n")
                
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
    def send(self):
        with open(self.filename, "rb") as file:
            while True:
                r = file.read(self.BUFSIZE)
                if not r:
                    break
                else:
                    try:
                        self.sock.sendto(r, self.address)
                    except Exception as info:
                        print(info)
                        
    # Close device socket
    def close_sock(self):
        print ('closing socket')
        self.sock.close()
        self.timer.do_run = False

dev1 = device("data.txt", "192.168.1.10", "36:DF:28:FC:D1:67", ('localhost', 12000), 
              '7A:D8:DD:50:8B:42', '10.10.10.2')
        
dev1.close_sock()
        

    