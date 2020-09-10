#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Lia Thomson

cyanoConstruct file to run (because there is currently no __main__ file)
"""

import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyanoConstruct import app

if(__name__ == "__main__"):
    app.run(debug=True)