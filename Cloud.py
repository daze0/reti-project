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
    def __init__(self, ip_n_port, ip, mac_addr):
        self.mac = mac_addr
        self.ip = ip
        # TCP Server socket setup
        self.socket_TCP = socket(AF_INET, SOCK_STREAM)
        self.socket_TCP.bind((ip_n_port))
        self.socket_TCP.listen(3)
        # By default connection_socket is set to server socket
        self.connection_socket = self.socket_TCP
    
    def get_message(self):
        self.connection_socket, address = self.socket_TCP.accept()
        print('READY')
        try:
            data = self.connection_socket.recv(4096)
            # Loop keeps going until there are no more data segments
            while data: 
                print('data received(%s bytes from %s):\n%s' % (len(data), address, data.decode()))
                # Receive next iteration data
                data = self.connection_socket.recv(4096)
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
    cloud = Cloud(('localhost', 42000), '10.10.10.2', 'FE:D7:0B:E6:43:C5')
    print('Cloud server on..')
    while True:
        cloud.get_message()
    signal.signal(signal.SIGINT, cloud.signal_handler)
    cloud.socket_TCP.close()
    