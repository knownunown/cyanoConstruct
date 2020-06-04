#misc other stuff

#design
from cyanoConstruct import defaultUser, checkType, SequenceMismatchError, SequenceNotFoundError, maxPosition, printActions
from string import ascii_letters, digits

#assembly
from datetime import datetime

#zips
import os
from shutil import rmtree, make_archive
from uuid import uuid1

#misc.
def boolJS(b):
	if(b == "true"):
		return True
	elif(b == "false"):
		return False
	else:
		if(type(b) != str):
			raise TypeError("b not a boolean")
		else:
			raise ValueError("b not true or false")


#Design
def validateNewNS(newNSType, newNSName, newNSSeq):
	"""Validates the input from creating a new NamedSequence on the design page."""
	validInput = True
	outputStr = ""

						#####	TYPE CHECKING	#####
	if(type(newNSType) != type(newNSName) != type(newNSSeq) != str):
		validInput = False
		outputStr += "ERROR: input received not all strings.<br>"
	
	try:
		checkType(newNSType, "newNSType")
	except ValueError:
		validInput = False
		outputStr += "ERROR: '" + newNSType + "' is not a valid type.<br>"
	

						#####	VALIDATE NAME 	#####
	#length
	if(len(newNSName) < 1 or len(newNSName) > 20):
		validInput = False
		outputStr += "ERROR: Sequence name must be 1-20 characters.<br>"
	
	#whether it already exists in default:
	longNames = {"Pr": "promoter", "RBS": "ribosome binding site", "GOI": "gene", "Term": "terminator"}
	for elemType in ["Pr", "RBS", "GOI", "Term"]:
		try:
			defaultUser.findNamedSequence(elemType, newNSName, newNSSeq)
						
			validInput = False
			outputStr += "ERROR: " + newNSName + " already exists in the default library as a " + longNames[elemType] + ".<br>"
			break
		except SequenceMismatchError:
			validInput = False
			outputStr += "ERROR: " + newNSName + " already exists in the default library as a " + longNames[elemType] + ", and with a different sequence.<br>"
			break
		except SequenceNotFoundError:
			pass
	
	#characters
	validCharacters = ascii_letters + digits + "_-. "
	
	invalidCharactersName = []
	
	for character in newNSName:
		if((character not in validCharacters) and (character not in invalidCharactersName)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not allowed in a sequence's name.<br>"
			invalidCharactersName.append(character)


						#####	VALIDATE SEQUENCE 	#####
	#length
	if(len(newNSSeq) < 1 or len(newNSSeq) > 99999): #I don't know what limits should be used
		validInput = False
		outputStr += "ERROR: Sequence must be 1-99999 nucleotides.<br>"
	
	#characters
	validNucleotides = "AGTCBDHKMNRSVWY"
	
	invalidCharactersSeq = []
	for character in newNSSeq:
		if((character not in validNucleotides) and (character not in invalidCharactersSeq)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not an allowed nucleotide.<br>"
			invalidCharactersSeq.append(character)

	return (validInput, outputStr)

def validateSpacers(newPosStr, newTerminalStr):
	validInput = True
	outputStr = ""

	#position
	try:
		newPos = int(newPosStr)
	except Exception:
		validInput = False
		outputStr += "ERROR: position not an integer.<br>"
		
	if(validInput):
		if((newPos < 0) or (newPos > maxPosition)):
			if(newPos != 999):
				validInput = False
				outputStr += "ERROR: Position must be in range 1-" + str(maxPosition) + ".<br>"

	#isTerminal
	try:
		isTerminal = boolJS(newTerminalStr)
	except Exception:
		validInput = False
		outputStr += "ERROR: Last element value not valid.<br>"

	#if the position is the maximum allowed position, it must be terminal
	if(validInput and (newPos == maxPosition) and (not isTerminal)):
		validInput = False
		outputStr += "ERROR: " + str(newPos) + " is the last allowed position, so it must be terminal.<br>"

	return (validInput, outputStr, newPos, isTerminal)

def validatePrimers(TMstr, rangeStr):
	validInput = True
	outputStr = ""

	#type
	try:
		TMnum = float(TMstr)
	except Exception:
		validInput = False
		outputStr += "ERROR: TM not a number.<br>"
	
	try:
		rangeNum = float(rangeStr)
	except Exception:
		validInput = False
		outputStr += "ERROR: TM range not a number.<br>"
	
	#proper ranges
	if(validInput):	
		if(TMnum < 20 or TMnum > 80): #I don't know what to actually limit it by
			validInput = False
			outputStr += "ERROR: Melting point out of range 20-80<br>"
		
		if(rangeNum < 1 or rangeNum > 10):
			validInput = False
			outputStr += "ERROR: Range for melting point must be in range 1-10.<br>"

	return (validInput, outputStr, TMnum, rangeNum)


def validateBackbone(newName, newSeq):
	"""Validates the input from creating a new NamedSequence on the design page."""
	validInput = True
	outputStr = ""

						#####	TYPE CHECKING	#####
	if(type(newName) != type(newSeq) != str):
		validInput = False
		outputStr += "ERROR: input received not all strings.<br>"
	

						#####	VALIDATE NAME 	#####
	#length
	if(len(newName) < 1 or len(newName) > 20):
		validInput = False
		outputStr += "ERROR: Backbone name must be 1-20 characters.<br>"
	
	#whether it already exists in default:
		try:
			defaultUser.findBackbone(newName)
						
			validInput = False
			outputStr += "ERROR: Backbone {name} already exists in the default library.<br>".format(name = newName)

		except BackboneNotFoundError:
			pass
	
	#characters
	validCharacters = ascii_letters + digits + "_-. "
	
	invalidCharactersName = []
	
	for character in newName:
		if((character not in validCharacters) and (character not in invalidCharactersName)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not allowed in a sequence's name.<br>"
			invalidCharactersName.append(character)


						#####	VALIDATE SEQUENCE 	#####
	#length
	if(len(newSeq) < 1 or len(newSeq) > 999999): #I don't know what limits should be used
		validInput = False
		outputStr += "ERROR: Sequence must be 1-999999 nucleotides.<br>"
	
	#characters
	validNucleotides = "AGTCBDHKMNRSVWY"
	
	invalidCharactersSeq = []
	for character in newSeq:
		if((character not in validNucleotides) and (character not in invalidCharactersSeq)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not an allowed nucleotide.<br>"
			invalidCharactersSeq.append(character)

	return (validInput, outputStr)


#Assembly
def addCompAssemblyGB(comp, features, i):
	"""Add feature of component for a GenBank file."""
	lenSeq = len(comp.getFullSeq())
	
	if(comp.getType() == "GOI"):
		features.append("\tgene\t\t" + str(i + 1) + ".." + str(i + lenSeq))
		features.append("\t\t\t/gene=\"" + comp.getName() + "\"")
	else:
		regTypes = {"Pr": "promoter", "RBS" : "ribosome_binding_site", "Term": "terminator"}
		regName = regTypes[comp.getType()]
		longTypes = {"Pr": "promoter", "RBS" : "RBS", "Term": "terminator"}
		longType = longTypes[comp.getType()]

		features.append("\tregulatory\t" + str(i + 1) + ".." + str(i + lenSeq))
		features.append("\t\t\t/regulatory_class=" + regName)
											#get a longer thing to say here
		features.append("\t\t\t/note=\"" + longType + " " + comp.getName() + "\"")
	
	return i + lenSeq

def finishCompAssemblyGB(features, fullSeq):
	"""Make the head and ORIGIN section of the GenBank file, then join all parts together into a single string."""
	#fileHead	
	date = datetime.today().strftime("%d-%b-%Y").upper()
	
	completeFile = ["LOCUS\tAssembled sequence\t" + str(len(fullSeq)) + " bp\tDNA\tlinear\t" + date,
				"DEFINITION\tSequence assembled from CyanoConstruct",
				"FEATURES\tLocation/Qualifiers"]
	
	#process sequence for ORIGIN section
	seq = fullSeq.lower()
	
	i = 0
	origin = ["ORIGIN"]
	
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

		origin.append(line)

		i += 1
		
	remainder = len(seq) % 60
	if(remainder != 0): #is not zero
		
		line = str(i * 60 + 1).rjust(9, " ") + " "
		for j in range(remainder):
			line += seq[i * 60 + j]
			if((j + 1) % 10 == 0):
				line += " "
		
		origin.append(line)

	#merge sections
	completeFile.extend(features)
	completeFile.extend(origin)
	completeFile.append("//")
	
	return "\n".join(completeFile)	


#ZIP-related functions
def makeZIP(filesDict):
	if(type(filesDict) != dict):
		raise TypeError("files not a dict")
		
	if(printActions):
		print("CREATING FASTA AND ZIP FILES")
	
	#check if no files have been produced
	if(filesDict == {}):
		if(printActions):
			print("NO SEQUENCE; NO FILES CREATED")
		
		return None
	
	submissionID = uuid1().hex
	
	#paths
	filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
	sessionDir = os.path.join(filesDirPath, submissionID)
	
	os.mkdir(sessionDir)
	
	if(printActions):
		print("MADE DIRECTORY: " + sessionDir)	
	
	#write files
	for fileName in filesDict:
		newName = os.path.join(sessionDir, fileName)
		with open(newName, "w") as f:
			f.write(filesDict[fileName])
			
	#make zip
	zipPath = os.path.join(os.path.join(filesDirPath, "zips"), submissionID)
	make_archive(zipPath, "zip", sessionDir)
	
	#read zip as a byte file
	with open(zipPath + ".zip", "rb") as f:
		data = f.readlines()
	
	#delete the session directory & zip file
	rmtree(sessionDir)
	os.remove(zipPath + ".zip")
	
	if(printActions):
		print("FINISHED CREATING FILES FOR SESSION " + submissionID)

	return data

def makeAllLibraryZIP(user):
	if(type(user) != UserData):
		raise TypeError("user not a UserData")

	filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
	sessionDir = os.path.join(filesDirPath, uuid1().hex)
	libraryDir = os.path.join(sessionDir, user.getEmail() + "Library")

	try:
		os.mkdir(sessionDir)
	except OSError: #if it exists
		pass
	os.mkdir(libraryDir)
	
	if(printActions):
		print("MADE DIRECTORY: " + libraryDir)
		
	#great now what?
	sortedNS = user.getSortedNS()
	for typeKey in sortedNS:
		if(sortedNS[typeKey] == []): #do nothing if the folder would be empty
			continue

		#make folder for the type		
		typeDir = os.path.join(libraryDir, typeKey)
		os.mkdir(typeDir)
		
		for ns in sortedNS[typeKey]:
			nsComps = ns.getAllComponents()
			
			if(nsComps == []): #do nothing if the folder would be empty
				continue

			#make folder for the sequence
			nameDir = os.path.join(typeDir, ns.getName())
			os.mkdir(nameDir)
			
			nsComps.sort() #is this necessary?
			
			for comp in nsComps:
				#make folder for the component
				compDir = os.path.join(nameDir, comp.getNameID())
				os.mkdir(compDir)
				
				compZIP = comp.getCompZIP()

				#make the files for the component
				for fileName in compZIP:
					filePath = os.path.join(compDir, fileName)

					with open(filePath, "w") as f:
						f.write(compZIP[fileName])
	
	#make the zip
	zipPath = os.path.join(sessionDir, "libraryZIP")
	
	make_archive(zipPath, "zip", libraryDir)
	
	#read zip as a byte file
	with open(zipPath + ".zip", "rb") as f:
		data = f.readlines()
		
	rmtree(sessionDir)

	if(printActions):
		print("FINISHED CREATING LIBRARY ZIP FOR USER " + user.getEmail())
	
	return data