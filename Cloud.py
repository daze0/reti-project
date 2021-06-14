#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:24:27 2021
@author: fedebruno and daze
"""

from socket import SOCK_STREAM, AF_INET, socket
import pickle
import sys
import signal
import time
from packet import Packet

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
        self.connection_socket, address = self.accept_connection()
        while True:
            try:
                data = self.connection_socket.recv(4096)
                if data:
                    # Pkt headers 'n' message retrieval
                    pkt_received = pickle.loads(data)
                    source_ip = pkt_received.get_src_ip()
                    destination_ip = pkt_received.get_dst_ip()
                    source_mac = pkt_received.get_src_mac()
                    destination_mac = pkt_received.get_dst_mac()
                    epoch_time = float(pkt_received.get_epoch_time())
                    message = pkt_received.get_payload()
                    # Important infos
                    print('Data received(%s bytes from %s %s)' % (len(data), source_ip, source_mac))
                    print("TCP_time: %s seconds" % (time.time()-float(epoch_time)))
                    # Final measurement message output
                    print("Message: \n" + message)
            except Exception as exc:
                print(exc)
                self.connection_socket.close()
            
    def accept_connection(self):
         while True:
            connection_socket, address = self.socket_TCP.accept()
            if self.connection_socket != None:
                print('READY')
                return connection_socket, address
                
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: Cloud server shutting down..')
        try:
            self.connection_socket.close() 
            self.socket_TCP.close()
        finally:
            sys.exit(0)
        
if __name__ == '__main__':
    cloud = Cloud(('localhost', 45006), '10.10.10.2', 'FE:D7:0B:E6:43:C5')
    print('Cloud server on..')
    signal.signal(signal.SIGINT, cloud.signal_handler)
    cloud.get_message()
    cloud.socket_TCP.close()
    