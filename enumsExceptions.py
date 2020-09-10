#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains custom errors. If enums were in use, they would be here too.

@author: Lia Thomson
"""

#Parent class for errors
class Error(Exception):
	def __init__(self, message):
		if(type(message) != str):
			raise TypeError("message not a string")
			
		self.__message = message
	
	def __str__(self):
		return self.__message

#Various errors with self-descriptive names
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