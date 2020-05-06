#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 17:31:45 2020

@author: liathomson
"""
import random
from jinja2 import Markup

class NamedSequence:

    #misc
    typeShortToLong = {"Pr": "promoter", "RBS": "ribosome binding site", "GOI": "gene of interest", "Term": "terminator"}
    #nextTotalID = {"default": 1}

    def __init__(self, NStype, NSname, NSseq, nameID):
        #type checking
        if(NStype not in ["Pr", "RBS", "GOI", "Term"]):
            raise ValueError("NStype not valid")
        if(type(NSname) != str):
            raise TypeError("NSmame not a string")
        if(type(NSseq) != str):
            raise TypeError("NSseq not a string")
        if(type(nameID) != int):
            raise TypeError("newID not an int")
                            
        #assign stuff
        self.__elemType = NStype
        self.__name = NSname
        self.__seq = NSseq                                    #assume sequence has been vetted
        self.__nameID = nameID
    
    def __str__(self):
        return ("Named Sequence.\nType: " + self.getType() + "\nName: " + self.getName() + 
                "\nName ID: " + str(self.getNameID()) + "\nSequence:\n" + self.getSeq())
        
    #getters
    def getType(self):
        return self.__elemType
        
    def getName(self):
        return self.__name
    
    def getSeq(self):
        return self.__seq
    
    def getNameID(self):
        return self.__nameID

        
    #def getTotalID(self):
    #    return self.__totalID
    
    #other stuff



class SpacerData:
    start = "GAAGAC" #enzyme recog. site?
    end = "GTCTTC"

    #spacers for elements 0 and T
    spacer0L = "AGGA"
    spacer0R = "AAAA"
    spacerTL = "ACTC"
    spacerTR = "TACA"
    
    #spacers, from highest allowed fidelity to lowest    
    spacers985 = [spacer0L, spacer0R]
    spacers981 = ["TAGA","GATA","ATTA"]
    spacers958 = ["CTAA", "TGAA", "CCAG", "CGGA", "CATA"]
    spacers917 = ["GGAA", "GCCA", "CACG", "CTTC", "TCAA", "ACTG", "AAGC", "GACC", "ATCG", "AGAG", "AGCA", "TGAA", "GTGA", "ACGA", "ATAC", "CAAG", "AAGG"]

    spacers = spacers985 + spacers981  + spacers958 + spacers917

    #max position for an element for a given fidelity
    max985 = 0
    max981 = len(spacers981)
    max958 = max981 + len(spacers958)
    max917 = max958 + len(spacers917) + 1

    @staticmethod
    def getMaxPosition():
        return len(SpacerData.spacers) - 1

    def __init__(self, position, isTerminal):
        #type checking
        if(type(position) != int):
            raise TypeError("position is not an int")
        if(type(isTerminal) != bool):
            raise TypeError("isTerminal is not a boolean")

        if(position == 999): #special position for terminator
            self.__spacerLeft = SpacerData.spacerTL
            self.__spacerRight = SpacerData.spacerTR
            
            self.__isTerminal = False #idk
            self.__terminalLetter = "T" #I. don't know what to put here

        #validation
        elif(position < 0 or position > SpacerData.getMaxPosition()):
            raise ValueError("Position out of bounds. (0-" + str(SpacerData.getMaxPosition()) + ")")
        
        elif(position == SpacerData.getMaxPosition() and not isTerminal):
            raise Exception("Position " + position + " must be terminal.")
        
        #most kinds of things
        else:
            #left
            self.__spacerLeft = SpacerData.spacers[position]
            
            #right
            if(isTerminal):
                self.__spacerRight = SpacerData.spacerTL
                self.__isTerminal = True
                self.__terminalLetter = "L" #L for last I suppose
                
            else:
                self.__spacerRight = SpacerData.spacers[position + 1]
                self.__isTerminal = False
                self.__terminalLetter = "M"
        
            if(position == 0):
                self.__terminalLetter = "S" #to indicate it's the start

        self.__position = position
        
        #set the NN on each side
        self.setNN()
        self.setFullSpacerSeqs()

    def setFullSpacerSeqs(self):
        self.__fullSeqLeft = self.getSpacerLeft() + self.getLeftNN() + SpacerData.start
        self.__fullSeqRight = SpacerData.end + self.getRightNN() +  self.getSpacerRight() #actually, I don't know if it's that simple or if complementary bases need to be found

    def setNN(self):
        #technically, T is allowed in certain circumstances, but that would require passing in
        #the element type, which would be a pain
        self.__leftNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])
        self.__rightNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])

    #complicated getters
    def __str__(self):
        retStr = "Spacers for position " + str(self.getPosition())
        if(self.getIsTerminal()):
            retStr += " is terminal"
        else:
            retStr += " is not terminal"
            
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
        return self.__fullSeqLeft

    def getFullSeqRight(self):
        return self.__fullSeqRight


class PrimerData:
    def __init__(self, seq, TMgoal, TMrange):
        #type checking
        if(type(seq) != str):
            raise TypeError("seq not a string.")
        if(type(TMgoal) != int and type(TMgoal) != float):
            raise TypeError("TMgoal not an int or float.")
        if(type(TMrange) != int and type(TMrange) != float):
            raise TypeError("TMrange not an int or float")
        
        #get the primers
        self.findPrimers(seq, TMgoal, TMrange)
    
    @classmethod
    def makeNull(cls):
        nullData = cls("", 0, 0)
        nullData.__seqLeft = "Chose not to make primer."
        nullData.__seqRight = "Chose not to make primer."
        
        return nullData
    
    def addSpacerSeqs(self, spacerData):
        if(type(spacerData) != SpacerData):
            raise TypeError("spacerData not a SpacerData")
            
        #add them; again, complementary, inversion, etc. needed somewhere, I just don't know where
        self.__seqLeft = spacerData.getFullSeqLeft() + self.getSeqLeft()

        self.__seqRight = self.getSeqRight() + spacerData.getFullSeqRight() 
    
    def findPrimers(self, seq, TMgoal, TMrange):
        if(TMgoal <= TMrange):
            self.__primersFound = False
        
        else:
            try:
                #left primer
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
                        
                    TML = 64.9 + 41*(numGL + numCL - 16.4)/(numAL + numTL + numGL + numCL)
                    
                    i += 1
                        
                #right primer
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
    
                    TMR = 64.9 + 41*(numGR + numCR - 16.4)/(numAR + numTR + numGR + numCR)
    
                    j -= 1
            
                #compare the two
                if(i + j > len(seq)):
                    self.__primersFound = False
                    
                else:
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
            self.__seqLeft = "Not found."
            self.__GCleft = 0
            self.__TMleft = 0
            
            self.__seqRight = "Not found."
            self.__GCright = 0
            self.__TMright = 0

    def __str__(self):
        if(self.getPrimersFound()):
            tempGCleft = str(round(self.getGCleft() * 100, 4))
            tempGCright = str(round(self.getGCright() * 100, 4))
            tempTMleft = str(round(self.getTMleft(), 3))
            tempTMright = str(round(self.getTMright(), 3))
            
            retStr = "Left Primer: \nSequence: " + self.getSeqLeft() + "\nGC content: " + tempGCleft + "%\nTM: " + tempTMleft + "°C"
            retStr += "\n\nRight Primer: \nSequence: " + self.getSeqRight() + "\nGC content: " + tempGCright + "%\nTM: " + tempTMright + "°C"
        else:
            retStr = "No primers found."
        
        return retStr
    
    #basic getters
    def getPrimersFound(self):
        return self.__primersFound
    
    def getSeqLeft(self):
        return self.__seqLeft
    
    def getGCleft(self):
        return self.__GCleft
    
    def getTMleft(self):
        return self.__TMleft
    
    def getSeqRight(self):
        return self.__seqRight
    
    def getGCright(self):
        return self.__GCright
    
    def getTMright(self):
        return self.__TMright





class Component:
    start = "GAAGAC" #enzyme recog. site?
    end = "GTCTTC"
    
    nextTotalID = 1
    
    #standard init, requires NamedSequence, SpacerData, and PrimerData
    def __init__(self, namedSeq, spacerData, primerData):

        #type checking
        if(type(namedSeq) != NamedSequence):
            raise TypeError("namedSeq not a NamedSequence")
        if(type(spacerData) != SpacerData):
            raise TypeError("spacerData not a SpacerData")
        if(type(primerData) != PrimerData):
            raise TypeError("primerData not a PrimerData")
                            
        #assign
        self.__namedSeq = namedSeq
        self.__primerData = primerData
        self.__spacerData = spacerData
                
        #total ID—-necessary?
        self.__totalID = Component.nextTotalID
        Component.nextTotalID += 1

        #generate NN & ID        
        #self.setNN()
        self.setID()

    #does not require a NamedSequence, SpacerData, or PrimerData to create the component
    @staticmethod
    def makeFromNew(elemType, name, seq, position, isTerminal, TMgoal, TMrange):
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
        newNamedSequence = NamedSequence(elemType, name, seq)
        newSpacerData = SpacerData(position, isTerminal)
        newPrimerData = PrimerData(seq, TMgoal, TMrange)
        
        #make the component
        newComponent = Component(newNamedSequence, newSpacerData, newPrimerData) #or such
        return (newComponent, newNamedSequence)
    
    #requires a NamedSequence, but not a SpacerData or PrimerData to create the component
    @staticmethod
    def makeWithNamedSeq(namedSequence, position, isTerminal, TMgoal, TMrange):
        #type checking
        if(type(namedSequence) != NamedSequence):
            raise TypeError("namedSequence not a NamedSequence")
        if(type(position) != int):
            raise TypeError("position not an int")
        if(type(isTerminal) != bool):
            raise TypeError("isTerminal is not a bool")
        if(type(TMgoal) != int and type(TMgoal) != float):
            raise TypeError("TMgoal not an int or float")
        if(type(TMrange) != int and type(TMrange) != float):
            raise TypeError("TMrange not an int or float")
            
        #spacer and primer data
        newSpacerData = SpacerData(position, isTerminal)
        newPrimerData = PrimerData(namedSequence.getSeq(), TMgoal, TMrange)
        
        #make the component
        newComponent = Component(namedSequence, newSpacerData, newPrimerData) #or such
        return newComponent

    #setters for initialization
    def setNN(self):
        if(self.getType() == "GOI"):
            self.__leftNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])
        else:
            self.__leftNN = random.choice(["A", "G", "C", "T"]) + random.choice(["A", "G", "C", "T"])
    
        if(self.getType() == "RBS"):
            self.__rightNN = random.choice(["A", "G", "C"]) + random.choice(["A", "G", "C"])
        else:
            self.__rightNN = random.choice(["A", "G", "C", "T"]) + random.choice(["A", "G", "C", "T"])
    
    def setID(self):
        nameID = self.getNamedSequence().getNameID()
        self.__idStr = self.getType() + "-" + str(nameID).zfill(3) + "-" + str(self.getPosition()).zfill(3) + self.getTerminalLetter()

    #complicated getters
    def getFullSeq(self):
        #return self.getLeftSpacer() + self.getLeftNN() + Component.start + self.getSeq() + Component.end + self.getRightNN() + self.getRightSpacer()
        return self.getFullSpacerLeft() + self.getSeq() + self.getFullSpacerRight()
    
    def getLongName(self):
        retStr = self.getType() + " " + self.getName() + " Position: " + str(self.getPosition())
        if(self.getTerminal()):
            retStr += " terminal"
        else:
            retStr += " non-terminal"
        
        return retStr

    def getHTMLdisplay(self):
        retStr = "ID: " + str(self.getID()) + "<br>"

        retStr += "Position: " + str(self.getPosition()) + "<br>"
        retStr += "Terminal?: " + str(self.getTerminal()) + "<br>"

        retStr += "<br><span class = 'emphasized'>Spacers:</span><br>"
        retStr += "Left: " + self.getLeftSpacer() + "<br>"
        retStr += "Right: " + self.getRightSpacer() + "<br>"
        
        retStr += "<br><span class = 'emphasized'>Primers:</span><br>"
        retStr += "Left primer:<br>GC content: " + str(round(self.getLeftGC() * 100, 4)) + "%<br>TM: " + str(round(self.getLeftTM(), 4)) + "<br>Sequence:<br>" + self.getLeftPrimer() + "<br><br>"
        retStr += "Right primer:<br>GC content: " + str(round(self.getRightGC() * 100, 4)) + "%<br>TM: " + str(round(self.getRightTM(), 4)) + "<br>Sequence:<br>" + self.getRightPrimer() + "<br>"

        return Markup(retStr)

    def __str__(self):
        retStr = "Name: " + self.getName() + "\n"
        retStr += "seq: " + self.getSeq() + "\n"
        retStr += "elemType: " + self.getType() + "\n"
        retStr += "terminal: " + str(self.getTerminal()) + "\n"
        retStr += "position: " + str(self.getPosition()) + "\n"
        retStr += "leftPrimer: " + self.getLeftPrimer() + "\n"
        retStr += "leftGC: " + str(self.getLeftGC()) + "\n"
        retStr += "leftTM: " + str(self.getLeftTM()) + "\n"
        retStr += "rightPrimer: " + self.getRightPrimer() + "\n"
        retStr += "rightGC: " + str(self.getRightGC()) + "\n"
        retStr += "rightTM: " + str(self.getRightTM()) + "\n"
        retStr += "leftSpacer: " + self.getLeftSpacer() + "\n"
        retStr += "rightSpacer: " + self.getRightSpacer() + "\n"
        retStr += "leftNN: " + self.getLeftNN() + "\n"
        retStr += "rightNN: " + self.getRightNN()
        return retStr
    
    def getCompZIP(self):
        #primers and complete sequence
        retDict = {}
        
        idStr = self.getID()
        idStrAndName = self.getID() + " (" + self.getName() + ")"
        
        retDict[idStr + "-CompleteSequence.fasta"] = ">" + idStrAndName + " complete sequence\n" + self.getFullSeq()
        retDict[idStr + "-LeftPrimer.fasta"] = ">" + idStrAndName + " left primer\n" + self.getLeftPrimer()
        retDict[idStr + "-RightPrimer.fasta"] = ">" + idStrAndName + " right primer\n" + self.getRightPrimer()
        
        return retDict
    
    #basic getters
    def getID(self):
        return self.__idStr


    def getNamedSequence(self):
        return self.__namedSeq
    
    def getName(self):
        return self.getNamedSequence().getName()
    
    def getSeq(self):
        return self.getNamedSequence().getSeq()
    
    def getType(self):
        return self.getNamedSequence().getType()

    
    def getSpacerData(self):
        return self.__spacerData

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


    def getPrimerData(self):
        return self.__primerData
    
    def getLeftPrimer(self):
        return self.getPrimerData().getSeqLeft()
    
    def getLeftGC(self):
        return self.getPrimerData().getGCleft()
    
    def getLeftTM(self):
        return self.getPrimerData().getTMleft()
    
    def getRightPrimer(self):
        return self.getPrimerData().getSeqRight()
    
    def getRightGC(self):
        return self.getPrimerData().getGCright()
    
    def getRightTM(self):
        return self.getPrimerData().getTMright()
    