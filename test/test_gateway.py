#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 22:06:18 2021

@author: daze
"""

from factories import GatewayFactory

f = GatewayFactory()
gateway = f.default_gateway()