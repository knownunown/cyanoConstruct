#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 17:47:04 2020

@author: liathomson
"""
import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyanoConstruct import db

class NamedSeqs2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user_data2.id"))
    
    def __repr__(self):
        return "<Named Squence{}>".format(self.content)
    #ughhhhhh

class UserData2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    allNamedSeqs = db.relationship("NamedSeqs2", backref = "owner", lazy = "dynamic")

    def __repr__(self):
        return '<User {}>'.format(self.email)
    
