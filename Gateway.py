#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021
@authors: daze and fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys, time
import signal
from packet import Packet
import pickle
from network_interface import network_interface as ni

class Gateway:
    def __init__(self, ip_port_UDP, ip_port_TCP, ip_devnet,
                 ip_cloudnet, mac_addr, cloud_addr):
        # Set the gateway's 2 network interfaces' IPs
        self.dev_interface = ni(ip_devnet, mac_addr)
        self.cloud_interface = ni(ip_cloudnet, mac_addr)
        # UDP Server socket setupain loop
        self.socket_UDP = socket(AF_INET, SOCK_DGRAM)
        self.socket_UDP.bind((ip_port_UDP))
        print("UDP server up on port "+str(ip_port_UDP[1]))
        # TCP Client socket setup
        self.socket_TCP = socket(AF_INET, SOCK_STREAM)
        self.socket_TCP_flag = False
        self.ip_port_TCP = ip_port_TCP
         # ARP table creation
        self.arp_table_mac = {cloud_addr[0] : cloud_addr[1]}
        self.arp_table_socket = {cloud_addr[0] : self.socket_TCP}
        self.clients = {"192.168.1.10" : (None, False), "192.168.1.11" : (None, False)}
        # Number of devices
        self.NUM_DEVICES = 2
        self.true_counter = 0
    def manage_client(self):
        while True:
            data, addr = self.socket_UDP.recvfrom(4096)
            print("\nReceived {n_bytes} bytes..".format(n_bytes=len(data)))
            data = pickle.loads(data)
            print("\n{data}".format(data=data))
            if data:
                self.data_split(data)
            time.sleep(.5)
                    
    def data_split(self, pkt_received):
        ''' pkt_received: 
            ------------------------------------
            |   SRC_IP       \  DST_IP         |
            |   SRC_MAC      \  DST_MAC        \
            \            EPOCH TIME            \
            \             PAYLOAD              \
            ------------------------------------
        '''
        source_ip = pkt_received.get_src_ip()
        destination_ip = pkt_received.get_dst_ip()
        source_mac = pkt_received.get_src_mac()
        destination_mac = pkt_received.get_dst_mac()
        epoch_time = float(pkt_received.get_epoch_time())
        message = pkt_received.get_payload()
        ip_valid = False
        for i in self.clients.keys():
            if source_ip == i:
                print("---IP_address valid!---")
                self.true_counter += 1
                ip_valid = True
                # Print of timing
                print("\n    From ("+source_ip+" "+source_mac+")")
                print("    UDP_time: "+str(time.time()-float(epoch_time))+" seconds\n")
                # Compose message and send
                print("---Message under construction---")
                self.builder_message(source_ip, pkt_received)
                if self.true_counter == len(self.clients.keys()):
                    print("\n\n ")
                    self.send_message()
                    self._reset_clients_data()
                    return True
        if ip_valid == False:
            print("Invalid client ip...")
            print("Exit...")
            sys.exit(0)
                
    def builder_message(self, source_ip, pkt):
        lines = pkt.get_payload().split('\n')
        lines.remove("") # EOF
        message = ""
        try:
            for line in lines:
                line_data = line.split(" ")
                current = str(pkt.get_src_ip())+" "+line_data[0]+" "+line_data[1]+" "+line_data[2]+"\n"
                message += current
            pkt.set_payload(message)
            self.clients[source_ip] = (pkt, True)
        except Exception as exc:
            print(exc)
            self.socket_TCP.close()
            self.socket_UDP.close()
            print("\nClosing sockets..")
            print("\nExit..")
            sys.exit(0)
        
    def send_message(self):
        if self.socket_TCP_flag == False:
            try:
                self.socket_TCP.connect((self.ip_port_TCP))
                print("TCP connection over Cloud established on port "+str(self.ip_port_TCP[1]))
            except Exception as data:
                print (Exception,":",data)
                sys.exit(0)
            self.socket_TCP_flag = True
        for i in self.clients.keys():
            list_values = list(self.clients[i])
            pkt = list_values[0]
            pkt.set_epoch_time()
            self.socket_TCP.send(pickle.dumps(pkt))
            
    def is_bulkable(self, msg):
        return len(msg.encode()) < 4096
    
    def _reset_clients_data(self):
        for k in self.clients.keys():
            self.clients[k] = (None, False)
        self.true_counter = 0
            
    def signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self.socket_TCP.close()
            self.socket_UDP.close()
        finally:
            sys.exit(0)
        

if __name__ == '__main__':
    gateway = Gateway(('localhost', 10018), ('localhost', 45006), 
                      '192.168.1.1', '10.10.10.1', '7A:D8:DD:50:8B:42',
                      ('10.10.10.2', 'FE:D7:0B:E6:43:C5'))
    signal.signal(signal.SIGINT, gateway.signal_handler)
    gateway.manage_client()
