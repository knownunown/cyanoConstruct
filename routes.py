
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:54:27 2020

@author: Lia Thomson

cyanoConstruct routes file
"""
import cyanoConstruct.enumsExceptions as ee
from cyanoConstruct import app, UserData, SpacerData, PrimerData, NamedSequenceDB, UserDataDB, ComponentDB, BackboneDB, session
from cyanoConstruct import login, current_user, login_user, logout_user, login_required
import cyanoConstruct.routesFuncs as rf
from cyanoConstruct import defaultUser, nullPrimerData, printActions

#flask
from flask import request, render_template, jsonify, Response, redirect

#session stuff
from datetime import timedelta

#Google Login stuff
from google.oauth2 import id_token
from google.auth.transport import requests

#misc.
from ast import literal_eval as leval
from werkzeug.urls import url_parse #for redirect parsing
from time import time
import os
import re

##########################################################################################

CLIENT_ID = "431868350398-t0st3dhimv5i7rc3laka2lv2864kt4pd.apps.googleusercontent.com"

#user-related funcs
@login.user_loader
def load_user(user_id):
    try:
        return UserData.load(user_id)
    except Exception:
        return None

login.login_view = "login" #for redirecting if not logged in

def checkLoggedIn():
    return not getCurrUser().is_anonymous

def getCurrUser():
    return current_user

def checkPermission(comp):
    if(type(comp) != ComponentDB):
        raise TypeError("comp not a ComponentDB")
    
    if(comp.getUserID() != current_user.getID() and comp.getUserID() != defaultUser.getID()):
        raise ee.AccessError("Do not have permission to access component.")

def checkPermissionNS(ns):
    if(type(ns) != NamedSequenceDB):
        raise TypeError("ns not a NamedSequenceDB")
    
    if(ns.getUserID() != current_user.getID() and ns.getUserID() != defaultUser.getID()):
        raise ee.AccessError("Do not have permission to access sequence.")

def checkPermissionBB(bb):
    if(type(bb) != BackboneDB):
        raise TypeError("bb not a BackboneDB")

    if(bb.getUserID() != current_user.getID() and bb.getUserID() != defaultUser.getID()):
        raise ee.AccessError("Do not have permission to access this backbone.")

def permissionOwnNS(ns):
    if(type(ns) != NamedSequenceDB):
        raise TypeError("ns not a NamedSequenceDB")

    if(ns.getUserID() != current_user.getID()):
        raise ee.AccessError("Do not have permission to access this sequence.")

def permissionOwnComp(comp):
    if(type(comp) != ComponentDB):
        raise TypeError("comp not a ComponentDB")

    if(comp.getUserID() != current_user.getID()):
        raise ee.AccessError("Do not have permission to access component.")

def permissionOwnBB(bb):
    if(type(bb) != BackboneDB):
        raise TypeError("bb not a BackboneDB")

    if(bb.getUserID() != current_user.getID()):
        raise ee.AccessError("Do not have permission to access this backbone.")

#Selected objects (for designing components)
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
    if(type(newSelected) == NamedSequenceDB):
        session["selectedNS"] = newSelected.getID()
    elif(type(newSelected) == SpacerData):
        session["selectedSD"] = newSelected.toJSON()
    elif(type(newSelected) == PrimerData):
        session["selectedPD"] = newSelected.toJSON()
    else:
        raise TypeError("can't add item of type " + type(newSelected))

    session.modified = True
 
def clearSelected():
    for key in ["selectedNS", "selectedSD", "selectedPD"]:
        try:
            session.pop(key)
        except Exception:
            pass

##################################   ERRORS    ################################
##################################################################################

@app.errorhandler(404)
def error404(error):
    print("404 error: " + str(error))
    return render_template("404.html")

@app.errorhandler(500)
def error500(error):
    print("500 eror: " + str(error))
    #roll back the database somehow, because this is invoked by database errors
    return render_template("500.html")

def errorZIP(error):
    return render_template("noSeq.html",
                            errorMessage = str(error),
                            loggedIn = checkLoggedIn())

@app.route("/privacy")
def privacyPolicy():
    return render_template("privacy.html", loggedIn = checkLoggedIn())

##################################   LOG IN    ################################
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
    
    #get returnURL
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

        try:
            remember = rf.boolJS(loginData["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        validInput = True
    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"
    
    if(validInput):
        try:            
            user = UserData.load(email)
            
            login_user(user, remember = remember)
            
            clearSelected()

            #indicate success
            outputStr = "Successfully logged in as " + email + ".<br>"
            succeeded = True

        except Exception as e:
            outputStr = "ERROR: " + str(e) + "<br>"
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

@app.route("/loginGoogle", methods = ["POST"])
def loginGoogle():
    succeeded = False
    outputStr = ""

    try:
        print(str(request.form["loginData"]))
        print(len(request.form["loginData"]))
        loginData = leval(request.form["loginData"])

        token = loginData["IDtoken"]
        email = loginData["email"]
        try:
            remember = rf.boolJS(loginData["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        #check token

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']

        #actually log in OR register
        try:
            user = UserData.load(email)

            if(user.getGoogleAssoc()):
                if(user.getGoogleID() != userid):
                    raise Exception(" User ID and Email do not match.")
                else:
                    login_user(user, remember = remember) #I don't know else to handle that
                    outputStr = "Successfully logged in as {email}.".format(email = email)
            else:
                raise Exception("Account with this email already exists, not associated with Google.")

        except ee.UserNotFoundError:
            user = UserData.new(email)

            user.setGoogleAssoc(True)
            user.setGoogleID(userid)

            login_user(user, remember = remember)

            clearSelected()

            outputStr = "Successfully created account as {email}.".format(email = email)

        succeeded = True

    except ValueError:
        outputStr = "ERROR: Invalid input."
        # Invalid token

    except Exception as e:
        outputStr =  "ERROR: {}".format(e)
        print(e)

    return jsonify({"succeeded": succeeded, "output": outputStr})

@app.route("/logout", methods = ["POST", "GET"])
def logoutProcess():
    logout_user()
    clearSelected() 
    
    return redirect("/index")
        

@app.route("/registerProcess", methods = ["POST"])
def registerProcess():
    validInput = False
    outputStr = ""
    succeeded = False
    
    try:        
        registrationData = leval(request.form["registrationData"])
        email = registrationData["email"]
        try:
            remember = rf.boolJS(registrationData["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        validInput = True
        
    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"
    
    if(validInput): 
        try:
            user = UserData.new(email)
            login_user(user, remember = remember)
                        
            clearSelected()

            #indicate success
            outputStr += "Successfully registered and logged in as " + registrationData["email"] + ".<br>"
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"
        
        return jsonify({"output": outputStr, "succeeded": succeeded})
    

################################     USER PAGE   ################################
###################################################################################
    
@app.route("/account", methods = ["POST", "GET"])
@login_required
def accountInfo():
    currUser = getCurrUser()
    email = currUser.getEmail()
    
    googleAssoc = currUser.getEntry().getGoogleAssoc()

    return render_template("account.html", email = email,
                            googleAssoc = googleAssoc,
                           loggedIn = checkLoggedIn())


@app.route("/googleConnect", methods = ["POST"])
def googleConnect():
    outputStr = ""
    succeeded = False

    currUser = getCurrUser()

    try:
        connectData = leval(request.form["connectData"])

        token = connectData["IDtoken"]
        email = connectData["email"]

        #check token

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']

        u = UserData.load(email)

        if(u.getGoogleAssoc()):
            raise Exception("Already connected Google account with this email.")
        else:
            if(u.getEmail() != email):
                raise Exception("Emails don't match.") #what will this even mean?
            else:
                u.setGoogleAssoc(True)
                u.setGoogleID(userid)

                outputStr = "Successfully connected {email} with Google account.".format(email = email)

                succeeded = True

    except ValueError:
        outputStr = "ERROR: Invalid input."
        # Invalid token

    except Exception as e:
        outputStr =  "ERROR: {}".format(e)
        print(e)


    return jsonify({"output": outputStr, "succeeded": succeeded})

#################################    DESIGN     ##################################
###################################################################################
@app.route("/design", methods = ["POST", "GET"])
@login_required
def design():      
    userNamedSequences = getCurrUser().getSortedNS()
    defaultNamedSequences = defaultUser.getSortedNS()
    
    #make the named sequences more friendly to javascript
    NSNamesJSONifiable = {}
    NSSequencesJSONifiable = {}

    defaultNames = []
    
    #defaults first
    for typeKey in defaultNamedSequences.keys():
        NSNamesJSONifiable[typeKey] = [] 
        
        for ns in defaultNamedSequences[typeKey]:
            NSNamesJSONifiable[typeKey].append({"name": ns.getName(), "id": ns.getID()})
            
            NSSequencesJSONifiable[ns.getID()] = ns.getSeq()

            defaultNames.append(ns.getName())

    #user-made second
        for ns in userNamedSequences[typeKey]:
            if(ns.getName() not in defaultNames): #will not duplicate if it's actually a default NS
                NSNamesJSONifiable[typeKey].append({"name": ns.getName(), "id": ns.getID()})
                
                NSSequencesJSONifiable[ns.getID()] = ns.getSeq()

    
    return render_template("design.html", namedSequencesNames = NSNamesJSONifiable,
                           namedSequencesSequences = NSSequencesJSONifiable,
                           loggedIn = checkLoggedIn())

################################     Component   ################################

#in order to set it to the global
@app.route("/findNamedSeq", methods = ["POST"])
def findNamedSeq():
    currUser = getCurrUser()
    #get data
    try:
        nsID = request.form["NSid"]

        ns = NamedSequenceDB.query.get(nsID)
        
        if(ns is None):
            outputStr = "ERROR: Sequence does not exist."
        else:
            try:
                checkPermissionNS(ns)

                addToSelected(ns)

                outputStr = ""
                succeeded = True

            except ee.AccessError:
                outputStr = "ERROR: You do not have permission to access this sequence."

            except Exception as e:
                outputStr = str(e)

    except Exception:
        outputStr = "ERROR: Bad input."
        
    return jsonify({"output": outputStr, "succeeded": succeeded})

#really, it's making spacers
@app.route("/findSpacers", methods = ["POST"])
def findSpacers():
    #validation
    validInput = True
    succeeded = False

    #get data
    try:
        spacersData = leval(request.form["spacersData"])
        
        newPosStr = spacersData["componentPos"]
        newTerminalStr = spacersData["isTerminal"]
    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    if(validInput):
        validInput, outputStr, newPos, isTerminal = rf.validateSpacers(newPosStr, newTerminalStr)
    
    #obtain the actual spacers
    if(validInput):
        try:
            #make the SpacerData
            newSpacerData = SpacerData.makeNew(newPos, isTerminal)
            
            #add to outputStr
            if(newPos == 999):
                outputStr += "Spacers found for position T"
            else:
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
    outputStr = ""
    validInput = True
    succeeded = False

    #get form data
    try:
        primersData = leval(request.form["primersData"])
        TMstr = primersData["meltingPoint"]
        rangeStr = primersData["meltingPointRange"]
        skipStr = primersData["skipPrimers"]

    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received."

    #skip primers if relevant
    try:
        skipPrimers = rf.boolJS(skipStr)
    except Exception:
        validInput = False
        outputStr += "ERROR: Skip primers value not true or false.<br>"
    
    #skip primers if so
    if(skipPrimers):
        outputStr += "Chose not to make primers.<br>"
        addToSelected(nullPrimerData)
        
        succeeded = True
        
    elif(validInput):
        #that thrilling data validation
        if(validInput):
            validInput, outputStr, TMnum, rangeNum = rf.validatePrimers(TMstr, rangeStr)
        
        if(validInput):  
            #is there a spacer selected
            selectedSpacers = getSelectedSD()
            if(selectedSpacers == None):
                validInput = False
                outputStr += "ERROR: No spacers selected.<br>"
            
            selectedSpacers = SpacerData.fromJSON(selectedSpacers)

        #find the primers
        if(validInput):
            try:
                seqToEvaluate = getSelectedNS().getSeq()
                newPrimerData = PrimerData.makeNew(seqToEvaluate, TMnum, rangeNum)
                newPrimerData.addSpacerSeqs(selectedSpacers)
                
                if(newPrimerData.getPrimersFound()):
                    #outputStr
                    outputStr += str(newPrimerData).replace("\n", "<br>")
                    
                    #add to session selected
                    addToSelected(newPrimerData)
                    
                    succeeded = True
                    
                else:
                    outputStr += "Couldn't find primers for the specified sequence, melting point, and range.<br>"
            
            except Exception as e:
                outputStr += "ERROR: " + str(e) + "<br>"
    
        if(not succeeded):
            outputStr += "Primers not found."
        
    return jsonify({"output": outputStr, "succeeded": succeeded})

#actually creates the component
@app.route("/finishComponent", methods = ["POST"])
def finishComponent():
    #validation
    validInput = getAllSelected()
    succeeded = False
    newID = -1

    outputStr = ""
    
    if(validInput):
        try:
            currUser = getCurrUser()
            selectedNS = getSelectedNS()
            selectedSpacers = SpacerData.fromJSON(getSelectedSD())
            selectedPrimers = PrimerData.fromJSON(getSelectedPD())
            
            #check if it already exists in defaults
            try:
                defaultUser.findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise ee.AlreadyExistsError("Component already exists as a default component.")
            except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                pass
            
            #check if it already exists in personal library
            try:
                getCurrUser().findComponent(selectedNS.getType(), selectedNS.getName(), selectedSpacers.getPosition(), selectedSpacers.getTerminalLetter())
                raise ee.AlreadyExistsError("Component already exists as a user-made component.")
            except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                pass
            
            #add NS to personal library if it's not from there
            try:
                tempNS = currUser.addNSDB(selectedNS)
                selectedNS = tempNS
            except ee.AlreadyExistsError:
                pass
    
            newComponent = currUser.createComp(selectedNS, selectedSpacers, selectedPrimers)
            
            #modify output string
            libraryName = "Personal"
            outputStr = "<a target = '_blank' href = '/library#" + libraryName + newComponent.getNameID() + "'>" + newComponent.getNameID() + "</a> created."
            
            #set it as the tempComp (for the ZIP file)
            newID = newComponent.getID()

            succeeded = True
            
        except Exception as e:
            outputStr = "ERROR: " + str(e)

    else:
        outputStr += "ERROR: invalid input."
        
    return jsonify({"output": outputStr, "succeeded": succeeded, "newID": newID})

#domestication ZIP file
@app.route("/newComponent.zip")
def newCompZIP():
    try:
        newCompID = request.args.get("id")
        comp = ComponentDB.query.get(newCompID)
        checkPermission(comp)
        compZIP = comp.getCompZIP()

        data = rf.makeZIP(compZIP)

    except Exception as e:
        print("FAILED TO CREATE ZIP BECAUSE: " + str(e))
        return errorZIP(e)
    
    if(data == None):
        return errorZIP("No/invalid component to create a ZIP from.")


    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})

################################     Sequence    ################################
@app.route("/newNamedSeq", methods = ["POST"])
def newNamedSeq():
    outputStr = ""
    validInput = True
    succeeded = False

    #get data
    try:
        newNSData = leval(request.form["newNSData"])

        newNSType = newNSData["NStype"]
        newNSName = newNSData["NSname"]
        newNSSeq = newNSData["NSseq"].upper()

    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    #validation
    if(validInput):
        validInput, outputStr = rf.validatenewNS(newNSType, newNSName, newNSSeq)
    
    #finish validation
    if(validInput):
        try:
            getCurrUser().createNS(newNSType, newNSName, newNSSeq)

            libraryName = "Personal"

            outputStr += "Successfully created <a target = '_blank' href = '/library#{libraryName}{NSname}'>{NSname}</a>.".format(libraryName = libraryName,
                                                                                                                    NSname = newNSName)
            
            succeeded = True
            
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"
            
    if(not succeeded):
        outputStr += "Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})


################################     Backbone    ################################
@app.route("/newBackbone", methods = ["POST"])
def newBackbone2():
    outputStr = ""
    validInput = True
    succeeded = False

    try:
        backboneData = leval(request.form["newBackboneData"])

        BBname = backboneData["backboneName"]
        BBdesc = backboneData["backboneDesc"]
        BBseq = backboneData["backboneSeq"]
        BBtype = backboneData["backboneType"]
        BBfeatures = backboneData["backboneFeatures"]

    except Exception as e:
        print(e)
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    if(validInput):
        try:
            getCurrUser().findBackbone(BBname)
            outputStr = "ERROR: Backbone {name} already exists in your personal library.".format(name = BBname)
            validInput = False
        except ee.BackboneNotFoundError:
            pass            

    #general validation
    if(validInput):
        validInput, outputStr = rf.validateBackbone(BBname, BBdesc, BBseq, BBtype, BBfeatures)

    #validation of the sequence & features
    if(validInput):
        outputStr, validInput, BBdata = rf.processGBfeatures(BBseq, BBfeatures.splitlines(keepends = True), outputStr)
    
        seqBefore = BBdata["seqBefore"]
        seqAfter = BBdata["seqAfter"]
        features = BBdata["featureSection"]
    
    if(validInput):
        try:
            getCurrUser().createBackbone(BBname, BBtype, BBdesc, seqBefore, seqAfter, features)

            libraryName = "Personal"

            outputStr += "Successfully created <a target = '_blank' href = '/library#{libraryName}{BBname}Backbone'>{BBname}</a>.".format(
                                                                                        libraryName = libraryName,                                                                                        BBname = BBname)
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: {}<br>".format(e)

    
    return jsonify({"output": outputStr, "succeeded": succeeded})

@app.route("/backbonePreview", methods = ["POST"])
def backbonePreview():
    outputStr = ""
    validInput = True
    succeeded = False

    featureStr = ""


    try:
        previewData = leval(request.form["previewData"])
        #maybe evaluate the length of the thing before evaluating it? Because apparently leval could crash python if it's too much
        
        #remove all empty ones    
        keyList = list(previewData.keys())
        
        if(len(keyList) >= 64):
            validInput = False
            outputStr += "ERROR: only 64 features are allowed.<br>"
        
        for key in keyList:
            if(previewData[key] == {}):
                del previewData[key]
            int(key) #ensures all keys are integers
                
        print(previewData)
    except Exception as e:
        validInput = False
        print(e)
        outputStr = "ERROR: Invalid input received.<br>"
    
    if(validInput):
    
        allMolTypes = {"genomicDNA": "genomic DNA", "genomicRNA": "genomic RNA", "mRNA": "mRNA", "tRNA": "tRNA", "rRNA": "rRNA", "otherRNA": "other RNA", "otherDNA": "other DNA", "transcribedRNA": "transcribed RNA", "viralcRNA": "viral cRNA", "unassignedDNA": "unassigned DNA", "unassignedRNA": "unassigned RNA"}
        try:
            for key in previewData.keys():
                field = previewData[key]
                featType = field["featureType" + key]
                
                #get locations
                if(featType == "origin"):
                    locOrig = int(field["locationOrigin" + key])
                    if(locOrig < 1):
                        validInput = False
                        outputStr += "ERROR: origin location must be at least 1.<br>"
                        
                else:
                    locStart =  int(field["locationStart" + key])
                    locEnd =  int(field["locationEnd" + key])
                    
                    if(locStart < 1 or locEnd < 1):
                        outputStr += "ERROR: locations for feature #{} must be at least 1.<br>".format(key)
                    
                    if(locStart > locEnd):
                        validInput = False
                        outputStr += "ERROR: start location for feature #{} is greater than its end location.<br>".format(key)
                    
                #add to the featureStr
                if(featType == "origin"):
                    
                    featureStr += "\trep_origin\t{orig}\n".format(orig = locOrig)
                    
                    direction = False
                    
                    try:
                        direction = field["direction" + key]
                    except Exception:
                        pass
                    
                    if(direction):
                        if(direction not in ["left", "right", "both"]):
                            raise Exception("invalid direction {}".format(direction))
                        else:
                            featureStr += "\t\t\t/direction={direction}\n".format(direction = direction)
                    
                elif(featType == "source"):
                    organism = field["organism" + key]
                    molType = field["molType" + key]
                    
                    if(len(organism) > 64):
                        validInput = False
                        outputStr += "ERROR: organism name must be at most 64 characters long.<br>"
                    
                    molLong = allMolTypes[molType]
                    
                    featureStr += "\tsource\t\t{start}..{end}\n\t\t\t/organism=\"{organism}\"\n\t\t\t/mol_type=\"{molLong}\"\n".format(
                                    start = locStart,
                                    end = locEnd,
                                    organism = organism,
                                    molLong = molLong)
                    
                elif(featType == "CDS"):
                    gene = field["geneName" + key]
                    
                    if(len(gene) > 64):
                        validInput = False
                        outputStr += "ERROR: gene name must be at most 64 characters long.<br>"
                    
                    featureStr += "\tCDS\t\t{start}..{end}\n\t\t\t/gene=\"{geneName}\"\n".format(
                            start = locStart,
                            end = locEnd,
                            geneName = gene)
                    
                elif(featType == "misc"):
                    note = field["miscNote" + key]
                    
                    if(len(note) > 1024):
                        validInput = False
                        outputStr += "ERROR: note must be at most 1024 characters long.<br>"
                    
                    featureStr += "\tmisc_feature\t{start}..{end}\n\t\t\t/note=\"{note}\"\n".format(
                            start = locStart,
                            end = locEnd,
                            note = note)
                    
                else:
                    raise Exception("invalid featType {}".format(featType))

        except Exception as e:
            validInput = False
            print(e)
            outputStr = "ERROR: Invalid input received.<br>"
        
        if(validInput):
            succeeded = True
            #temp = featureStr.replace("\n", "<br>")
            #temp = temp.replace("\t", "&emsp;&emsp;&emsp;&emsp;")
            #outputStr += "<pre>" + temp + "</pre>"
            print(featureStr)
        
    return jsonify({"output": outputStr, "succeeded": succeeded, "featureStr": featureStr})#.replace("\n", "<br>")})

@app.route("/backboneFileProcess", methods = ["POST"])
def backboneFile():
    outputStr = ""
    validInput = True
    succeeded = False
    featureSection = ""
    sequenceOutput = ""
    definition = ""
    name = ""

    try:
        backboneData = request.data
        size = int(request.args.get("size"))
    except Exception as e:
        validInput = False
        print(e)
        outputStr = "ERROR: Invalid input received."
    
    if(validInput):
        try:
            #check the size of the data received & size of the data sent are the same
            if(len(backboneData) != size):
                raise Exception("File was not completely uploaded to server. Please try again.")
                        
            #otherwise
            outputStr, validInput, fileData = rf.readBackboneGB(backboneData, outputStr)
            
            name = fileData["name"]
            definition = fileData["definition"]
            featureSection = fileData["features"]
            sequenceOutput = fileData["sequence"]
            
            succeeded = True
                        
        except Exception as e:
            validInput = False
            print(e)
            outputStr = "ERROR: {}".format(e)
    
    return jsonify({"output": outputStr, "succeeded": succeeded, "featureStr": featureSection,
                    "sequence": sequenceOutput, "definition": definition,
                    "name": name})

##############################   ASSEMBLY  ##############################
##############################################################################
    
#the page for assembly
@app.route("/assemble", methods = ["POST", "GET"])
@login_required
def assemble():    
    allDefaultNS = defaultUser.getSortedNS()
    allSessionNS = getCurrUser().getSortedNS()
    
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
    
    #list of backbones & IDs
    availableBackbones = {"i": [], "r": []}
    backboneDescs = {}
    for BB in defaultUser.getSortedBB():
        availableBackbones[BB.getType()].append([BB.getID(), BB.getName()])
        backboneDescs[BB.getID()] = BB.getDesc()
    for BB in getCurrUser().getSortedBB():
        availableBackbones[BB.getType()].append([BB.getID(), BB.getName()])
        backboneDescs[BB.getID()] = BB.getDesc()

    seqElements = [["Pr", "Promoter"], ["RBS", "RBS"], ["GOI", "Gene"], ["Term", "Terminator"]]

    return render_template("assembly.html", fidelities = fidelities,
                           fidelityLimits = fidelityLimits,
                           availableElements = allAvailableNames, 
                           posTermComb = posTerminalComb,
                           availableBackbones = availableBackbones,
                           backboneDescs = backboneDescs,
                           seqElements = seqElements,
                           loggedIn = checkLoggedIn())

#process assembly
@app.route("/processAssembly", methods = ["POST"])
def processAssembly():
    outputStr = ""
    validInput = True
    succeeded = True

    #get info.
    try:
        formData = request.form["assemblyData"]
        dataDict = leval(formData)
    except Exception:
        validInput = False
        outputStr = "ERROR: bad input."

    if(validInput):
        #Validation where?
        
        if(printActions):
            print("ASSEMBLING SEQUENCE FROM:\n{}".format(dataDict))
        
        outputStr = "Backbone:<br>"

        #get the backbone
        try:
            bbID = int(dataDict["backbone"])

            bb = BackboneDB.query.get(bbID)

            if(bb is None):
                validInput = False
                suceeded = False
                outputStr = "ERROR: Could not find backbone."
            else:
                try:
                    checkPermissionBB(bb)

                    user = UserDataDB.query.get(bb.getUserID())

                    if(user.getEmail() == "default"):
                        libraryName = "Default"
                    else:
                        libraryName = "Personal"

                    outputStr += "Found:  <a target = '_blank' href = '/library#{libraryName}{BBname}Backbone'>{BBname}</a><br>".format(
                                                                            BBname = bb.getName(),
                                                                            libraryName = libraryName)

                    session["assemblyBackbone"] = bb.getID()

                except ee.AccessError:
                    validInput = False
                    suceeded = False
                    errorMessage = "ERROR: You do not have permission to use this backbone."
        except Exception as e:
            validInput = False
            suceeded = False
            print(e)

        #remove from the dict. the info. that doesn't need to be processed
        del dataDict["fidelity"]
        del dataDict["backbone"]

        outputStr += "<br>Components:<br>"
        
        #go through the dataDict, creating a difct of all elements, with the keys being the positions:
        gatheredElements = {}
        for key in dataDict.keys():
            number = int(key[8:])
            
            if(number not in gatheredElements.keys()):
                gatheredElements[number] = {}
                
            if(key[0:8] == "elemType"):
                gatheredElements[number]["type"] = dataDict[key]
                
            elif(key[0:8] == "elemName"):
                gatheredElements[number]["name"] = dataDict[key]

        compsList = []

        #find the components of gatheredElements
        for posKey in gatheredElements.keys():
            comp = gatheredElements[posKey]

            if(posKey == 0):
                terminalLetter = "S"
            elif(posKey == 999):
                terminalLetter = "T"
            elif(posKey < (len(dataDict) / 2) - 2):
                terminalLetter = "M"
            else:
                terminalLetter = "L"
                            
            try:
                try:                    #search defaults
                    foundComp = defaultUser.findComponent(comp["type"], comp["name"], posKey, terminalLetter)
                    libraryName = "Default"
                except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):    #search user-made
                    foundComp = getCurrUser().findComponent(comp["type"], comp["name"], posKey, terminalLetter)
                    libraryName = "Personal"
                    
                compsList.append(foundComp.getID())

                outputStr += ("Found: <a target = '_blank' href ='/library#" + libraryName + foundComp.getNameID() + "'>" + 
                              foundComp.getNameID() + "</a><br>")
            except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                outputStr += ("Could not find:<br>Type: " + comp["type"] + "<br>Name: " + comp["name"] + 
                              "<br>Position: " + str(posKey) + "<br>Terminal letter: " + terminalLetter + "<br>")
                
                succeeded = False
    
    #proceed if found everything
    if(succeeded):
        session["assemblyCompIDs"] = compsList
        outputStr += "<br>Full sequence can be downloaded."
        
    else:
        outputStr += "<br>Errors in finding components are often due to not having a component with the right terminal letter.<br>Sequence not created."
    
    return jsonify({"output": outputStr, "succeeded": succeeded})

#get the zip for the assembled sequence
@app.route("/assembledSequence.zip")
def assemblyZIP():
    try:
        compsList = session["assemblyCompIDs"]
        bbID = session["assemblyBackbone"]
    except KeyError:
        return errorZIP("No assembled sequence.")

    try:
        #get the backbone information.
        bb = BackboneDB.query.get(bbID)
        checkPermissionBB(bb)
        
        fullSeq = bb.getSeqBefore()
        
        i = len(fullSeq) #index (starting at zero) of the fullSeq to add at
        
        features = bb.getFeatures().splitlines()

        #add the sequence of the component
        for compID in compsList:
            comp = ComponentDB.query.get(compID)
            checkPermission(comp)

            if(comp.getPosition() == 0):
                fullSeq += comp.getSeq()
                i = rf.addCompAssemblyGB(comp, features, i)
                print("adding {compID} seq".format(compID = comp.getNameID()))

            else:
                fullSeq += comp.getLeftSpacer() + comp.getSeq()
                i = rf.addSpacerAssemblyGB(comp.getLeftSpacer(), features, i)
                print("adding {compID} left spacer: {spacer}".format(compID = comp.getNameID(), spacer = comp.getLeftSpacer()))
                i = rf.addCompAssemblyGB(comp, features, i)
                print("adding {compID} seq".format(compID = comp.getNameID()))

        lengthInsertion = i - len(bb.getSeqBefore())

        #process the features
        for j in range(len(features)):
            featRow = features[j].split("[AddLength]")

            if(len(featRow) > 1):
                for k in range(1, len(featRow), 2):
                    origIndex = int(featRow[k])
                    featRow[k] = str(origIndex + lengthInsertion)

                features[j] = "".join(featRow)

        #finish it off
        fullSeq += bb.getSeqAfter()

        fileGB = rf.finishCompAssemblyGB(features, fullSeq)
        fileFASTA = ">CyanoConstruct assembled sequence\n" + fullSeq

        data = rf.makeZIP({"fullSequence.fasta": fileFASTA, "fullSequence.gb": fileGB})

    except Exception as e:
        return errorZIP(e)
    
    if(data == None):
        return errorZIP("No assembled sequence.")

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})


##############################   LIBRARY   ##############################
@app.route("/components", methods = ["GET"])
def displayComps():
    return redirect("/library")

@app.route("/library", methods = ["GET"])
@login_required
def displayCompLib():

    currUser = getCurrUser()

    allNSandBB = {"Default": defaultUser.getSortedNS(),
            "Personal": currUser.getSortedNS()}

    allNSandBB["Default"]["BB"] = defaultUser.getSortedBB()
    allNSandBB["Personal"]["BB"] = currUser.getSortedBB()

    #used for formatting
    longNames = {"Pr": "Promoters", "RBS": "Ribosome Binding Sites", "GOI": "Genes of Interest", "Term": "Terminators",
                "BB": "Backbones"}

    return render_template("library.html", allNSandBB = allNSandBB,
                           longNames = longNames,
                           loggedIn = checkLoggedIn())


#make and send the ZIP file for a component
@app.route("/componentZIP.zip")
def getComponentZIP():
    try:
        comp = ComponentDB.query.get(request.args.get("id"))

        checkPermission(comp)
        
        compZIP = comp.getCompZIP()

        data = rf.makeZIP(compZIP)

    except Exception as e:
        return errorZIP(e)
    
    if(data == None):
        return errorZIP("No/invalid sequence to create a ZIP from.")
    
    else:
        return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='componentZIP.zip';"})
    
@app.route("/removeComponent", methods = ["POST"])
def removeComponent():

    succeeded = False
    errorMessage = ""

    try:
        compID = request.form["compID"]

        comp = ComponentDB.query.get(compID)

        if(comp is None):
            errorMessage = "Component does not exist."

        else:
            try:
                permissionOwnComp(comp)
                
                getCurrUser().removeFoundComponent(comp)
                
                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this component."
                    
            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."
            
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})

@app.route("/removeSequence", methods = ["POST"])
def removeSequence():
    succeeded = False
    errorMessage = ""

    try:
        nsID = request.form["sequenceID"]

        ns = NamedSequenceDB.query.get(nsID)
        
        if(ns is None):
            errorMessage = "Sequence does not exist."
        else:
            try:
                permissionOwnNS(ns)

                getCurrUser().removeFoundSequence(ns)

                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this sequence."

            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."
            
    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})

@app.route("/removeBackbone", methods = ["POST"])
def removeBackbone():
    succeeded = False
    errorMessage = ""

    try:
        bbID = request.form["backboneID"]

        bb = BackboneDB.query.get(bbID)
        
        print(bb)

        if(bb is None):
            errorMessage = "Backbone does not exist."
        else:
            try:
                permissionOwnBB(bb)

                getCurrUser().removeBackbone(bbID)

                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this backbone."

            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."
            
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
                data = rf.makeAllLibraryZIP(defaultUser)
                succeeded = True
            except Exception as e:
                errorMessage = str(e)
        elif(libraryName == "Personal"):
            try:
                data = rf.makeAllLibraryZIP(getCurrUser())
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
        return errorZIP(errorMessage)


################################################################################
################################################################################



@app.route("/index", methods = ["GET", "POST"])
@app.route("/", methods = ["GET", "POST"])
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

ids as mostly numbers (G00101 ee.g.) (ID which one and Pos (not huge))
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

