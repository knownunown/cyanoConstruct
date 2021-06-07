#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Misc. multi-use functions.

@author: Lia Thomson
"""

printActions = True


def printIf(message):
    """Helper function that prints a message if printActions is True."""
    if printActions:
        print(message)


def checkType(elemType, typeName):
    """Check if string elemType is valid, and raises an error with typeName as
    part of the message if not.

    RAISES
            TypeError: if elemType or typeName are not strings.
            ValueError: if elemType is not "Pr", "RBS", "GOI", or "Term"
    """
    if type(typeName) != str:
        raise TypeError("typeName not a string")

    if type(elemType) != str:
        raise TypeError(typeName + " not a string")
    if elemType not in ["Pr", "RBS", "GOI", "Term"]:
        raise ValueError(typeName + " not valid")
