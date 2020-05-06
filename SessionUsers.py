#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 15:22:25 2020

@author: liathomson
"""

from cyanoConstruct.Component import NamedSequence, SpacerData, PrimerData, Component

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
    
class SessionData:
    #yeah
    
    sessionsByID = {}
    
    def __init__(self, newID):
        self.__sessionID = newID
        self.__loggedIn = False
        self.__userData = UserData(newID)
        
        #no these Don't make sense thanks for asking
        self.__selectedDict = {"selectedNamedSequence": None, "selectedSpacers": None, "selectedPrimers": None}
        self.__forZipDict = {"newCompZip": None, "assemblyZip": None, "componentForZip": None}
    
    def logInAs(self, userData):
        self.__loggedIn = True
        self.__userData = userData
    
    def logOut(self):
        self.__loggedIn = False
        self.__userData = None

    #getters
    def getUserData(self):
        return self.__userData
    
    def getID(self):
        return self.__sessionID
    
    def getNextNSid(self):
        return self.__userData.getNextNSid()

    def getAllNS(self):
        return self.__userData.getAllNS()
    
    def getAllComps(self):
        return self.__userData.getAllComps()

    def getSelectedNS(self):
        return self.__selectedDict["selectedNamedSequence"]
    
    def getSelectedSpacers(self):
        return self.__selectedDict["selectedSpacers"]
    
    def getSelectedPrimers(self):
        return self.__selectedDict["selectedPrimers"]

    def getAllSelected(self):
        haveNS = self.getSelectedNS() != None
        haveSpacers = self.getSelectedSpacers() != None
        havePrimers = self.getSelectedPrimers() != None
        return (haveNS and haveSpacers and havePrimers)

    def findNamedSequence(self, NStype, NSname, NSseq):
        return self.__userData.findNamedSequence(NStype, NSname, NSseq)
    
    def findComponent(self, compType, compName, compPos, compTerminalLetter):
        return self.__userData.findComponent(compType, compName, compPos, compTerminalLetter)

    #selected
    def setSelectedNS(self, newNS):
        if(type(newNS) != NamedSequence):
            raise TypeError("newNS not a NamedSequence")
        
        self.__selectedDict["selectedNamedSequence"] = newNS
    
    def setSelectedSpacers(self, newSpacers):
        if(type(newSpacers) != SpacerData):
            raise TypeError("newSpacers not a SpacerData")
            
        self.__selectedDict["selectedSpacers"] = newSpacers
    
    def setSelectedPrimers(self, newPrimers):
        if(type(newPrimers) != PrimerData):
            raise TypeError("newPrimers not a PrimerData")
            
        self.__selectedDict["selectedPrimers"] = newPrimers

    def getNewCompZip(self):
        return self.__forZipDict["newCompZip"]
    
    def getAssemblyZip(self):
        return self.__forZipDict["assemblyZip"]

    def getComponentForZip(self):
        return self.__forZipDict["componentForZip"]

    #forZip
    def setNewCompZip(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZipDict["newCompZip"] = newFile
    
    def setAssemblyZip(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZipDict["assemblyZip"] = newFile

    def setComponentForZip(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZipDict["componentForZip"] = newFile
        
    #all NamedSequences
    def addNS(self, newNS):
        return self.__userData.addNS(newNS)
    
    #all Components
    def addComp(self, newComp):
        return self.__userData.addComp(newComp)

    def removeComponent(self, compType, compName, compPos, compTerminalLetter):
        return self.getUserData().removeComponent(compType, compName, compPos, compTerminalLetter)

    def removeSequence(self, seqType, seqName):
        return self.getUserData().removeSequence(seqType, seqName)

    #make stuff
    def makeFromNew(self, elemType, name, seq, position, isTerminal, TMgoal, TMrange):
        return self.__userData.makeFromNew(elemType, name, seq, position, isTerminal, TMgoal, TMrange)
    
    def createNS(self, NStype, NSname, NSseq):
        return self.__userData.createNS(NStype, NSname, NSseq)
    
class UserData:
    def __init__(self, newID):
        self.__id = newID
        self.__allNSdict = {"Pr" : {}, "RBS": {}, "GOI": {}, "Term": {}}
        self.__allCompsDict = {"Pr" : {}, "RBS": {}, "GOI": {}, "Term": {}}

        if(newID == "default"):
            self.__nextNSid = {"Pr": 1, "RBS": 1, "GOI": 1, "Term": 1}
        else:
            self.__nextNSid = {"Pr": 101, "RBS": 101, "GOI": 101, "Term": 101}
    
    
    #getters
    def getID(self):
        return self.__id
    
    def getAllNS(self):
        return self.__allNSdict
    
    def getAllComps(self):
        return self.__allCompsDict
    
    def getNextNSid(self):
        return self.__nextNSid
    
    def findNamedSequence(self, NStype, NSname, NSseq):
        if(NStype not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("elemType not valid")
        if(type(NSname) != str):
            raise TypeError("name not a string")
        if(type(NSseq) != str):
            raise TypeError("seq not a string")

        seq = NSseq.upper()
        
        try:
            namedSeq = self.__allNSdict[NStype][NSname]
            
            #check sequence
            if(namedSeq.getSeq() == seq):
                return namedSeq
            else:
                raise SequenceMismatchError("Sequence does not match stored sequence.")
            
        except KeyError:
            raise SequenceNotFoundError("Could not find sequence.")

    def findComponent(self, compType, compName, compPos, compTerminalLetter):
        if(compType not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("compType not valid")
        if(type(compName) != str):
            raise TypeError("compName not a string")
        if(type(compPos) != int):
            raise TypeError("comPos not an int")
        if(type(compTerminalLetter) != str):
            raise TypeError("compTerminalLetter not a string")
                     
        #no error handling?
        return self.getAllComps()[compType][compName][compPos][compTerminalLetter]

    def removeComponent(self, compType, compName, compPos, compTerminalLetter):
        if(compType not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("compType not valid")
        if(type(compName) != str):
            raise TypeError("compName not a string")
        if(type(compPos) != int):
            raise TypeError("comPos not an int")
        if(type(compTerminalLetter) != str):
            raise TypeError("compTerminalLetter not a string")

        del self.getAllComps()[compType][compName][compPos][compTerminalLetter]

    def removeSequence(self, seqType, seqName):
        if(seqType not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("compType not valid")
        if(type(seqName) != str):
            raise TypeError("compName not a string")

        #remove all components
        allPosKeys = list(self.getAllComps()[seqType][seqName].keys())
        for posKey in allPosKeys:
            allTerminalLetterKeys = list(self.getAllComps()[seqType][seqName][posKey].keys())
            for terminalLetter in allTerminalLetterKeys:
                self.removeComponent(seqType, seqName, posKey, terminalLetter)

        #remove NS
        del self.getAllNS()[seqType][seqName]
    
    #add to the dict
    def addNS(self, newNS):
        if(type(newNS) != NamedSequence):
            raise TypeError("newNS not a NamedSequence")
        
        #check if it already exists
        try:
            self.__allNSdict[newNS.getType()][newNS.getName()]
            raise AlreadyExistsError("newNS already in library") #should define a different kind of exception
            
        #if it doesn't
        except KeyError:
            self.__allNSdict[newNS.getType()][newNS.getName()] = newNS
    
    def addComp(self, newComp):
        if(type(newComp) != Component):
            raise TypeError("newComp not a Component")
        
        #check if it already exists
        try:
            self.getAllComps()[newComp.getType()][newComp.getName()][newComp.getPosition()][newComp.getTerminalLetter()]
            raise AlreadyExistsError("Component already in library.")
            
        #if it doesn't
        except KeyError:
            try:
                #if there is already a comp with the same position (but different terminalLetter)
                self.getAllComps()[newComp.getType()][newComp.getName()][newComp.getPosition()][newComp.getTerminalLetter()] = newComp
                
            except KeyError:
                try:
                    #if there is already a comp with the same name (but different position)
                    self.getAllComps()[newComp.getType()][newComp.getName()][newComp.getPosition()] = {newComp.getTerminalLetter(): newComp}
                    
                except KeyError:
                    #if there is not already a comp with the same name
                    self.getAllComps()[newComp.getType()][newComp.getName()] = {newComp.getPosition(): {newComp.getTerminalLetter(): newComp}}
    
    def createNS(self, NStype, NSname, NSseq):
        #type checking
        if(NStype not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("NStype not valid")
        if(type(NSname) != str):
            raise TypeError("NSname not a string")
        if(type(NSseq) != str):
            raise TypeError("NSseq not a string")
                    
        #look to see if it's already made
        for typeKey in self.__allNSdict.keys():
            for nameKey in self.__allNSdict[typeKey].keys():
                if(NSname == nameKey):
                    raise Exception(nameKey + " already made as a " + NamedSequence.typeShortToLong[typeKey] + ".")

        #nameID
        nameID = self.__nextNSid[NStype]
        self.__nextNSid[NStype] += 1

        #create it
        newNS = NamedSequence(NStype, NSname, NSseq, nameID)
        
        #add it to self
        self.addNS(newNS)
        
        return newNS
        
    #creates a new component and adds it
    def makeFromNew(self, elemType, name, seq, position, isTerminal, TMgoal, TMrange):
        #type checking
        if(elemType not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("elemType not valid")
        if(type(name) != str):
            raise TypeError("name not a string")
        if(type(seq) != str):
            raise TypeError("seq not a string")
        if(type(position) != int):
            raise TypeError("position not an int")
        if(type(isTerminal) != bool):
            raise TypeError("isTerminal is not a bool")
        if(type(TMgoal) != int and type(TMgoal) != float):
            raise TypeError("TMgoal not an int or float")
        if(type(TMrange) != int and type(TMrange) != float):
            raise TypeError("TMrange not an int or float")
        
        #make the other class instances
        newNamedSequence = self.createNS(elemType, name, seq)
        
        newSpacerData = SpacerData(position, isTerminal)
        newPrimerData = PrimerData(seq, TMgoal, TMrange)
        newPrimerData.addSpacerSeqs(newSpacerData)
        
        #make the component
        newComponent = Component(newNamedSequence, newSpacerData, newPrimerData) #or such
        
        self.addComp(newComponent)
                
        return (newComponent, newNamedSequence)
