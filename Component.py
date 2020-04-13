#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 17:31:45 2020

@author: liathomson
"""

#gross

#imported stuff: why not. You know. Actually import it.

def findsecondTM(seq, TMgoal):
    TM2 = 0
    numA = 0
    numT = 0
    numG = 0
    numC = 0
    i = -2 ## compensates for the "\n" at the end of elm. where did the \n come from???

    while TM2 - TMgoal > 1 or TM2 -TMgoal < -1: #oh I see, going backwards
        if seq[i] == "A":
            numA +=1
        elif seq[i] == "T":
            numT +=1
        elif seq[i] == "G":
            numG +=1
        elif seq[i] == "C":
            numC +=1
        TM2 = 64.9 + 41*(numG+numC-16.4)/(numA+numT+numG+numC)
        i -= 1
    gccontent2 = (numG +numC)/(len(seq[i:]))
    gccontent2 = round(gccontent2, 4) * 100
    gccontent2 = str(gccontent2)+" %"

    return(i, TM2, gccontent2)
    
def findTM(seq, TMgoal):
    try:
        TM = 0
        numA = 0
        numT = 0
        numG = 0
        numC = 0
        i = 0

        while TM - TMgoal > 1 or TM -TMgoal < -1:
            if seq[i] == "A":
                numA +=1
            elif seq[i] == "T":
                numT +=1
            elif seq[i] == "G":
                numG +=1
            elif seq[i] == "C":
                numC +=1
            TM = 64.9 + 41*(numG+numC-16.4)/(numA+numT+numG+numC)
            i += 1

        gccontent1 = (numG +numC)/(len(seq[0:i]))   #gc content is the gc content of the first i letters in the seq. (WHY?)
        gccontent1 = round(gccontent1, 4) * 100     #convert it to a pretty percentage
        gccontent1 = str(gccontent1)+" %"
        j, TM2, gccontent2 = findsecondTM(seq, TMgoal) #goes backwards through the seq. and gets the same stuff
        if i +j > len(seq):
            return("TM not possible", "No sequence possible","No GC %", "TM not possible", "No sequence possible", "No GC%")
        return(round(TM, 4), seq[0:i], gccontent1, round(TM2,4), seq[j:], gccontent2)
    except IndexError:
        seq = ''.join(seq)
        return("TM not possible", "No sequence possible", "", "", "", "")

#not imported
class Component:
    spacer0 = "TTTGCC" #seq. elem. 0 must always begin with
    spacerT = "GCAAGG" #seq. terminator must always end with

    #assume spacers is a fixed list from highest fidelity to lowest
    spacers = ['TGCC', 'GCAA', 'ACTA', 'TTAC', 'CAGA', 'TGTG', 'GAGC', 'AGGA', 'ATTC', 'CGAA', 'ATAG', "AAGG", "AAAA", "ACCG"]
    spacersFirst = [spacer0] + spacers #or so; offset from spacersFirst & with another one
    spacersEnd = spacers
    
    start = "GAAGAC" #enzyme recog. site?
    end = "GTCTTC"

    nextID = 1
    
    #except it needs to be sorted by type
    allPrevNames = {"Pr": [], "RBS": [], "GOI": [], "Term": []}
    nextNameIDs = {"Pr": 0, "RBS": 1, "GOI": 1, "Term": 0}
    
    def __init__(self, name, seq, elemType, terminal, position, TM, makeID = False, special = False):
        
        #type checking
        if(type(name) != str):
            raise TypeError("name not a string")
        if(type(seq) != str):
            raise TypeError("seq not a string")
        if(elemType not in ["Pr", "RBS", "GOI", "Term"]):
            raise TypeError("elemType not valid")
        if(type(terminal) != bool):
            raise TypeError("terminal not a boolean")
        if(type(position) != int):
            raise TypeError("position not an int")
        else:
            if(position <= 0 and not special):
                raise ValueError("position must be greater than 0")
        if(type(TM) != float):
            raise TypeError("TM not a float")
        
        if(special):
            if(special != "0" and special != "T"):
                raise ValueError("special not 0 or T")
        
        Component.allPrevNames[elemType].append(name)
        
        
        #assign basic stuff
        self.name = name
        self.seq = seq              #letters
        self.elemType = elemType    #RBS, Pr, Term, GOI
        self.terminal = terminal    #boolean
        
        if(terminal):
            self.terminalLetter = "T"
        else:
            self.terminalLetter = "M"
        
        self.position = position    #int
        self.TM = TM                #float
        
        #idk if I'll need this?
        self.idNum = Component.nextID
        Component.nextID += 1
        
        self.setPrimers()
        
        if(makeID):
            self.setID()
        
        if(special and special == "T"):
            self.leftSpacer = Component.spacersEnd[-1] #obviously this is Not Good Structure
            self.rightSpacer = Component.spacerT                
        else:
            self.setSpacers();
        
        #check if can get primers at desired TM?        

    def setPrimers(self):
        #copied/pasted from original code
        firstTM, firstseq, gccontent1, lastTM, lastseq, gccontent2 = findTM(self.seq, self.TM)

        self.leftPrimer = firstseq
        self.rightPrimer = lastseq
        self.leftGC = gccontent1
        self.rightGC = gccontent2
        self.leftTM = firstTM
        self.rightTM = lastTM
        
    def setSpacers(self):
        self.leftSpacer = Component.spacersFirst[self.position]
        if(self.terminal):
            self.rightSpacer = Component.spacersEnd[-1] #sub-optimal
        else:
            self.rightSpacer = Component.spacersEnd[self.position]

    def setID(self):        

        newName = True
        for i in range(len(Component.allPrevNames[self.elemType])):
            if(self.name == Component.allPrevNames[self.elemType][i]):
                newName = False
                self.idStr = self.elemType + "-" + str(i + 1).zfill(3) + "-" + str(self.position).zfill(3) + self.terminalLetter
                break
            
        if(newName):
            Component.allPrevNames[self.elemType].append(self.name)
            self.idStr = self.elemType + "-" + str(Component.nextNameID[self.elemType]).zfill(3) + "-" + str(self.position).zfill(3) + self.terminalLetter
            Component.nextNameIDs[self.elemType] += 1
            
    def getFullSeq(self):
        ret = self.leftSpacer + "NN" + Component.start + self.seq + Component.end + "NN" + self.rightSpacer
        return ret
    
    def getLongName(self):
        ret = self.elemType + " " + self.name + " Position: " + str(self.position)
        if(self.terminal):
            ret += " terminal"
        else:
            ret += " non-terminal"
        
        return ret
    
    def __str__(self):
        ret = "Name: " + self.name + "\n"
        ret += "seq: " + self.seq + "\n"
        ret += "elemType: " + self.elemType + "\n"
        ret += "terminal: " + str(self.terminal) + "\n"
        ret += "position: " + str(self.position) + "\n"
        ret += "TM: " + str(self.TM) + "\n"
        ret += "leftPrimer: " + self.leftPrimer + "\n"
        ret += "leftGC: " + str(self.leftGC) + "\n"
        ret += "leftTM: " + str(self.leftTM) + "\n"
        ret += "rightPrimer: " + self.rightPrimer + "\n"
        ret += "rightGC: " + str(self.rightGC) + "\n"
        ret += "rightTM: " + str(self.rightTM) + "\n"
        ret += "leftSpacer: " + self.leftSpacer + "\n"
        ret += "rightSpacer: " + self.rightSpacer
        return ret

