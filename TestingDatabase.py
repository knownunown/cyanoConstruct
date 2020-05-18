#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database testing
"""

#okay That's enough of that

email = "echidna"

s = SessionData(email)
u = UserData.load(email)
s.setUser(u)

s.makeFromNew("Pr", "promoter A", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCACAAAGTTTTCGTTACATAAAAATAGTGTCTACTTAGCTAAAAATTAAGGGTTTTTTACACCTTTTTGACAGTTAATCTCCTAGCCTAAAAAGCAAGAGTTTTTAACTAAGACTCTTGCCCTTTACAACCTC", 1, False, 55, 4)
s.makeFromNew("Pr", "promoter B", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCATAAGACTCTTGCCCTTTACAACCTC", 1, False, 55, 4)

print("getAllNS()")
print(s.getAllNS())
print("")

print("getAllComps()")
print(s.getAllComps())

ns1 = s.getAllNS()[0]
s.makeWithNamedSequence(ns1, 1, True, 55, 5)

compArray = []
for c in s.getAllComps():
    compArray.append(c)

for c in compArray:
    print(c.getName() + " " + str(c.getPosition()) + " " + c.getTerminalLetter())
    
s.getSortedComps()


allDefaultNS = s.getSortedNS()
#dict of all components
allAvailableNames = {}
allComponentsPosition = {}
validTerminals = {} #####<----- I would like to re-do this
posTerminalComb = []

#what do I need? the names of all seqs for each type
#the position of each seq for such
#if there are valid terminals for them

for typeKey in allDefaultNS.keys():
    allAvailableNames[typeKey] = []
    validTerminals[typeKey] = []
    
    #default library
    for ns in allDefaultNS[typeKey]:
        allAvailableNames[typeKey].append(ns.getName()) #add names
        
        allComponentsPosition[ns.getName()] = [] #add positions
        for comp in ns.components:
            if(comp.getPosition() not in allComponentsPosition[ns.getName()]): #add only if it's not already there
                allComponentsPosition[ns.getName()].append(comp.getPosition())
            
            #add terminals
            if((comp.getTerminal()) and (comp.getName() not in validTerminals[typeKey])):
                validTerminals[typeKey].append(comp.getName())            

    posTerminalComb.append([comp.getName(), str(comp.getPosition()),  str(comp.getTerminalLetter())])


print("names")
print(allAvailableNames)
print("posititons:")
print(allComponentsPosition)   
print("terminals:")
print(validTerminals)
