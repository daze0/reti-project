#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:24:27 2021

@author: fedebruno and daze
"""

from socket import SOCK_STREAM, AF_INET, socket

import sys

import signal

class Cloud:        
    def __init__(self, ip_addr, port):
        # TCP Server socket setup
        self.socket_TCP = socket(AF_INET, SOCK_STREAM)
        self.socket_TCP.bind((ip_addr, port))
        self.socket_TCP.listen(3)
        # By default connection_socket is set to server socket
        self.connection_socket = self.socket_TCP
    
    def get_message(self):
        while True:
            print('READY')
            self.connection_socket, address = self.socket_TCP.accept()
            try:
                data = self.connection_socket.recv(4096)
                print('received %s bytes from %s' % (len(data), address)) 
                print('data:\n' + data.decode())
            except Exception as exc:
                print('Errore   ' + exc)
                self.connection_socket.close()
                
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: Cloud server shutting down..')
        try:
            self.connection_socket.close() 
            self.socket_TCP.close()
        finally:
            sys.exit(0)
        
if __name__ == '__main__':
    cloud = Cloud('localhost', 42004)
    print('Cloud server on..')
    cloud.get_message()
    signal.signal(signal.SIGINT, cloud.signal_handler)
    cloud.socket_TCP.close()
    