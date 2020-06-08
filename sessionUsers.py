#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 19:58:38 2020

@author: Lia Thomson

cyanoConstruct sessionUsers file (UserData class)
"""
from cyanoConstruct import printActions
from cyanoConstruct import db, UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, BackboneDB
from cyanoConstruct import NamedSequence, SpacerData, PrimerData, checkType
from cyanoConstruct import AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, BackboneNotFoundError, NotLoggedInError

class UserData:
    def __init__(self):
        """Creates an empty UserData. Should not be accessed except through new or load"""
        self.__DBid = -1
        self.__entryDB = None

        self.__selectedNS = None
        self.__selectedSD = None
        self.__selectedPD = None
        return
    
    @classmethod
    def new(cls, email):
        """Create a new user: creates a UserData and a UserDataDB. Return the created userData."""
        if(printActions):
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
        """Load a user from the UserDataDB table."""
        queryResults = UserDataDB.query.filter_by(email = email).all()
        
        #check results
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

    #properties for Flask-Login
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.getEmail()

    #basic setters
    def setSelectedNS(self, namedSeq):
        if(type(namedSeq) != NamedSequenceDB):
            raise TypeError("namedSeq not a NamedSequenceDB")

        print("adding: {}".format(namedSeq))

        self.__selectedNS = namedSeq

    def setSelectedSD(self, spacerData):
        if(type(spacerData) != SpacerData):
            raise TypeError("spacerData not a SpacerData")


        print("adding: {}".format(spacerData))

        self.__selectedSD = spacerData

    def setSelectedPD(self, primerData):
        if(type(primerData) != PrimerData):
            raise TypeError("primerData not a PrimerData")

        print("adding: {}".format(primerData))

        self.__selectedPD = primerData

    def setGoogleAssoc(self, assoc):
        if(type(assoc) != bool):
            raise TypeError("assoc not a bool")

        return self.getEntry().setGoogleAssoc(assoc)

    def setGoogleID(self, newID):
        if(type(newID) != str):
            raise TypeError("newID not a str")

        return self.getEntry().setGoogleID(newID)

    #getters
    def getID(self):
        return self.__DBid
    
    def getEntry(self):
        return self.__entryDB

    def getEmail(self):
        return self.getEntry().getEmail()

    def getSelectedNS(self):
        return self.__selectedNS

    def getSelectedSD(self):
        return self.__selectedSD

    def getSelectedPD(self):
        return self.__selectedPD

    def getNextNSid(self):
        return self.getEntry().getNextNSid()

    def getGoogleAssoc(self):
        return self.getEntry().getGoogleAssoc()

    def getGoogleID(self):
        return self.getEntry().getGoogleID()

    #get all query
    def getAllNSQuery(self): #a query
        return self.getEntry().getAllNamedSeqs()
    
    def getAllCompsQuery(self): #a query
        return self.getEntry().getAllComponents()
    
    def getAllBBQuery(self):
        return self.getEntry().getAllBackbones()    

    #get all array
    def getAllNS(self):
        return self.getAllNSQuery().all()
            
    def getAllComps(self):
        return self.getAllCompsQuery().all()
    
    def getAllBB(self):
        return self.getEntry().getAllBackbones().all()

    #get sorted
    def getSortedNS(self):
        """Return dict, key: type, value: sorted array of all NamedSequenceDB of the type."""
        #the use of order_by is likely unnecessary, but not deeply detrimental
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
    
    def getSortedNSandComps(self):
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

        return (allNS, retDict)
    
    def getSortedBB(self):
        allBB = self.getAllBB()
        allBB.sort()

        return allBB

    #find
    def findNamedSequenceNoSeq(self, NStype, NSname):
        """Searches UserDataDB for NamedSequenceDB with specifications; don't need sequence."""
        #type checking
        checkType(NStype, "NStype")
        if(type(NSname) != str):
            raise TypeError("name not a string")

        #query database
        namedSeqList = self.getAllNSQuery().filter_by(elemType = NStype, name = NSname).all()
                
        #handle the results from the query
        if(len(namedSeqList) == 0):
            raise SequenceNotFoundError("Could not find sequence.")
        if(len(namedSeqList) > 1):
            raise Exception("Multiple sequences found.")
        else:
            return namedSeqList[0]

    def findNamedSequence(self, NStype, NSname, NSseq):
        """Searches UserDataDB for named sequence with specifications; checks sequence."""
        foundNS = self.findNamedSequenceNoSeq(NStype, NSname)

        #type check & pre-process sequence
        if(type(NSseq) != str):
            raise TypeError("NSseq not a string")

        seq = NSseq.upper()
        
        #check sequence
        if(foundNS.getSeq() == seq):
            return foundNS
        else:
            raise SequenceMismatchError("Sequence does not match stored sequence.")

    def findComponent(self, compType, compName, compPos, compTerminalLetter):
        """Searches UserDataDB for component with specifications."""
        #type checking
        checkType(compType, "compType")
        if(type(compName) != str):
            raise TypeError("compName not a string")
        if(type(compPos) != int):
            raise TypeError("comPos not an int")
        if(type(compTerminalLetter) != str):
            raise TypeError("compTerminalLetter not a string")

        foundNS = self.findNamedSequenceNoSeq(compType, compName)

        #search for the Component
        for comp in foundNS.getAllComponents():
            if((comp.getPosition() == compPos) and (comp.getTerminalLetter() == compTerminalLetter)):
                   return comp
        
        #did not find it
        raise ComponentNotFoundError("Could not find component.")

    def findBackbone(self, name):
        """Searches BackboneDB for backbone with the same name."""
        backboneList = self.getAllBBQuery().filter_by(name = name).all()

        #handle the results from the query
        if(len(backboneList) == 0):
            raise BackboneNotFoundError("Could not find backbone.")
        if(len(backboneList) > 1):
            raise Exception("Multiple backbones found.")
        else:
            return backboneList[0]
    
    #remove
    def removeComponent(self, compType, compName, compPos, compTerminalLetter):
        """Removes component from UserDataDB by finding it and calling on removeFoundComp."""
        #find component
        foundComp = self.findComponent(compType, compName, compPos, compTerminalLetter)

        self.removeFoundComponent(foundComp)

    def removeComponentByID(self, id):
        foundComp = ComponentDB.query.get(id) #i'm not sure I like how this accesses it

        self.removeFoundComp(foundComp)
        
    def removeFoundComponent(self, foundComp):
        """Removes component and its associated primerData and spacerData from the database."""
        foundSpacerData = foundComp.getSpacerData()
        foundPrimerData = foundComp.getPrimerData()

        #remove them from database
        db.session.delete(foundComp)
        db.session.delete(foundSpacerData)
        db.session.delete(foundPrimerData)
        db.session.commit()
        
    def removeSequenceByID(self, id):
        """Removes namedSequence from database based on its ID."""
        foundNS = NamedSequenceDB.query.get(id)

        for foundComp in foundNS.getAllComponents():
            self.removeFoundComponent(foundComp)

        db.session.delete(foundNS)
        db.session.commit()

    def removeFoundSequence(self, foundNS):
        #remove all components using the NamedSequence
        for foundComp in foundNS.getAllComponents():
            self.removeFoundComponent(foundComp)
        
        #remove the NamedSequence
        db.session.delete(foundNS)
        
        db.session.commit()

    def removeSequence(self, seqType, seqName):
        """Removes namedSequence from UserDataDB by finding it, removing all its components, and removing it."""
        foundNS = self.findNamedSequenceNoSeq(seqType, seqName)
        
        self.removeFoundSequence(foundNS)

    def removeBackbone(self, id): #check permissions
        foundBB = BackboneDB.query.get(id)

        if(foundBB is None):
            raise BackboneNotFoundError("Backbone with that id was not found.")
        
        db.session.delete(foundBB)

        db.session.commit()
    
    #add, create, make
    def addNSDB(self, namedSeq):
        """Pass in a NamedSequenceDB, will create a copy in current user."""
        
        if(type(namedSeq) != NamedSequenceDB):
            raise TypeError("namedSeq not a NamedSequenceDB.")
        
        #check if it already exists
        try:
            self.findNamedSequence(namedSeq.getType(), namedSeq.getName(), namedSeq.getSeq())
            
            #raise error if it exists
            raise AlreadyExistsError("Sequence already exists.")
            
        except SequenceNotFoundError:
            pass

        #make entry
        NStype = namedSeq.getType()
        NSname = namedSeq.getName()
        NSseq = namedSeq.getSeq()
        
        nameID = namedSeq.getNameID() #####<----- What if, somehow, that NameID already exists in the personal library?
        
        ns = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq, nameID = nameID, user_id = self.getID())
        
        #add to database
        db.session.add(ns)
        
        self.getEntry().incrementID(NStype)
        
        db.session.commit()
        
        return ns
        
    def addNS(self, namedSeq):
        """Pass in a NamedSequence, will create a NamedSequenceDB and add it to the database."""
        #type checking
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
        
        ns = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq, nameID = nameID, user_id = self.getID())
        
        #add to database
        db.session.add(ns)
        
        self.getEntry().incrementID(NStype)
        
        db.session.commit()
        
        return ns
            
    def createNS(self, NStype, NSname, NSseq):
        """Pass in raw data, creates a NamedSequence and then makes NamedSequenceDB via self.addNS(newNS)"""
        #type checking
        checkType(NStype, "NStype")

        #get the nameID
        nameID = self.getEntry().getNextNSid()[NStype]

        #create it
        newNS = NamedSequence.makeNew(NStype, NSname, NSseq, nameID)
        
        #add it to self
        NSentry = self.addNS(newNS)
                
        return NSentry
    
    def createComp(self, NSentry, spacerData, primerData):
        """Make a ComponentDB and associated SpacerDataDB, PrimerDataDB in database."""        
        #type checking
        if(type(NSentry) != NamedSequenceDB):
            raise TypeError("NSentry not a NamedSequenceDB")
        if(type(spacerData) != SpacerData):
            raise TypeError("spacerData not a SpacerData")
        if(type(primerData) != PrimerData):
            raise TypeError("primerData not a PrimerData")
                    
        #check if it already exists
        try:
            self.findComponent(NSentry.getType(), NSentry.getName(), spacerData.getPosition(), spacerData.getTerminalLetter())

            raise AlreadyExistsError("Component already exists.")
        except ComponentNotFoundError:
            pass
        
        #create database entries
        s = SpacerDataDB(position = spacerData.getPosition(), spacerLeft = spacerData.getSpacerLeft(), spacerRight = spacerData.getSpacerRight(),
                 isTerminal = spacerData.getIsTerminal(), terminalLetter = spacerData.getTerminalLetter(),
                 leftNN = spacerData.getLeftNN(), rightNN = spacerData.getRightNN())

        p = PrimerDataDB(primersFound = primerData.getPrimersFound(), seqLeft = primerData.getSeqLeft(), seqRight = primerData.getSeqRight(),
                 GCleft = primerData.getGCleft(), GCright = primerData.getGCright(), TMleft = primerData.getTMleft(), TMright = primerData.getTMright())

        c = ComponentDB(namedSequence_id = NSentry.getID(), user_id = self.getID())
        
        #add to the database
        db.session.add(c)
        db.session.add(s)
        db.session.add(p)
        
        db.session.commit()
        
        #edit database entries so they have proper relations
        c.setSpacerDataID(s.getID())
        c.setPrimerDataID(p.getID())
        s.setCompID(c.getID())
        p.setCompID(c.getID())

        db.session.commit() #is it necessary? perhaps

        return c
        
    def makeWithNamedSequence(self, ns, position, isTerminal, TMgoal, TMrange):
        """Make a ComponentDB with a NamedSequenceDB, but no PrimerData or SpacerData, which are made here."""
        #type checking
        if(type(ns) != NamedSequenceDB):
            raise TypeError("ns not a NamedSequenceDB")        
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
        """Make a ComponentDB with no pre-existing NamedSequenceDB, PrimerData, or SpacerData. (Used for default user.)"""
        ns = self.createNS(elemType, name, seq)
        
        return self.makeWithNamedSequence(ns, position, isTerminal, TMgoal, TMrange)

    def createBackbone(self, name, seq):
        """Create a BackboneDB using its name and sequence."""
        #see if it exists already
        try:
            self.findBackbone(name)
            raise AlreadyExistsError("Backbone {name} already exists.".format(name = name))
        except BackboneNotFoundError:
            pass

        #create
        bb = BackboneDB(name = name, seq = seq, user_id = self.getID())

        db.session.add(bb)

        db.session.commit()

        return bb


