#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:27:32 2020

@author: Lia Thomson

cyanoConstruct config file
"""
import os

class Config(object):
    SECRET_KEY = "Salix babylonica crispa" #should get a better secret key
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cyano.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    static_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
    
"""
class Config(object):
    SECRET_KEY = "Salix babylonica crispa" #should get a better secret key
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
                                username="cyanogate",
                                password="CanisLupus",
                                hostname="cyanogate.mysql.pythonanywhere-services.com",
                                databasename="cyanogate$cyanoconstruct",
                                )

    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""