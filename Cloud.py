#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:24:27 2021

@author: fedebruno
"""

from socket import SOCK_STREAM, AF_INET, socket

import sys

import signal

class Cloud:
    
    socket_TCP = socket(AF_INET, SOCK_STREAM)
    
    server_address = ()
    
    def __init__(self, ip_add, port_add):
        self.server_address = (ip_add, port_add)
        self.socket_TCP.bind(self.server_address)
        self.socket_TCP.listen(1)

    def get_server_address(self):
        return self.server_address
    
    def get_file(self):
        while True:
            print('READY')
            self.connection_socket, address = self.socket_TCP.accept()
            try:
                data = self.connection_socket.recv(1080).decode()
                print('Data     ' + data)
                self.connection_socket.close()
            except Exception as exc:
                print('Errore   ' + exc)
                self.connection_socket.close()
                
    def signal_handler(self):
        print('Ctrl+c pressed')
        try:
            if (self.socket_TCP):
                self.connection_socket.close()
                self.socket_TCP.close()
        finally:
            sys.exit(0)
        
if __name__ == '__main__':
    cloud = Cloud('localhost', 42000)
    print('get start')
    cloud.get_file()
    signal.signal(signal.SIGINT, cloud.signal_handler())
    cloud.socket_TCP.close()
    