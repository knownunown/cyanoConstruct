#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database file.
Contains the tables: UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB.

@author: Lia Thomson
"""

from jinja2 import Markup #for HTML display of Component
from datetime import datetime, timedelta #for time in GenBank file
from time import time

from cyanoConstruct import db

EXPIRATIONSECS = 3600 #expires in an hour

class UserDataDB(db.Model):
	__tablename__ = "UserData"
	
	#columns
	#user identification
	id = db.Column(db.Integer, primary_key = True)
	
	email = db.Column(db.String(254), unique = True)

	#google-related info.
	googleAssoc = db.Column(db.Boolean, default = False, nullable = False)
	googleID = db.Column(db.Text)

	#temporary password & expiration (NOT IN USE CURRENTLY)
	tempPass = db.Column(db.String(32))
	tempExp = db.Column(db.Integer)

	#next NS ids
	nextNSidPR = db.Column(db.Integer)
	nextNSidRBS = db.Column(db.Integer)
	nextNSidGOI = db.Column(db.Integer)
	nextNSidTERM = db.Column(db.Integer)
	
	def __repr__(self):
		return '<User {}>'.format(self.id)
	
	def incrementID(self, NStype):
		"""Add one to the NSid for the appropriate NamedSequence type.
		
		PARAMETER:
			NStype: string type to increase
		
		RETURNS:
			the new integer NSid for the appropriate type
		"""
		if(type(NStype) != str):
			raise TypeError("NStype not a str")

		#increment		
		if(NStype == "Pr"):
			self.nextNSidPR += 1
			return self.nextNSidPR
		elif(NStype == "RBS"):
			self.nextNSidRBS += 1
			return self.nextNSidRBS
		elif(NStype == "GOI"):
			self.nextNSidGOI += 1
			return self.nextNSidGOI
		else:
			self.nextNSidTERM += 1
			return self.nextNSidTERM

	#getters
	def getID(self):
		return self.id
	
	def getEmail(self):
		return self.email

	def getGoogleAssoc(self):
		return self.googleAssoc

	def getGoogleID(self):
		return self.googleID

	def getNextNSid(self):
		return {"Pr": self.nextNSidPR,
				"RBS": self.nextNSidRBS,
				"GOI": self.nextNSidGOI,
				"Term": self.nextNSidTERM}

	def getAllNamedSeqs(self):
		return NamedSequenceDB.query.filter_by(user_id = self.id)
	
	def getAllComponents(self):
		return ComponentDB.query.filter_by(user_id = self.id)

	def getAllBackbones(self):
		return BackboneDB.query.filter_by(user_id = self.id)

	#setters
	def setEmail(self, newEmail):
		self.email = newEmail
		db.session.commit()

	def setGoogleAssoc(self, newValue):
		self.googleAssoc = newValue
		db.session.commit()

	def setGoogleID(self, newID):
		self.googleID = newID
		db.session.commit()

	def setTemp(self, temp):
		"""Set temporary password & expiration time"""
		self.timeExp = int(time() + EXPIRATIONSECS)
		self.tempPass = temp
		db.session.commit()

	#check temporary password (NOT IN USE)
	def compareTemp(self, temp):
		if(time() > self.timeExp):
			#somehow indicate it's too late
			return False
		else:
			return self.tempPass == temp

class NamedSequenceDB(db.Model):
	__tablename__ = "NamedSequence"
	
	#columns
	id = db.Column(db.Integer, primary_key = True)
	
	elemType = db.Column(db.String(4))
	name = db.Column(db.String(20))
	seq = db.Column(db.Text())
	nameID = db.Column(db.Integer)
	
	user_id = db.Column(db.Integer)
	
	def __repr__(self):
		return "<NamedSequence {id}: {type}-{nameID} {name}>".format(
					id = self.getID(),
					type = self.getType(),
					nameID = self.getNameID().zfill(3),
					name = self.getName())
			
	def __str__(self):
		return "<NamedSequence {type}-{nameID}: {name}, {comps} components.".format(
					type = self.getType(),
					nameID = self.getNameID().zfill(3),
					name = self.getName(),
					comps = len(self.getAllComponents()))

	#getters
	def getID(self):
		return self.id
	
	def getUserID(self):
		return self.user_id
		
	def getType(self):
		return self.elemType
		
	def getName(self):
		return self.name
	
	def getSeq(self):
		return self.seq
	
	def getNameID(self):
		return self.nameID
	
	def getAllComponents(self):
		return self.getAllComponentsQuery().all()
	
	def getAllComponentsQuery(self):
		return ComponentDB.query.filter_by(namedSequence_id = self.id)


	def getHTMLdisplay(self):
		"""Return an HTML string for the display of a NamedSequence and its
		Components on the /library page."""
		#get the longName for the type
		longNamesSingular = {"Pr": "Promoter",
							"RBS": "Ribosome Binding Site",
							"GOI": "Gene",
							"Term": "Terminator"}
		longName = longNamesSingular[self.getType()]

		#get the libraryName
		if UserDataDB.query.get(self.getUserID()).getEmail() == "default":
			libraryName = "Default"
			isDefault = True
		else:
			libraryName = "Personal"
			isDefault = False

		#start an array that will collect multiple strings to join and return
		retArray = []

		#add the information about the named sequence
		retArray.append("""<div class = "hideableTitle nameTitle" id = "{libraryName}{NSname}">
						<input class = "titleLeft subtleButton" type = "button" 
							onclick = "toggleDisplay('{libraryName}{NSname}Data'); 
							switchToggleText(this);" value = "Name: {NSname}">
						<span class = "titleRight monospaced">[Click to show]</span>
						</div>
		
						<div id = "{libraryName}{NSname}Data" class = "hideableDiv" style = "display: none">

						<!-- info about the named sequence -->
						<p>{longName}: {NSname}</p>

						<p>Sequence:</p>
						<div class = "sequence monospaced">{NSseq}</div>

						<br>""".format(libraryName = libraryName,
										NSname = Markup.escape(self.getName()),
										longName = longName,
										NSseq = self.getSeq(),
										))

		#get and sort all components derived from this named sequence
		allComps = self.getAllComponents()
		allComps.sort()

		#add the information about each component
		for comp in allComps:
			retArray.append("""<div class = "hideableTitle compTitle" id = "{libraryName}{compNameID}">
							<input class = "titleLeft subtleButton" type = "button" 
								onclick = "toggleDisplay('{libraryName}{compNameID}Data'); 
								switchToggleText(this);" value = "ID: {compNameID}">
							<span class = "titleRight monospaced">[Click to show]</span>
							</div>

							<div id = "{libraryName}{compNameID}Data" 
								class = "hideableDiv componentData" style = "display: none">

							<p>{compHTML}</p>

							<hr>

							<p><span class = 'emphasized'>Complete Sequence:</span></p>
							<div class = "sequence monospaced">
								{seqHTML}
							</div>

							<br>

							<input type = "button" class = "styledButton" 
								value = "Download Sequences" 
								onclick = "downloadComponentSequence({compID})">""".format(
													libraryName = libraryName,
													compNameID = comp.getNameID(),
													compHTML = comp.getHTMLstr(),
													seqHTML = comp.getSeqHTML(),
													compID = comp.getID()
													))

			#add a "Remove Component" button if it is not the default library
			if(not isDefault):
				retArray.append("""<br><hr><input type = "button" 
									class = "styledButton" value = "Remove Component" 
									onclick = "removeComponent({compID})">""".format(
														compID = comp.getID()))

			retArray.append("""</div><div class = "hideableBottom"></div>""")

		#add a "Remove Sequence" button if it is not the default library
		if(not isDefault):
			retArray.append("""<br><hr><input type = "button" 
								class = "styledButton" value = "Remove Sequence" 
								onclick = "removeSequence('{NSID}')">""".format(
				NSID = self.getID()))

		#finish the HTML string
		retArray.append("""</div><div class = "hideableBottom"></div>""")

		#make a single string from retArray
		retStr = "".join(retArray)

		return Markup(retStr)

	#comparisons
	
	#self == other
	def __eq__(self, other):
		return ((self.getType() == other.getType()) and (self.getNameID() == other.getNameID()))
	
	#self != other
	def __ne__(self, other):
		return ((self.getType() != other.getType()) or (self.getNameID() != other.getNameID()))

	#self < other
	def __lt__(self, other):
		typeOrder = ["Pr", "RBS" "GOI", "Term"]
		selfIndex = typeOrder.index(self.getType())
		otherIndex = typeOrder.index(other.getType())
		
		if(selfIndex == otherIndex):
			return self.getNameID() < other.getNameID()
		else:
			return selfIndex < otherIndex
	
	#self <= other
	def __le__(self, other):
		typeOrder = ["Pr", "RBS" "GOI", "Term"]
		selfIndex = typeOrder.index(self.getType())
		otherIndex = typeOrder.index(other.getType())
		
		if(selfIndex == otherIndex):
			return self.getNameID() <= other.getNameID()
		else:
			return selfIndex <= otherIndex
	
	#self > other
	def __gt__(self, other):
		typeOrder = ["Pr", "RBS" "GOI", "Term"]
		selfIndex = typeOrder.index(self.getType())
		otherIndex = typeOrder.index(other.getType())
		
		if(selfIndex == otherIndex):
			return self.getNameID() > other.getNameID()
		else:
			return selfIndex > otherIndex
	
	#self >= other
	def __ge__(self, other):
		typeOrder = ["Pr", "RBS" "GOI", "Term"]
		selfIndex = typeOrder.index(self.getType())
		otherIndex = typeOrder.index(other.getType())
		
		if(selfIndex == otherIndex):
			return self.getNameID() >= other.getNameID()
		else:
			return selfIndex >= otherIndex

class SpacerDataDB(db.Model):
	__tablename__ = "SpacerData"

	start = "GAAGAC" #enzyme recog. site
	end = "GTCTTC"

	#columns
	id = db.Column(db.Integer, primary_key=True)
	
	position = db.Column(db.SmallInteger)
	spacerLeft = db.Column(db.String(4))
	spacerRight = db.Column(db.String(4))
	isTerminal = db.Column(db.Boolean)
	terminalLetter = db.Column(db.String(1))
	leftNN = db.Column(db.String(2))
	rightNN = db.Column(db.String(2))

	comp_id = db.Column(db.Integer)

	def __repr__(self):
		return "<SpacerData {}>".format(self.id)
	
	def __str__(self):
		return "SpacerData: " + str(self.getPosition()) + " " + self.getTerminalLetter()

	#setters

	def setCompID(self, compID):
		self.comp_id = compID

	#getters
	def getID(self):
		return self.id
	
	def getCompID(self):
		return self.comp_id
	
	def getPosition(self):
		return self.position

	def getSpacerLeft(self):
		return self.spacerLeft
	
	def getSpacerRight(self):
		return self.spacerRight
	
	def getIsTerminal(self):
		return self.isTerminal
	
	def getTerminalLetter(self):
		return self.terminalLetter

	def getLeftNN(self):
		return self.leftNN
	
	def getRightNN(self):
		return self.rightNN

	def getFullSeqLeft(self):
		return SpacerDataDB.start + self.getLeftNN() + self.getSpacerLeft()

	def getFullSeqRight(self):
		return self.getSpacerRight() + self.getRightNN() + SpacerDataDB.end


	#comparisons
	#sorts first by position, then by terminal letter
	def __eq__(self, other):
		return ((self.getPosition() == other.getPosition()) and (self.getTerminalLetter() == other.getTerminalLetter()))
	
	def __ne__(self, other):
		return ((self.getPosition() != other.getPosition()) or (self.getTerminalLetter() != other.getTerminalLetter()))

	def __lt__(self, other):
		if(self.getPosition() == other.getPosition()):
			letterOrder = ["S", "M", "T", "L"]
			return letterOrder.index(self.getTerminalLetter()) < letterOrder.index(other.getTerminalLetter())
		else:
			return self.getPosition() < other.getPosition()
	
	def __le__(self, other):
		if(self.getPosition() == other.getPosition()):
			letterOrder = ["S", "M", "T", "L"]
			return letterOrder.index(self.getTerminalLetter()) <= letterOrder.index(other.getTerminalLetter())
		else:
			return self.getPosition() <= other.getPosition()
	
	def __gt__(self, other):
		if(self.getPosition() == other.getPosition()):
			letterOrder = ["S", "M", "T", "L"]
			return letterOrder.index(self.getTerminalLetter()) > letterOrder.index(other.getTerminalLetter())
		else:
			return self.getPosition() > other.getPosition()
	
	def __ge__(self, other):
		if(self.getPosition() == other.getPosition()):
			letterOrder = ["S", "M", "T", "L"]
			return letterOrder.index(self.getTerminalLetter()) >= letterOrder.index(other.getTerminalLetter())
		else:
			return self.getPosition() >= other.getPosition()
	

class PrimerDataDB(db.Model):
	__tablename__ = "PrimerData"
	
	#columns
	id = db.Column(db.Integer, primary_key=True)
	
	primersFound = db.Column(db.Boolean)
	seqLeft = db.Column(db.Text) #gross
	seqRight = db.Column(db.Text)
	GCleft = db.Column(db.Float)
	GCright = db.Column(db.Float)
	TMleft = db.Column(db.Float)
	TMright = db.Column(db.Float)
	
	comp_id = db.Column(db.Integer)

	def __repr__(self):
		return "<PrimerData {}>".format(self.id)
	
	def __str__(self):
		if(self.getPrimersFound()):
			tempGCleft = str(round(self.getGCleft() * 100, 4))
			tempGCright = str(round(self.getGCright() * 100, 4))
			tempTMleft = str(round(self.getTMleft(), 3))
			tempTMright = str(round(self.getTMright(), 3))
			
			retStr = ("Left Primer:\nSequence: {leftSeq}\nGCcontent: {leftGC}%\nTM: {leftTM}°C\n\n"
					 "Right Primer:\nSequence: {rightSeq}\nGCcontent: {rightGC}%\nTM: {rightTM}°C").format(
							 leftSeq = self.getLeftSeq(),
							 leftGC = tempGCleft,
							 leftTM = tempTMleft,
							 rightSeq = self.getRightSeq(),
							 rightGC = tempGCright,
							 rightTM = tempTMright)
			
		else:
			retStr = "No primers found."
		
		return retStr

	
	#setters	
	def setCompID(self, compID):
		self.comp_id = compID
	
	#getters
	def getID(self):
		return self.id
	
	def getCompID(self):
		return self.comp_id
	
	def getPrimersFound(self):
		return self.primersFound
	
	def getLeftSeq(self):
		return self.seqLeft
	
	def getGCleft(self):
		return self.GCleft
	
	def getTMleft(self):
		return self.TMleft
	
	def getRightSeq(self):
		return self.seqRight
	
	def getGCright(self):
		return self.GCright
	
	def getTMright(self):
		return self.TMright


class ComponentDB(db.Model):
	__tablename__ = "Component"
	
	id = db.Column(db.Integer, primary_key=True)
		
	namedSequence_id = db.Column(db.Integer)
	spacerData_id = db.Column(db.Integer)
	primerData_id = db.Column(db.Integer)
	user_id = db.Column(db.Integer)

	def __repr__(self):
		return "<Component {id} {nameID} {name}>".format(
								id = self.getID(),
								nameID = self.getNameID(),
								name = self.getName())
	
	def __str__(self):
		return "Component {nameID}: {name}".format(
								nameID = self.getNameID(),
								name = self.getName())

	#setters
	def setNamedSequenceID(self, newID):
		self.namedSequence_id = newID

	def setSpacerDataID(self, newID):
		self.spacerData_id = newID

	def setPrimerDataID(self, newID):
		self.primerData_id = newID

	def setUserID(self, newID):
		self.user_id = newID

	#complicated getters
	def getSeqHTML(self):
		"""Return HTML string for the display of the Component.
		HTML unsafe."""
		retStr = ("<span class = 'enzymeSeq'>{enzymeLeft}</span>"
					"<span class = 'nnSeq'>{nnLeft}</span>"
					"<span class = 'spacerSeq'>{spacerLeft}</span>"
					"<span class = 'seq'>{seq}</span>"
					"<span class = 'spacerSeq'>{spacerRight}</span>"
					"<span class = 'nnSeq'>{nnRight}</span>"
					"<span class = 'enzymeSeq'>{enzymeRight}</span>").format(
											enzymeLeft = SpacerDataDB.start,
											nnLeft = self.getLeftNN(),
											spacerLeft = self.getLeftSpacer(),
											seq = self.getSeq(),
											spacerRight = self.getRightSpacer(),
											nnRight = self.getRightNN(),
											enzymeRight = SpacerDataDB.end)
		return retStr

	def getFullSeq(self):
		return self.getFullSpacerLeft() + self.getSeq() + self.getFullSpacerRight()
	
	def getLongName(self):
		retStr = "{type} {name} Position: {pos}".format(
							type = self.getType(),
							name = self.getName(),
							position = self.getPosition())

		if(self.getTerminal()):
			retStr += " last"
		else:
			retStr += " not last"
		
		return retStr

	def getHTMLdisplay(self):
		"""Return HTML string for the display of the component, but HTML safe"""
		return Markup(self.getHTMLstr())
	
	def getHTMLstr(self):
		"""Return an HTML string that displays the component's information."""
		retStr = """ID: {nameID}<br>
					Position: {pos}<br>
					Last?: {terminal}<br>
					<br><span class = "emphasized">Spacers:</span><br>
					Left: {leftSpacer}<br>
					Right: <rightSpacer><br>
					<br><span class = "emphasized">Primers:</span><br>"
					Left Primer:<br>
					GC content: {leftGC}%<br>
					TM: {leftTM}°C<br>
					Sequence:<br>
					<span class = "monospaced">{leftPrimer}</span>
					<br><br>
					Right Primer:<br>
					GC content: {rightGC}%<br>
					TM: {rightTM}°C<br>
					Sequence:<br>
					<span class = "monospaced">{rightPrimer}</span>
					<br>""".format(
								nameID = self.getNameID(),
								pos = self.getPosition(),
								terminal = self.getTerminal(),
								leftSpacer = self.getLeftSpacer(),
								rightSpacer = self.getRightSpacer(),
								leftGC = round(self.getLeftGC() * 100, 4),
								lefTM = round(self.getLeftTM(), 4),
								rightGC = round(self.getRightGC() * 100, 4),
								rightTM = round(self.getRightTM(), 4))

		return retStr
	def getCompZIP(self, offset):
		"""Return a dictionary of the component's primers and complete sequence.
		Used to generate a .zip file."""
		#primers and complete sequence
		retDict = {}
		
		idStr = self.getNameID()
		idStrAndName = "{nameID} ({name})".format(
							nameID = self.getNameID(),
							name = self.getName())
		
		#add the files to the dictionary
		retDict[idStr + "-CompleteSequence.fasta"] = ">" + idStrAndName + " complete sequence\n" + self.getFullSeq()
		retDict[idStr + "-LeftPrimer.fasta"] = ">" + idStrAndName + " left primer\n" + self.getLeftPrimer()
		retDict[idStr + "-RightPrimer.fasta"] = ">" + idStrAndName + " right primer\n" + self.getRightPrimer()
		retDict[idStr + "-CompleteSequence.gb"] = self.getGenBankFile(offset)
		
		return retDict
	
	def getGenBankFile(self, offset):
		"""Return a string formatted like a .gb file.
		
		PARAMETER:
			offset: integer number of seconds to offset the time from UTC
		
		RETURNS:
			finishedFile: string formatted as the contents of a .gb file
		"""
		if(type(offset) != int):
			raise TypeError("offset not an int")
		
		#lengths 
		lenSpacerL = 4
		lenSpacerR = 4
		lenNNL = 2
		lenNNR = 2
		lenEnzymeL = 6
		lenEnzymeR = 6
		lenSeq = len(self.getSeq())
		lenTotal = lenSpacerL + lenSpacerR + lenNNL + lenNNR + lenEnzymeL + lenEnzymeR + lenSeq
	
		#date; get the day-hour-year, adjusting for the timezone of the user with offset
		date = (datetime.utcnow() - timedelta(minutes = offset)).strftime("%d-%b-%Y")
	
		#fileByLines is an array of strings. Each string is one line.
		fileByLines = []
		
		#add the header
		fileByLines.append("LOCUS\t\t{nameID}\t{length} bp\tDNA\tlinear\t{date}".format(
								nameID = self.getNameID(),
								length = lenTotal,
								date = date))
		fileByLines.append("DEFINITION\t{nameID} ({name}) component from CyanoConstruct.".format(
								nameID = self.getNameID(),
								name = self.getName()))
		fileByLines.append("FEATURES\t\tLocation/Qualifiers")
		
		#add onto the feature section
		
		#i is the length of the sequence so far (as it goes through each feature)
		i = 0

		#EnzymeLeft
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenEnzymeL))
		fileByLines.append("\t\t\t/note=\"enzyme recog. site (left) (BbsI)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#CFEC67") #this is only for benchling
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#CFEC67")
		i += lenEnzymeL
		
		#NNleft
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenNNL))
		fileByLines.append("\t\t\t/note=\"NN (left)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#62E6D0")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#62E6D0")
		i += lenNNL
		
		#spacerLeft
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenSpacerL))
		fileByLines.append("\t\t\t/note=\"spacer (left)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#E6855F")
		i += lenSpacerL
		
		#sequence of the component
		if(self.getType() == "GOI"):
			#add a feature with the key "gene" if it is a GOI
			fileByLines.append("\tgene\t\t" + str(i + 1) + ".." + str(i + lenSeq))
			fileByLines.append("\t\t\t/gene=\"" + self.getName() + "\"")
		else:
			#add a feature with the key "regulatory" if it is not a GOI
			
			#get the long versions of the type
			regTypes = {"Pr": "promoter", "RBS" : "ribosome_binding_site", "Term": "terminator"}
			regName = regTypes[self.getType()]
			longTypes = {"Pr": "promoter", "RBS" : "RBS", "Term": "terminator"}
			longType = longTypes[self.getType()]
			
			#add the feature by lines
			fileByLines.append("\tregulatory\t" + str(i + 1) + ".." + str(i + lenSeq))
			fileByLines.append("\t\t\t/regulatory_class=" + regName)
			fileByLines.append("\t\t\t/note=\"" + longType + " " + self.getName() + "\"")
		
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#AB81E1")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#AB81E1")
		
		i += lenSeq

		#spacerRight
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenSpacerR))
		fileByLines.append("\t\t\t/note=\"spacer (right)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#E6855F")
		i += lenSpacerL

		#NNright
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenNNR))
		fileByLines.append("\t\t\t/note=\"NN (right)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#62E6D0")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#62E6D0")
		i += lenNNL

		#EnzymeRight
		fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenEnzymeR))
		fileByLines.append("\t\t\t/note=\"enzyme recog. site (right) (BbsI)\"")
		fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#CFEC67")
		fileByLines.append("\t\t\t/ApEinfo_revcolor=#CFEC67")
		i += lenEnzymeL

		#end of adding to the feature section
		
		#the sequence
		fileByLines.append("ORIGIN")
		
		i = 0 #re-use of i
		
		#get the sequence, lower-case
		seq = self.getFullSeq().lower()
		
		#add most lines, which are 60 nucleotides long
		while(i < (len(seq) // 60)):
			i60 = i * 60
			line = "{number} {block1} {block2} {block3} {block4} {block5} {block6}".format(
					**{"number" : str(i60 + 1).rjust(9, " "),
					"block1" : seq[i60 : i60 + 10],
					"block2" : seq[i60 + 10 : i60 + 20],
					"block3" : seq[i60 + 20 : i60 + 30],
					"block4" : seq[i60 + 30 : i60 + 40],
					"block5" : seq[i60 + 40 : i60 + 50],
					"block6" : seq[i60 + 50 : i60 + 60]})
	
			fileByLines.append(line)
	
			i += 1
		
		#add the last line, which is not 60 nucleotides long
		remainder = len(seq) % 60
		if(remainder != 0): #is not zero
			
			line = str(i * 60 + 1).rjust(9, " ") + " "
			for j in range(remainder):
				line += seq[i * 60 + j]
				if((j + 1) % 10 == 0):
					line += " "
			
			fileByLines.append(line)
			
		
		#finish file
		fileByLines.append("//")
		
		#join the lines together into one string
		finishedFile = "\n".join(fileByLines)
		
		return finishedFile
		
	#getters
	def getNameID(self):
		nameID = self.getNamedSequence().getNameID()
		return "{type}-{nameID}-{pos}{terminal}".format(
					type = self.getType(),
					nameID = nameID.zfill(3),
					pos = self.getPosition().zfill(3),
					terminal = self.getTerminalLetter())

	#ids
	def getID(self):
		return self.id
	
	def getNamedSeqID(self):
		return self.namedSequence_id
	
	def getUserID(self):
		return self.user_id


	#named sequence info.
	def getNamedSequence(self):
		return NamedSequenceDB.query.get(self.getNamedSeqID())
	
	def getName(self):
		return self.getNamedSequence().getName()
	
	def getSeq(self):
		return self.getNamedSequence().getSeq()
	
	def getType(self):
		return self.getNamedSequence().getType()


	#spacer info
	def getSpacerData(self):
		return SpacerDataDB.query.get(self.spacerData_id)
	
	def getTerminal(self):
		return self.getSpacerData().getIsTerminal()
	
	def getTerminalLetter(self):
		return self.getSpacerData().getTerminalLetter()
	
	def getPosition(self):
		return self.getSpacerData().getPosition()

	def getLeftSpacer(self):
		return self.getSpacerData().getSpacerLeft()
	
	def getRightSpacer(self):
		return self.getSpacerData().getSpacerRight() #what is this naming

	def getLeftNN(self):
		return self.getSpacerData().getLeftNN()
	
	def getRightNN(self):
		return self.getSpacerData().getRightNN()

	def getFullSpacerLeft(self):
		return self.getSpacerData().getFullSeqLeft()

	def getFullSpacerRight(self):
		return self.getSpacerData().getFullSeqRight()

	#primer info.
	def getPrimerData(self):
		return PrimerDataDB.query.get(self.primerData_id)
		
	def getLeftPrimer(self):
		return self.getPrimerData().getLeftSeq()
	
	def getLeftGC(self):
		return self.getPrimerData().getGCleft()
	
	def getLeftTM(self):
		return self.getPrimerData().getTMleft()
	
	def getRightPrimer(self):
		return self.getPrimerData().getRightSeq()
	
	def getRightGC(self):
		return self.getPrimerData().getGCright()
	
	def getRightTM(self):
		return self.getPrimerData().getTMright()

	#comparisons
	#sort first by NamedSequence, then by SpacerData
	def __eq__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() == other.getSpacerData()
		else:
			return False
	
	def __ne__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() != other.getSpacerData()
		else:
			return True

	def __lt__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() < other.getSpacerData()
		else:
			return self.getNamedSequence() < other.getNamedSequence()
	
	def __le__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() <= other.getSpacerData()
		else:
			return self.getNamedSequence() <= other.getNamedSequence()
	
	def __gt__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() > other.getSpacerData()
		else:
			return self.getNamedSequence() > other.getNamedSequence()
		
	def __ge__(self, other):
		if(self.getNamedSequence() == other.getNamedSequence()):
			return self.getSpacerData() >= other.getSpacerData()
		else:
			return self.getNamedSequence() >= other.getNamedSequence()

class BackboneDB(db.Model):
	__tablename__ = "Backbone"

	#columns
	id = db.Column(db.Integer, primary_key = True)
	
	name = db.Column(db.String(20))
	desc = db.Column(db.String(128), nullable = False, default = "No description.") #Need to mark as unsafe for HTML
	type = db.Column(db.String(1), nullable = False, default = "i")
	seqBefore = db.Column(db.Text(), nullable = False, default = "")
	seqAfter = db.Column(db.Text(), nullable = False, default = "")
	features = db.Column(db.Text(), nullable = False, default = "FEATURES\t\t\tLocation/Qualifiers")

	user_id = db.Column(db.Integer)

	def __repr__(self):
		return "<Backbone {ID} {Name}".format(ID = self.getID(), Name = self.getName())
	
	def __str__(self):
		return "Backbone {Name}".format(Name = self.getName())

	#setters
	def setUserID(self, newID):
		self.user_id = newID

	#getters
	def getID(self):
		return self.id
	
	def getUserID(self):
		return self.user_id

	def getName(self):
		return self.name

	def getType(self):
		return self.type

	def getTypeLong(self):
		longTypes = {"i": "integrative", "r": "replicative"}
		return longTypes[self.getType()]
	
	def getDesc(self):
		return self.desc

	def getSeqBefore(self):
		return self.seqBefore

	def getSeqAfter(self):
		return self.seqAfter

	def getSeq(self):
		return self.seqBefore + self.seqAfter

	def getFeatures(self):
		return self.features

	def getHTMLdisplay(self):
		"""Return HTML string to display the backbone on the /library page."""
		#get the library name
		if UserDataDB.query.get(self.getUserID()).getEmail() == "default":
			libraryName = "Default"
			isDefault = True
		else:
			libraryName = "Personal"
			isDefault = False

		retArray = []

		retArray.append("""<div class = "hideableTitle nameTitle" id = "{libraryName}{BBname}Backbone">
							<input class = "titleLeft subtleButton" type = "button" 
								onclick = "toggleDisplay('{libraryName}{BBname}BackboneData'); 
								switchToggleText(this);" value = "Name: {BBname}">
							<span class = "titleRight monospaced">[Click to show]</span>
							</div>

							<div id = "{libraryName}{BBname}BackboneData" 
								class = "hideableDiv" style = "display: none">
	
							<!-- info about the named sequence -->
							<p>Backbone: {BBname}</p>
	
							<p>Type: {BBtype}</p>
	
							<p>Description:</p>
							<p>{BBdesc}</p>
	
							<p>Sequence:</p>
							<div class = "sequence monospaced">
								{BBseqBefore}
								<span class = 'insertionSeq'>INSERTION</span>
								{BBseqAfter}
							</div>
	
							<br>""".format(libraryName = libraryName,
											BBname = Markup.escape(self.getName()),
											BBtype = self.getTypeLong(),
											BBdesc = Markup.escape(self.getDesc()),
											BBseqBefore = self.getSeqBefore(),
											BBseqAfter = self.getSeqAfter()
											))


		#add a "Remove Backbone" button if it is not the default library
		if(not isDefault):
			retArray.append("""<br><hr><input type = "button" class = "styledButton" 
								value = "Remove Backbone" onclick = "removeBackbone('{BBID}')">""".format(
														BBID = self.getID()))
		
		#finish the string
		retArray.append("""</div><div class = "hideableBottom"></div>""")

		retStr = "".join(retArray)

		return Markup(retStr)

	#comparisons
	#sort by name
	def __eq__(self, other):
		return self.getName() == other.getName()

	def __ne__(self, other):
		return self.getName() != other.getName()

	def __lt__(self, other):
		return self.getName() < other.getName()

	def __le__(self, other):
		return self.getName() <= other.getName()
	
	def __gt__(self, other):
		return self.getName() > other.getName()
		
	def __ge__(self, other):
		return self.getName() >= other.getName()
