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
    def __init__(self, ip_port_UDP, ip_port_TCP, ip_devnet, ip_cloudnet, mac_addr, cloud_addr):
        # Set the gateway's 2 network interfaces' IPs
        self.ip_devnet = ip_devnet 
        self.ip_cloudnet = ip_cloudnet
        # Set gateway's mac address
        self.mac = mac_addr
        # UDP Server socket setup
        self.socket_UDP = socket(AF_INET, SOCK_DGRAM)
        self.socket_UDP.bind((ip_port_UDP))
        print("UDP server up on port "+str(ip_port_UDP[1]))
        # TCP Client socket setup
        self.socket_TCP = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket_TCP.connect((ip_port_TCP))
        except Exception as data:
            print (Exception,":",data)
            sys.exit(0)
        print("TCP connection over Cloud established on port "+str(ip_port_TCP[1]))
         # ARP table creation
        self.arp_table_mac = {cloud_addr[0] : cloud_addr[1]}
        self.arp_table_socket = {cloud_addr[0] : self.socket_TCP}
        
    def manage_client(self):
        while True:
            data, addr = self.socket_UDP.recvfrom(4096)
            print("\nReceived {n_bytes} bytes..".format(n_bytes=len(data)))
            data = data.decode() 
            print("\n{data}".format(data=data))
            if data:
                self.data_split(data)
            time.sleep(.5)
                    
    def data_split(self, databox):
        ''' databox: 
            ------------------------------------
            |   HEADERS                        |
            |   time1 temperature1 humidity1   \
            \   time2 temperature2 humidity2   \
            |   ..... ............ .........   \
            \   timeN temperatureN humidityN   |
            \                                  \ EOF
            ------------------------------------
        '''
        lines = databox.split("\n")
        lines.remove('') #EOF
        print("File split in lines..")
        headers = lines[0]
        # Packet Headers retrieval
        source_ip = headers[0:12]
        destination_ip = headers[12:22]
        source_mac = headers[22:39]
        destination_mac = headers[39:56]
        epoch_time = float(headers[56:74])
        lines.remove(headers)
        # Packet Message retrieval
        message = ""
        for line in lines:
            message = message + line + '\n'
        # Important infos
        print("The packed received:\nSource MAC address: {source_mac},\nDestination MAC address: {destination_mac}".format(source_mac=source_mac, destination_mac=destination_mac))
        print("\nSource IP address: {source_ip}, Destination IP address: {destination_ip}".format(source_ip=source_ip, destination_ip=destination_ip))
        print("\nEpoch time: {time},\nTime elapsed: {elapsed_time}".format(time=epoch_time, elapsed_time=time.time()-epoch_time))
        print("\nMessage: \n" + message)
        # Packet Header recomposing
        ethernet_header = self.mac + self.arp_table_mac[destination_ip]
        IP_header = source_ip + destination_ip
        epoch_time = time.time()
        new_headers = IP_header + ethernet_header + str(epoch_time)
        # Compose message and send
        self.send_message(self.arp_table_socket[destination_ip], new_headers, 
                          source_ip, lines)
                
    def send_message(self, dst_socket, headers, device_ip_addr, lines):
        message = ""
        previous = ""
        sent = False
        try:
            for line in lines:
                line_data = line.split(" ")
                current = device_ip_addr+" "+line_data[0]+" "+line_data[1]+" "+line_data[2]+"\n"
                # Bulk up message with current new message part
                if self.is_bulkable(headers+'\n'+message):
                   message += current
                # Segmentation 
                else:
                    if previous != "":
                        message = message.replace(previous, "")
                        dst_socket.send((headers+'\n'+message).encode())
                        sent = True
                        message = previous + current
                previous = current
        except Exception as exc:
            print(exc)
            sys.exit(0)
        # Message never gets segmented
        if not sent:
            dst_socket.send((headers+'\n'+message).encode())
            
    def is_bulkable(self, msg):
        return len(msg.encode()) < 4096
            
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self.socket_TCP.close()
        finally:
            sys.exit(0)
        

if __name__ == '__main__':
    gateway = Gateway(('localhost', 10000), ('localhost', 45000), 
                      '192.168.1.1', '10.10.10.1', '7A:D8:DD:50:8B:42',
                      ('10.10.10.2', 'FE:D7:0B:E6:43:C5'))
    signal.signal(signal.SIGINT, gateway.signal_handler)
    gateway.manage_client()
