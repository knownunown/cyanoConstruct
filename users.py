#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserData class, used to manage users and their actions.

@author: Lia Thomson
"""
from misc import printIf, checkType
from database import db, UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, BackboneDB
from component import NamedSequence, SpacerData, PrimerData
import enumsExceptions as e

class UserData:
	def __init__(self):
		"""Create an empty UserData. Should not be accessed except through new or load"""
		self.__DBid = -1
		self.__entryDB = None
	
	@classmethod
	def new(cls, email):
		"""Create a new user: creates a UserData and a UserDataDB.
		
		PARAMTERS:
			email: string email of the user
		
		RETURN:
			newUserData: created UserData
		"""
		printIf("Calling UserData.new({email}).\n".format(email = email))

		#type validation
		if(type(email) != str):
			raise TypeError("email not a str")
							
		#see if a user with the email already exists
		if(UserDataDB.query.filter_by(email = email).all() != []):
			raise e.AlreadyExistsError("User with email {email} already exists.".format(
																email = email))

		#initialize
		newUserData = cls()
		
		#start nextNSid (the first number for the IDs of named sequences of the user)
		if(email == "default"):
			nextNSid = 1
		else:
			nextNSid = 101
		
		#add user to database
		u = UserDataDB(nextNSidPR = nextNSid, nextNSidRBS = nextNSid,
						nextNSidGOI = nextNSid, nextNSidTERM = nextNSid,
						email = email)

		db.session.add(u)
		db.session.commit()
		
		#add database info. to the user
		newUserData.__DBid = u.id
		newUserData.__entryDB = u
		
		return newUserData

	@classmethod
	def load(cls, email):
		"""Load a user from the UserDataDB table.
		
		PARAMETERS:
			email: string email for the user to load
		
		RETURNS:
			newUserData: created UserData loaded from the database
		"""
		#search for users in the database with the email
		queryResults = UserDataDB.query.filter_by(email = email).all()
		
		#check results
		if(len(queryResults) == 0):
			raise e.UserNotFoundError("Could not find user.")
		elif(len(queryResults) > 1):
			raise Exception("Multiple users exists with this email.")
		else:
			#create the UserData from the database entry
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

	def getNextNSid(self):
		return self.getEntry().getNextNSid()

	def getGoogleAssoc(self):
		return self.getEntry().getGoogleAssoc()

	def getGoogleID(self):
		return self.getEntry().getGoogleID()

	#get all query (is a query, so the results can be ordered, filtered, etc.)
	def getAllNSQuery(self):
		return self.getEntry().getAllNamedSeqs()
	
	def getAllCompsQuery(self):
		return self.getEntry().getAllComponents()
	
	def getAllBBQuery(self):
		return self.getEntry().getAllBackbones()	

	#get all array (is an array, so the results can't be easily filtered etc.)
	def getAllNS(self):
		return self.getAllNSQuery().all()
			
	def getAllComps(self):
		return self.getAllCompsQuery().all()
	
	def getAllBB(self):
		return self.getEntry().getAllBackbones().all()

	#get sorted
	def getSortedNS(self):
		"""Return dict of sorted NamedSequenceDBs of the user.
		
		RETURNS:
			sortedNS: dict, with the keys as types (e.g. RBS), and the values
				a sorted array of all NamedSequenceDB of the type.
		"""
		#the use of order_by is likely unnecessary, but not deeply detrimental
		allPr = self.getAllNSQuery().filter_by(elemType = "Pr").order_by(NamedSequenceDB.nameID.asc()).all()
		allRBS = self.getAllNSQuery().filter_by(elemType = "RBS").order_by(NamedSequenceDB.nameID.asc()).all()
		allGOI = self.getAllNSQuery().filter_by(elemType = "GOI").order_by(NamedSequenceDB.nameID.asc()).all()
		allTerm = self.getAllNSQuery().filter_by(elemType = "Term").order_by(NamedSequenceDB.nameID.asc()).all()

		sortedNS = {"Pr": allPr, "RBS": allRBS, "GOI": allGOI, "Term": allTerm}

		return sortedNS
	
	def getSortedComps(self):
		"""Return dict of sorted ComponentDBs of the user.
		Calls getSortedNSandComps and only returns the sorted components.
		
		RETURNS:
			retDict: a dictionary with keys being types (e.g. RBS), values being
				another dictionary. That dictionary has keys being named sequence
				names, the values being an array of components
		"""
		#call getSortedNSandComps
		allNS, retDict = self.getSortedNSandComps()

		#only return retDict
		return retDict
	
	def getSortedNSandComps(self):
		"""Return sorted NamedSequenceDBs and ComponentDBs of the user.
		
		RETURNS:
			allNS: dict, with keys as types and values as the sorted array of all
				NamedSequenceDB of the type.
			retDict: a dictionary with keys being types (e.g. RBS), values being
				another dictionary. That dictionary has keys being named sequence
				names, the values being an array of components

		"""
		#get sorted NamedSequenceDBs
		allNS = self.getSortedNS()
		
		#start return dictionary
		retDict = {}
		
		#get all components
		allComps = self.getAllCompsQuery()
		
		#for type in allNS
		for nsGroupKey in allNS:
			#start the type dict
			typeRow = {}
			#for each NamedSequenceDB for the type
			for ns in allNS[nsGroupKey]:
				#this may not be efficient
				
				#first obtain the components of that sequence
				sortedComps = allComps.filter_by(namedSequence_id = ns.getID()).all()
				#then sort the components
				sortedComps.sort()
				#then add it to the type dict
				typeRow[ns.getName()] = sortedComps
			
			#set the value for the retDict for each type
			retDict[nsGroupKey] = typeRow

		return (allNS, retDict)
	
	def getSortedBB(self):
		"""Return sorted array of all BackboneDBs of the user."""
		allBB = self.getAllBB()
		allBB.sort()

		return allBB

	#find functions
	def findNamedSequenceNoSeq(self, NStype, NSname):
		"""Searches UserDataDB for a NamedSequenceDB; don't need sequence.
		
		PARAMETERS:
			NStype: string type of the named sequence
			NSname: string name of the named sequence
		
		RETURNS:
			found NamedSequenceDB
		
		RAISES:
			SequenceNotFoundError: if the named sequence was not found
			Exception: if multiple named sequences that fits the requirements were found
		"""
		#type checking
		checkType(NStype, "NStype")
		if(type(NSname) != str):
			raise TypeError("name not a string")

		#query database
		namedSeqList = self.getAllNSQuery().filter_by(elemType = NStype, name = NSname).all()
				
		#handle the results from the query
		if(len(namedSeqList) == 0):
			raise e.SequenceNotFoundError("Could not find sequence.")
		if(len(namedSeqList) > 1):
			raise Exception("Multiple sequences found.")
		else:
			return namedSeqList[0]

	def findNamedSequence(self, NStype, NSname, NSseq):
		"""Searches UserDataDB for a NamedSequenceDB; checks sequence.
		Does so by calling findNamedSequenceNoSeq and then checking the sequence.
		
		PARAMETERS:
			NStype: string type of the named sequence to find
			NSname: string name of the named sequence to find
			NSseq: string sequence of the named sequence to find
		
		RETURNS:
			found NamedSequenceDB
		"""
		#find a NamedSequenceDB that fits the type and the name specifications
		foundNS = self.findNamedSequenceNoSeq(NStype, NSname)

		#type check & pre-process sequence
		if(type(NSseq) != str):
			raise TypeError("NSseq not a string")

		seq = NSseq.upper()
		
		#check sequence
		if(foundNS.getSeq() == seq):
			return foundNS
		else:
			raise e.SequenceMismatchError("Sequence does not match stored sequence.")

	def findComponent(self, compType, compName, compPos, compTerminalLetter):
		"""Searches UserDataDB for ComponentDB with specifications.
		
		PARAMETERS:
			compType: string type of the component's sequence to find
			compName: string name of the component's sequence to find
			compPos: integer position of the component
			compTerminalLetter: string component's terminal letter
		
		RETURNS:
			comp: found component that fits the paramters
		
		RAISES:
			ComponentNotFoundError: if no component was found that fits the parameters.
		"""
		#type checking
		checkType(compType, "compType")
		if(type(compName) != str):
			raise TypeError("compName not a string")
		if(type(compPos) != int):
			raise TypeError("comPos not an int")
		if(type(compTerminalLetter) != str):
			raise TypeError("compTerminalLetter not a string")

		#first search for a NamedSequenceDB that fits the type and name
		foundNS = self.findNamedSequenceNoSeq(compType, compName)

		#search through the components of foundNS
		for comp in foundNS.getAllComponents():
			#for each component, check the position and terminal letter
			if((comp.getPosition() == compPos) and (comp.getTerminalLetter() == compTerminalLetter)):
				#return if found.
				return comp
		
		#did not find it
		raise e.ComponentNotFoundError("Could not find component.")

	def findBackbone(self, name):
		"""Searches for a BackboneDB by the name.
		
		PARAMETERS:
			name: string name of the backbone to find
			
		RETURNS:
			found BackboneDB
		
		RAISES:
			BackboneNotFoundError: if no backbone with the name was found
			Exception: if multiple backbones with the name were found
		"""
		backboneList = self.getAllBBQuery().filter_by(name = name).all()

		#handle the results from the query
		if(len(backboneList) == 0):
			raise e.BackboneNotFoundError("Could not find backbone.")
		if(len(backboneList) > 1):
			raise Exception("Multiple backbones found.")
		else:
			return backboneList[0]
	
	#remove functions
	def removeComponent(self, compType, compName, compPos, compTerminalLetter):
		"""Removes component from UserDataDB by finding it and calling on removeFoundComp."""
		#find component
		foundComp = self.findComponent(compType, compName, compPos, compTerminalLetter)
		#remove the component
		self.removeFoundComponent(foundComp)

	def removeComponentByID(self, id):
		"""Removes component from UserDataDB using its database ID and calling removeFoundComp.
		
		PARAMETER:
			id: integer ID of the ComponentDB in the database
		
		RAISES:
			ComponentNotFoundError: if a component with that ID was not found.

		"""
		#(Is this ever used?)
		#find component
		foundComp = ComponentDB.query.get(id) #i'm not sure I like how this accesses it
		
		if(foundComp is None):
			raise e.ComponentNotFoundError("Component with that id was not found.")
		
		#remove the component
		self.removeFoundComp(foundComp)
		
	def removeFoundComponent(self, foundComp):
		"""Removes ComponentDB from the database.
		
		PARAMETER:
			foundCom: ComponentDB to remove from the database
		"""
		
		#type checking
		if(type(foundComp) != ComponentDB):
			raise TypeError("foundComp not a ComponentDB")
		
		#get the SpacerDataDB and PrimerDataDB associated with the component
		foundSpacerData = foundComp.getSpacerData()
		foundPrimerData = foundComp.getPrimerData()

		#remove them from database
		db.session.delete(foundComp)
		db.session.delete(foundSpacerData)
		db.session.delete(foundPrimerData)
		db.session.commit()
		
	def removeSequenceByID(self, id):
		"""Removes NamedSequenceDB from database based on its database ID.
		
		PARAMETER:
			id: integer ID of the NamedSequenceDB in the database
		
		RAISES:
			SequenceNotFoundError: if a named sequence with that ID was not found.
		"""
		#get the NamedSequenceDB
		foundNS = NamedSequenceDB.query.get(id)
		
		#if there was no NamedSequenceDB found
		if(foundNS is None):
			raise e.SequenceNotFoundError("Named sequence with that id was not found.")

		self.removeFoundSequence(foundNS)

	def removeFoundSequence(self, foundNS):
		"""Removes found NamedSequenceDB from the database."""
		#go through all of the components that use the sequence and remove them
		for foundComp in foundNS.getAllComponents():
			self.removeFoundComponent(foundComp)
		
		#delete the NamedSequenceDB
		db.session.delete(foundNS)
		db.session.commit()

	def removeSequence(self, seqType, seqName):
		"""Finds and removes NamedSequenceDB from the database.
		
		PARAMETERS:
			seqType: string type of the NamedSequenceDB
			seqName: string name of the NamedSequenceDB
		"""
		#search for the NamedSequenceDB
		foundNS = self.findNamedSequenceNoSeq(seqType, seqName)
		
		#remove it
		self.removeFoundSequence(foundNS)

	def removeBackbone(self, id): #?! check permissions
		"""Removes BackboneDB from database based on its database ID.
		
		PARAMETER:
			id: integer ID of the BackboneDB in the database
		
		RAISES:
			BackboneNotFoundError: if a backbone with that ID was not found.
		"""
		#get the BackboneDB
		foundBB = BackboneDB.query.get(id)

		#if there was no backbone found
		if(foundBB is None):
			raise e.BackboneNotFoundError("Backbone with that id was not found.")

		#remove the backbone		
		db.session.delete(foundBB)
		db.session.commit()
	
	#add, create, make
	def addNSDB(self, namedSeq):
		"""Create a copy of a NamedSequenceDB in the user's library.
		
		PARAMETER:
			namedSeq: NamedSequenceDB to copy
			
		RAISES:
			AlreadyExistsError: if a named sequence of the same name is already
				in the user's library
		"""
		#type checking		
		if(type(namedSeq) != NamedSequenceDB):
			raise TypeError("namedSeq not a NamedSequenceDB.")
		
		#check if it already exists
		try:
			self.findNamedSequence(namedSeq.getType(), namedSeq.getName(), namedSeq.getSeq())
			
			#raise error if it exists
			raise e.AlreadyExistsError("Sequence already exists.")
		except e.SequenceNotFoundError:
			pass

		#get info. about namedSeq
		NStype = namedSeq.getType()
		NSname = namedSeq.getName()
		NSseq = namedSeq.getSeq()
		
		nameID = namedSeq.getNameID() #####<----- What if, somehow, that NameID already exists in the personal library?
		
		#create a new NamedSequenceDB using the information from namedSeq
		#the only difference is the user_id
		ns = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq,
							 nameID = nameID, user_id = self.getID())
		
		#add to database
		db.session.add(ns)
		db.session.commit()
		
		#increment NS id
		self.getEntry().incrementID(NStype)
		
		return ns
		
	def addNS(self, namedSeq):
		"""Add a NamedSequenceDB to the database using a NamedSequence.
		
		PARAMETERS:
			namedSeq: NamedSequence to make a NamedSequenceDB from
		
		RAISES:
			AlreadyExistsError: if a NamedSequenceDB with the same name and type
				already exists in the database for the user
		"""
		#type checking
		if(type(namedSeq) != NamedSequence):
			raise TypeError("namedSeq not a NamedSequence.")
		
		#check if it already exists
		try:
			self.findNamedSequenceNoSeq(namedSeq.getType(), namedSeq.getName())
			
			#an error will be raised if it exists
			raise e.AlreadyExistsError("Sequence already exists.")
			
		except e.SequenceNotFoundError:
			pass

		#make entry
		NStype = namedSeq.getType()
		NSname = namedSeq.getName()
		NSseq = namedSeq.getSeq()
		
		nameID = self.getEntry().getNextNSid()[NStype]
		
		ns = NamedSequenceDB(elemType = NStype, name = NSname, seq = NSseq,
							 nameID = nameID, user_id = self.getID())
		
		#add to database
		db.session.add(ns)		
		db.session.commit()

		#increment NS id
		self.getEntry().incrementID(NStype)
		
		return ns
			
	def createNS(self, NStype, NSname, NSseq):
		"""Create a NamedSequence using raw data and then adding it to the database
		as a NamedSequenceDB.

		PARAMETERS:
			NStype: string type of the named sequence
			NSname: string name of the named sequence
			NSseq: string sequence of the named sequence
		
		RETURNS:
			NSentry: created NamedSequenceDB that is in the database
		"""
		#type checking
		checkType(NStype, "NStype")

		#get the nameID
		nameID = self.getEntry().getNextNSid()[NStype]

		#create it as a NamedSequence
		newNS = NamedSequence.makeNew(NStype, NSname, NSseq, nameID)
		
		#add it as a NamedSequenceDB to the database and the user
		NSentry = self.addNS(newNS)
				
		return NSentry
	
	def createComp(self, NSentry, spacerData, primerData):
		"""Make a ComponentDB and add to the database using a NamedSequenceDB in the
		database, a SpacerData, and a PrimerData.
		
		PARAMETERS:
			NSentry: NamedSequenceDB in the database that the component will use
			spacerData: SpacerData for the component
			primerData: PrimerData for the component
		
		RETURNS:
			c: created ComponentDB that is now in the database.
		"""
		#type checking
		if(type(NSentry) != NamedSequenceDB):
			raise TypeError("NSentry not a NamedSequenceDB")
		if(type(spacerData) != SpacerData):
			raise TypeError("spacerData not a SpacerData")
		if(type(primerData) != PrimerData):
			raise TypeError("primerData not a PrimerData")
		
		#check if the component already exists
		try:
			self.findComponent(NSentry.getType(), NSentry.getName(),
								spacerData.getPosition(), spacerData.getTerminalLetter())

			raise e.AlreadyExistsError("Component already exists.")
		except e.ComponentNotFoundError:
			pass
		
		#create database entries
		s = SpacerDataDB(position = spacerData.getPosition(),
						 spacerLeft = spacerData.getSpacerLeft(),
						 spacerRight = spacerData.getSpacerRight(),
						 isTerminal = spacerData.getIsTerminal(),
						 terminalLetter = spacerData.getTerminalLetter(),
						 leftNN = spacerData.getLeftNN(),
						 rightNN = spacerData.getRightNN())

		p = PrimerDataDB(primersFound = primerData.getPrimersFound(),
						 seqLeft = primerData.getLeftSeq(),
						 seqRight = primerData.getRightSeq(),
						 GCleft = primerData.getGCleft(),
						 GCright = primerData.getGCright(),
						 TMleft = primerData.getTMleft(),
						 TMright = primerData.getTMright())

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

		db.session.commit()

		return c
		
	def makeWithNamedSequence(self, ns, position, isTerminal, TMgoal, TMrange):
		"""Make a ComponentDB with a NamedSequenceDB, but no PrimerData or SpacerData.
						
		PARAMETERS:
			ns: NamedSequenceDB in the database that the component will use
			position: integer position of the component
			isTerminal: boolean if component is terminal
			TMgoal: desired TM for the primers
			TMrange: allowance for the TM. (The found TM will be within TMgoal ± TMrange)

		RETURNS:
			created ComponentDB
		"""
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
		
		#make a SpacerData
		newSpacerData = SpacerData.makeNew(position, isTerminal)

		#make a PrimerData
		newPrimerData = PrimerData.makeNew(ns.getSeq(), TMgoal, TMrange)
		newPrimerData.addSpacerSeqs(newSpacerData)

		return self.createComp(ns, newSpacerData, newPrimerData)
	
	#creates a new component and adds it
	def makeFromNew(self, elemType, name, seq, position, isTerminal, TMgoal, TMrange):
		"""Make a ComponentDB with no pre-existing NamedSequenceDB, PrimerData, or SpacerData.
		Used for default user.
		
		PARAMETERS:
			elemType: string type of the sequence
			seq: string sequence of the sequence
			position: integer position of the component
			isTerminal: boolean if component is terminal
			TMgoal: desired TM for the primers
			TMrange: allowance for the TM. (The found TM will be within TMgoal ± TMrange)

		RETURNS:
			created ComponentDB
		"""
		#make NamedSequenceDB
		ns = self.createNS(elemType, name, seq)
		
		return self.makeWithNamedSequence(ns, position, isTerminal, TMgoal, TMrange)

	def createBackbone(self, name, BBtype, desc, seqBefore, seqAfter, features):
		"""Create a BackboneDB and add it to the database.
		
		PARAMETERS:
			name: string name of the backbone
			BBtype: string type of the backbone; is either "i" for integrative or
				"r" for replicative
			desc: string description of the backbone
			seqBefore: string sequence of the backbone before the insertion region
			seqAfter: string sequence of the backbone after the insertion region
			features: string features, formatted as it should appear in a .gb file
		
		RETURNS:
			bb: created BackboneDB
		
		RAISES:
			AlreadyExistsError: if a backbone with the same name is already in
				the user's library
		"""
		#type checking
		if(type(name) != str):
			raise TypeError("backbone name not a string")
		if(type(BBtype) != str):
			raise TypeError("backbone type not a string")
		elif(BBtype not in ["i", "r"]):
			raise ValueError("backbone type not valid")
		if(type(desc) != str):
			raise TypeError("backbone desc not a string")
		if(type(seqBefore) != str):
			raise TypeError("backbone seqBefore not a string")
		if(type(seqAfter) != str):
			raise TypeError("backbone seqAfter not a string")
		if(type(features) != str):
			raise TypeError("backbone features not a string")
		
		print("done with the type checking")

		#see if it exists already
		try:
			self.findBackbone(name)
			raise e.AlreadyExistsError("Backbone {name} already exists.".format(name = name))
		except e.BackboneNotFoundError:
			pass

		#create in database
		bb = BackboneDB(name = name, type = BBtype, desc = desc, seqBefore = seqBefore,
						seqAfter = seqAfter, features = features, user_id = self.getID())

		db.session.add(bb)
		db.session.commit()

		return bb


try:
    defaultUser = UserData.load("default")
except e.UserNotFoundError:
    defaultUser = UserData.new("default")
