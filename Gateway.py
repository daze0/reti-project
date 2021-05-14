#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@authors: daze and fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys, time

class Gateway:
    def __init__(self, ip_UDP, port_UDP, ip_TCP, port_TCP):
        self.filename = 'data_file.txt'
        # UDP Server socket setup
        self.socket_UDP = socket(AF_INET, SOCK_DGRAM)
        self.socket_UDP.bind((ip_UDP, port_UDP))
        print("UDP server up on port "+str(port_UDP))
        # TCP Client socket setup
        self.socket_TCP = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket_TCP.connect((ip_TCP,port_TCP))
        except Exception as data:
            print (Exception,":",data)
            sys.exit(0)
        print("TCP connection over Cloud established..")
    
    def get_file(self):
        while True:
            data = self.socket_UDP.recvfrom(4096)[0]
            if not data:
                break
            else:
                with open(self.filename, 'wb') as file:
                    file.write(data)
                print("data received and saved..")
                    
    def forward_data(self):
        with open(self.filename, 'rt') as file:
            lines = file.readlines()
            print(lines)
            ip = lines.pop(0)
            print(ip)
            for line in lines:
                line_data = line.split(" ")
                self.send_message(self, ip, line_data[0], line_data[1], line_data[2])
                
                    
    def send_message(self, device_ip_addr, measurement_time, temperature, humidity):
        message = device_ip_addr+"-"+measurement_time+"-"+temperature+"-"+humidity
        self.socket_TCP.send(message.encode())

    def close_socket_TCP(self):
        self.socket_TCP.close()
        

if __name__ == '__main__':
    gateway = Gateway('localhost', 11000, 'localhost', 41000)
    while True:
        gateway.get_file()
        time.sleep(1)
        gateway.forward_data()