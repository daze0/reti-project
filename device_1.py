
"""
Created on Mon May 10 17:07:38 2021

@author: daze and fedebruno
"""

from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread, currentThread
import time, os, Measurement

class device:
    def __init__(self, device_ip, server_addr): #deviceip, ('192.168.1.1', 10000)
        # Socket used to connect to the GATEWAY
        self.sock = socket(AF_INET, SOCK_DGRAM)
        # timer thread flag
        #self.socket_on = True
        # Arg type validity check
        try:
            self.server_address = tuple(server_addr)
        except TypeError as info:
            print(info)
        # Useful for sending data periodically to the server
        # Initially set at -1
        self.data_dump_timer = -1
        # This is the filename of the file that contains 24h worth of data 
        self.filename = "data_1.txt"
        # CONSTANTS
        self.SEP = " "
        self.PERIOD = 25 # secs
        self.BUFSIZE = 4096
        # Device IP as file header
        self.ip = device_ip
        with open(self.filename, "wt") as f:
            f.write(self.ip+"\n")
        # Start timer thread
        self.timer = Thread(target=self.checktimer)
        self.timer.start()
        while True:
            self.get_data()
            time.sleep(5)
    
    # Periodically send data to GATEWAY
    def checktimer(self):
        t = currentThread()
        self.data_dump_timer = 0
        while getattr(t, "do_run", True):
            # check if timer has already been set
            if self.data_dump_timer == -1:
                self.data_dump_timer = time.time()
            #if set verify if elapsed time is equal or greater than period break cycle
            if time.time()-self.data_dump_timer >= self.PERIOD:
                self.send()
                self.data_dump_timer = -1
                os.remove(self.filename)
                with open(self.filename, "wt") as f:
                    f.write(self.ip+"\n")   
            time.sleep(1)
                
    # Get a measurement from the user
    # Write it on data file
    def get_data(self):
        print("\nNew measurement: ")
        measure = Measurement.Measurement()
        with open(self.filename, "a") as f:
            f.write(measure.get_time()+self.SEP+measure.get_temperature()+self.SEP+measure.get_humidity()+"\n")
            print("Time: "+measure.get_time())
            print("Temperature: "+measure.get_temperature())
            print("Humidity: "+measure.get_humidity())
        return True
        
    # Send data file to GATEWAY
    def send(self):
        with open(self.filename, "rb") as file:
            while True:
                r = file.read(self.BUFSIZE)
                if not r:
                    break
                else:
                    try:
                        self.sock.sendto(r, self.server_address)
                    except Exception as info:
                        print(info)
                        
    # Close device socket
    def close_sock(self):
        print ('closing socket')
        self.sock.close()
        self.timer.do_run = False

dev1 = device("192.168.1.13", ('localhost', 13008))

#while dev1.get_data():
#   continue
        
#dev1.close_sock()