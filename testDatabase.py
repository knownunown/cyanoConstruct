#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:51:41 2020

@author: liathomson
"""

#testing out the databse

import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyanoConstruct import db
from cyanoConstruct.CCDatabase import UserData2, NamedSeqs2

user = UserData2(email = "testyThing@gmail.com")
namedSeq = NamedSeqs2(content = "yay. words", owner = user)