#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:54:27 2020

@author: Lia Thomson
"""
#get directory containing the cyanoConstruct module
import os
from sys import path as sysPath

sysPath.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#import cyanoConstruct stuff
#from cyanoConstruct import CyanoConstructMod as ccm
from cyanoConstruct import app
from cyanoConstruct.Component import NamedSequence, SpacerData, PrimerData, Component
from cyanoConstruct.SessionUsers import SessionData, AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError

#flask
from flask import request, render_template, jsonify, Response, session
#import json
#from jinja2 import Markup

#session stuff
from uuid import uuid1
from datetime import timedelta

#misc.
from ast import literal_eval as leval
from shutil import rmtree, make_archive
from string import ascii_letters, digits
#from copy import deepcopy

##########################################################################################
#globals
startEndComps = [None, None]

printActions = True

defaultSession = SessionData("default")

nullPrimerData = PrimerData.makeNull() #the PrimerData used if making primers is skipped

#sessions
allSessions = {}

haveLoaded = {}

##########################################################################################

def checkLoggedIn():
    return ("loggedIn" in session)

def redirectIfNotLoggedIn():
    if(not checkLoggedIn()):
        #uhhhh
        return

#sets sessionID if there isn't one
def checkSessionID():
    if("sessionID" not in session):
        newID = uuid1().hex
        session["sessionID"] = newID
        allSessions[newID] = SessionData(newID)

        if(printActions):
            print("new sessionID and SessionData")

    
    try:
        haveLoaded[session["sessionID"]]
        
    except KeyError:
        newID = session["sessionID"]
        
        allSessions[newID] = SessionData(newID)
        
        haveLoaded[newID] = True
        
    return session["sessionID"]

def getSessionData():
    return allSessions[checkSessionID()]

def addToSelected(newSelected):
    sessionData = getSessionData()
    
    if(type(newSelected) == NamedSequence):
        sessionData.setSelectedNS(newSelected)
    elif(type(newSelected) == SpacerData):
        sessionData.setSelectedSpacers(newSelected)
    elif(type(newSelected) == PrimerData):
        sessionData.setSelectedPrimers(newSelected)
    else:
        raise TypeError("can't add item of type " + type(newSelected))

"""
def addToSelected2(newSelected):
    global selectedDict
    if(type(newSelected) == NamedSequence):
        selectedDict["selectedNamedSequence"] = newSelected
    elif(type(newSelected) == SpacerData):
        selectedDict["selectedSpacers"] = newSelected
    elif(type(newSelected) == PrimerData):
        selectedDict["selectedPrimers"] = newSelected
    else:
        raise TypeError("can't add item of type " + type(newSelected))
"""

def addToZip(newFile, key):
    if(type(newFile) != dict):
        raise TypeError("newFile not a dict")

    sessionData = getSessionData()

    if(key == "newCompZip"):
        sessionData.setNewCompZip(newFile)
    elif(key == "assemblyZip"):
        sessionData.setAssemblyZip(newFile)
    elif(key == "componentForZip"):
        sessionData.setComponentForZip(newFile)
    else:
        raise ValueError("key not valid")

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
    
    submissionID = checkSessionID()
    
    #paths
    #auuuughhhh
    filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    print(filesDirPath)
    #filesDirPath = filePath.rsplit("/", 1)[0] + "/files"
    sessionDir = filesDirPath + "/" + submissionID
    
    os.mkdir(sessionDir)
    
    if(printActions):
        print("MADE DIRECTORY: " + sessionDir)    
    
    #write files
    for filename in filesDict:
        newName = sessionDir + "/" + filename
        with open(newName, "w") as f:
            f.write(filesDict[filename])
            
    #make zip
    zipPath = filesDirPath + "/zips/" + submissionID 
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

def flattenDicts(d):
    if(type(d) != dict):
        raise TypeError("d not a dict")
        
    ret = []
    flattenCompsFunc(d, ret)
    return ret

def flattenCompsFunc(d, array):
    #recursive function called by flattenDicts; should not be directly used
    for key in d:
        if(type(d[key]) == dict):
            flattenCompsFunc(d[key], array)
        else:
            array.append(d[key])

"""def addToComps(comp, allComps):
    try:
        #if there is already a comp in allComps with the same position (but different terminalLetter)
        allComps[comp.getType()][comp.getName()][comp.getPosition()][comp.getTerminalLetter()] = comp
        
    except KeyError:
        try:
            #if there is already a comp in allComps with the same name (but different position)
            allComps[comp.getType()][comp.getName()][comp.getPosition()] = {comp.getTerminalLetter(): comp}
            
        except KeyError:
            #if there is not already a comp in allComps with the same name
            allComps[comp.getType()][comp.getName()] = {comp.getPosition(): {comp.getTerminalLetter(): comp}}
"""

def addToComps(comp):
    sessionData = getSessionData()
    
    sessionData.addComp(comp)
    
def addToNS(NS):
    #allNS[NS.getType()][NS.getName()] = NS
    sessionData = getSessionData()
    
    sessionData.addNS(NS)

def addDefaultComp(comp):
    defaultSession.addComp(comp)

def addDefaultNS(NS):
    defaultSession.addNS(NS)

"""
def getDefaults():
    return (deepcopy(allNSdict["default"]), deepcopy(allCompsDict["default"]))
"""
"""
def makeDefaults(currentAllNamedSequences, currentAllComps):    
    promoterComp, promoterNamedSeq = Component.makeFromNew("Pr", "psbA", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCACAAAGTTTTCGTTACATAAAAATAGTGTCTACTTAGCTAAAAATTAAGGGTTTTTTACACCTTTTTGACAGTTAATCTCCTAGCCTAAAAAGCAAGAGTTTTTAACTAAGACTCTTGCCCTTTACAACCTC",
                                                                     0, False, 45.0, 2, "default")
    
    terminatorComp, terminatorNamedSeq = Component.makeFromNew("Term", "T1", "ATTTGTCCTACTCAGGAGAGCGTTCACCGACAAACAACAGATAAAACGAAAGGCCCAGTCTTTCGACTGAGCCTTTCGTTTTATTTG",
                                                                         999, False, 45.0, 2, "default")
    
    addToComps(promoterComp, currentAllComps)
    addToComps(terminatorComp, currentAllComps)
    addToNS(promoterNamedSeq, currentAllNamedSequences)
    addToNS(terminatorNamedSeq, currentAllNamedSequences)
    
    global startEndComps
    startEndComps[0] = promoterComp
    startEndComps[1] = terminatorComp
"""
def makeDefaults():    
    promoterComp, promoterNamedSeq = defaultSession.makeFromNew("Pr", "psbA", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCACAAAGTTTTCGTTACATAAAAATAGTGTCTACTTAGCTAAAAATTAAGGGTTTTTTACACCTTTTTGACAGTTAATCTCCTAGCCTAAAAAGCAAGAGTTTTTAACTAAGACTCTTGCCCTTTACAACCTC",
                                                                     0, False, 45.0, 2)
    
    terminatorComp, terminatorNamedSeq = defaultSession.makeFromNew("Term", "T1", "ATTTGTCCTACTCAGGAGAGCGTTCACCGACAAACAACAGATAAAACGAAAGGCCCAGTCTTTCGACTGAGCCTTTCGTTTTATTTG",
                                                                         999, False, 45.0, 2)
    #addDefaultComp(promoterComp)
    #addDefaultComp(terminatorComp)
    
    #addDefaultNS(promoterNamedSeq)
    #addDefaultNS(terminatorNamedSeq)
    
    #consider using some other way to do this
    global startEndComps
    startEndComps[0] = promoterComp
    startEndComps[1] = terminatorComp

def makeMore():
    
    S3, S3NS = defaultSession.makeFromNew("RBS", "S3", "AGTCAAGTAGGAGATTAATTCAATG",
                                               1, False, 45.0, 2)
    
    A, ANS = defaultSession.makeFromNew("RBS", "A", "AACAAAATGAGGAGGTACTGAGATG",
                                             1, False, 45.0, 2)
        
    adh2, adhNS = defaultSession.makeFromNew("GOI", "adh", "ATGCATATTAAAGCCTACGCTGCCCTGGAAGCCAACGGAAAACTCCAACCCTTTGAATACGACCCCGGTGCCCTGGGTGCTAATGAGGTGGAGATTGAGGTGCAGTATTGTGGGGTGTGCCACAGTGATTTGTCCATGATTAATAACGAATGGGGCATTTCCAATTACCCCCTAGTGCCGGGTCATGAGGTGGTGGGTACTGTGGCCGCCATGGGCGAAGGGGTGAACCATGTTGAGGTGGGGGATTTAGTGGGGCTGGGTTGGCATTCGGGCTACTGCATGACCTGCCATAGTTGTTTATCTGGCTACCACAACCTTTGTGCCACGGCGGAATCGACCATTGTGGGCCACTACGGTGGCTTTGGCGATCGGGTTCGGGCCAAGGGAGTCAGCGTGGTGAAATTACCTAAAGGCATTGACCTAGCCAGTGCCGGGCCCCTTTTCTGTGGAGGAATTACCGTTTTCAGTCCTATGGTGGAACTGAGTTTAAAGCCCACTGCAAAAGTGGCAGTGATCGGCATTGGGGGCTTGGGCCATTTAGCGGTGCAATTTCTCCGGGCCTGGGGCTGTGAAGTGACTGCCTTTACCTCCAGTGCCAGGAAGCAAACGGAAGTGTTGGAATTGGGCGCTCACCACATACTAGATTCCACCAATCCAGAGGCGATCGCCAGTGCGGAAGGCAAATTTGACTATATTATCTCCACTGTGAACCTGAAGCTTGACTGGAACTTATACATCAGCACCCTGGCGCCCCAGGGACATTTCCACTTTGTTGGGGTGGTGTTGGAGCCTTTGGATCTAAATCTTTTTCCCCTTTTGATGGGACAACGCTCCGTTTCTGCCTCCCCAGTGGGTAGTCCCGCCACCATTGCCACCATGTTGGACTTTGCTGTGCGCCATGACATTAAACCCGTGGTGGAACAATTTAGCTTTGATCAGATCAACGAGGCGATCGCCCATCTAGAAAGCGGCAAAGCCCATTATCGGGTAGTGCTCAGCCATAGTAAAAATTAG",
                                                  2, False, 45.0, 2)
    adh3 = Component.makeWithNamedSeq(adhNS, 2, True, 45.0, 2)
        
    pdc, pdcNS = defaultSession.makeFromNew("GOI", "pdc", "ATGCATAGTTATACTGTCGGTACCTATTTAGCGGAGCGGCTTGTCCAGATTGGTCTCAAGCATCACTTCGCAGTCGCGGGCGACTACAACCTCGTCCTTCTTGACAACCTGCTTTTGAACAAAAACATGGAGCAGGTTTATTGCTGTAACGAACTGAACTGCGGTTTCAGTGCAGAAGGTTATGCTCGTGCCAAAGGCGCAGCAGCAGCCGTCGTTACCTACAGCGTTGGTGCGCTTTCCGCATTTGATGCTATCGGTGGCGCCTATGCAGAAAACCTTCCGGTTATCCTGATCTCCGGTGCTCCGAACAACAACGACCACGCTGCTGGTCATGTGTTGCATCATGCTCTTGGCAAAACCGACTATCACTATCAGTTGGAAATGGCCAAGAACATCACGGCCGCCGCTGAAGCGATTTACACCCCGGAAGAAGCTCCGGCTAAAATCGATCACGTGATCAAAACTGCTCTTCGCGAGAAGAAGCCGGTTTATCTCGAAATCGCTTGCAACACTGCTTCCATGCCCTGCGCCGCTCCTGGACCGGCAAGTGCATTGTTCAATGACGAAGCCAGCGACGAAGCATCCTTGAATGCAGCGGTTGACGAAACCCTGAAATTCATCGCCAACCGCGACAAAGTTGCCGTCCTCGTCGGCAGCAAGCTGCGCGCTGCTGGTGCTGAAGAAGCTGCTGTTAAATTCACCGACGCTTTGGGCGGTGCAGTGGCTACTATGGCTGCTGCCAAGAGCTTCTTCCCAGAAGAAAATGCCAATTACATTGGTACCTCATGGGGCGAAGTCAGCTATCCGGGCGTTGAAAAGACGATGAAAGAAGCCGATGCGGTTATCGCTCTGGCTCCTGTCTTCAACGACTACTCCACCACTGGTTGGACGGATATCCCTGATCCTAAGAAACTGGTTCTCGCTGAACCGCGTTCTGTCGTTGTCAACGGCATTCGCTTCCCCAGCGTTCATCTGAAAGACTATCTGACCCGTTTGGCTCAGAAAGTTTCCAAGAAAACCGGTTCTTTGGACTTCTTCAAATCCCTCAATGCAGGTGAACTGAAGAAAGCCGCTCCGGCTGATCCGAGTGCTCCGTTGGTCAACGCAGAAATCGCCCGTCAGGTCGAAGCTCTTCTGACCCCGAACACGACGGTTATTGCTGAAACCGGTGACTCTTGGTTCAATGCTCAGCGCATGAAGCTCCCGAACGGTGCTCGCGTTGAATATGAAATGCAGTGGGGTCACATTGGTTGGTCCGTTCCTGCCGCCTTCGGTTATGCCGTCGGTGCTCCGGAACGTCGCAACATCCTCATGGTTGGTGATGGTTCCTTCCAGCTGACGGCTCAGGAAGTTGCTCAGATGGTTCGCCTGAAACTGCCGGTTATCATCTTCTTGATCAATAACTATGGTTACACCATCGAAGTTATGATCCATGATGGTCCGTACAACAACATCAAGAACTGGGATTATGCCGGTCTGATGGAAGTGTTCAACGGTAACGGTGGTTATGACAGCGGTGCTGCTAAAGGCCTGAAGGCTAAAACCGGTGGCGAACTGGCAGAAGCTATCAAGGTTGCTCTGGCAAACACCGACGGCCCAACCCTGATCGAATGCTTCATCGGTCGTGAAGACTGCACTGAAGAATTGGTCAAATGGGGTAAGCGCGTTGCTGCCGCCAACAGCCGTAAGCCTGTTAACAAGCTCCTCTAG",
                                                 3, True, 45.0, 2)
    
    #addDefaultComp(S3)
    #addDefaultComp(A)
    #addDefaultComp(adh2)
    addDefaultComp(adh3)
    #addDefaultComp(pdc)

    #addDefaultNS(S3NS)
    #addDefaultNS(ANS)
    #addDefaultNS(adhNS)
    #addDefaultNS(pdcNS)

makeDefaults()
makeMore()

"""
def makeMore(currentAllNamedSequences, currentAllComps):
    
    S3, S3NS = Component.makeFromNew("RBS", "S3", "AGTCAAGTAGGAGATTAATTCAATG",
                                               1, False, 45.0, 2, "default")
    
    A, ANS = Component.makeFromNew("RBS", "A", "AACAAAATGAGGAGGTACTGAGATG",
                                             1, False, 45.0, 2, "default")
        
    adh2, adhNS = Component.makeFromNew("GOI", "adh", "ATGCATATTAAAGCCTACGCTGCCCTGGAAGCCAACGGAAAACTCCAACCCTTTGAATACGACCCCGGTGCCCTGGGTGCTAATGAGGTGGAGATTGAGGTGCAGTATTGTGGGGTGTGCCACAGTGATTTGTCCATGATTAATAACGAATGGGGCATTTCCAATTACCCCCTAGTGCCGGGTCATGAGGTGGTGGGTACTGTGGCCGCCATGGGCGAAGGGGTGAACCATGTTGAGGTGGGGGATTTAGTGGGGCTGGGTTGGCATTCGGGCTACTGCATGACCTGCCATAGTTGTTTATCTGGCTACCACAACCTTTGTGCCACGGCGGAATCGACCATTGTGGGCCACTACGGTGGCTTTGGCGATCGGGTTCGGGCCAAGGGAGTCAGCGTGGTGAAATTACCTAAAGGCATTGACCTAGCCAGTGCCGGGCCCCTTTTCTGTGGAGGAATTACCGTTTTCAGTCCTATGGTGGAACTGAGTTTAAAGCCCACTGCAAAAGTGGCAGTGATCGGCATTGGGGGCTTGGGCCATTTAGCGGTGCAATTTCTCCGGGCCTGGGGCTGTGAAGTGACTGCCTTTACCTCCAGTGCCAGGAAGCAAACGGAAGTGTTGGAATTGGGCGCTCACCACATACTAGATTCCACCAATCCAGAGGCGATCGCCAGTGCGGAAGGCAAATTTGACTATATTATCTCCACTGTGAACCTGAAGCTTGACTGGAACTTATACATCAGCACCCTGGCGCCCCAGGGACATTTCCACTTTGTTGGGGTGGTGTTGGAGCCTTTGGATCTAAATCTTTTTCCCCTTTTGATGGGACAACGCTCCGTTTCTGCCTCCCCAGTGGGTAGTCCCGCCACCATTGCCACCATGTTGGACTTTGCTGTGCGCCATGACATTAAACCCGTGGTGGAACAATTTAGCTTTGATCAGATCAACGAGGCGATCGCCCATCTAGAAAGCGGCAAAGCCCATTATCGGGTAGTGCTCAGCCATAGTAAAAATTAG",
                                                  2, False, 45.0, 2, "default")
    adh3 = Component.makeWithNamedSeq(adhNS, 2, True, 45.0, 2)
        
    pdc, pdcNS = Component.makeFromNew("GOI", "pdc", "ATGCATAGTTATACTGTCGGTACCTATTTAGCGGAGCGGCTTGTCCAGATTGGTCTCAAGCATCACTTCGCAGTCGCGGGCGACTACAACCTCGTCCTTCTTGACAACCTGCTTTTGAACAAAAACATGGAGCAGGTTTATTGCTGTAACGAACTGAACTGCGGTTTCAGTGCAGAAGGTTATGCTCGTGCCAAAGGCGCAGCAGCAGCCGTCGTTACCTACAGCGTTGGTGCGCTTTCCGCATTTGATGCTATCGGTGGCGCCTATGCAGAAAACCTTCCGGTTATCCTGATCTCCGGTGCTCCGAACAACAACGACCACGCTGCTGGTCATGTGTTGCATCATGCTCTTGGCAAAACCGACTATCACTATCAGTTGGAAATGGCCAAGAACATCACGGCCGCCGCTGAAGCGATTTACACCCCGGAAGAAGCTCCGGCTAAAATCGATCACGTGATCAAAACTGCTCTTCGCGAGAAGAAGCCGGTTTATCTCGAAATCGCTTGCAACACTGCTTCCATGCCCTGCGCCGCTCCTGGACCGGCAAGTGCATTGTTCAATGACGAAGCCAGCGACGAAGCATCCTTGAATGCAGCGGTTGACGAAACCCTGAAATTCATCGCCAACCGCGACAAAGTTGCCGTCCTCGTCGGCAGCAAGCTGCGCGCTGCTGGTGCTGAAGAAGCTGCTGTTAAATTCACCGACGCTTTGGGCGGTGCAGTGGCTACTATGGCTGCTGCCAAGAGCTTCTTCCCAGAAGAAAATGCCAATTACATTGGTACCTCATGGGGCGAAGTCAGCTATCCGGGCGTTGAAAAGACGATGAAAGAAGCCGATGCGGTTATCGCTCTGGCTCCTGTCTTCAACGACTACTCCACCACTGGTTGGACGGATATCCCTGATCCTAAGAAACTGGTTCTCGCTGAACCGCGTTCTGTCGTTGTCAACGGCATTCGCTTCCCCAGCGTTCATCTGAAAGACTATCTGACCCGTTTGGCTCAGAAAGTTTCCAAGAAAACCGGTTCTTTGGACTTCTTCAAATCCCTCAATGCAGGTGAACTGAAGAAAGCCGCTCCGGCTGATCCGAGTGCTCCGTTGGTCAACGCAGAAATCGCCCGTCAGGTCGAAGCTCTTCTGACCCCGAACACGACGGTTATTGCTGAAACCGGTGACTCTTGGTTCAATGCTCAGCGCATGAAGCTCCCGAACGGTGCTCGCGTTGAATATGAAATGCAGTGGGGTCACATTGGTTGGTCCGTTCCTGCCGCCTTCGGTTATGCCGTCGGTGCTCCGGAACGTCGCAACATCCTCATGGTTGGTGATGGTTCCTTCCAGCTGACGGCTCAGGAAGTTGCTCAGATGGTTCGCCTGAAACTGCCGGTTATCATCTTCTTGATCAATAACTATGGTTACACCATCGAAGTTATGATCCATGATGGTCCGTACAACAACATCAAGAACTGGGATTATGCCGGTCTGATGGAAGTGTTCAACGGTAACGGTGGTTATGACAGCGGTGCTGCTAAAGGCCTGAAGGCTAAAACCGGTGGCGAACTGGCAGAAGCTATCAAGGTTGCTCTGGCAAACACCGACGGCCCAACCCTGATCGAATGCTTCATCGGTCGTGAAGACTGCACTGAAGAATTGGTCAAATGGGGTAAGCGCGTTGCTGCCGCCAACAGCCGTAAGCCTGTTAACAAGCTCCTCTAG",
                                                 3, True, 45.0, 2, "default")
    
    addToComps(S3, currentAllComps)
    addToComps(A, currentAllComps)
    addToComps(adh2, currentAllComps)
    addToComps(adh3, currentAllComps)
    addToComps(pdc, currentAllComps)

    addToNS(S3NS, currentAllNamedSequences)
    addToNS(ANS, currentAllNamedSequences)
    addToNS(adhNS, currentAllNamedSequences)
    addToNS(pdcNS, currentAllNamedSequences)
    
#load with some defaults
#makeDefaults(currentAllNamedSequences, currentAllComps)
#makeMore(currentAllNamedSequences, currentAllComps)

makeDefaults(allNSdict["default"], allCompsDict["default"])
makeMore(allNSdict["default"], allCompsDict["default"])
"""



##############################     DOMESTICATION     ##############################
###################################################################################

#the page for domestication
@app.route("/domesticate", methods = ["POST", "GET"], endpoint = "domesticate")
def domesticate():
    sessionData = getSessionData()
    sessionNamedSequences = sessionData.getAllNS()
    defaultNamedSequences = defaultSession.getAllNS()
    
    #make the named sequences more friendly to javascript
    NSNamesJSONifiable = {}
    NSSequencesJSONifiable = {}
    
    #defaults first
    for typeKey in defaultNamedSequences.keys():
        NSNamesJSONifiable[typeKey] = [] 
        
        for NSName in defaultNamedSequences[typeKey]:
            NSNamesJSONifiable[typeKey].append(NSName)
            
            NSSequencesJSONifiable[NSName] = defaultNamedSequences[typeKey][NSName].getSeq()

    #user-made second
        
        for NSName in sessionNamedSequences[typeKey]:
            if(NSName not in NSNamesJSONifiable[typeKey]): #will not duplicate if it's actually a default NS
                NSNamesJSONifiable[typeKey].append(NSName)
                
                NSSequencesJSONifiable[NSName] = sessionNamedSequences[typeKey][NSName].getSeq()

    
    return render_template("domesticate.html", namedSequencesNames = NSNamesJSONifiable,
                           namedSequencesSequences = NSSequencesJSONifiable)

#make a new NamedSequence
@app.route("/newNamedSeq", methods = ["POST"])
def newNamedSeq():
    #get data
    newNSData = leval(request.form["newNSData"])

    newNSType = newNSData["NStype"]
    newNSName = newNSData["NSname"]
    newNSSeq = newNSData["NSseq"].upper()

    #validation
    outputStr = ""
    validInput = True
    succeeded = False

    #type
    if(type(newNSType) != type(newNSName) != type(newNSSeq) != str):
        validInput = False
        outputStr += "ERROR: input received not all strings.<br>"
    
    #validate type
    if(newNSType not in ["Pr", "RBS", "GOI", "Term"]):
        validInput = False
        outputStr += "ERROR: '" + newNSType + "' is not a valid type.<br>"
    
    #validate name
    #length
    if(len(newNSName) < 1 or len(newNSName) > 20):
        validInput = False
        outputStr += "ERROR: Sequence name must be 1-20 characters.<br>"
    
    #check if it already exists in default:
    for elemType in ["Pr", "RBS", "GOI", "Term"]:
        longNames = {"Pr": "promoter", "RBS": "ribosome binding site", "GOI": "gene", "Term": "terminator"}
        try:
            defaultSession.findNamedSequence(elemType, newNSName, newNSSeq)
                        
            validInput = False
            outputStr += "ERROR: " + newNSName + " already exists in the default library as a " + longNames[elemType] + ".<br>"
            break
        except SequenceMismatchError:
            validInput = False
            outputStr += "ERROR: " + newNSName + " already exists in the default library as a " + longNames[elemType] + ".<br>"
            break
        except SequenceNotFoundError:
            pass

    
    #characters
    validCharacters = ascii_letters + digits + "_-."
    
    invalidCharactersName = []
    
    for character in newNSName:
        if(character not in validCharacters and character not in invalidCharactersName):
            validInput = False
            outputStr += "ERROR: '" + character + "' is not allowed in a sequence's name.<br>"
            invalidCharactersName.append(character)

    #validate sequence
    #length
    if(len(newNSSeq) < 1 or len(newNSSeq) > 99999): #I don't know what limits should be used
        validInput = False
        outputStr += "ERROR: Sequence must be 1-99999 nucleotides.<br>"
    
    #characters/nucleotides
    validNucleotides = "AGTCBDHKMNRSVWY"
    
    invalidCharactersSeq = []
    for character in newNSSeq.upper():
        if((character not in validNucleotides) and (character not in invalidCharactersSeq)):
            validInput = False
            outputStr += "ERROR: '" + character + "' is not an allowed nucleotide.<br>"
            invalidCharactersSeq.append(character)
    
    #finish validation
    if(validInput):
        try:
            getSessionData().createNS(newNSType, newNSName, newNSSeq)
            #newNamedSeq = NamedSequence(newNSType, newNSName, newNSSeq)
            #addToNS(newNamedSeq)
            outputStr += "Successfully created sequence " + newNSName + "."
            
            succeeded = True
            
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"
            
    if(not succeeded):
        outputStr += "Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#in order to set it to the global
@app.route("/findNamedSeq", methods = ["POST"])
def findNamedSeq():
    #sessionID = checkSessionID()
    sessionData = getSessionData()
    #get data
    namedSeqData = leval(request.form["namedSeqData"])
        
    NStype = namedSeqData["NStype"]
    NSname = namedSeqData["NSname"]
    NSseq = namedSeqData["NSseq"]

    try:
        #search for it
        #foundNamedSequence = NamedSequence.findNamedSequence(NStype, NSname, NSseq, sessionID)
        try:        #search default first
            foundNamedSequence = defaultSession.findNamedSequence(NStype, NSname, NSseq)
        except Exception:
            foundNamedSequence = sessionData.findNamedSequence(NStype, NSname, NSseq)
        
        #add to session selected
        addToSelected(foundNamedSequence)
        
        outputStr = ""
        
        succeeded = True
    
    except Exception as e:
        outputStr = "ERROR: " + str(e)
        succeeded = False
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#really, it's making spacers
@app.route("/findSpacers", methods = ["POST"])
def findSpacers():
    #get data
    spacersData = leval(request.form["spacersData"])
    
    newPosStr = spacersData["componentPos"]
    newTerminalStr = spacersData["isTerminal"]
    
    #validation
    outputStr = ""
    validInput = True
    succeeded = False

    #position
    try:
        newPos = int(newPosStr)
    except Exception:
        validInput = False
        outputStr += "ERROR: position not an integer.<br>"
    
    #position
    maxPosition = SpacerData.getMaxPosition()
    
    if(validInput):            
        if((newPos <= 0) or (newPos > maxPosition)):
            validInput = False
            outputStr += "ERROR: Position must be in range 1-" + str(maxPosition) + ".<br>"
                        
    #isTerminal
    if(newTerminalStr == "false"):  #because JavaScript uses true & false in all lower-case
        isTerminal = False          #but Python capitlizes them
    elif(newTerminalStr == "true"):
        isTerminal = True
    else:
        validInput = False
        outputStr += "ERROR: Terminal??? not valid.<br>"

    #if the position is the maximum allowed position, it must be terminal
    if(validInput and (newPos == maxPosition) and (not isTerminal)):
        validInput = False
        outputStr += "ERROR: " + str(newPos) + " is the last allowed position, so it must be terminal.<br>"
    
    #obtain the actual spacers
    if(validInput):
        try:
            #make the SpacerData
            newSpacerData = SpacerData(newPos, isTerminal)
            
            #add to outputStr
            outputStr += "Spacers found for position " + str(newPos)
            if(isTerminal):
                outputStr += " last element:"
            else:
                outputStr += " not last element:"
            outputStr += "<br>Left spacer: " + newSpacerData.getSpacerLeft() + "<br>Right spacer: " + newSpacerData.getSpacerRight()
            outputStr += "<br>Should the randomly generated 2 nucleotides also be included here?"
            
            #add to current session
            addToSelected(newSpacerData)
            
            succeeded = True
            
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"
            
    if(not succeeded):
        outputStr += "Spacers not found."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#make PrimerData
@app.route("/findPrimers", methods = ["POST"])
def findPrimers():
    #get form data
    primersData = leval(request.form["primersData"])

    outputStr = ""
    validInput = True
    succeeded = False
    
    TMstr = primersData["meltingPoint"]
    rangeStr = primersData["meltingPointRange"]
    if(primersData["skipPrimers"] == "true"):
        skipPrimers = True
    elif(primersData["skipPrimers"] == "false"):
        skipPrimers = False
    else:
        validInput = False
        outputStr += "ERROR: Skip primers value not true or false.<br>"
    
    #skip primers if so
    if(skipPrimers):
        outputStr += "Chose not to make primers.<br>"
        addToSelected(nullPrimerData)
        
        succeeded = True
        
        
    else:
        #that thrilling data validation
        
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
        
        #is there a spacer selected
        selectedSpacers = getSessionData().getSelectedSpacers()
        if(selectedSpacers == None):
            validInput = False
            outputStr += "ERROR: No spacers selected."
        
        #find the primers
        if(validInput):
            try:
                seqToEvaluate = getSessionData().getSelectedNS().getSeq()
                newPrimerData = PrimerData(seqToEvaluate, TMnum, rangeNum)
                newPrimerData.addSpacerSeqs(selectedSpacers)
                
                if(newPrimerData.getPrimersFound()): #returns False if no primers, a string otherwise
                    #outputStr
                    outputStr += str(newPrimerData).replace("\n", "<br>")
                    
                    #add to session selected
                    addToSelected(newPrimerData)
                    
                    succeeded = True
                    
                else:
                    outputStr += "Couldn't find primers for the specified sequence, melting point & range.<br>"
            
            except Exception as e:
                outputStr += "ERROR: " + str(e) + "<br>"
    
        if(not succeeded):
            outputStr += "Primers not found."
        
    return jsonify({"output": outputStr, "succeeded": succeeded})

#actually creates the component
@app.route("/finishDomestication", methods = ["POST"])
def finishDomestication():
    #validation
    validInput = getSessionData().getAllSelected()
    #validInput = (selectedDict["selectedNamedSequence"] != None and selectedDict["selectedPrimers"] != None and selectedDict["selectedSpacers"] != None)
    succeeded = False
    
    outputStr = ""
    
    if(validInput):
        try:
            #make the component
            #augh.
            sessionData = getSessionData()
            selectedNS = sessionData.getSelectedNS()
            selectedSpacers = sessionData.getSelectedSpacers()
            selectedPrimers = sessionData.getSelectedPrimers()
            
            #check if it already exists in defaults
            try:
                defaultSession.findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise Exception("Component already exists as a default component.")
            except KeyError:
                pass
            
            #check if it already exists in personal library
            try:
                getSessionData().findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise Exception("Component already exists as a user-made component.")
            except KeyError:
                pass
            
            #add NS to personal library if it's not from there
            try:
                addToNS(selectedNS)
            except AlreadyExistsError:
                pass
            
            newComponent = Component(selectedNS, selectedSpacers, selectedPrimers)
            #add it to the current component
            addToComps(newComponent) #note it will allow duplicates of defaults
            
            #modify output string
            #outputStr = newComponent.getID() + " created."
            libraryName = "Personal"
            outputStr = "<a target = '_blank' href = '/components#" + libraryName + newComponent.getID() + "'>" + newComponent.getID() + "</a> created."
            
            #set it as the tempComp (for the ZIP file)
            addToZip(newComponent.getCompZIP(), "newCompZip")
            
            succeeded = True
            
        except Exception as e:
            outputStr = "ERROR: " + str(e)
        
    return jsonify({"output": outputStr, "succeeded": succeeded})

#domestication ZIP file
@app.route("/domesticationZips.zip")
def domesticationZips():
    try:
        data = makeZIP(getSessionData().getNewCompZip())
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html")
    
    if(data == None):
        return render_template("noSeq.html")


    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})



##############################     ASSEMBLY     ##############################
##############################################################################
    
#the page for assembly
@app.route("/assemble", methods = ["POST", "GET"])
def assemble():
    sessionData = getSessionData()
    allSessionComps = sessionData.getAllComps()
    allDefaultComps = defaultSession.getAllComps()
    
    #dict of all components
    allAvailableNames = {"Pr": [], "RBS": [], "GOI": [], "Term": []}
    allComponentsPosition = {}
    validTerminals = {"Pr": [], "RBS": [], "GOI": [], "Term": []}

    for typeKey in allAvailableNames.keys():
        allDefaultNameKeys = list(allDefaultComps[typeKey].keys())
        print("defaults")
        print(allDefaultNameKeys)
        
        allUserNameKeys = list(allSessionComps[typeKey].keys())
        print("user")
        print(allUserNameKeys)
        
        #start off with the default allAvailableNames
        allAvailableNames[typeKey] = allDefaultNameKeys.copy()
        
        #add user sequences to allAvailableNames
        for userNameKey in allUserNameKeys:
            if(userNameKey not in allDefaultNameKeys):
                allAvailableNames[typeKey].append(userNameKey)
                
        #add defaults
        for defaultNameKey in allDefaultNameKeys:
            #add positions
            allPositionKeys = list(allDefaultComps[typeKey][defaultNameKey].keys())
            allComponentsPosition[defaultNameKey] = allPositionKeys

            #add terminals            
            for positionKey in allPositionKeys:
                try:
                    if(allDefaultComps[typeKey][defaultNameKey][positionKey]["L"] != []): #terminalLetter L
                        validTerminals[typeKey].append(defaultNameKey)
                except KeyError:
                    continue

        
        for userNameKey in allUserNameKeys:
            #add positions
            allPositionKeys = list(allSessionComps[typeKey][userNameKey].keys())
            
            #if the sequence is there
            if(userNameKey in allComponentsPosition.keys()):
                for posKey in allPositionKeys:
                    #do nothing if it's already there
                    if(posKey in allComponentsPosition[userNameKey]):
                        continue
                    #append if it isn't
                    else:
                        allComponentsPosition[userNameKey].append(posKey)
            #if the sequence is not at all there already
            else:
                allComponentsPosition[userNameKey] = allPositionKeys
            
            #add terminals
            for positionKey in allPositionKeys:
                try:
                    #don't add if it's already there
                    if(userNameKey in validTerminals[typeKey]):
                        continue
                    
                    if(allSessionComps[typeKey][userNameKey][positionKey]["L"] != []): #terminalLetter L
                        validTerminals[typeKey].append(userNameKey)
                except KeyError:
                    continue
            
       
        """
    #dictionary of all component names sorted by position
    allComponentsPosition = {}
    for outerKey in allSessionComps.keys(): #so, the type?
        for innerKey in allCompsDict[sessionID][outerKey].keys(): #this is Sub Ideal if mult. comps have same name      
            allComponentsPosition[innerKey] = list(allCompsDict[sessionID][outerKey][innerKey].keys())
        
    #dictionary of all valid terminators
    validTerminals = {"Pr": [], "RBS": [], "GOI": [], "Term": []}
    for typeKey in allCompsDict[sessionID].keys():
        for nameKey in allCompsDict[sessionID][typeKey].keys():
            for positionKey in allCompsDict[sessionID][typeKey][nameKey]:
                try:
                    if(allCompsDict[sessionID][typeKey][nameKey][positionKey]["L"] != []):
                        validTerminals[typeKey].append(nameKey)
                except KeyError:
                    continue
        """

    print("names")
    print(allAvailableNames)
    print("posititons:")
    print(allComponentsPosition)   
    print("terminals:")
    print(validTerminals)
    
    #list of fidelities
    fidelities = ["98.1%", "95.8%", "91.7%"]

    fidelityLimits = {"98.1%": SpacerData.max981, "95.8%": SpacerData.max958, "91.7%": SpacerData.max917}
    
    return render_template("assembly.html", fidelities = fidelities,
                           fidelityLimits = fidelityLimits,
                           availableElements = allAvailableNames, 
                           componentsPosition = allComponentsPosition,
                           validTerminals = validTerminals)

#process assembly
@app.route("/processAssembly", methods = ["POST"])
def processAssembly():
    #get info.
    formData = request.form["assemblyData"]
    dataDict = leval(formData)
    
    #Validation where?
    
    if(printActions):
        print("ASSEMBLING SEQUENCE FROM:\n" + str(dataDict))
    
    #remove from the dict. the info. that doesn't need to be processed
    del dataDict["fidelity"]
    del dataDict["elemName0"]
    del dataDict["elemType0"]
    del dataDict["elemName999"]
    del dataDict["elemType999"]
    
    #go through the dataDict, creating an array of all elements with the format:
    #{'position': position, 'type': elemType, 'name': elemName}
    gatheredElements = []
    for key in dataDict.keys():
        number = int(key[8:])
        
        if number > len(gatheredElements): #assumes the elements are in order
            gatheredElements.append({"position": number}) #add a new element
            
        if(key[0:8] == "elemType"):
            gatheredElements[number - 1]["type"] = dataDict[key]
            
        elif(key[0:8] == "elemName"):
            gatheredElements[number - 1]["name"] = dataDict[key]

    outputStr = ""

    succeeded = True
    compsList = []

    #find the components of gatheredElements
    for comp in gatheredElements:
        if(comp["position"] < len(dataDict) / 2):
            terminalLetter = "M"
        else:
            terminalLetter = "L"
                        
        try:
            try:                    #search defaults
                foundComp = defaultSession.findComponent(comp["type"], comp["name"], comp["position"], terminalLetter)
                libraryName = "Default"
            except Exception:       #search user-made
                foundComp = getSessionData().findComponent(comp["type"], comp["name"], comp["position"], terminalLetter)
                libraryName = "Personal"
                
            #foundComp = allCompsDict[sessionID][comp["type"]][comp["name"]][comp["position"]][terminalLetter]
            compsList.append(foundComp)
            #libraryName = "Personal"
            outputStr += ("Found: <a target = '_blank' href ='/components#" + libraryName + foundComp.getID() + "'>" + 
                          foundComp.getID() + "</a><br>")
        except KeyError:
            outputStr += ("Could not find:<br>Type: " + comp["type"] + "<br>Name: " + comp["name"] + 
                          "<br>Position: " + str(comp["position"]) + "<br>Terminal letter: " + terminalLetter + "<br>")
            
            succeeded = False
    
    #start fullSeq with element 0
    fullSeq = startEndComps[0].getFullSeq()
    
    #proceed if found everything
    if(succeeded):
        outputStr += "<br>Sequences of each element (not including element 0 and element T):<br>"
        
        #add the sequence of the component to the output strings
        for comp in compsList:
            outputStr += "<br>" + comp.getID() + ":<br>" + comp.getFullSeq()
            
            fullSeq += comp.getFullSeq()
        
        #finish fullSeq with element T
        fullSeq += startEndComps[1].getFullSeq()

        #finish outputStr
        outputStr += "<br><br>Full sequence:<br>"  + fullSeq
        
        #slap that sequence into the variable
        addToZip({"fullSequence.fasta": ">Cyano'Construct sequence\n" + fullSeq}, "assemblyZip")
        
    else:
        outputStr += "Errors in finding components are often due to not having a component with the right terminal letter.<br>Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#get the zip for the assembled sequence
@app.route("/assembledSequence.zip")
def assemblyZIP():    
    try:
        data = makeZIP(getSessionData().getAssemblyZip()) #validate it first?
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html")
    
    if(data == None):
        return render_template("noSeq.html")
    

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})


##############################     COMPONENT LIST     ##############################
#components page
@app.route("/components", methods = ["GET"])
def displayComps():
    #sessionID = checkSessionID()
    sessionData = getSessionData()
        
    allLibraries = {"Default": {"components": defaultSession.getAllComps(), "namedSeqs": defaultSession.getAllNS()}, 
                    "Personal": {"components": sessionData.getAllComps(), "namedSeqs": sessionData.getAllNS()}}    
    #riiiighhhht, damn
    
    #used for formatting
    longNames = {"Pr": "Promoters", "RBS": "Ribosome Binding Sites", "GOI": "Genes of Interest", "Term": "Terminators"}
    longNamesSingular = {"Pr": "Promoter", "RBS": "Ribosome Binding Site", "GOI": "Gene", "Term": "Terminator"}
    return render_template("components.html", allLibraries = allLibraries,
                           longNames = longNames, longNamesSingular = longNamesSingular)

#find the component to make ZIP file for
@app.route("/locateComponentForZip", methods = ["POST"])
def getComponentSequence():
    #get data
    component = request.form["component"]

    componentDict = leval(component)
    
    print(componentDict)
    
    #validation?
    succeeded = False
    try:
        #parse the data
        elemType = componentDict["elemType"]
        name = componentDict["name"]
        pos = int(componentDict["pos"])
        terminal = componentDict["terminal"] #? shouldn't it be:
        #if(componentDict["terminal"]):
        #    terminal = "L"
        #else:
        #    terminal = "M"
        
        try:
            #defaults first
            foundComp = defaultSession.findComponent(elemType, name, pos, terminal)
        except KeyError:
            foundComp = getSessionData().findComponent(elemType, name, pos, terminal)
                
        addToZip(foundComp.getCompZIP(), "componentForZip")
        
        succeeded = True
        
    except Exception as e:
        if(printActions):
            print("ERROR GETTING ZIP FILE DUE TO: " + str(e))
    
    return jsonify({"succeeded": succeeded})

#make and send the ZIP file for a component
@app.route("/componentZip.zip")
def getComponentZips():
    #sessionID = checkSessionID()

    try:
        data = makeZIP(getSessionData().getComponentForZip())
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html")
    
    if(data == None):
        return render_template("noSeq.html")
    
    else:
        return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='componentZip.zip';"})

@app.route("/removeComponent", methods = ["POST"])
def removeComponent():
    succeeded = False
    errorMessage = ""
    
    component = request.form["componentToRemove"]

    componentDict = leval(component)
    
    try:
        elemType = componentDict["elemType"]
        name = componentDict["name"]
        pos = int(componentDict["pos"])
        terminal = componentDict["terminal"]              
        
        getSessionData().removeComponent(elemType, name, pos, terminal)
        
        succeeded = True
    
    except Exception as e:
        errorMessage = str(e)
            
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})

@app.route("/removeSequence", methods = ["POST"])
def removeSequence():
    succeeded = False
    errorMessage = ""
    
    namedSequence = request.form["sequenceToRemove"]

    sequenceDict = leval(namedSequence)
    
    try:
        elemType = sequenceDict["elemType"]
        name = sequenceDict["name"]
        
        getSessionData().removeSequence(elemType, name)
        
        succeeded = True
    
    except Exception as e:
        errorMessage = str(e)
            
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})


################################################################################
################################################################################



@app.route("/index", methods = ["GET", "POST"], endpoint = "index")
@app.route("/", methods = ["GET", "POST"], endpoint = "index")
def index():
    sessionID = checkSessionID()
    
    sessionData = getSessionData()
    print(sessionData)
    
    print("\n\n")
    
    print(sessionData.getID())
    
    print("\n\n")

    
    print(sessionData.getAllNS())
    print("\n\n")
    
    print(sessionData.getAllComps())
    print("\n\n")
    
    print(sessionData.getNextNSid())
    print("\n\n")
    
    return render_template("index.html", sessionID = sessionID)

#sets session timeout
@app.before_request
def before_request():
    #set sessions to expire 24 hours after being changed
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)
    session.modified = True


#############################################

if __name__ == '__main__':
    #run
    app.run(debug=True)

"""
fasta label benchling
ids for each elem. or total?
linkers/overhangs: need a database of them & which positions they'll be at
- recog. sequences allowed determined by fidelity; higher means fewer
- add lower fidelity ones at the end, after the higher ones

personal libraries; accounts

ids as mostly numbers (G00101 e.g.) (ID which one and Pos (not huge))
- personal libraries

in domestication tab
- give: seq: position, class
- TM for primers
- makes annotated FASTA
- adds seq. elem. to personal library
- determines plasmid type (? wait what)
- terminators & promoters can change position but will have fixed ones at the top & bottom

prevent stop codons from being accidentally made

terminator has dif. link; need to then define elements in domestication step as right before the terminator or not

relationship b/t fidelity & num. elements (& linker sequences)
- lower fidelity more elem.s allowed, throw them in after the higher fidelity ones though

conflicting combinations? (of elements, linkers, etc. b/c would bind etc. stop codons as well)

[linker]NNEnzymeRecog[element]EnzymeRecogNN[linker]

can also add a reporter based on seq. & TM, no position

also label the info spit out with ids of elements probably

backbone: class and reporter (select)

assembly, domestication, library: as tabs/pages
- checkbox for actually own it

assembly step, two fastas:
    - operon construct w/out backbone
    - w/ backbone; entire plasmid
domestication:
    - primer 1
    - primer 2
    - entire sequence

assembly:
    - select promoter (always pos 0.) (select which)
    - add part
        - select class
        - options dependent on position & class
    - will spit out FASTAs
        - operon (entirety of the asembly steps, only need to access seq. data)
        - total

domesticate parts

need options based on library; gray out not allowed
"""

