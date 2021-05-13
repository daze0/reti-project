#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@author: fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM

class Gateway:
    
    socket_UDP = socket(AF_INET, SOCK_DGRAM)

    address_UDP = ()
    
    socket_TCP = socket(AF_INET, SOCK_STREAM)
    
    address_TCP = ()
    
    devices = {}
    
    lista_mex = list()
    
    file_name = 'data_file.txt'
    
    
    
    def __init__(self, ip_UDP, port_UDP, ip_TCP, port_TCP):
        self.address_UDP = (ip_UDP, port_UDP)
        self.address_TCP = (ip_TCP, port_TCP)
        self.socket_UDP.bind(self.address_UDP)
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
    def open_file(self):
        with open(self.file_name, 'wb') as file:
            while True:
                data = self.socket_UDP.recvfrom(4096)[0]
                if not data:
                    break
                else:
                    file.write(data)
                    
    
                    
    
    def send_message(self, message):
        self.socket_TCP.send(message.encode())

    def close_socket_TCP(self):
        self.socket_TCP.close()
        

if __name__ == '__main__':
    gateway = Gateway('localhost', 11111, 'localhost', 42000)
    gateway.get_files()
    '''for i in gateway.lista_mex:
        gateway.send_message(gateway.lista_mex[i])
    gateway.close_socket_TCP()'''
    