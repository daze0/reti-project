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

BACKLOG = 3

class Cloud:        
    def __init__(self, ip_n_port, ip, mac_addr):
        self._mac = mac_addr
        self._ip = ip
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
                data = self._connection_socket.recv(4096)
                if data:
                    # Important infos
                    print('data received(%s bytes from %s):\n%s' % (len(data), address, data.decode()))
                    # Pkt headers 'n' message retrieval
                    data = data.decode() 
                    lines = data.split('\n')
                    lines.remove('') #EOF
                    headers = lines[0]
                    source_ip = headers[0:12]
                    destination_ip = headers[12:22]
                    source_mac = headers[22:39]
                    destination_mac = headers[39:56]
                    epoch_time = float(headers[56:74])
                    lines.remove(headers)
                    message = ""
                    for line in lines:
                        message = message + line + '\n'
                    # Important infos for debugging
                    print("\nPacket integrity:\ndestination MAC address matches client MAC address: {mac}".format(mac=(self._mac == destination_mac)))
                    print("\ndestination IP address matches client IP address: {mac}".format(mac=(self._ip == destination_ip)))
                    print("\nThe packed received:\n Source MAC address: {source_mac},\nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
                    print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
                    print("\nEpoch time: {epochtime},\nTime elapsed: {elapsed_time}".format(epochtime=epoch_time, elapsed_time=time.time()-epoch_time))
                    # Final measurement message output
                    print("\nMessage: \n" + message)
            except Exception as exc:
                print('Errore   ' + exc)
                self._connection_socket.close()
            
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
        
if __name__ == '__main__':
    cloud = Cloud(('localhost', 45000), '10.10.10.2', 'FE:D7:0B:E6:43:C5')
    print('Cloud server on..')
    signal.signal(signal.SIGINT, cloud.signal_handler)
    cloud.get_message()
    cloud.socket_TCP.close()
    