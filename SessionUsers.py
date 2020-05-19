#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 19:58:38 2020

@author: Lia Thomson

cyanoConstruct sessionUsers file (SessionData and UserData classes)
"""

from cyanoConstruct import db, NamedSequence, SpacerData, PrimerData, checkType, UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, NotLoggedInError, UserDataDB

class SessionData:
    #defaultSession = SessionData.loadDefault()
    #nullPrimerData = PrimerData.makeNull() #the PrimerData used if making primers is skipped
    allSessions = {}

    maxTries = 5

    @classmethod
    def setSession(cls, sessionID, sessionData):
        if(type(sessionID) != str):
            raise TypeError("sessionID not a str")
        if(type(sessionData) != cls):
            raise TypeError("sessionData not a SessionData")

        cls.allSessions[sessionID] = sessionData

    @classmethod
    def getSession(cls, sessionID):
        print(cls.allSessions)

        try:
            return cls.allSessions[sessionID]
        except KeyError:
            return cls.tryGetSessionAgain(sessionID, 0) #or something

    @classmethod
    def tryGetSessionAgain(cls, sessionID, i):
        print("trying again at iteration " + str(i))
        print(cls.allSessions)

        if(i >= maxTries):
            return None

        try:
            return cls.allSessions[sessionID]
        except KeyError:
            return cls.tryGetSessionAgain(sessionID, i + 1)

    @classmethod
    def loadDefault(cls):
        defaultSession = cls("default")
        try:
            defaultUser = UserData.load("default") #edit to be load
        except UserNotFoundError:
            defaultUser = UserData.new("default")
        defaultSession.setUser(defaultUser)

        return defaultSession

    def __init__(self, newID):
        """Creates an instance of SessionData, which will store:
            sessionID
            loggedIn
            userData
            selected NS, SD, PD
            three different kinds of zips (why not just one?)"""
            
        self.__sessionID = newID
        self.__loggedIn = False
        self.__userData = None
        
        #no these Don't make sense thanks for asking
        self.__selectedDict = {"selectedNamedSequence": None, "selectedSpacers": None, "selectedPrimers": None}
        self.__forZIPDict = {"newCompZIP": None, "assemblyZIP": None, "componentForZIP": None}
        
        self.__libraryName = None

        SessionData.setSession(newID, self)
    
    def setUser(self, userData): #probably rename this
        """Assigns a UserData to the SessionData"""
        
        if(type(userData) != UserData):
            raise TypeError("userData not a UserData")
        
        self.__loggedIn = True
        self.__userData = userData
    
    def removeUser(self):
        """Removes the UserData from the SessionData"""
        self.__loggedIn = False
        self.__userData = None

    #getters
    def getUserData(self):
        return self.__userData
    
    def getID(self):
        return self.__sessionID
    
    def getLoggedIn(self):
        return self.__loggedIn
    
    def getEmail(self):
        if(self.getLoggedIn()):
            return self.getUserData().getEmail()
        else:
            raise NotLoggedInError("Not logged in.")
    
    def getNextNSid(self):
        if(self.getLoggedIn()):
            return self.getUserData().getNextNSid()
        else:
            raise NotLoggedInError("Not logged in.")

    def getAllNS(self): #returns a database entry: what to do with this
        if(self.getLoggedIn()):
            return self.getUserData().getAllNS()
        else:
            raise NotLoggedInError("Not logged in.")
    
    def getAllComps(self):
        if(self.getLoggedIn()):
            return self.getUserData().getAllComps()
        else:
            raise NotLoggedInError("Not logged in.")

    def getSelectedNS(self):
        return self.__selectedDict["selectedNamedSequence"]
    
    def getSelectedSpacers(self):
        return self.__selectedDict["selectedSpacers"]
    
    def getSelectedPrimers(self):
        return self.__selectedDict["selectedPrimers"]

    def getAllSelected(self):
        haveNS = self.getSelectedNS() is not None
        haveSpacers = self.getSelectedSpacers() is not None
        havePrimers = self.getSelectedPrimers() is not None
        return (haveNS and haveSpacers and havePrimers)

    def getLibraryName(self):
        return self.__libraryName

    def findNamedSequence(self, NStype, NSname, NSseq):
        if(self.getLoggedIn()):
            return self.getUserData().findNamedSequence(NStype, NSname, NSseq)
        else:
            raise NotLoggedInError("Not logged in.")
    
    def findComponent(self, compType, compName, compPos, compTerminalLetter):
        if(self.getLoggedIn()):
            return self.getUserData().findComponent(compType, compName, compPos, compTerminalLetter)
        else:
            raise NotLoggedInError("Not logged in.")

    def getSortedNS(self):
        if(self.getLoggedIn()):
            return self.getUserData().getSortedNS()
        else:
            raise NotLoggedInError("Not logged in.")

    def getSortedComps(self):
        if(self.getLoggedIn()):
            return self.getUserData().getSortedComps()
        else:
            raise NotLoggedInError("Not logged in.")

    #selected
    def setSelectedNS(self, newNS):
        if(type(newNS) != NamedSequenceDB): #####<----- is this not a NamedSequenceDB?
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

    def getNewCompZIP(self):
        return self.__forZIPDict["newCompZIP"]
    
    def getAssemblyZIP(self):
        return self.__forZIPDict["assemblyZIP"]

    def getComponentForZIP(self):
        return self.__forZIPDict["componentForZIP"]

    #forZIP
    def setNewCompZIP(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZIPDict["newCompZIP"] = newFile
    
    def setAssemblyZIP(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZIPDict["assemblyZIP"] = newFile

    def setComponentForZIP(self, newFile):
        if(type(newFile) != dict):
            raise TypeError("newFile not a dict")
        self.__forZIPDict["componentForZIP"] = newFile
        
    def setLibraryName(self, libraryName):
        self.__libraryName = libraryName
        
    #all NamedSequences
    def addNS(self, newNS):
        if(self.getLoggedIn()):
            return self.getUserData().addNS(newNS)
        else:
            raise NotLoggedInError("Not logged in.")

    def addNSDB(self, namedSeq):    #####<---- I would like to phase this out eventually, and just pass an id through
        if(self.getLoggedIn()):
            return self.getUserData().addNSDB(namedSeq)
        else:
            raise NotLoggedInError("Not logged in.")

    #all Components
    def addComp(self, newComp):
        if(self.getLoggedIn()):
            return self.getUserData().addComp(newComp)
        else:
            raise NotLoggedInError("Not logged in.")

    def removeComponent(self, compType, compName, compPos, compTerminalLetter):
        if(self.getLoggedIn()):
            return self.getUserData().removeComponent(compType, compName, compPos, compTerminalLetter)
        else:
            raise NotLoggedInError("Not logged in.")

    def removeSequence(self, seqType, seqName):
        if(self.getLoggedIn()):
            return self.getUserData().removeSequence(seqType, seqName)
        else:
            raise NotLoggedInError("Not logged in.")

    #make stuff
    def makeFromNew(self, elemType, name, seq, position, isTerminal, TMgoal, TMrange):
        if(self.getLoggedIn()):
            return self.getUserData().makeFromNew(elemType, name, seq, position, isTerminal, TMgoal, TMrange)
        else:
            raise NotLoggedInError("Not logged in.")
    
    def createNS(self, NStype, NSname, NSseq):
        if(self.getLoggedIn()):
            return self.getUserData().createNS(NStype, NSname, NSseq)
        else:
            raise NotLoggedInError("Not logged in.")
    
    def createComp(self, NSentry, spacerData, primerData):
        if(self.getLoggedIn()):
            return self.getUserData().createComp(NSentry, spacerData, primerData)
        else:
            raise NotLoggedInError("Not logged in.")

    def makeWithNamedSequence(self, ns, position, isTerminal, TMgoal, TMrange):
        if(self.getLoggedIn()):
            return self.getUserData().makeWithNamedSequence(ns, position, isTerminal, TMgoal, TMrange)
        else:
            raise NotLoggedInError("Not logged in.")
    
    #idk man
    def getStartEndComps(self):
        if(self.getLoggedIn()):
            return self.getUserData().getStartEndComps()
        else:
            raise NotLoggedInError("Not logged in.")
    
class UserData:
    def __init__(self):
        """Creates an empty UserData. Should not be accessed except through makeNew or load"""
        self.__DBid = -1
        self.__entryDB = None
        return
    
    @classmethod
    def new(cls, email):
        print("Calling UserData.new(" + str(email) + ").\n")        
        #type validation
        if(type(email) != str):
            raise TypeError("email not a str")
                            
        #see if it already exists
        if(UserDataDB.query.filter_by(email = email).all() != []):
            raise AlreadyExistsError("User with email " + email + " already exists.")

        #begin creating stuff
        newUserData = cls()
        
        if(email == "default"):
            nextNSid = 1
        else:
            nextNSid = 101
        
        #add to database
        u = UserDataDB(nextNSidPR = nextNSid, nextNSidRBS = nextNSid, nextNSidGOI = nextNSid, nextNSidTERM = nextNSid,
                       email = email)

        db.session.add(u)
        db.session.commit()
        
        #finish off
        newUserData.__DBid = u.id
        newUserData.__entryDB = u
        
        return newUserData

    @classmethod
    def load(cls, email):
        queryResults = UserDataDB.query.filter_by(email = email).all()
        
        if(len(queryResults) == 0):
            raise UserNotFoundError("Could not find user.")
        elif(len(queryResults) > 1):
            raise Exception("Multiple users exists with this email.")
        else:
            u = queryResults[0]

            newUserData = cls()
            
            newUserData.__DBid = u.getID()
            newUserData.__entryDB = u
            
            return newUserData

    #getters    
    def getID(self): #potentially superfluous, not currently in use
        return self.__DBid
    
    def getEntry(self):
        return self.__entryDB

    def getEmail(self):
        return self.getEntry().getEmail()    

    def getAllNSQuery(self):
        return self.getEntry().getAllNamedSeqs()
    
    def getAllCompsQuery(self):
        return self.getEntry().getAllComponents()
    
    def getAllNS(self):
        return self.getAllNSQuery().all()
            
    def getAllComps(self):
        return self.getAllCompsQuery().all()
        
    def getSortedNS(self):
        allPr = self.getAllNSQuery().filter_by(elemType = "Pr").order_by(NamedSequenceDB.nameID.asc()).all()
        allRBS = self.getAllNSQuery().filter_by(elemType = "RBS").order_by(NamedSequenceDB.nameID.asc()).all()
        allGOI = self.getAllNSQuery().filter_by(elemType = "GOI").order_by(NamedSequenceDB.nameID.asc()).all()
        allTerm = self.getAllNSQuery().filter_by(elemType = "Term").order_by(NamedSequenceDB.nameID.asc()).all()
        return {"Pr": allPr, "RBS": allRBS, "GOI": allGOI, "Term": allTerm}
    
    def getSortedComps(self):
        allNS = self.getSortedNS()
        
        retDict = {}
        
        allComps = self.getAllCompsQuery()
        
        for nsGroupKey in allNS:
            typeRow = {}
            for ns in allNS[nsGroupKey]:
                
                #is this efficient? I don't know
                sortedComps = allComps.filter_by(namedSequence_id = ns.getID()).all()
                sortedComps.sort()
                typeRow[ns.getName()] = sortedComps
                
            retDict[nsGroupKey] = typeRow

        return retDict
    
    def findNamedSequence(self, NStype, NSname, NSseq):
        """Searches UserDataDB for named sequence with specifications"""
        checkType(NStype, "NStype")

        if(type(NSname) != str):
            raise TypeError("name not a string")
        if(type(NSseq) != str):
            raise TypeError("seq not a string")

        #some preprocessing of the input
        seq = NSseq.upper()
        
        #query the database for actual searching
        namedSeqList = self.getAllNSQuery().filter_by(elemType = NStype, name = NSname).all()
                
        #handle the results from the query
        if(len(namedSeqList) == 0):
            raise SequenceNotFoundError("Could not find sequence.")
        if(len(namedSeqList) > 1):
            raise Exception("Multiple sequences found.")
        else:
            namedSeq = namedSeqList[0]
            #check sequence
            if(namedSeq.getSeq() == seq):
                return namedSeq #return the NamedSequence database entry. This is okay?
            else:
                raise SequenceMismatchError("Sequence does not match stored sequence.")
    
    def findNamedSequenceNoSeq(self, NStype, NSname):
        checkType(NStype, "NStype")

        if(type(NSname) != str):
            raise TypeError("name not a string")

        #query the database for actual searching
        namedSeqList = self.getAllNSQuery().filter_by(elemType = NStype, name = NSname).all()
                
        #handle the results from the query
        if(len(namedSeqList) == 0):
            raise SequenceNotFoundError("Could not find sequence.")
        if(len(namedSeqList) > 1):
            raise Exception("Multiple sequences found.")
        else:
            return namedSeqList[0]
    
    def findComponent(self, compType, compName, compPos, compTerminalLetter):
        """Searches UserDataDB for component with specifications"""
        checkType(compType, "compType")

        if(type(compName) != str):
            raise TypeError("compName not a string")
        if(type(compPos) != int):
            raise TypeError("comPos not an int")
        if(type(compTerminalLetter) != str):
            raise TypeError("compTerminalLetter not a string")


        #search for the NamedSequence
        possibleNS = self.getAllNSQuery().filter_by(elemType = compType, name = compName).all()
        
        
        if(len(possibleNS) == 0):
            raise SequenceNotFoundError("No sequence of type " + compType + " ID " + str(compName) + " found.")
        elif(len(possibleNS) > 1):
            raise Exception("Multiple sequences of type " + compType + " ID " + str(compName) + " found.")
        else:
            ns = possibleNS[0]
            
            #search for the Component
            for comp in ns.getAllComponents():
                if((comp.getPosition() == compPos) and (comp.getTerminalLetter() == compTerminalLetter)):
                       return comp
                            
        #did not find it
        raise ComponentNotFoundError("Could not find component.")
        
    def removeComponent(self, compType, compName, compPos, compTerminalLetter):
        """Removes component from UserDataDB by finding it and calling on removeFoundComp"""
        #find component
        foundComp = self.findComponent(compType, compName, compPos, compTerminalLetter)

        self.removeFoundComponent(foundComp)
        
    def removeFoundComponent(self, foundComp):
        """Removes component and its associated primerData and spacerData from the database"""
        foundSpacerData = foundComp.getSpacerData()
        foundPrimerData = foundComp.getPrimerData()

        #check if foundPrimerData is actually the null primer; do not delete it then

        #remove them from database
        db.session.delete(foundComp)
        db.session.delete(foundSpacerData)
        db.session.delete(foundPrimerData)
        db.session.commit()
        
    def removeSequence(self, seqType, seqName):
        """Removes namedSequence from UserDataDB by finding it, removing all its components, and removing it."""
        foundNS = self.findNamedSequenceNoSeq(seqType, seqName)
        
        #remove all components using the NamedSequence
        for foundComp in foundNS.getAllComponents():
            self.removeFoundComponent(foundComp)
        
        #remove the NamedSequence
        db.session.delete(foundNS)
        
        db.session.commit()
    
    def addNSDB(self, namedSeq):
        """Pass in a NamedSequenceDB, will create a copy in current user."""
        
        if(type(namedSeq) != NamedSequenceDB):
            raise TypeError("namedSeq not a NamedSequenceDB.")
        
        #check if it already exists
        try:
            self.findNamedSequence(namedSeq.getType(), namedSeq.getName(), namedSeq.getSeq())
            
            #an error will be raised if it exists
            raise AlreadyExistsError("Sequence already exists.")
            
        except SequenceNotFoundError:
            pass

        #make entry
        NStype = namedSeq.getType()
        NSname = namedSeq.getName()
        NSseq = namedSeq.getSeq()
        
        nameID = namedSeq.getNameID() #self.getEntry().getNextNSid()[NStype]
        
        n = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq, nameID = nameID, user_id = self.getEntry().getID())
        
        #add to database
        db.session.add(n)
        
        self.getEntry().incrementID(NStype)
        
        db.session.commit()
        
        return n
        
    
    def addNS(self, namedSeq):
        """Pass in a NamedSequence, will create a NamedSequenceDB and add it to the database."""
        
        if(type(namedSeq) != NamedSequence):
            raise TypeError("namedSeq not a NamedSequence.")
        
        #check if it already exists
        try:
            self.findNamedSequence(namedSeq.getType(), namedSeq.getName(), namedSeq.getSeq())
            
            #an error will be raised if it exists
            
            raise AlreadyExistsError("Sequence already exists.")
            
        except SequenceNotFoundError:
            pass

        #make entry
        NStype = namedSeq.getType()
        NSname = namedSeq.getName()
        NSseq = namedSeq.getSeq()
        
        nameID = self.getEntry().getNextNSid()[NStype]
        
        n = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq, nameID = nameID, user_id = self.getEntry().getID())
        
        #add to database
        db.session.add(n)
        
        self.getEntry().incrementID(NStype)
        
        db.session.commit()
        
        return n
            
    def createNS(self, NStype, NSname, NSseq):
        """Pass in raw data, creates a NamedSequence and then makes NamedSequenceDB via self.addNS(newNS)"""
        #type checking
        checkType(NStype, "NStype")

        if(type(NSname) != str):
            raise TypeError("NSname not a string")
        if(type(NSseq) != str):
            raise TypeError("NSseq not a string")


        #get the nameID
        nameID = self.getEntry().getNextNSid()[NStype]

        #create it
        newNS = NamedSequence.makeNew(NStype, NSname, NSseq, nameID)
        
        #add it to self
        NSentry = self.addNS(newNS)
        
        #change newNS so it knows it's been loaded into the database
        newNS.setDBid(NSentry.id) #####<----- why? It works but is inefficient
        
        return NSentry
    
    def createComp(self, NSentry, spacerData, primerData):
        if(type(NSentry) != NamedSequenceDB):
            raise TypeError("NSentry not a NamedSequenceDB")
        if(type(spacerData) != SpacerData):
            raise TypeError("spacerData not a SpacerData")
        if(type(primerData) != PrimerData):
            raise TypeError("primerData not a PrimerData")
                    
        """Make a ComponentDB and associated SpacerDataDB, PrimerDataDB in database."""        
        #check if it already exists
        try:
            self.findComponent(NSentry.getType(), NSentry.getName(), spacerData.getPosition(), spacerData.getTerminalLetter())

            raise AlreadyExistsError("Component already exists.")
        except ComponentNotFoundError:
            pass
                
        s = SpacerDataDB(position = spacerData.getPosition(), spacerLeft = spacerData.getSpacerLeft(), spacerRight = spacerData.getSpacerRight(),
                 isTerminal = spacerData.getIsTerminal(), terminalLetter = spacerData.getTerminalLetter(),
                 leftNN = spacerData.getLeftNN(), rightNN = spacerData.getRightNN())

        p = PrimerDataDB(primersFound = primerData.getPrimersFound(), seqLeft = primerData.getSeqLeft(), seqRight = primerData.getSeqRight(),
                 GCleft = primerData.getGCleft(), GCright = primerData.getGCright(), TMleft = primerData.getTMleft(), TMright = primerData.getTMright())

        c = ComponentDB(namedSequence_id = NSentry.getID(), user_id = self.getEntry().getID())

        #s.comp = c
        #p.comp = c
        
        #add to the database
        db.session.add(c)
        db.session.add(s)
        db.session.add(p)
        
        db.session.commit()
        
        #of questionable use, but regardless
#        spacerData.setDBid(s.id)
#        primerData.setDBid(p.id)

        c.setSpacerDataID(s.getID())
        c.setPrimerDataID(p.getID())
        s.setCompID(c.getID())
        p.setCompID(c.getID())

        db.session.commit() #is it necessary? perhaps

        return c
        
    def makeWithNamedSequence(self, ns, position, isTerminal, TMgoal, TMrange):
        if(type(ns) != NamedSequenceDB):
            raise TypeError("ns not a NamedSequenceDB")
        
        #type checking
        if(type(position) != int):
            raise TypeError("position not an int")
        if(type(isTerminal) != bool):
            raise TypeError("isTerminal is not a bool")
        if(type(TMgoal) != int and type(TMgoal) != float):
            raise TypeError("TMgoal not an int or float")
        if(type(TMrange) != int and type(TMrange) != float):
            raise TypeError("TMrange not an int or float")
        
        #SpacerData
        newSpacerData = SpacerData.makeNew(position, isTerminal)

        #PrimerData
        newPrimerData = PrimerData.makeNew(ns.getSeq(), TMgoal, TMrange)
        newPrimerData.addSpacerSeqs(newSpacerData)

        return self.createComp(ns, newSpacerData, newPrimerData)
    
    #creates a new component and adds it
    def makeFromNew(self, elemType, name, seq, position, isTerminal, TMgoal, TMrange):
        #NamedSequenceDB
        ns = self.createNS(elemType, name, seq)
        
        return self.makeWithNamedSequence(ns, position, isTerminal, TMgoal, TMrange)
        
    def getNextNSid(self):
        return self.getEntry().getNextNSid()

    def getStartEndComps(self):
        if(self.getEntry().getEmail() != "default"):
            raise Exception("can't get StartEndComps from non-default session")
        
        startComp = self.findComponent("Pr", "psbA", 0, "S")
        endComp = self.findComponent("Term", "T1", 999, "T")
        
        return (startComp, endComp)

class Globals:
    defaultSession = SessionData.loadDefault()
    nullPrimerData = PrimerData.makeNull()

    @classmethod
    def getDefault(cls):
        return cls.defaultSession

    @classmethod
    def getNullPrimerData(cls):
        return cls.nullPrimerData