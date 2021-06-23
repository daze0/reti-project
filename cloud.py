 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:24:27 2021

@author: fedebruno and daze
"""

from socket import SOCK_STREAM, AF_INET, socket
import sys
import signal
import time
from packet import Packet 
import pickle
from network_interface import NetworkInterface as ni

BACKLOG = 4
BUFSIZE = 4096

class Cloud:        
    def __init__(self, ip_n_port, ip, mac_addr):
        self._mac = mac_addr
        self._ip = ip
        self._cloud_interface = ni(ip, mac_addr)
        # TCP Server socket setup
        self._socket_TCP = socket(AF_INET, SOCK_STREAM)
        self._socket_TCP.bind((ip_n_port))
        self._socket_TCP.listen(BACKLOG)
        # By default connection_socket is set to server socket
        self._connection_socket = self._socket_TCP
        # It's on message
        print("Cloud server is on (%s, %s)" % (ip_n_port))
        # CTRL+C signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        # Cloud main loop
        self._get_message()
        # Ultimately close socket
        self._socket_TCP.close()
    
    def _get_message(self):
        self._connection_socket, address = self._accept_connection()
        while True:
            try:
                data = self._connection_socket.recv(BUFSIZE)
                if data:
                    pkt_received = pickle.loads(data)
                    # Important infos
                    print('received %s bytes from %s: ' % (len(data), address))
                    self._print_data(pkt_received)
            except Exception as exc:
                print('Errore   ' + exc)
                self._connection_socket.close()
                self._socket_TCP.close()
                sys.exit(0)
                
    def _print_data(self, pkt_received):
         epoch_time = float(pkt_received.get_epoch_time())
         message = pkt_received.get_payload()
         # Time passed by since epoch_time timestamp
         print("\nElapsed time: {elapsed_time}".format(elapsed_time=time.time()-epoch_time))
         # Final measurement message output
         print("\nIp address Time T U \n" + message)
            
    def _accept_connection(self):
         while True:
            connection_socket, address = self._socket_TCP.accept()
            if self._connection_socket != None:
                print('READY')
                return connection_socket, address
                
    def _signal_handler(self, signal, frame):
        print('Ctrl+c pressed: Cloud server shutting down..')
        try:
            self._connection_socket.close()
            self._socket_TCP.close()
        finally:
            sys.exit(0)
    