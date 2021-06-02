#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM
import time
from threading import Thread, currentThread
import os

class device:
    def __init__(self, device_ip, device_mac, addr, router_mac, target_ip): 
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
        self.filename = "data.txt"
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
        self.headers = IP_header + ethernet_header
        with open(self.filename, "wt") as f:
            f.write(self.headers+"\n")
        # Start timer thread
        self.timer = Thread(target=self.checktimer)
        self.timer.start()
    
    # Periodically send data to GATEWAY
    def checktimer(self):
        t = currentThread()
        while getattr(t, "do_run", True):
            # check if timer has already been set
            if self.data_dump_timer == -1:
                self.data_dump_timer = time.time()
            #if set verify if elapsed time is equal or greater than period break cycle
            if time.time()-self.data_dump_timer >= self.PERIOD:
                self.send()
                self.data_dump_timer = -1
                os.remove(self.filename)
                with open(self.filename, "wt") as f:
                    f.write(self.headers+"\n")   
            time.sleep(1)
                
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

dev1 = device("192.168.1.12", "36:DF:28:FC:D1:67", ('localhost', 12000), '7A:D8:DD:50:8B:42', '10.10.10.2')

while dev1.get_data():
    continue
        
dev1.close_sock()
        

    