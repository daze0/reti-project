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
        while True:
            self.connection_socket, address = self.socket_TCP.accept()
            if self.connection_socket != None:
                print('READY')
                break
        while True:
            try:
                data = self.connection_socket.recv(4096)
                # Important infos
                print('data received(%s bytes from %s):\n%s' % (len(data), address, data.decode()))
                # Pkt headers 'n' message retrieval
                data = data.decode() #???
                source_ip = data[0:12]
                destination_ip = data[12:22]
                source_mac = data[22:39]
                destination_mac = data[39:57]
                message = data[57:]
                # Important infos for debugging
                print("\nPacket integrity:\ndestination MAC address matches client 1 MAC address: {mac}".format(mac=(self.mac == destination_mac)))
                print("\ndestination IP address matches client 1 IP address: {mac}".format(mac=(self.ip == destination_ip)))
                print("\nThe packed received:\n Source MAC address: {source_mac}, Destination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
                print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
                # Final measurement message output
                print("\nMessage: " + message)
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
    signal.signal(signal.SIGINT, cloud.signal_handler)
    cloud.get_message()
    cloud.socket_TCP.close()
    