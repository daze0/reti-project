#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 22:06:18 2021

@author: daze
"""

import sys
sys.path.append('../')
import factories as f

gateway = f.GatewayFactory().default_gateway()