#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@author: fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys

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
        '''try:
            self.socket_TCP.connect(self.address_TCP)
        except Exception as exc:
            print(exc)'''
    
    '''
    def get_files(self):
        while True:
            print("ready\n")
            data, device_address = self.socket_UDP.recvfrom(4096)
            if self.devices.__contains__(device_address)==False:
                self.devices.append(device_address)
                i=0
                    self.devices[device_address] = 'device_'+i+''
                    i = i + 1
            print(data.decode('utf-8'))
            self.lista_mex.append(data)
            #print(self.lista_mex)
        #return self.lista_mex
    '''
    # 
    def get_file(self):
        with open(self.filename, 'wb') as file:
            while True:
                data = self.socket_UDP.recvfrom(4096)[0]
                if not data:
                    break
                else:
                    print("saving received data..") 
                    file.write(data)
                    
    def forward_data(self):
        with open(self.filename, 'rt') as file:
            ip = file.readline()
            for line in file.readlines()-ip:
                line_data = line.split(" ")
                print(line_data) #debug
                self.send_message(self, ip, line_data[0], line_data[1], line_data[2])
                
                    
    def send_message(self, device_ip_addr, measurement_time, temperature, humidity):
        self.socket_TCP.send((device_ip_addr+"-"+measurement_time+"-"+temperature+"-"+humidity).encode())

    def close_socket_TCP(self):
        self.socket_TCP.close()
        

if __name__ == '__main__':
    gateway = Gateway('localhost', 10001, 'localhost', 42000)
    while True:
        gateway.get_file()
    '''for i in gateway.lista_mex:
        gateway.send_message(gateway.lista_mex[i])
    gateway.close_socket_TCP()'''
    