#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 12:19:14 2021

@author: daze
"""

from subprocess import Popen
import sys
sys.path.append('../')
import factories as f

def execute(target):
    Popen(["python", target + ".py"])
    
def test():
    print("Device 1")
    execute("test_dev1")
    
    print("Device 2")
    execute("test_dev2")
    
    print("Device 3")
    execute("test_dev3")
    
    print("Device 4")
    execute("test_dev4")
    
if __name__ == "__main__":
    test()

