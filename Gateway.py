#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@authors: daze and fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys, time
import signal
from threading import Thread


class Gateway:
    def __init__(self, ip_UDP, port_UDP, ip_TCP, port_TCP):
        # Attribute data_pool is a dictionary that contains pending
        # fragments from iterations of manage_client() while True loop.
        self.data_pool = {}
        # Attribute clients contains clients that have connected to UDP server socket
        self.clients = {}
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
        t = Thread(target=self.manage_client)
        t.start()
        t.join()
        
    
    def manage_client(self):
        # First receive helps to identify current client
        # Valid clients: the ones who send data
        first_data, curr_address = self.socket_UDP.recvfrom(4096)
        # Add current client address to the dictionary
        self.clients[curr_address[0]] = curr_address[1] 
        # Every loop iteration refers to a single databox 
        while True:
            data, address = self.socket_UDP.recvfrom(4096)
            if not data:
                self.pick_pending(curr_address)
                break
            elif address != curr_address:
                #TODO: add data_pool dictionary to implementation
                self.data_pool[address] = data
                continue
            else:
                self.print_received_data(data, address)
                self.forward_data(data, address)
    
    def print_received_data(self, data, addr):
        data = data.decode() # ???
        print('received %s bytes from %s' % (len(data.encode()), addr))
        print('data:\n'+data)
                
    def pick_pending(self, curr_addr):
        for k in self.data_pool.keys():
            if k == curr_addr:
                self.print_received_data(self.data_pool[k]) 
                self.forward_data(self.data_pool[k], curr_addr)
                    
    def forward_data(self, databox, dest_addr):
        ''' databox: 
            ------------------------------------
            \   <device-ip-address>            |
            |   time1 temperature1 humidity1   \
            \   time2 temperature2 humidity2   \
            |   ..... ............ .........   \
            \   timeN temperatureN humidityN   \
            ------------------------------------
        '''
        lines = databox.split("\n")
        print("forwarding data to " + str(dest_addr))
        ip = str(lines[0])
        lines.remove(ip)
        lines.remove('') #EOF
        print(str(lines))
        self.send_message(ip, lines)
                
    def send_message(self, device_ip_addr, lines):
        message = ""
        previous = ""
        sent = False
        for line in lines:
            line_data = line.split(" ")
            current = device_ip_addr+" "+line_data[0]+" "+line_data[1]+" "+line_data[2]+"\n"
            # Bulk up message with current new message part
            if len(message.encode()) < 4096:
               message += current
            # Segmentation
            else:
                if previous != "":
                    message = message.replace(previous, "")
                    self.socket_TCP.send(message.encode())
                    sent = True
                    message = previous + current
            previous = current
        # Message never gets segmented
        if not sent:
            self.socket_TCP.send(message.encode())
            
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self.socket_TCP.close()
        finally:
            sys.exit(0)
        

if __name__ == '__main__':
    gateway = Gateway('localhost', 13000, 'localhost', 42000)
    signal.signal(signal.SIGINT, gateway.signal_handler)
    while True:
        gateway.get_file()
        time.sleep(1)