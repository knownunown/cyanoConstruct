"""
Defines the classes: NamedSequence, SpacerData, PrimerData

@author: Lia Thomson
"""

import random
#from jinja2 import Markup

#from cyanoConstruct import NamedSequenceDB, SpacerDataDB, PrimerDataDB
from misc import checkType

def inverseSeq(sequence):
        """Return complementary strand to an all-caps 5' to 3' sequence.

        PARAMETER:
                sequence: string of all-caps characters; the sequence to invert

        RETURNS:
                finalSeq: string of inverse sequence

        RAISES:
                TypeError: if sequence is not a string
                ValueError: if the sequence has an invalid nucleotide.
        """
        if(type(sequence) != str):
                raise TypeError("sequence not a string")

        #create dict of complementary bases
        pairs = {'A': 'T', 'C': 'G', 'B': 'V', 'D': 'H', 'K': 'M', 'N': 'N',
                         'R': 'Y', 'S': 'S', 'W': 'W', 'T': 'A', 'G': 'C', 'V': 'B',
                         'H': 'D', 'M': 'K', 'Y': 'R'}

        #initialize the array, which will be built upon nucleotide by nucleotide
        array = []

        try:
                #go through the sequence from the end to the beginning

                i = len(sequence) - 1

                while(i >= 0):
                        #add the complementary nucleotide to the array
                        array.append(pairs[sequence[i]])
                        i -= 1
        except KeyError:
                raise ValueError("sequence has invalid nucleotide")

        finalSeq = "".join(array)

        return finalSeq

class NamedSequence:
        """NamedSequence class is used to store a named sequence's info. without
        adding it to the database."""

        #initialization methods
        def __init__(self):
                """Blank initialization method."""
                pass

        @classmethod
        def makeNew(cls, NSType, NSName, NSSeq, nameID):
                """Create a new NamedSequence.

                PARAMETERS:
                        NSType: string type of the named sequence
                        NSName: string name of the named sequence
                        NSSeq: string sequence of the named sequence
                        NSnameID: string name ID of the named sequence

                RETURNS:
                        newNS: the new NamedSequence
                """
                #type checking
                checkType(NSType, "NSType")

                if(type(NSName) != str):
                        raise TypeError("NSName not a string")
                if(type(NSSeq) != str):
                        raise TypeError("NSSeq not a string")
                if(type(nameID) != int):
                        raise TypeError("newID not an int")

                #initialize the instance
                newNS = cls()

                #set instance's variables
                newNS.__type = NSType
                newNS.__name = NSName
                newNS.__seq = NSSeq
                newNS.__nameID = nameID

                return newNS

        #json stuff
        def toJSON(self):
                """Return a JSON-friendly version of the NamedSequence."""
                return vars(self)

        @classmethod
        def fromJSON(cls, JSONDict):
                """Create a NamedSequence using a JSON dict.

                PARAMETERS:
                        JSONDict: dictionary containing the relevant namedSequence information.

                RETURNS:
                        newNS: created NamedSequence

                RAISES:
                        Exception: if the JSONDict is lacking one of the necessary fields
                """
                newNS = cls()

                prefix = "_NamedSequence__" #used to get private fields

                try:
                        #set the properties
                        newNS.__type = JSONDict[prefix + "type"]
                        newNS.__name = JSONDict[prefix + "name"]
                        newNS.__seq = JSONDict[prefix + "seq"]
                        newNS.__nameID = int(JSONDict[prefix + "nameID"])
                except KeyError:
                        raise Exception("Can't create a NamedSequence from this JSONDict.")

                return newNS

        #getters
        def __str__(self):
                return ("Named Sequence.\nType: " + self.getType() + "\nName: " + self.getName() +
                                "\nName ID: " + str(self.getNameID()) + "\nSequence:\n" + self.getSeq())

        def getType(self):
                return self.__type

        def getName(self):
                return self.__name

        def getSeq(self):
                return self.__seq

        def getNameID(self):
                return self.__nameID

class SpacerData:
	"""SpacerData is a class used to store spacer data before adding it to the database.
	It also stores spacer-relevant variables."""
	
	#Spacer-relevant variables
	
	#enzyme recognition sites
	start = "GAAGAC"
	end = "GTCTTC"

	#spacers for elements 0 and T
	spacer0L = "AGGA"
	spacer0R = "AAAA"
	spacerTL = "ACTC"
	spacerTR = "TACA"
	
	#spacers, from highest allowed fidelity to lowest	
	spacers985 = [spacer0L, spacer0R]
	spacers981 = ["CAGA", "GATA", "ATTA", "ACTC", "TACA"]
	spacers958 = ["CCAG","CGGA","TGAA"]
	spacers917 = ["GGAA", "GCCA", "CACG", "CTTC", "ACTG", "AAGC", "GACC", "ATCG", "AGAG",
	              "AGCA", "GTGA", "ACGA", "ATAC", "CAAG", "AAGG"]

	spacers = spacers985 + spacers981 + spacers958 + spacers917

	#max position for an element for a given fidelity
	max985 = 1
	max981 = len(spacers981)
	max958 = max981 + len(spacers958)
	max917 = max958 + len(spacers917) + 1

	@staticmethod
	def getMaxPosition():
		"""Returns the maximum allowed position of a component."""
		return len(SpacerData.spacers) - 1

	def __init__(self):
		"""Empty initialization method."""
		pass

	@classmethod
	def makeNew(cls, position, isTerminal):
		"""Create a new SpacerData.
		
		PARAMETERS:
			position: integer position of the component the spacers are for
			isTerminal: boolean if spacers are for a terminal component
		
		RETURNS:
			newSpacerData: created 
		
		RAISES:
			Exception: if the JSONDict is lacking one of the necessary fields
		"""
		#type checking
		if(type(position) != int):
			raise TypeError("position is not an int")
		if(type(isTerminal) != bool):
			raise TypeError("isTerminal is not a boolean")

		#initialize the instance
		newSpacerData = cls()

		#999 is the special position for element T
		if(position == 999):
			newSpacerData.__spacerLeft = SpacerData.spacerTL
			newSpacerData.__spacerRight = SpacerData.spacerTR
			
			newSpacerData.__isTerminal = False #I don't know if this is appropriate
			newSpacerData.__terminalLetter = "T" #T for terminator

		#validation
		elif(position < 0 or position > SpacerData.getMaxPosition()):
			raise ValueError("Position out of bounds. (0-{max})".format(
				max = SpacerData.getMaxPosition()))
		
		elif(position == SpacerData.getMaxPosition() and not isTerminal):
			raise Exception("Position " + position + " must be terminal.")
		
		#other positions
		else:
			#set the left spacer sequence
			newSpacerData.__spacerLeft = SpacerData.spacers[position]
			
			#set the right spacer sequence
			if(isTerminal):
				#if the spacers are for a terminal element
				newSpacerData.__spacerRight = SpacerData.spacerTL
				newSpacerData.__isTerminal = True
				newSpacerData.__terminalLetter = "L" #L for last
				
			else:
				#if the spacers are not for a terminal element
				newSpacerData.__spacerRight = SpacerData.spacers[position + 1]
				newSpacerData.__isTerminal = False
				newSpacerData.__terminalLetter = "M" #m for middle
		
			if(position == 0):
				#if these are spacers for an element 0
				newSpacerData.__terminalLetter = "S" #s for start

		#set position
		newSpacerData.__position = position
		
		#set the NN on each side
		newSpacerData.setNN()
		newSpacerData.setFullSpacerSeqs()
				
		return newSpacerData

	#json stuff
	def toJSON(self):
		"""Returns a JSON-friendly version of the SpacerData."""
		return vars(self)
	
	@classmethod
	def fromJSON(cls, JSONDict):
		"""Create a SpacerData using a JSON dict.
		
		PARAMETERS:
			JSONDict: dictionary containing the relevant spacer data information.
			
		RETURNS:
			newSpacerData: created SpacerData
			
		RAISES:
			Exception: if the JSONDict is lacking one of the necessary fields
		"""
		newSpacerData = cls()
				
		prefix = "_SpacerData__" #used to get private fields
		
		try:
			#set the properties
			newSpacerData.__spacerLeft = JSONDict[prefix + "spacerLeft"]
			newSpacerData.__spacerRight = JSONDict[prefix + "spacerRight"]
			newSpacerData.__isTerminal = JSONDict[prefix + "isTerminal"]
			newSpacerData.__terminalLetter = JSONDict[prefix + "terminalLetter"]
			newSpacerData.__position = JSONDict[prefix + "position"]
			newSpacerData.__leftNN = JSONDict[prefix + "leftNN"]
			newSpacerData.__rightNN = JSONDict[prefix + "rightNN"]
			newSpacerData.__fullSeqLeft = JSONDict[prefix + "fullSeqLeft"]
			newSpacerData.__fullSeqRight = JSONDict[prefix + "fullSeqRight"]

		except KeyError:
			raise Exception("Can't create a NamedSequence from this JSONDict.")
		
		return newSpacerData

	#setters
	def setFullSpacerSeqs(self):
		"""Set the SpacerData's full left sequence and full right sequence."""
		self.__fullSeqLeft = self.getSpacerLeft() + self.getLeftNN() + SpacerData.start
		self.__fullSeqRight = SpacerData.end + self.getRightNN() + self.getSpacerRight()

	def setNN(self):
		"""Calculate and set the SpacerData's NN."""
		#randomly choose A, G, or C for all four N nucleotides 
		#technically, T is allowed in certain circumstances, but it is less
		#complicated to not allow T
		self.__leftNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])
		self.__rightNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])

	#complicated getters
	def __str__(self):
		retStr = "Spacers for position " + str(self.getPosition())
		if(self.getIsTerminal()):
			retStr += " is last element"
		else:
			retStr += " is middle element"
			
		retStr += "\nLeft:\n" + self.getSpacerLeft()
		retStr += "\nRight:\n" + self.getSpacerRight()
		retStr += "\nTerminal Letter: " + self.getTerminalLetter()
		return retStr

	#basic getters
	def getPosition(self):
		return self.__position 

	def getSpacerLeft(self):
		return self.__spacerLeft
	
	def getSpacerRight(self):
		return self.__spacerRight
	
	def getIsTerminal(self):
		return self.__isTerminal
	
	def getTerminalLetter(self):
		return self.__terminalLetter

	def getLeftNN(self):
		return self.__leftNN
	
	def getRightNN(self):
		return self.__rightNN

	def getFullSeqLeft(self):
		return self.getSpacerLeft() + self.getLeftNN() + SpacerData.start

	def getFullSeqRight(self):
		return SpacerData.end + self.getRightNN() + self.getSpacerRight()


class PrimerData:
        """PrimerData is a class used to store primer data before adding it to the database."""

        def __init__(self):
                """Empty initializer"""
                pass

        @classmethod
        def makeNew(cls, seq, TMgoal, TMrange):
                """Create a new PrimerData.

                PARAMETERS:
                        seq: string sequence of the component the primers are for
                        TMgoal: desired TM for the primers
                        TMrange: allowance for the TM. (The found TM will be within TMgoal ± TMrange)

                RETURNS:
                        newPrimerData: created PrimerData
                """
                #type checking
                if(type(seq) != str):
                        raise TypeError("seq not a string.")
                if(type(TMgoal) != int and type(TMgoal) != float):
                        raise TypeError("TMgoal not an int or float.")
                if(type(TMrange) != int and type(TMrange) != float):
                        raise TypeError("TMrange not an int or float")

                newPrimerData = cls()

                #calculate primers
                newPrimerData.findPrimers(seq, TMgoal, TMrange)
 
                return newPrimerData

        #json stuff
        def toJSON(self):
                """Returns a JSON-friendly version of the PrimerData."""
                return vars(self)

        @classmethod
        def fromJSON(cls, JSONDict):
                """Create a PrimerData from a JSON dict.

                PARAMETERS:
                        JSONDict: dictionary containing the relevant primer data information.

                RETURNS:
                        newPrimerData: created PrimerData

                RAISES:
                        Exception: if the JSONDict is lacking one of the necessary fields
                """
                newPrimerData = cls()

                prefix = "_PrimerData__" #used to get private fields

                try:
                        newPrimerData.__primersFound = JSONDict[prefix + "primersFound"]
                        newPrimerData.__seqLeft = JSONDict[prefix + "seqLeft"]
                        newPrimerData.__GCleft = JSONDict[prefix + "GCleft"]
                        newPrimerData.__TMleft = JSONDict[prefix + "TMleft"]
                        newPrimerData.__seqRight = JSONDict[prefix + "seqRight"]
                        newPrimerData.__GCright = JSONDict[prefix + "GCright"]
                        newPrimerData.__TMright = JSONDict[prefix + "TMright"]

                except KeyError:
                        raise Exception("Can't create a PrimerData from this JSONDict.")

                return newPrimerData

        @classmethod
        def makeNull(cls):
                """Create a null PrimerData, which is used when primers are not generated."""
                nullData = cls.makeNew("", 0, 0)
                nullData.__seqLeft = "Chose not to make primer."
                nullData.__seqRight = "Chose not to make primer."

                return nullData

        #various functions used to calculate primers and PrimerDatas
        def addSpacerSeqs(self, spacerData):
                """Add left and right spacer sequences to incorporate into primer sequences.

                PARAMETERS:
                        spacerData: SpacerData to use
                """
                if(type(spacerData) != SpacerData):
                        raise TypeError("spacerData not a SpacerData")

                if(self.getPrimersFound()):
                        #modify the PrimerData's left and right sequences to include the spacers
                        self.__seqLeft = spacerData.getFullSeqLeft() + self.getLeftSeq()
                        self.__seqRight = self.getRightSeq() + spacerData.getFullSeqRight()

                        #invert the right primer, so it is the proper 5'-3' complementary
                        #strand to the component
                        self.invertRightPrimer()

        def invertRightPrimer(self):
                """Replace the right primer with its inverse sequence."""
                self.__seqRight = inverseSeq(self.getRightSeq())

        def findPrimers(self, seq, TMgoal, TMrange):
                """Find primers and assign them to self.

                PARAMETERS:
                        seq: string sequence of the component needing primers
                        TMgoal: number that is the preferred TM
                        TMrange: allowance for the TM, so the TM found is within TMgoal ± TMrange
                """
                if(TMgoal <= TMrange):
                        self.__primersFound = False

                else:
                        try:
                                #find the left primer
                                TML = 0
                                numAL = 0
                                numTL = 0
                                numGL = 0
                                numCL = 0
                                i = 0

                                while abs(TML - TMgoal) > TMrange:
                                        if seq[i] == "A":
                                                numAL +=1
                                        elif seq[i] == "T":
                                                numTL +=1
                                        elif seq[i] == "G":
                                                numGL +=1
                                        elif seq[i] == "C":
                                                numCL +=1

                                        try:
                                                TML = 64.9 + 41*(numGL + numCL - 16.4)/(numAL + numTL + numGL + numCL)
                                        except ZeroDivisionError:
                                                pass

                                        i += 1

                                #find the right primer
                                TMR = 0
                                numAR = 0
                                numTR = 0
                                numGR = 0
                                numCR = 0
                                j = -1

                                while abs(TMR - TMgoal) > TMrange:
                                        if seq[j] == "A":
                                                numAR +=1
                                        elif seq[j] == "T":
                                                numTR +=1
                                        elif seq[j] == "G":
                                                numGR +=1
                                        elif seq[j] == "C":
                                                numCR +=1

                                        try:
                                                TMR = 64.9 + 41*(numGR + numCR - 16.4)/(numAR + numTR + numGR + numCR)
                                        except ZeroDivisionError:
                                                pass

                                        j -= 1

                                #compare the two; if the primers overlap, they aren't valid
                                if(i + j > len(seq)):
                                        self.__primersFound = False

                                else:
                                        #assign properties if primers were found in the range
                                        self.__primersFound = True

                                        self.__seqLeft = seq[0:i]
                                        self.__GCleft = (numGL + numCL) / len(self.__seqLeft)
                                        self.__TMleft = TML

                                        self.__seqRight = seq[j:]
                                        self.__GCright = (numGR + numCR) / len(self.__seqRight)
                                        self.__TMright = TMR

                        except IndexError:
                                self.__primersFound = False

                if(not self.getPrimersFound()):
                        #assign properties if primers were not found in the range
                        self.__seqLeft = "Not found."
                        self.__GCleft = 0
                        self.__TMleft = 0

                        self.__seqRight = "Not found."
                        self.__GCright = 0
                        self.__TMright = 0

        #complex getters
        def __str__(self):
                if(self.getPrimersFound()):
                        tempGCleft = str(round(self.getGCleft() * 100, 4))
                        tempGCright = str(round(self.getGCright() * 100, 4))
                        tempTMleft = str(round(self.getTMleft(), 3))
                        tempTMright = str(round(self.getTMright(), 3))

                        retStr = "Left Primer: \nSequence: " + self.getLeftSeq() + "\nGC content: " + tempGCleft + "%\nTM: " + tempTMleft + "°C"
                        retStr += "\n\nRight Primer: \nSequence: " + self.getRightSeq() + "\nGC content: " + tempGCright + "%\nTM: " + tempTMright + "°C"
                else:
                        retStr = "No primers found."

                return retStr

        #basic getters
        def getPrimersFound(self):
                return self.__primersFound

        def getLeftSeq(self):
                return self.__seqLeft

        def getGCleft(self):
                return self.__GCleft

        def getTMleft(self):
                return self.__TMleft

        def getRightSeq(self):
                return self.__seqRight

        def getGCright(self):
                return self.__GCright

        def getTMright(self):
                return self.__TMright

nullPrimerData = PrimerData.makeNull()
