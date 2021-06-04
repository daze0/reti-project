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

#CONSTANTS 
SEP = " "
PERIOD = 25 # secs
BUFSIZE = 4096

class Device:
    def __init__(self, filename, device_ip, device_mac, gateway_addr, router_mac, target_ip): 
        # Socket used to connect to the GATEWAY
        self._sock = socket(AF_INET, SOCK_DGRAM)
        # timer thread flag
        #self.socket_on = True
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
        # HEADERS creation
        IP_header = self._ip + target_ip
        ethernet_header = self._mac + self._router_mac
        headers = IP_header + ethernet_header
        # Periodically send data to GATEWAY
        self._timer = time.time()
        while True:
            if time.time() - self._timer >= PERIOD:
                self._send(headers)
                self._timer = time.time()
                os.remove(self._filename)
            self._get_random_data()
            time.sleep(5)
            
    def _update_epoch_header(self, headers):
        epoch_time = time.time()
        headers = headers + str(epoch_time)
        self._headers = headers
        return headers
                
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
        measure = Measurement.Measurement()
        with open(self._filename, "a") as f:
            time = measure.get_time()
            temperature = measure.get_temperature()
            humidity = measure.get_humidity()
            f.write(time+SEP+temperature+SEP+humidity+"\n")
        print("Time: "+time)
        print("Temperature: "+temperature)
        print("Humidity: "+humidity)
        return True
        
    # Send data file to GATEWAY
    def _send(self, headers):
        with open(self._filename, "rb") as file:
            while True:
                r = file.read(BUFSIZE)
                if not r:
                    break
                else:
                    try:
                        new_headers = self._update_epoch_header(headers)
                        msg = new_headers + '\n' + r.decode()
                        self._sock.sendto(msg.encode(), self._address)
                    except Exception as info:
                        print(info)
                        
    # Close device socket
    def _close_sock(self):
        print ('closing socket')
        self._sock.close()
        
if __name__ == '__main__':
    dev1 = Device("data.txt", "192.168.1.10", "36:DF:28:FC:D1:67", ('localhost', 10000), 
                  '7A:D8:DD:50:8B:42', '10.10.10.2')
    dev1.close_sock()
        

    