
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:54:27 2020

@author: Lia Thomson

cyanoConstruct routes file
"""

import os

from cyanoConstruct import app, UserData, SpacerData, PrimerData, AlreadyExistsError, SequenceMismatchError,  SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, NamedSequenceDB, UserDataDB, ComponentDB, Globals, session
from cyanoConstruct import login, current_user, login_user, logout_user, login_required #import statements are messy


#flask
from flask import request, render_template, jsonify, Response, redirect
#import json
#from jinja2 import Markup

#session stuff
from uuid import uuid1
from datetime import timedelta

#misc.
from ast import literal_eval as leval
from shutil import rmtree, make_archive
from string import ascii_letters, digits
from werkzeug.urls import url_parse #for redirect parsing
from time import time

##########################################################################################
#globals
printActions = True
##########################################################################################

@login.user_loader
def load_user(user_id):
    try:
        return UserData.load(user_id)
    except Exception:
        return None

login.login_view = "login" #for redirecting if not logged in

######

def checkLoggedIn():
    return not getSessionData().is_anonymous

#sets sessionID if there isn't one
def checkSessionID():               #####<----- only used for naming folders right now
    return uuid1().hex

def getSessionData():
    return current_user

def checkPermission(comp):
    if(type(comp) != ComponentDB):
        raise TypeError("comp not a ComponentDB")
    
    if(comp.getUserID() != current_user.getID() and comp.getUserID() != Globals.getDefault().getID()):
        raise Exception("Do not have permission to access component.")
    

def getSelectedNS():
    try:
        NSID = session["selectedNS"]

        return NamedSequenceDB.query.get(NSID)

    except KeyError:
        return None

def getSelectedSD():
    try:
        return session["selectedSD"]
    except KeyError:
        return None

def getSelectedPD():
    try:
        return session["selectedPD"]
    except KeyError:
        return None

def getAllSelected():
    return ((getSelectedNS() is not None) and (getSelectedSD() is not None) and (getSelectedPD() is not None))

def addToSelected(newSelected):
    if(type(newSelected) == NamedSequenceDB): #####<----- edit to store an int ID of the NSDB instead
        session["selectedNS"] = newSelected.getID()
    elif(type(newSelected) == SpacerData):
        session["selectedSD"] = newSelected.toJSON()
    elif(type(newSelected) == PrimerData):
        session["selectedPD"] = newSelected.toJSON()
    else:
        raise TypeError("can't add item of type " + type(newSelected))
    
    session.modified = True

def addToSelectedOriginal(newSelected):
    sessionData = getSessionData()
    
    if(type(newSelected) == NamedSequenceDB): #####<----- edit to store an int ID of the NSDB instead
        sessionData.setSelectedNS(newSelected)
    elif(type(newSelected) == SpacerData):
        sessionData.setSelectedSpacers(newSelected)
    elif(type(newSelected) == PrimerData):
        sessionData.setSelectedPrimers(newSelected)
    else:
        raise TypeError("can't add item of type " + type(newSelected))

def saveAssemblyZIP(): #how do handle this?
    pass

def makeAllLibraryZIP(user):
    if(type(user) != UserData):
        raise TypeError("user not a UserData")

    filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    sessionDir = os.path.join(filesDirPath, checkSessionID())
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

##################################     ERRORS     ################################
##################################################################################

#temp disabled because called on js files

"""
@app.errorhandler(404)
def error404(error):
    print("404 error: " + str(error))
    return render_template("404.html")

@app.errorhandler(500)
def error500(error):
    print("500 eror: " + str(error))
    #roll back the database somehow, because this is invoked by database errors
    return render_template("500.html")
"""

##################################     LOG IN     ################################
##################################################################################

@app.route("/login", methods = ["POST", "GET"])
def login():
    #redirect if already logged in
    if(checkLoggedIn()):
        return redirect("/index")

    #get all "emails" for testing
    allEmails = []
    for user in UserDataDB.query.order_by(UserDataDB.email).all():
        allEmails.append(user.getEmail())
    
    #get the returnURL to use after a successful log in.
    """if("returnURL" in session):
        returnURL = session["returnURL"]
    else:
        returnURL = "index"""

    returnURL = request.args.get('next')
    if(not returnURL or (url_parse(returnURL).netloc != '')):
        returnURL = "/index"
        
    return render_template("login.html", returnURL = returnURL, allEmails = allEmails, 
                           loggedIn = checkLoggedIn())

@app.route("/loginProcess", methods = ["POST"])
def loginProcess():
    validInput = False
    outputStr = ""
    succeeded = False

    try:
        loginData = leval(request.form["loginData"])
        email = loginData["email"]

        if(loginData["remember"] == "true"):
            remember = True
        elif(loginData["remember"] == "false"):
            remember = False
        else:
            raise ValueError("invalid remember me")

        validInput = True
    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"
    
    if(validInput):
        try:
            #load the user
            """
            sessionData = getSessionData()
            user = UserData.load(loginData["email"])
            sessionData.setUser(user)
            
            #alter globals
            session["loggedIn"] = True
            """
            
            user = UserData.load(email)
            
            login_user(user, remember = remember) #add remember me functionality
            
            #indicate success
            outputStr = "Successfully logged in as " + email + ".<br>"
            succeeded = True
        except Exception as e:
            outputStr = "ERROR: " + str(e) + "<br>" #####<----- maybe I shouldn't use .innerHTML with this?
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

@app.route("/logout", methods = ["POST", "GET"])
def logoutProcess():
    if("loggedIn" in session):
        session.pop("loggedIn", False) ####<----- keep? or will Flask-Login do this
        
    logout_user()
    return redirect("/index")
        

@app.route("/registerProcess", methods = ["POST"])
def registerProcess():
    validInput = False
    outputStr = ""
    succeeded = False
    
    try:
        registrationData = leval(request.form["registrationData"])
        email = registrationData["email"]
        if(registrationData["remember"] == "true"):
            remember = True
        elif(registrationData["remember"] == "false"):
            remember = False
        else:
            raise ValueError("invalid remember me")

        validInput = True
        
    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"
    
    if(validInput):    
        try:
            #create UserData
            #sessionData = getSessionData()
            user = UserData.new(email)
            login_user(user, remember = remember)
            #sessionData.setUser(user)
            
            #alter globals
            session["loggedIn"] = True
            
            #indicate success
            outputStr += "Successfully registered and logged in as " + registrationData["email"] + ".<br>"
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"
        
        return jsonify({"output": outputStr, "succeeded": succeeded})
    

################################     USER PAGE     ################################
###################################################################################
    
@app.route("/account", methods = ["POST", "GET"])
@login_required
def accountInfo():
    sessionData = getSessionData()
    email = sessionData.getEmail()
    
    return render_template("account.html", email = email,
                           loggedIn = checkLoggedIn())


##############################     DOMESTICATION     ##############################
###################################################################################

#the page for domestication
@app.route("/domesticate", methods = ["POST", "GET"], endpoint = "domesticate")
@login_required
def domesticate():
    
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
                           loggedIn = checkLoggedIn())

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
        selectedSpacers = getSelectedSD()
        if(selectedSpacers == None):
            validInput = False
            outputStr += "ERROR: No spacers selected."
        
        selectedSpacers = SpacerData.fromJSON(selectedSpacers)

        #find the primers
        if(validInput):
            try:
                seqToEvaluate = getSelectedNS().getSeq() #fix this
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
    validInput = getAllSelected()
    #validInput = (selectedDict["selectedNamedSequence"] != None and selectedDict["selectedPrimers"] != None and selectedDict["selectedSpacers"] != None)
    succeeded = False
    newID = -1

    outputStr = ""
    
    if(validInput):
        try:
            sessionData = getSessionData()
            selectedNS = getSelectedNS()
            selectedSpacers = SpacerData.fromJSON(getSelectedSD())
            selectedPrimers = PrimerData.fromJSON(getSelectedPD())

            print("trying to make a component from:")
            print(sessionData)
            print(selectedNS)
            print(selectedSpacers)
            print(selectedPrimers)
            print("\n")
            
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
            newID = newComponent.getID()

            succeeded = True
            
        except Exception as e:
            outputStr = "ERROR: " + str(e)

    else:
        outputStr + "ERROR: invalid input."
        
    return jsonify({"output": outputStr, "succeeded": succeeded, "newID": newID})

#domestication ZIP file
@app.route("/domesticationZIPs.zip")
def domesticationZIPs():
    try:
        newCompID = request.args.get("id")
        compZIP = ComponentDB.query.get(newCompID).getCompZIP()

        data = makeZIP(compZIP)

    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = checkLoggedIn())


    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})



##############################     ASSEMBLY     ##############################
##############################################################################
    
#the page for assembly
@app.route("/assemble", methods = ["POST", "GET"])
@login_required
def assemble():       
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
                           loggedIn = checkLoggedIn())

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
    del dataDict["backbone"]
    
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
            compsList.append(foundComp.getID())
            #libraryName = "Personal"
            outputStr += ("Found: <a target = '_blank' href ='/components#" + libraryName + foundComp.getNameID() + "'>" + 
                          foundComp.getNameID() + "</a><br>")
        except (SequenceNotFoundError, ComponentNotFoundError):
            outputStr += ("Could not find:<br>Type: " + comp["type"] + "<br>Name: " + comp["name"] + 
                          "<br>Position: " + str(comp["position"]) + "<br>Terminal letter: " + terminalLetter + "<br>")
            
            succeeded = False
    
    #proceed if found everything
    if(succeeded):
        session["assemblyCompIDs"] = compsList
        outputStr += "Full sequence can be downloaded."
        
    else:
        outputStr += "Errors in finding components are often due to not having a component with the right terminal letter.<br>Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

def startAssemblyGB():
    fileHead = []
    fileHead.append("LOCUS\tAssembled seq\t" + str(25) + " bp\tDNA\tlinear\t" + "26-MAY-2020")
    fileHead.append("DEFINITION\tSequence assembled from CyanoConstruct")
    fileHead.append("FEATURES\tLocation/Qualifiers")
    
    return fileHead

def startOrigin():
    return ["ORIGIN"]

def addCompAssemblyGB(comp, features, i):
    lenSeq = len(comp.getFullSeq())
    
    if(comp.getType() == "GOI"):
        features.append("\tgene\t\t" + str(i + 1) + ".." + str(i + lenSeq))
        features.append("\t\t\t/gene=\"" + comp.getName() + "\"")
    else:
        regTypes = {"Pr": "promoter", "RBS" : "ribosome_binding_site", "Term": "terminator"}
        regName = regTypes[comp.getType()]
        features.append("\tregulatory\t" + str(i + 1) + ".." + str(i + lenSeq))
        features.append("\t\t\t/regulatory_class=" + regName)
                                            #get a longer thing to say here
        features.append("\t\t\t/note=\"" + comp.getType() + " " + comp.getName() + "\"")
    
    return i + lenSeq

def finishCompAssemblyGB(features, origin, fullSeq):
    #paste features and origin section together, add a // and join it into a thing
    
    seq = fullSeq.lower()
    
    i = 0
    
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

    features.extend(origin)
    
    features.append("//")
    
    return "\n".join(features)    

#get the zip for the assembled sequence
@app.route("/assembledSequence.zip")
def assemblyZIP():
    try:
        compsList = session["assemblyCompIDs"]
    except KeyError:
        print("FAILED TO CREATE ZIP BECAUSE NO ASSEMBLED SEQUENCE")
        return render_template("noSeq.html", loggedIn = checkLoggedIn())

    try:
        startEndComps = Globals.getDefault().getStartEndComps()

        #start with element 0
        fullSeq = startEndComps[0].getFullSeq()

        fileGB = startAssemblyGB()
        originSection = startOrigin()
        i = 0 #index (starting at zero) of the fullSeq to add at

        i = addCompAssemblyGB(startEndComps[0], fileGB, i)

        #add the sequence of the component
        for compID in compsList: #I hope this is in order
            comp = ComponentDB.query.get(compID)
            print(comp.getName())
            print(i)
            fullSeq += comp.getFullSeq()
            i = addCompAssemblyGB(comp, fileGB, i)
        
        #finish fullSeq with element T
        fullSeq += startEndComps[1].getFullSeq()
        i = addCompAssemblyGB(startEndComps[1], fileGB, i)
                
    
        fileGB = finishCompAssemblyGB(fileGB, originSection, fullSeq)
        fileFASTA = ">CyanoConstruct sequence\n" + fullSeq

        data = makeZIP({"fullSequence.fasta": fileFASTA, "fullSequence.gb": fileGB})

    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = checkLoggedIn())    

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})

def assemblyZIP2():
    try:
        data = makeZIP(getSessionData().getAssemblyZIP()) #validate it first?
    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})


##############################     COMPONENT LIST     ##############################
#components page
@app.route("/components", methods = ["GET"])
@login_required
def displayComps():
    array = [time()]
    
    sessionData = getSessionData()

    array.append(time())

    allNS = {}
    allComps = {}

    allNS["Default"], allComps["Default"] = Globals.getDefault().getSortedNSandComps()
    allNS["Personal"], allComps["Personal"] = sessionData.getSortedNSandComps()

    array.append(time())

    #replace the NamedSequenceDBs with the name and sequence
    for libraryName in allNS.keys():
        for typeKey in allNS[libraryName].keys():
            typeNS = {}
            for ns in allNS[libraryName][typeKey]:
                typeNS[ns.getName()] = ns.getSeq()
            allNS[libraryName][typeKey] = typeNS

    array.append(time())

    #used for formatting
    longNames = {"Pr": "Promoters", "RBS": "Ribosome Binding Sites", "GOI": "Genes of Interest", "Term": "Terminators"}
    longNamesSingular = {"Pr": "Promoter", "RBS": "Ribosome Binding Site", "GOI": "Gene", "Term": "Terminator"}

    rendered = render_template("components.html", allComps = allComps, allNS = allNS,
                           longNames = longNames, longNamesSingular = longNamesSingular,
                           loggedIn = checkLoggedIn())

    array.append(time())
    
    explanations = ["getSessionData()", "getSortedNSandComps()", "replace NS with seqs", "render_template"]
    
    for i in range(len(array) - 1):
        print(explanations[i] + ":\t" + str(array[i+1]-array[i]))

    return rendered

#make and send the ZIP file for a component
@app.route("/componentZIP.zip")
def getComponentZIP():
    try:
        comp = ComponentDB.query.get(request.args.get("id"))
        
        checkPermission(comp)
        
        compZIP = comp.getCompZIP()

        data = makeZIP(compZIP)

    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    
    if(data == None):
        return render_template("noSeq.html", loggedIn = checkLoggedIn())
    
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
        session["libraryName"] = "Default"

        succeeded = True
        errorMessage = ""
    elif(libraryName == "Personal"):
        session["libraryName"] = "Personal"

        succeeded = True
        errorMessage = ""
    else:
        errorMessage = "Can't find " + libraryName + " library."
        
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})
        
@app.route("/library.zip")
def libraryZIP():
    succeeded = False
    try:
        libraryName = session["libraryName"]

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

    except KeyError:
        succeeded = False
        errorMessage = "Library not found."

    
    if(succeeded):
        return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='library.zip';"})
    else:
        print(errorMessage)
        return render_template("noSeq.html", loggedIn = checkLoggedIn()) #####<----- I need something better than this


################################################################################
################################################################################



@app.route("/index", methods = ["GET", "POST"], endpoint = "index")
@app.route("/", methods = ["GET", "POST"], endpoint = "index")
def index():    
    if(checkLoggedIn()):
        logInMessage = "Logged in as: " + current_user.getEmail() + "."
    else:
        logInMessage = "Not logged in."


    return render_template("index.html", logInMessage = logInMessage, loggedIn = checkLoggedIn())

"""
#sets session timeout
@app.before_request
def before_request():
    #set sessions to expire 30 days after being changed
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)
    session.modified = True
"""

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

