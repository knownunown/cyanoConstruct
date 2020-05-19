
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:54:27 2020

@author: Lia Thomson

cyanoConstruct routes file
"""

import os

from cyanoConstruct import app, SessionData, UserData, SpacerData, PrimerData, AlreadyExistsError, SequenceMismatchError,  SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, NamedSequenceDB, UserDataDB, Globals

#flask
from flask import request, render_template, jsonify, Response, session, redirect
#import json
#from jinja2 import Markup

#session stuff
from uuid import uuid1
from datetime import timedelta

#misc.
from ast import literal_eval as leval
from shutil import rmtree, make_archive
from string import ascii_letters, digits

##########################################################################################
#globals
printActions = True
##########################################################################################

def checkLoggedIn():
    return getSessionData().getLoggedIn()

def redirectIfNotLoggedIn():
    if(not checkLoggedIn()):
        return (True, redirect("/login"))
    else:
        return (False, None)

#sets sessionID if there isn't one
def checkSessionID():
    if("sessionID" not in session):
        newID = uuid1().hex
        session["sessionID"] = newID
        SessionData(newID)

        if(printActions):
            print("new sessionID and SessionData: " + newID)

            
    return session["sessionID"]

def getSessionData():
    return SessionData.getSession(checkSessionID())

def addToSelected(newSelected):
    sessionData = getSessionData()
    
    if(type(newSelected) == NamedSequenceDB): #####<----- edit to store an int ID of the NSDB instead
        sessionData.setSelectedNS(newSelected)
    elif(type(newSelected) == SpacerData):
        sessionData.setSelectedSpacers(newSelected)
    elif(type(newSelected) == PrimerData):
        sessionData.setSelectedPrimers(newSelected)
    else:
        raise TypeError("can't add item of type " + type(newSelected))

def addToZIP(newFile, key):
    if(type(newFile) != dict):
        raise TypeError("newFile not a dict")

    sessionData = getSessionData()

    if(key == "newCompZIP"):
        sessionData.setNewCompZIP(newFile)
    elif(key == "assemblyZIP"):
        sessionData.setAssemblyZIP(newFile)
    elif(key == "componentForZIP"):
        sessionData.setComponentForZIP(newFile)
    else:
        raise ValueError("key not valid")

def makeAllLibraryZIP(session):
    if(type(session) != SessionData):
        raise TypeError("session not a SessionData")

    filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    sessionDir = os.path.join(filesDirPath, checkSessionID())
    libraryDir = os.path.join(sessionDir, session.getEmail() + "Library")

    try:
        os.mkdir(sessionDir)
    except OSError: #if it exists
        pass
    os.mkdir(libraryDir)
    
    if(printActions):
        print("MADE DIRECTORY: " + libraryDir)
        
    #great now what?
    sortedNS = session.getSortedNS()
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
        print("FINISHED CREATING LIBRARY ZIP FOR SESSION " + checkSessionID())
    
    return data

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


def addToNS(NS):
    sessionData = getSessionData()
    
    return sessionData.addNSDB(NS)

def addDefaultComp(comp):
    Globals.getDefault().addComp(comp)

def addDefaultNS(NS):
    Globals.getDefault().addNS(NS)

def makeDefaults():
    Globals.getDefault().makeFromNew("Pr", "psbA", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCACAAAGTTTTCGTTACATAAAAATAGTGTCTACTTAGCTAAAAATTAAGGGTTTTTTACACCTTTTTGACAGTTAATCTCCTAGCCTAAAAAGCAAGAGTTTTTAACTAAGACTCTTGCCCTTTACAACCTC",
                                                                     0, False, 45.0, 2)
    
    Globals.getDefault().makeFromNew("Term", "T1", "ATTTGTCCTACTCAGGAGAGCGTTCACCGACAAACAACAGATAAAACGAAAGGCCCAGTCTTTCGACTGAGCCTTTCGTTTTATTTG",
                                                                         999, False, 45.0, 2)

def makeMore():
    Globals.getDefault().makeFromNew("RBS", "S3", "AGTCAAGTAGGAGATTAATTCAATG",
                                               1, False, 45.0, 2)
    
    Globals.getDefault().makeFromNew("RBS", "A", "AACAAAATGAGGAGGTACTGAGATG",
                                             1, False, 45.0, 2)
        
    adhNS = Globals.getDefault().createNS("GOI", "adh", "ATGCATATTAAAGCCTACGCTGCCCTGGAAGCCAACGGAAAACTCCAACCCTTTGAATACGACCCCGGTGCCCTGGGTGCTAATGAGGTGGAGATTGAGGTGCAGTATTGTGGGGTGTGCCACAGTGATTTGTCCATGATTAATAACGAATGGGGCATTTCCAATTACCCCCTAGTGCCGGGTCATGAGGTGGTGGGTACTGTGGCCGCCATGGGCGAAGGGGTGAACCATGTTGAGGTGGGGGATTTAGTGGGGCTGGGTTGGCATTCGGGCTACTGCATGACCTGCCATAGTTGTTTATCTGGCTACCACAACCTTTGTGCCACGGCGGAATCGACCATTGTGGGCCACTACGGTGGCTTTGGCGATCGGGTTCGGGCCAAGGGAGTCAGCGTGGTGAAATTACCTAAAGGCATTGACCTAGCCAGTGCCGGGCCCCTTTTCTGTGGAGGAATTACCGTTTTCAGTCCTATGGTGGAACTGAGTTTAAAGCCCACTGCAAAAGTGGCAGTGATCGGCATTGGGGGCTTGGGCCATTTAGCGGTGCAATTTCTCCGGGCCTGGGGCTGTGAAGTGACTGCCTTTACCTCCAGTGCCAGGAAGCAAACGGAAGTGTTGGAATTGGGCGCTCACCACATACTAGATTCCACCAATCCAGAGGCGATCGCCAGTGCGGAAGGCAAATTTGACTATATTATCTCCACTGTGAACCTGAAGCTTGACTGGAACTTATACATCAGCACCCTGGCGCCCCAGGGACATTTCCACTTTGTTGGGGTGGTGTTGGAGCCTTTGGATCTAAATCTTTTTCCCCTTTTGATGGGACAACGCTCCGTTTCTGCCTCCCCAGTGGGTAGTCCCGCCACCATTGCCACCATGTTGGACTTTGCTGTGCGCCATGACATTAAACCCGTGGTGGAACAATTTAGCTTTGATCAGATCAACGAGGCGATCGCCCATCTAGAAAGCGGCAAAGCCCATTATCGGGTAGTGCTCAGCCATAGTAAAAATTAG")
    Globals.getDefault().makeWithNamedSequence(adhNS, 2, False, 45.0, 2)
    Globals.getDefault().makeWithNamedSequence(adhNS, 2, True, 45.0, 2)
        
    Globals.getDefault().makeFromNew("GOI", "pdc", "ATGCATAGTTATACTGTCGGTACCTATTTAGCGGAGCGGCTTGTCCAGATTGGTCTCAAGCATCACTTCGCAGTCGCGGGCGACTACAACCTCGTCCTTCTTGACAACCTGCTTTTGAACAAAAACATGGAGCAGGTTTATTGCTGTAACGAACTGAACTGCGGTTTCAGTGCAGAAGGTTATGCTCGTGCCAAAGGCGCAGCAGCAGCCGTCGTTACCTACAGCGTTGGTGCGCTTTCCGCATTTGATGCTATCGGTGGCGCCTATGCAGAAAACCTTCCGGTTATCCTGATCTCCGGTGCTCCGAACAACAACGACCACGCTGCTGGTCATGTGTTGCATCATGCTCTTGGCAAAACCGACTATCACTATCAGTTGGAAATGGCCAAGAACATCACGGCCGCCGCTGAAGCGATTTACACCCCGGAAGAAGCTCCGGCTAAAATCGATCACGTGATCAAAACTGCTCTTCGCGAGAAGAAGCCGGTTTATCTCGAAATCGCTTGCAACACTGCTTCCATGCCCTGCGCCGCTCCTGGACCGGCAAGTGCATTGTTCAATGACGAAGCCAGCGACGAAGCATCCTTGAATGCAGCGGTTGACGAAACCCTGAAATTCATCGCCAACCGCGACAAAGTTGCCGTCCTCGTCGGCAGCAAGCTGCGCGCTGCTGGTGCTGAAGAAGCTGCTGTTAAATTCACCGACGCTTTGGGCGGTGCAGTGGCTACTATGGCTGCTGCCAAGAGCTTCTTCCCAGAAGAAAATGCCAATTACATTGGTACCTCATGGGGCGAAGTCAGCTATCCGGGCGTTGAAAAGACGATGAAAGAAGCCGATGCGGTTATCGCTCTGGCTCCTGTCTTCAACGACTACTCCACCACTGGTTGGACGGATATCCCTGATCCTAAGAAACTGGTTCTCGCTGAACCGCGTTCTGTCGTTGTCAACGGCATTCGCTTCCCCAGCGTTCATCTGAAAGACTATCTGACCCGTTTGGCTCAGAAAGTTTCCAAGAAAACCGGTTCTTTGGACTTCTTCAAATCCCTCAATGCAGGTGAACTGAAGAAAGCCGCTCCGGCTGATCCGAGTGCTCCGTTGGTCAACGCAGAAATCGCCCGTCAGGTCGAAGCTCTTCTGACCCCGAACACGACGGTTATTGCTGAAACCGGTGACTCTTGGTTCAATGCTCAGCGCATGAAGCTCCCGAACGGTGCTCGCGTTGAATATGAAATGCAGTGGGGTCACATTGGTTGGTCCGTTCCTGCCGCCTTCGGTTATGCCGTCGGTGCTCCGGAACGTCGCAACATCCTCATGGTTGGTGATGGTTCCTTCCAGCTGACGGCTCAGGAAGTTGCTCAGATGGTTCGCCTGAAACTGCCGGTTATCATCTTCTTGATCAATAACTATGGTTACACCATCGAAGTTATGATCCATGATGGTCCGTACAACAACATCAAGAACTGGGATTATGCCGGTCTGATGGAAGTGTTCAACGGTAACGGTGGTTATGACAGCGGTGCTGCTAAAGGCCTGAAGGCTAAAACCGGTGGCGAACTGGCAGAAGCTATCAAGGTTGCTCTGGCAAACACCGACGGCCCAACCCTGATCGAATGCTTCATCGGTCGTGAAGACTGCACTGAAGAATTGGTCAAATGGGGTAAGCGCGTTGCTGCCGCCAACAGCCGTAAGCCTGTTAACAAGCTCCTCTAG",
                                                 3, True, 45.0, 2)

try:
    makeDefaults()
    makeMore()
except AlreadyExistsError:
    pass

##################################     LOG IN     ################################
##################################################################################

@app.route("/login", methods = ["POST", "GET"])
def login():
    #get all "emails" for testing
    allEmails = []
    for user in UserDataDB.query.order_by(UserDataDB.email).all():
        allEmails.append(user.getEmail())
    
    #get the returnURL to use after a successful log in.
    if("returnURL" in session):
        returnURL = session["returnURL"]
    else:
        returnURL = "index"
        
    return render_template("login.html", returnURL = returnURL, allEmails = allEmails, 
                           loggedIn = getSessionData().getLoggedIn())

@app.route("/loginProcess", methods = ["POST"])
def loginProcess():
    loginData = leval(request.form["loginData"])
    
    succeeded = False
    outputStr = ""
        
    try:
        #load the user
        sessionData = getSessionData()
        user = UserData.load(loginData["email"])
        sessionData.setUser(user)
        
        #alter globals
        session["loggedIn"] = True
        #allSessions[checkSessionID()] = sessionData #####<----- I dislike this
                
        #indicate success
        outputStr = "Successfully logged in as " + loginData["email"] + ".<br>"
        succeeded = True
    except Exception as e:
        outputStr = "ERROR: " + str(e) + "<br>" #####<----- maybe I shouldn't use .innerHTML with this?
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

@app.route("/logout", methods = ["POST", "GET"])
def logoutProcess():
    if("loggedIn" in session):
        session.pop("loggedIn", False)
        getSessionData().removeUser()
        #and all that
        #some sort of success message
    else:
        #already not logged in
        getSessionData().removeUser() #just in case?
    
    return redirect("/index")
        

@app.route("/registerProcess", methods = ["POST"])
def registerProcess():
    registrationData = leval(request.form["registrationData"])
    
    succeeded = False
    outputStr = ""
    
    try:
        #create UserData
        sessionData = getSessionData()
        user = UserData.new(registrationData["email"])
        sessionData.setUser(user)
        
        #alter globals
        session["loggedIn"] = True
        #allSessions[checkSessionID()] = sessionData #####<----- I dislike this
        
        #indicate success
        outputStr += "Successfully registered and logged in as " + registrationData["email"] + ".<br>"
        succeeded = True
    except Exception as e:
        outputStr += "ERROR: " + str(e) + "<br>"
    
    return jsonify({"output": outputStr, "succeeded": succeeded})
    

################################     USER PAGE     ################################
###################################################################################
    
@app.route("/account", methods = ["POST", "GET"])
def accountInfo():
    shouldRedirect, retValue = redirectIfNotLoggedIn()
    if(shouldRedirect):
        session["returnURL"] = "account"
        return retValue
    else:
        session["returnURL"] = "index"

    sessionData = getSessionData()
    email = sessionData.getEmail()
    
    return render_template("account.html", email = email,
                           loggedIn = sessionData.getLoggedIn())


##############################     DOMESTICATION     ##############################
###################################################################################

#the page for domestication
@app.route("/domesticate", methods = ["POST", "GET"], endpoint = "domesticate")
def domesticate():
    shouldRedirect, retValue = redirectIfNotLoggedIn()
    if(shouldRedirect):
        session["returnURL"] = "domesticate"
        return retValue
    else:
        session["returnURL"] = "index"
    
    sessionData = getSessionData()
        
    sessionNamedSequences = sessionData.getSortedNS()
    defaultNamedSequences = Globals.getDefault().getSortedNS()
    
    #make the named sequences more friendly to javascript
    NSNamesJSONifiable = {}
    NSSequencesJSONifiable = {}
    
    #defaults first
    for typeKey in defaultNamedSequences.keys():
        NSNamesJSONifiable[typeKey] = [] 
        
        for ns in defaultNamedSequences[typeKey]:
            NSNamesJSONifiable[typeKey].append(ns.getName())
            
            NSSequencesJSONifiable[ns.getName()] = ns.getSeq()

    #user-made second
        for ns in sessionNamedSequences[typeKey]:
            if(ns.getName() not in NSNamesJSONifiable[typeKey]): #will not duplicate if it's actually a default NS
                NSNamesJSONifiable[typeKey].append(ns.getName())
                
                NSSequencesJSONifiable[ns.getName()] = ns.getSeq()

    
    return render_template("domesticate.html", namedSequencesNames = NSNamesJSONifiable,
                           namedSequencesSequences = NSSequencesJSONifiable,
                           loggedIn = getSessionData().getLoggedIn())

#make a new NamedSequence
@app.route("/newNamedSeq", methods = ["POST"])
def newNamedSeq():
    #get data
    newNSData = leval(request.form["newNSData"]) #do not do this all in one step w/out error handling

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
            Globals.getDefault().findNamedSequence(elemType, newNSName, newNSSeq)
                        
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

    #try:
        #search for it
        #foundNamedSequence = NamedSequence.findNamedSequence(NStype, NSname, NSseq, sessionID)
    try:        #search default first
        foundNamedSequence = Globals.getDefault().findNamedSequence(NStype, NSname, NSseq)
    except Exception:
        foundNamedSequence = sessionData.findNamedSequence(NStype, NSname, NSseq)
        
    #add to session selected
    addToSelected(foundNamedSequence) #####<----- strange way to call, but I think it works
    
    outputStr = ""
    
    succeeded = True
    
    #except Exception as e:
    #    outputStr = "ERROR: " + str(e)
    #    succeeded = False
    
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
        outputStr += "ERROR: Terminal value not valid.<br>"

    #if the position is the maximum allowed position, it must be terminal
    if(validInput and (newPos == maxPosition) and (not isTerminal)):
        validInput = False
        outputStr += "ERROR: " + str(newPos) + " is the last allowed position, so it must be terminal.<br>"
    
    #obtain the actual spacers
    if(validInput):
        try:
            #make the SpacerData
            newSpacerData = SpacerData.makeNew(newPos, isTerminal)
            
            #add to outputStr
            outputStr += "Spacers found for position " + str(newPos)
            if(isTerminal):
                outputStr += " last element:"
            else:
                outputStr += " not last element:"
            outputStr += "<br>Left spacer: " + newSpacerData.getSpacerLeft() + "<br>Right spacer: " + newSpacerData.getSpacerRight()
            
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
        addToSelected(Globals.getNullPrimerData())
        
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
                newPrimerData = PrimerData.makeNew(seqToEvaluate, TMnum, rangeNum)
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
            sessionData = getSessionData()
            selectedNS = sessionData.getSelectedNS()
            selectedSpacers = sessionData.getSelectedSpacers()
            selectedPrimers = sessionData.getSelectedPrimers()
            
            #check if it already exists in defaults
            try:
                Globals.getDefault().findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise AlreadyExistsError("Component already exists as a default component.")
            except (SequenceNotFoundError, ComponentNotFoundError):
                pass
            
            #check if it already exists in personal library
            try:
                getSessionData().findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise AlreadyExistsError("Component already exists as a user-made component.")
            except (SequenceNotFoundError, ComponentNotFoundError):
                pass
            
            #add NS to personal library if it's not from there
            try:
                tempNS = addToNS(selectedNS)
                selectedNS = tempNS
            except AlreadyExistsError:
                pass
    
            newComponent = sessionData.createComp(selectedNS, selectedSpacers, selectedPrimers)
            
            #modify output string
            #outputStr = newComponent.getID() + " created."
            libraryName = "Personal"
            outputStr = "<a target = '_blank' href = '/components#" + libraryName + newComponent.getNameID() + "'>" + newComponent.getNameID() + "</a> created."
            
            #set it as the tempComp (for the ZIP file)
            addToZIP(newComponent.getCompZIP(), "newCompZIP")
            
            succeeded = True
            
        except Exception as e:
            outputStr = "ERROR: " + str(e)
        
    return jsonify({"output": outputStr, "succeeded": succeeded})

#domestication ZIP file
@app.route("/domesticationZIPs.zip")
def domesticationZIPs():
    try:
        data = makeZIP(getSessionData().getNewCompZIP())
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())


    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})



##############################     ASSEMBLY     ##############################
##############################################################################
    
#the page for assembly
@app.route("/assemble", methods = ["POST", "GET"])
def assemble():
    shouldRedirect, retValue = redirectIfNotLoggedIn()
    if(shouldRedirect):
        session["returnURL"] = "assemble"
        return retValue
    else:
        session["returnURL"] = "index"
       
    allDefaultNS = Globals.getDefault().getSortedNS()
    allSessionNS = getSessionData().getSortedNS()
    
    #dict of all components
    allAvailableNames = {}
    posTerminalComb = {}

    for typeKey in allDefaultNS.keys():
        allAvailableNames[typeKey] = []
        
        #default library
        for ns in allDefaultNS[typeKey]:
            allAvailableNames[typeKey].append(ns.getName()) #add names
                        
            posTerminalComb[ns.getName()] = []
            
            for comp in ns.getAllComponents():                                
                #the combination
                posTermCombRow = {"position": comp.getPosition(), "terminalLetter": comp.getTerminalLetter()}
                if(posTermCombRow not in posTerminalComb[ns.getName()]):
                    posTerminalComb[ns.getName()].append(posTermCombRow)
                        
        #user-made library
        for ns in allSessionNS[typeKey]:
            if(ns.getName() not in allAvailableNames[typeKey]): #add user-made sequences if not already there
                allAvailableNames[typeKey].append(ns.getName())
            
                if(ns.getName() not in posTerminalComb):
                    posTerminalComb[ns.getName()] = []
                
            for comp in ns.getAllComponents():
                                    
                #that combination
                posTermCombRow = {"position": comp.getPosition(), "terminalLetter": comp.getTerminalLetter()}
                if(posTermCombRow not in posTerminalComb[ns.getName()]):
                    posTerminalComb[ns.getName()].append(posTermCombRow)
    
    #list of fidelities
    fidelities = ["98.1%", "95.8%", "91.7%"]

    fidelityLimits = {"98.1%": SpacerData.max981, "95.8%": SpacerData.max958, "91.7%": SpacerData.max917}
    
    return render_template("assembly.html", fidelities = fidelities,
                           fidelityLimits = fidelityLimits,
                           availableElements = allAvailableNames, 
                           posTermComb = posTerminalComb,
                           loggedIn = getSessionData().getLoggedIn())

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
                foundComp = Globals.getDefault().findComponent(comp["type"], comp["name"], comp["position"], terminalLetter)
                libraryName = "Default"
            except (SequenceNotFoundError, ComponentNotFoundError):       #search user-made
                foundComp = getSessionData().findComponent(comp["type"], comp["name"], comp["position"], terminalLetter)
                libraryName = "Personal"
                
            #foundComp = allCompsDict[sessionID][comp["type"]][comp["name"]][comp["position"]][terminalLetter]
            compsList.append(foundComp)
            #libraryName = "Personal"
            outputStr += ("Found: <a target = '_blank' href ='/components#" + libraryName + foundComp.getNameID() + "'>" + 
                          foundComp.getNameID() + "</a><br>")
        except (SequenceNotFoundError, ComponentNotFoundError):
            outputStr += ("Could not find:<br>Type: " + comp["type"] + "<br>Name: " + comp["name"] + 
                          "<br>Position: " + str(comp["position"]) + "<br>Terminal letter: " + terminalLetter + "<br>")
            
            succeeded = False
    
    #start fullSeq with element 0
    startEndComps = Globals.getDefault().getStartEndComps()
    
    fullSeq = startEndComps[0].getFullSeq()
    
    #proceed if found everything
    if(succeeded):
        outputStr += "<br>Sequences of each element (not including element 0 and element T):<br>"
        
        #add the sequence of the component to the output strings
        for comp in compsList:
            outputStr += "<br>" + comp.getNameID() + ":<br>" + comp.getFullSeq()
            
            fullSeq += comp.getFullSeq()
        
        #finish fullSeq with element T
        fullSeq += startEndComps[1].getFullSeq()

        #finish outputStr
        outputStr += "<br><br>Full sequence:<br>"  + fullSeq
        
        #slap that sequence into the variable
        addToZIP({"fullSequence.fasta": ">CyanoConstruct sequence\n" + fullSeq}, "assemblyZIP")
        
    else:
        outputStr += "Errors in finding components are often due to not having a component with the right terminal letter.<br>Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#get the zip for the assembled sequence
@app.route("/assembledSequence.zip")
def assemblyZIP():    
    try:
        data = makeZIP(getSessionData().getAssemblyZIP()) #validate it first?
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())
    

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})


##############################     COMPONENT LIST     ##############################
#components page
@app.route("/components", methods = ["GET"])
def displayComps():
    shouldRedirect, retValue = redirectIfNotLoggedIn()
    if(shouldRedirect):
        session["returnURL"] = "components"
        return retValue
    else:
        session["returnURL"] = "index"
    
    sessionData = getSessionData()
    
    allComps = {"Default": Globals.getDefault().getSortedComps(), 
                    "Personal": sessionData.getSortedComps()}

    allNS = {"Default": Globals.getDefault().getSortedNS(),
             "Personal": sessionData.getSortedNS()}

    #replace the NamedSequenceDBs with the name and sequence
    for libraryName in allNS.keys():
        for typeKey in allNS[libraryName].keys():
            typeNS = {}
            for ns in allNS[libraryName][typeKey]:
                typeNS[ns.getName()] = ns.getSeq()
            allNS[libraryName][typeKey] = typeNS

    #used for formatting
    longNames = {"Pr": "Promoters", "RBS": "Ribosome Binding Sites", "GOI": "Genes of Interest", "Term": "Terminators"}
    longNamesSingular = {"Pr": "Promoter", "RBS": "Ribosome Binding Site", "GOI": "Gene", "Term": "Terminator"}
    return render_template("components.html", allComps = allComps, allNS = allNS,
                           longNames = longNames, longNamesSingular = longNamesSingular,
                           loggedIn = getSessionData().getLoggedIn())

#find the component to make ZIP file for
@app.route("/locateComponentForZIP", methods = ["POST"])
def getComponentSequence():
    #get data
    component = request.form["component"]

    componentDict = leval(component)
        
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
            foundComp = Globals.getDefault().findComponent(elemType, name, pos, terminal)
        except (SequenceNotFoundError, ComponentNotFoundError):
            foundComp = getSessionData().findComponent(elemType, name, pos, terminal)
                
        addToZIP(foundComp.getCompZIP(), "componentForZIP")
        
        succeeded = True
        
    except Exception as e:
        if(printActions):
            print("ERROR GETTING ZIP FILE DUE TO: " + str(e))
    
    return jsonify({"succeeded": succeeded})

#make and send the ZIP file for a component
@app.route("/componentZIP.zip")
def getComponentZIPs():
    #sessionID = checkSessionID()

    try:
        data = makeZIP(getSessionData().getComponentForZIP())
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn())
    
    else:
        return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='componentZIP.zip';"})

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

@app.route("/downloadLibrary", methods = ["POST"])
def downloadLibrary():
    libraryName = request.form["libraryName"]
    
    succeeded = False    
    
    if(libraryName == "Default"):
        getSessionData().setLibraryName("Default")
        succeeded = True
        errorMessage = ""
    elif(libraryName == "Personal"):
        getSessionData().setLibraryName("Personal")
        succeeded = True
        errorMessage = ""
    else:
        errorMessage = "Can't find " + libraryName + " library."
        
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})
        
@app.route("/library.zip")
def libraryZIP():
    libraryName = getSessionData().getLibraryName()
    
    if(libraryName == "Default"):
        try:
            data = makeAllLibraryZIP(Globals.getDefault())
            succeeded = True
        except Exception as e:
            errorMessage = str(e)
    elif(libraryName == "Personal"):
        try:
            data = makeAllLibraryZIP(getSessionData())
            succeeded = True
        except Exception as e:
            errorMessage = str(e)
    
    if(succeeded):
        return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='library.zip';"})
    else:
        print(errorMessage)
        return render_template("noSeq.html", loggedIn = getSessionData().getLoggedIn()) #####<----- I need something better than this


################################################################################
################################################################################



@app.route("/index", methods = ["GET", "POST"], endpoint = "index")
@app.route("/", methods = ["GET", "POST"], endpoint = "index")
def index():    
    sessionID = checkSessionID()
    return render_template("index.html", sessionID = sessionID, loggedIn = getSessionData().getLoggedIn())

#sets session timeout
@app.before_request
def before_request():
    #set sessions to expire 30 days after being changed
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)
    session.modified = True


#############################################

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

