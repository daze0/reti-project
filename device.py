#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM
import time, os, Measurement, sys, signal

class device:
    def __init__(self, device_ip, device_mac,  server_addr, router_mac, target_ip): #deviceip, ('192.168.1.1', 10000)
        # Socket used to connect to the GATEWAY
        self.sock = socket(AF_INET, SOCK_DGRAM)
        # timer thread flag
        #self.socket_on = True
        # Arg type validity check
        try:
            self.server_address = tuple(server_addr)
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
        self.timer = time.time()
        while True:
            if time.time() - self.timer >= self.PERIOD:
                self.send()
                self.timer = time.time()
                os.remove(self.filename)
                with open(self.filename, "wt") as f:
                    f.write(self.ip+"\n")
            self.get_data()
            time.sleep(5)
                
    # Get a measurement from the user
    # Write it on data file
    def get_data(self):
        print("\nNew measurement: ")
        measure = Measurement.Measurement()
        with open(self.filename, "a") as f:
            f.write(measure.get_time()+self.SEP+measure.get_temperature()+self.SEP+measure.get_humidity()+"\n")
            print("Time: "+measure.get_time())
            print("Temperature: "+measure.get_temperature())
            print("Humidity: "+measure.get_humidity())
        return True
        
    # Send data file to GATEWAY
    def send(self):
        mess = bytes()
        with open(self.filename, "rb") as file:
            while True:
                r = file.read(self.BUFSIZE)
                if not r:
                    break
                else:
                    mess += r
            try:
                self.sock.sendto(mess, self.server_address)
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
        finally:
            sys.exit(0)


dev1 = device("192.168.1.10", "36:DF:28:FC:D1:67", ('localhost', 13018), 
              '7A:D8:DD:50:8B:42', '10.10.10.2')
signal.signal(signal.SIGINT, dev1.signal_handler)
        

    