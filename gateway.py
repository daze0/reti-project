#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:37:59 2021

@authors: daze and fedebruno
"""

from socket import AF_INET, socket, SOCK_DGRAM, SOCK_STREAM
import sys, time
import signal
from packet import Packet, PacketBuilder
import pickle
from network_interface import NetworkInterface as ni

class Gateway:
    def __init__(self, ip_port_UDP, ip_port_TCP, ip_devnet, ip_cloudnet, mac_addr, cloud_addr):
        # Set the gateway's 2 network interfaces' IPs
        self._device_interface = ni(ip_devnet, mac_addr)
        self._cloud_interface = ni(ip_cloudnet, mac_addr)
        # UDP Server socket setup
        self._socket_UDP = socket(AF_INET, SOCK_DGRAM)
        self._socket_UDP.bind((ip_port_UDP))
        print("UDP server up on port "+str(ip_port_UDP[1]))
        # TCP Client socket setup
        self._socket_TCP = socket(AF_INET, SOCK_STREAM)
        self._ip_port_TCP = ip_port_TCP
         # ARP tables creation
        self._arp_table_mac = {cloud_addr[0] : cloud_addr[1]}
        self._clients = {"192.168.1.10": (None, False), "192.168.1.15": (None, False),
                         "192.168.1.20": (None, False), "192.168.1.25": (None, False)}
        self._true_counter = 0
        self._TCP_connection_flag = False
        # CTRL+C signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        # Gateway main loop
        self._manage_client()
        
    def _manage_client(self):
        while True:
            data, addr = self._socket_UDP.recvfrom(4096)
            print("\nReceived {n_bytes} bytes..".format(n_bytes=len(data)))
            data = pickle.loads(data)  
            print("\n{data}".format(data=data))
            if data:
                self._data_split(data) 
            time.sleep(.5)
                    
    def _data_split(self, pkt_received):
        ''' pkt_received: 
            ------------------------------------
            |   SRC_IP       \  DST_IP         |
            |   SRC_MAC      \  DST_MAC        \
            \            EPOCH TIME            \
            \             PAYLOAD              \
            ------------------------------------
        '''
        # Epoch time and source IP headers retrieval
        epoch_time = float(pkt_received.get_epoch_time())
        source_ip = pkt_received.get_src_ip()
        # Important infos
        print("Elapsed time: {elapsed_time}".format(elapsed_time=time.time()-epoch_time))
        ip_valid = False
        # Adds message to clients' dictionary and eventually sends collected data
        for ip in self._clients.keys():
            # Check if source_ip is a valid ip and if that same ip value is set to default
            if ip == source_ip and self._clients[ip] == (None, False):
                print("\nsource IP is valid and never touched\n")
                self._clients[ip] = (pkt_received, True)
                self._true_counter += 1
                ip_valid = True
                # When all clients have sent their measurements
                # send new packet and reset every client's tuple
                if self._true_counter == len(self._clients.keys()):
                    print("\nall clients are connected, ready to send!\n")
                    self._send_message()
                    print("\npkt sent\n")
                    self._reset_clients_data()
                    print("\nclients data reset\n")
            elif ip == source_ip and self._clients[ip] != (None, False):
                ip_valid = True
        if not ip_valid:
            print("Invalid client tried to connect! Exit..")
            try:
                self._socket_TCP.close()
            finally:
                sys.exit(0)
                
    def _reset_clients_data(self):
        for k in self._clients.keys():
            self._clients[k] = (None, False)
        self._true_counter = 0
        
    def _open_TCP_connection(self):
        # TCP Client socket setup
        try:
            self._socket_TCP.connect((self._ip_port_TCP[0], self._ip_port_TCP[1]))
        except Exception as data:
            print (Exception,":",data)
            sys.exit(0)
        print("TCP connection over Cloud established on port "+str(self._ip_port_TCP[1]))
        
    def _send_message(self):
        # Open TCP connection only when all devices' pkts are received
        if not self._TCP_connection_flag:
            self._open_TCP_connection()
            self._TCP_connection_flag = True
        # Loop through each client and format each payload
        message = ""
        for ip in self._clients.keys():
            pkt = self._clients.get(ip)[0]
            lines = pkt.get_payload().split('\n')
            lines.remove('') #EOF
            # Formatting new payload
            for line in lines:
                line_data = line.split(" ")
                current = ip+" " +line_data[0]+" "+line_data[1]+" "+line_data[2]+"\n"
                message += current
        # create a packet each with appropriate headers and new payload
        pkt_to_send = PacketBuilder()\
            .ethernet_header(self._cloud_interface.get_mac_address(), self._arp_table_mac[pkt.get_dst_ip()])\
            .IP_header(self._cloud_interface.get_ip_address(), list(self._arp_table_mac.keys())[0])\
            .epoch_time()\
            .payload(message)\
            .build()
        try:
            # Then serialize it and send it
            serialized_pkt_to_send = pickle.dumps(pkt_to_send)
            self._socket_TCP.send(serialized_pkt_to_send) 
            # TODO: set socket timeout
        except Exception as exc:
            print(exc)
            sys.exit(0)
        print("\nDATA SENT CORRECTLY\n")

    def _signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self._socket_TCP.close()
        finally:
            sys.exit(0)
        