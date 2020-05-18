#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:27:32 2020

@author: liathomson
"""

#configuration I suppose

class Config(object):
    SECRET_KEY = "Salix-babylonica" #should get a better secret key
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test42.db"
    #SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False