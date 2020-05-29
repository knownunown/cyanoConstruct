#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 20:44:56 2020

@author: Lia Thomson

cyanoConstruct enumsExceptions file
"""

#from enum import Enum

class Error(Exception):
    def __init__(self, message):
        if(type(message) != str):
            raise TypeError("message not a string")
            
        self.__message = message
    
    def __str__(self):
        return self.__message

class AlreadyExistsError(Error):
    pass
    
class SequenceMismatchError(Error):
    pass
    
class SequenceNotFoundError(Error):
    pass

class ComponentNotFoundError(Error):
    pass

class BackboneNotFoundError(Error):
    pass

class UserNotFoundError(Error):
    pass

class NotLoggedInError(Error):
    pass

class AccessError(Error):
    pass