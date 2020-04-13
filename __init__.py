#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: liathomson
"""

#__init__.py

from flask import Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = "salix" #not good form

from cyanoConstruct import CyanoConstructMod
from cyanoConstruct import Component

__version__ = "0.1"