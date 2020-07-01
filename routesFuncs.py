#misc other stuff

#design
from cyanoConstruct.enumsExceptions import SequenceMismatchError, SequenceNotFoundError, BackboneNotFoundError
from cyanoConstruct import defaultUser, checkType, maxPosition, printActions
from string import ascii_letters, digits, punctuation

#assembly
from datetime import datetime
import re

#zips
import os
from shutil import rmtree, make_archive
from uuid import uuid1, uuid4

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

#temporary passwords or something
def makePass():
	"""Return 32-character long string of random letters and numbers."""
	temp = uuid.uuid4().hex + uuid.uuid4().hex

	characters = "{letters}{digits}{d1}{d2}".format(
				letters = ascii_letters,
				digits = digits,
				d1 = digits[random.randrange(10)],
				d2 = digits[random.randrange(10)])

	password = []

	for i in range(0, 64, 2):
		index1 = int(temp[i : i + 2], 16)
		index = (int) (index1 / 4)

		password.append(characters[index])
		
	return "".join(password)

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
	validCharacters = ascii_letters + digits + punctuation + " "
	
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


def validateBackbone(newName, newDesc, newSeq, newType, newFeatures):
	"""Validates the input from creating a new NamedSequence on the design page."""
	validInput = True
	outputStr = ""

						#####	TYPE CHECKING	#####
	if(type(newName) != type(newDesc) != type(newSeq) != str) != type(newType) != type(newFeatures):
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
	validCharacters = ascii_letters + digits + punctuation + " "
	
	invalidCharactersName = []
	
	for character in newName:
		if((character not in validCharacters) and (character not in invalidCharactersName)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not allowed in a sequence's name.<br>"
			invalidCharactersName.append(character)

						#####	VALIDATE DESCRIPTION 	#####
	if(len(newDesc) < 1 or len(newDesc) > 128):
		validInput = False
		outputStr += "ERROR: Description must be 1-128 characters long.<br>"


						#####	VALIDATE SEQUENCE 	#####
	#length
	if(len(newSeq) < 1 or len(newSeq) > 999999): #I don't know what limits should be used
		validInput = False
		outputStr += "ERROR: Sequence must be 1-999999 nucleotides.<br>"
	
	#characters
	validNucleotides = "AGTCBDHKMNRSVWYagtcbdhkmnrsvwy"
	
	invalidCharactersSeq = []
	for character in newSeq:
		if((character not in validNucleotides) and (character not in invalidCharactersSeq)):
			validInput = False
			outputStr += "ERROR: '" + character + "' is not an allowed nucleotide.<br>"
			invalidCharactersSeq.append(character)

						#####	VALIDATE TYPE 	#####	
	if(newType != "i" and newType != "r"):
		validInput = False
		outputStr += "ERROR: Invalid backbone type received.<br>"
		
						#####	VALIDATE Features 	#####
	#currently assumes it's fine

	return (validInput, outputStr)

def searchBackbone(seq):
	#search the main sequence
	patternL = "{spacerL}\w\w{start}".format(spacerL = "AGGA", start = "GTCTTC")
	patternR = "{end}\w\w{spacerR}".format(end = "GAAGAC", spacerR = "TACA")

	sitesL = [m.start() for m in re.finditer(patternL, seq)]
	sitesR = [m.start() for m in re.finditer(patternR, seq)]

	#search the very end and beginning, combined (since it's ciruclar)
	loopLen = 11 #length of the pattern (spacer-4 bp, NN-2 bp, recog.-6 bp) - 1
	
	veryEnd = seq[-loopLen:] + seq[0:loopLen]
	
	matchL = re.search(patternL, veryEnd)
	if(matchL):
		index = matchL.start()
		if(index < loopLen):
			index = len(seq) - (loopLen - index)
		else:
			index -= loopLen

		sitesL.append(index)

	matchR = re.search(patternR, veryEnd)
	if(matchR):
		index = matchR.start()
		if(index < loopLen):
			index = len(seq) - (loopLen - index)
		else:
			index -= loopLen
			
		sitesR.append(index)

	return (sitesL, sitesR)

def validateSearchBackbone(outputStr, seq):
	validInput = True
	sitesL, sitesR = searchBackbone(seq)

	if(len(sitesL) == 0):
		validInput = False
		sitesL.append(None)
		outputStr += "ERROR: No match found for the <span class = 'monospaced'>AGGANNGTCTTC</span> pattern.<br>"
	elif(len(sitesL) > 1):
		validInput = False
		outputStr += "ERROR: Multiple matches found for the <span class = 'monospaced'>AGGANNGTCTTC</span> pattern.<br>"

	if(len(sitesR) == 0):
		validInput = False
		sitesR.append(None)
		outputStr += "ERROR: No match found for the <span class = 'monospaced'>GAAGACNNTACA</span> pattern.<br>"
	elif(len(sitesL) > 1):
		validInput = False
		outputStr += "ERROR: Multiple matches found for the <span class = 'monospaced'>GAAGACNNTACA</span> pattern.<br>"

	return (validInput, outputStr, sitesL[0], sitesR[0])

def extractSequence(originSeq):
	"""Remove all numbers and whitespace from a string."""
	seq = re.sub("\s|\d", "", originSeq)
	return seq

def readBackboneGB(dataBytes, outputStr):
	validInput = True

	features = None
	definition = None
	name = None
	molType = None
	seq = None
	division = None

	try:
		backboneData = dataBytes.splitlines(keepends = True)
		
		for i in range(len(backboneData)):
			backboneData[i] = backboneData[i].decode()
					
	except Exception as e:
		validInput = False
		print(e)
		outputStr += "ERROR: Invalid input received."  
	
	if(validInput):
		#check the first line
		try:
			header = backboneData[0].split()
			
			if(header[0] != "LOCUS"):
				raise Exception("no LOCUS")
						
			lengthIndex = -1
			
			#find the length
			for i in range(len(header) - 1):
				if(header[i + 1][-2:] == "bp"):
					if(header[i + 1][-3:-2] == "-"):
						try:
							length = int(header[i + 1][0:-3])
							lengthIndex = i + 1
						except Exception:
							pass
					else:
						try:
							length = int(header[i + 1][0:-2])
							lengthIndex = i + 1
						except Exception:
							pass
				else:
					try:
						length = int(header[i + 1])
						lengthIndex = i + 1
					except Exception:
						pass
			
			if(lengthIndex == -1):
				raise Exception("Could not find length of sequence.")
			
			#remove "bp" if it's there
			if(header[lengthIndex + 1] == "bp"):
				header.pop(lengthIndex + 1)
						
			if(len(header) < lengthIndex + 3):
				raise Exception("First line is too short. It must have the format: LOCUS locus_name sequence_length molecule_type (optional: circular or linear) (optional: GenBank_division) modification_date")
			elif(len(header) > lengthIndex + 5):
				raise Exception("First line is too long. It must have the format: LOCUS locus_name sequence_length molecule_type (optional: circular or linear) (optional: GenBank_division) modification_date")

			#name
			name = " ".join(header[1:lengthIndex])
			
			#sequence type (molecule type) & division
			molType = header[lengthIndex + 1]
			if(molType.find("DNA") == -1):
				raise Exception("Sequence must be a DNA sequence.")
			
			if(header[lengthIndex + 2] == "linear"):
				raise Exception("Sequence must be circular, not linear.")
			elif(header[lengthIndex + 2] == "circular"):
				if(len(header) == 6):
					division = ""
				else:
					division = header[lengthIndex + 3]
			else: #assume it is the division
				if(len(header) == 7):
					raise Exception("Unexpected word: {}".format(header[lengthIndex + 2]))
				else:
					if(len(header) == 5): #it is not the division, but the modification date
						division = ""
					else:
						division = header[lengthIndex + 2] #it is the division
						
			#the modification date will be dropped
			
			#definition
			defRow = backboneData[1].split(maxsplit = 1)
			
			if(defRow[0] != "DEFINITION"):
				raise Exception("No DEFINITION")
			
			if(len(defRow) == 1):
				definition = ""
			else:
				definition = defRow[1].rstrip()
			
			#IGNORES other information like Accession, Source, Journal, etc.
			
			#search for the relevant regions: the FEATURES and the ORIGIN
			featureIndex = -1
			originIndex = -1
			originEnd = -1
						
			for i in range(len(backboneData) - 2):
				if backboneData[i + 2][0:6] == "ORIGIN":
					originIndex = i + 2
				elif backboneData[i + 2][0:8] == "FEATURES":
					featureIndex = i + 2
				elif backboneData[i + 2][0:2] == "//":
					originEnd = i + 2
			
			if(featureIndex == -1):
				raise Exception("No FEATURE section found.")
			if(originIndex == -1):
				raise Exception("No ORIGIN section found.")
			if(originEnd == -1):
				raise Exception("No end of .gb (//) found.")
			if(originIndex < featureIndex):
				raise Exception("Origin section should not be before feature section.")
			if(originEnd < originIndex):
				raise Exception("End of .gb should be after Origin section.")
				
			#first look at the origin
			seq = extractSequence("\n".join(backboneData[originIndex + 1 : originEnd]))
			
			if(len(seq) != length):
				raise Exception("Length of sequence declared in the first line ({firstLine} bp) and of the actual sequence in the ORIGIN section ({originSec} bp) are inconsistent.".format(
						firstLine = length,
						originSec = len(seq)))

			#replace spacing of the FEATURES section with tabs
			for i in range(featureIndex + 1, originIndex):
				if(backboneData[i].lstrip()[0] != "/"):
					row = backboneData[i].split(maxsplit = 1)

					if(len(row) == 2):
						if(len(row[0]) <= 6):
							backboneData[i] = "\t{row1}\t\t{row2}".format(row1 = row[0], row2 = row[1])
						else:
							backboneData[i] = "\t{row1}\t{row2}".format(row1 = row[0], row2 = row[1])
					else:
						backboneData[i] = "\t{row}".format(row = row[0])
				else:
					backboneData[i] = "\t\t\t{row}\n".format(row = backboneData[i].strip())
			
			features = "".join(backboneData[featureIndex + 1:originIndex])

		except Exception as e:
			validInput = False
			outputStr += "ERROR: {}".format(e)
		
	return (outputStr, validInput, {"name": name, "molType": molType, "division": division, "definition": definition, "features" : features, "sequence": seq})
			
def processGBfeatures(seq, features, outputStr):
	sequenceBefore = None
	sequenceAfter = None
	featureSection = None
	
	#do some MORE processing whee
	validInput, outputStr, siteL, siteR = validateSearchBackbone(outputStr, seq)

	length = len(seq)

	if(printActions):
		print("siteL {} siteR {}".format(siteL, siteR))

	if(validInput):
		try:
			if(siteL + 4 >= length):
				insL = 5 - (length - siteL)
			else:
				insL = siteL + 5
			
			if(siteR + 7 >= length):
				insR = 8 - (length - siteR)
			else:
				insR = siteR + 8

			if(printActions):
				print((insL, insR))

			if(insR >= insL):
				insertionAdjustment = (insR - insL) + 1
				rightmost = insR
			else: #if the insertion region wraps back around
				insertionAdjustment = insR
				rightmost = length + 1

			if(printActions):
		 		print("insertionAdjustment {} rightmost {}".format(insertionAdjustment, rightmost))
			
			deleteNextLine = False

			#Go through every feature
			for i in range(len(features)):
				features[i] = features[i].lstrip()
				
				if(features[i]):
					if(features[i][0] != "/"):
						#extract the row
						row = features[i].split(maxsplit = 1)

						if(printActions):
							print(features[i])

						if(len(row) > 1):
							#should have numbers in the string of the format NUMBER..NUMBER							
							rowElements = re.split("(\d+..\d+)", row[1])
							if(rowElements[0] == "join("):
								isJoin = True
							else:
								isJoin = False

							pairsRemove = 0

							for j in range(1, len(rowElements), 2):
								removeFeature = False
								
								#this SHOULD be the pattern
								startIndex, endIndex = rowElements[j].split("..")
								newStart = int(startIndex)
								
								if(newStart > length):
									newStart -= length
									
								newEnd = int(endIndex)
								if(newEnd > length):
									newEnd -= length
								
								if(printActions):
									print("newStart {} newEnd {} \t insL {} insR {}".format(newStart, newEnd,
										  insL, insR))
								
								if(insR >= insL):
									if(newStart >= insL and newStart <= insR):
										#start within insertion region
										if(newEnd >= insL and newEnd <= insR):
											removeFeature = True
											
											if(printActions):
												print("need to remove the entire thing")

										else:
											newStart = insR + 1
											if(newStart > length):
												newStart = newStart - length
									elif(newEnd > insL and newEnd <= insR):
										#end within insertion region
										newEnd = insL - 1
										if(newEnd < 1):
											newEnd = length + newEnd
										
									#what is insR2 I'm not sure
									insR2 = insR

								else:
									if(newStart <= insR):
										#start within insertion region
										if(newEnd <= insR):
											removeFeature = True

											if(printActions):
												print("need to remove the entire thing")
											#remove the entire thing
										else:
											newStart = insR + 1
											if(newStart > length):
												newStart = newStart - length
									if(newEnd >= insL):
										#end within insertion region
										if(newStart >= insL):
											removeFeature = True

											if(printActions):
												print("need to remove the entire thing")
										else:
											newEnd = insL - 1
											if(newEnd < 1):
												newEnd = length + newEnd

									if(printActions):
										print("newStart {} newEnd {} insR {}".format(newStart, newEnd, insR))

										print("newStart -= insR; newEnd -= insR")

									newStart -= insR
									newEnd -= insR
									
									insR2 = length - insR

								#add to the numbers as necessary
								#get the strings to replace them with
								if(newStart >= insR2):

									if(newStart >= rightmost):
										startStr = "[AddLength]{}[AddLength]".format(newStart - insertionAdjustment)
									else:
										startStr = str(newStart - insertionAdjustment)
								else:
									startStr = str(newStart)
								
								if(newEnd >= insR2):
									if(newEnd >= rightmost):
										endStr = "[AddLength]{}[AddLength]".format(newEnd - insertionAdjustment)
									else:
										endStr = str(newEnd - insertionAdjustment)
								else:
									endStr = str(newEnd)
									
								#finalllyyyyy
								if(removeFeature):
									rowElements[j] = ""
									pairsRemove += 1
								else:
									rowElements[j] = "{start}..{end}".format(start = startStr, end = endStr)

							if(pairsRemove == int(len(rowElements) / 2)):
								deleteNextLine = True
								features[i] = ""
								if(printActions):
									print("isJoin = {} \tpairsRemove = {} \tint(len(rowElements) / 2) - 1) = {}".format(
										isJoin, pairsRemove, int(len(rowElements) / 2) - 1))
							else:
								if(printActions):
									print("isJoin = {} \tpairsRemove = {} \tint(len(rowElements) / 2) - 1) = {}".format(
										isJoin, pairsRemove, int(len(rowElements) / 2) - 1))
								deleteNextLine = False

								#replace the row with the properly formatted one
								if(len(row[0]) <= 3):
									features[i] = "\t{row1}\t\t{row2}".format(row1 = row[0], row2 = "".join(rowElements))
								else:
									features[i] = "\t{row1}\t{row2}".format(row1 = row[0], row2 = "".join(rowElements))

							#remove empty numbers in a join
							if(isJoin):
								while(features[i].find(",,") != -1):
									features[i] = features[i].replace(",,", ",")
								features[i] = features[i].replace("(,", "(")
								features[i] = features[i].replace(",)", ")")
								features[i] = features[i].replace("( ", "(")
								features[i] = features[i].replace(" )", ")")

								#remove the join() if there's only one set of numbers remaining
								if(pairsRemove == int(len(rowElements) / 2) - 1):
									features[i] = features[i].replace("join(", "")
									features[i] = features[i].replace(")", "")

							if(printActions):
								print(features[i])
								print("===")
					else:
						#add three tabs to the beginning
						features[i] = "\t\t\t" + features[i]

				if(deleteNextLine):
					features[i] = ""

			featureSection = "".join(features)

			#remove the stuff
			if(insL <= insR):
				sequenceBefore = seq[0:insL - 1]
				sequenceAfter = seq[insR:]
			else:
				sequenceBefore = seq[insR:insL - 1]
				sequenceAfter = ""

		except Exception as e:
			outputStr += "ERROR: {}".format(e)
			validInput = False
	
	return(outputStr, validInput, {"seqBefore": sequenceBefore, "seqAfter": sequenceAfter, "featureSection": featureSection})
	
#Assembly
def addSpacerAssemblyGB(spacer, features, i):
	lenSpacer = len(spacer)
	features.append("\tmisc_feature\t{start}..{end}".format(
										start = i + 1,
										end = i + lenSpacer))
	features.append("\t\t\t/note=\"spacer\"")
	features.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
	features.append("\t\t\t/ApEinfo_revcolor=#E6855F")

	return i + lenSpacer

def addCompAssemblyGB(comp, features, i):
	"""Add feature of component for a GenBank file."""
	lenSeq = len(comp.getSeq())
	
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
		features.append("\t\t\t/note=\"" + longType + " " + comp.getName() + "\"")
	
	return i + lenSeq

def finishCompAssemblyGB(features, fullSeq):
	"""Make the head and ORIGIN section of the GenBank file, then join all parts together into a single string."""
	#fileHead	
	date = datetime.today().strftime("%d-%b-%Y").upper()
	
	completeFile = ["LOCUS\t\tAssembled_sequence\t" + str(len(fullSeq)) + " bp\tDNA\tcircular\tSYN\t" + date,
				"DEFINITION\tSequence assembled from CyanoConstruct",
				"FEATURES\t\tLocation/Qualifiers"]
	
	#process sequence for ORIGIN section
	seq = fullSeq.lower()
	
	i = 0
	origin = ["ORIGIN"]
	
	#most lines (60 nucleotides per line)
	while(i < (len(seq) // 60)):
		i60 = i * 60
		line = "{number} {block1} {block2} {block3} {block4} {block5} {block6}".format(
				number = str(i60 + 1).rjust(9, " "),
				block1 = seq[i60 : i60 + 10],
				block2 = seq[i60 + 10 : i60 + 20],
				block3 = seq[i60 + 20 : i60 + 30],
				block4 = seq[i60 + 30 : i60 + 40],
				block5 = seq[i60 + 40 : i60 + 50],
				block6 = seq[i60 + 50 : i60 + 60])

		origin.append(line)

		i += 1
		
	#final line
	remainder = len(seq) % 60
	if(remainder != 0):
		
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