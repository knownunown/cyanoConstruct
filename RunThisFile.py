#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 14:06:24 2020

@author: Lia Thomson

cyanoConstruct file to run (because there is currently no __main__ file)
"""

import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyanoConstruct import app

app.run(debug=True)