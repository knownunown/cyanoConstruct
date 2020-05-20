#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:31:17 2020

@author: liathomson
"""

from cyanoConstruct import AlreadyExistsError

class AllSessions:
    def __init__(self):
        self.__allSessions = {}
    
    def addSession(self, sessionID, sessionData):
        try:
            self.__allSessions[sessionID]
            
            raise AlreadyExistsError("session already exists")
        except KeyError:
            self.__allSessions[sessionID] = sessionData
    
    def getSession(self, sessionID):
        print("allSessions dict")
        print(self.__allSessions)
        print("allSessions self")
        print(self)
        
        try:
            return self.__allSessions[sessionID]
        except KeyError:
            return None
