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
        '''self._arp_table_clients = {"192.168.1.10": "36:DF:28:FC:D1:67", 
                                   "192.168.1.15": "04:EA:56:E2:2D:63",
                                   "192.168.1.20": "6A:6C:39:F0:66:7A",
                                   "192.168.1.25": "96:34:75:51:CC:73"}
        # Merge \/  /\ # ???
        '''
        self._clients = {("192.168.1.10", "36:DF:28:FC:D1:67"): (None, False), ("192.168.1.15", "04:EA:56:E2:2D:63"): (None, False),
                         ("192.168.1.20", "6A:6C:39:F0:66:7A"): (None, False), ("192.168.1.25", "96:34:75:51:CC:73"): (None, False)}
        self._active_clients_counter = 0
        self._TCP_connection_flag = False
        # CTRL+C signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        # Gateway main loop
        self._manage_client()
    
    # Receives data from a device, deserializes it, sends ACK and proceeds
    def _manage_client(self):
        while True:
            data, addr = self._socket_UDP.recvfrom(4096)
            print("\nReceived {n_bytes} bytes..".format(n_bytes=len(data)))
            data = pickle.loads(data)  
            print("\n{data}".format(data=data))
            if data:
                self._send_ack(addr, data.get_src_ip()) 
                self._data_split(data) 
            time.sleep(.5)
    
    def _mac_of(self, ip):
        for key in self._clients.keys():
            client_ip = key[0]
            client_mac = key[1]
            if client_ip == ip:
                return client_mac
        return 'notfound'
            
    # Sends an ACK to waiting device
    def _send_ack(self, device_addr, device_ip):
        ack = PacketBuilder(special_pkt=True)\
            .ethernet_header(self._device_interface.get_mac_address(), self._mac_of(device_ip))\
            .IP_header(self._device_interface.get_ip_address(), device_ip)\
            .epoch_time()\
            .payload(bytes(1))\
            .build()
        serialized_ack = pickle.dumps(ack)
        try:          
            self._socket_UDP.sendto(serialized_ack, device_addr)
            print("ACK sent back to device")
        except Exception as exc:
            print(exc)
            self._socket_TCP.close()
            sys.exit(0)
            
    
    # Data elaboration support method: splits, identifies and processes pkt data
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
        for key in self._clients.keys():
            client_ip = key[0]
            # Check if source_ip is a valid ip and if that same ip value is set to default
            if client_ip == source_ip and self._clients[key] == (None, False):
                print("\nsource IP is valid and never touched")
                self._clients[key] = (pkt_received, True)
                self._active_clients_counter += 1
                ip_valid = True
                # When all clients have sent their measurements
                # send new packet and reset every client's tuple
                if self._all_clients_active():
                    print("\nall clients are connected, ready to send!")
                    self._send_message()
                    print("\npkt sent..")
                    self._reset_clients_data()
                    print("\nclients data reset..")
            elif client_ip == source_ip and self._clients[key] != (None, False):
                ip_valid = True
        if not ip_valid:
            print("Invalid client tried to connect! Exit..")
            try:
                self._socket_TCP.close()
            finally:
                sys.exit(0)
    
    def _all_clients_active(self):
        if self._active_clients_counter == len(self._clients.keys()):
            return True
        else:
            return False
                
    def _reset_clients_data(self):
        for k in self._clients.keys():
            self._clients[k] = (None, False)
        self._active_clients_counter = 0
        
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
        for key in self._clients.keys():
            client_ip = key[0]
            client_mac = key[1]
            pkt = self._clients.get(key)[0]
            lines = pkt.get_payload().split('\n')
            lines.remove('') #EOF
            # Formatting old payloads and adding them in new bulk payload
            for line in lines:
                line_data = line.split(" ")
                current = client_ip+" " +line_data[0]+" "+line_data[1]+" "+line_data[2]+"\n"
                message += current
        # create a packet with appropriate headers and new bulk payload
        pkt_to_send = PacketBuilder()\
            .ethernet_header(self._cloud_interface.get_mac_address(), self._arp_table_mac[pkt.get_dst_ip()])\
            .IP_header(self._cloud_interface.get_ip_address(), pkt.get_dst_ip())\
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
            self._socket_TCP.close()
            sys.exit(0)
        print("\nDATA SENT CORRECTLY\n")

    def _signal_handler(self, signal, frame):
        print('Ctrl+c pressed: sockets shutting down..')
        try:
            self._socket_TCP.close()
        finally:
            sys.exit(0)
        