#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@authors: daze and fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys, time
import signal


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
        print("TCP connection over Cloud established..")
    
    def get_file(self):
        full_msg = str()
        while True:
            data, address = self.socket_UDP.recvfrom(4096)
            if not data:
                break
            else:
                full_msg += data.decode()
                print('received %s bytes from %s' % (len(data), address))
                print('data:\n'+data.decode())
                print('cumulative data:\n'+full_msg)
                self.forward_data(data, address)
                    
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
        lines = databox.decode().split("\n")
        print("forwarding data to " + str(dest_addr))
        ip = lines[0]
        lines.remove(ip)
        lines.remove('') #EOF
        print(lines)
        for line in lines:
            line_data = line.split(" ")
            self.send_message(ip, line_data[0], line_data[1], line_data[2])
                
    def send_message(self, device_ip_addr, measurement_time, temperature, humidity):
        message = device_ip_addr+"-"+measurement_time+"-"+temperature+"-"+humidity
        self.socket_TCP.send(message.encode())

    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self.socket_TCP.close()
        finally:
            sys.exit(0)
        

if __name__ == '__main__':
    gateway = Gateway('localhost', 12000, 'localhost', 42000)
    signal.signal(signal.SIGINT, gateway.signal_handler)
    while True:
        gateway.get_file()
        time.sleep(1)
        gateway.forward_data()