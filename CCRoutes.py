#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 14:54:27 2020

@author: Lia Thomson
"""
#get directory containing the cyanoConstruct module
import os
from sys import path as sysPath
filePath = os.path.realpath(__file__)
sysPath.append(filePath.rsplit("/",2)[0]) #this only works for macs and linux lol

#import cyanoConstruct stuff
from cyanoConstruct import CyanoConstructMod as ccm
from cyanoConstruct import app, Component

#flask
from flask import request, render_template, jsonify, Response, session
import json

#session stuff
from uuid import uuid1
from datetime import timedelta

#misc.
from ast import literal_eval as leval
from shutil import rmtree, make_archive

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

def formatOptions(): #nevermind; the csv file isn't formatted well enough to do this
    table = ccm.assemblycode #definitely will want some checking for proper formatting
    
    lastRowBlank = True
    currentType = None
    
    elementTypes = []
    elementNames = {}
    
    for row in table:
        if(row == ["﻿Op Name", "Seq"]): #the first row
            continue
        
        elif(row == ["","\n"]): #blank row
            lastRowBlank = True
            currentType = None #superfluous, but included anyway
            
        elif(row == ["Backbones", "\n"]): #i.e. if all the important info. has been acquired
            break
        
        elif(len(row) == 1): #i.e. it's a sequence
            lastRowBlank = True
            continue
        
        elif(lastRowBlank): #i.e. it's a new type of thing
            lastRowBlank = False
            
            currentType = row[0]
            elementTypes.append(currentType)
            elementNames[currentType] = []
            
        else: #i.e. it's an option            
            elementNames[currentType].append(row[0])
            
    return (elementTypes, elementNames)
"""

def processData(dataDict):
    if(type(dataDict) != dict):
        raise TypeError("dataDict not a dict.")

    #should check the values to make sure they're valid
    
    #extract fidelity and melting point from the dict
    fidelity = dataDict["fidelity"]
    TM = dataDict["meltingPt"]
 
    del dataDict["fidelity"]
    del dataDict["meltingPt"]
        
    #create arrays from dict
    sequence = []
    names = []
    
    for key in dataDict.keys():
        if(key[4] == "T"):          #i.e. an element Type
            sequence.append(dataDict[key])
        elif(key[4] == "N"):        #i.e. an element Name
            names.append(dataDict[key])
        else:
            raise Exception("What is " + key + "?")

    elements = [None for x in range(len(names))]
    
    return ccm.createseq(elements, names, fidelity, TM)


def flattenDicts(d):
    if(type(d) != dict):
        raise TypeError("d not a dict")
        
    ret = []
    flattenCompsFunc(d, ret)
    return ret

def flattenCompsFunc(d, array):
    for key in d:
        if(type(d[key]) == dict):
            flattenCompsFunc(d[key], array)
        else:
            array.append(d[key])

def addToComps(comp, allComps):
    try:
        allComps[comp.elemType][comp.name][comp.position][comp.terminalLetter] = comp
    except KeyError:
        allComps[comp.elemType][comp.name] = {comp.position: {comp.terminalLetter: comp}}


startEndComps = [None, None]


def makeDefaults(currentAllComps):
    promoter = Component.Component("psbA", "ATTTAGCGTCTTCTAATCCAGTGTAGACAGTAGTTTTGGCTCCGTTGAGCACTGTAGCCTTGGGCGATCGCTCTAAACATTACATAAATTCACAAAGTTTTCGTTACATAAAAATAGTGTCTACTTAGCTAAAAATTAAGGGTTTTTTACACCTTTTTGACAGTTAATCTCCTAGCCTAAAAAGCAAGAGTTTTTAACTAAGACTCTTGCCCTTTACAACCTC",
                                   "Pr", False, 0, 41.0, True, "0")
    terminator = Component.Component("T1", "ATTTGTCCTACTCAGGAGAGCGTTCACCGACAAACAACAGATAAAACGAAAGGCCCAGTCTTTCGACTGAGCCTTTCGTTTTATTTG",
                                     "Term", False, 999, 41.0, True, "T")
    addToComps(promoter, currentAllComps)
    addToComps(terminator, currentAllComps)
    
    global startEndComps
    startEndComps[0] = promoter
    startEndComps[1] = terminator

def makeMore(currentAllComps):
    S3 = Component.Component("S3", "AGTCAAGTAGGAGATTAATTCAATG", "RBS", False, 1, 41.0, True)
    A = Component.Component("A", "AACAAAATGAGGAGGTACTGAGATG", "RBS", False, 1, 40.0, True)
    
    adh2 = Component.Component("adh", "ATGCATATTAAAGCCTACGCTGCCCTGGAAGCCAACGGAAAACTCCAACCCTTTGAATACGACCCCGGTGCCCTGGGTGCTAATGAGGTGGAGATTGAGGTGCAGTATTGTGGGGTGTGCCACAGTGATTTGTCCATGATTAATAACGAATGGGGCATTTCCAATTACCCCCTAGTGCCGGGTCATGAGGTGGTGGGTACTGTGGCCGCCATGGGCGAAGGGGTGAACCATGTTGAGGTGGGGGATTTAGTGGGGCTGGGTTGGCATTCGGGCTACTGCATGACCTGCCATAGTTGTTTATCTGGCTACCACAACCTTTGTGCCACGGCGGAATCGACCATTGTGGGCCACTACGGTGGCTTTGGCGATCGGGTTCGGGCCAAGGGAGTCAGCGTGGTGAAATTACCTAAAGGCATTGACCTAGCCAGTGCCGGGCCCCTTTTCTGTGGAGGAATTACCGTTTTCAGTCCTATGGTGGAACTGAGTTTAAAGCCCACTGCAAAAGTGGCAGTGATCGGCATTGGGGGCTTGGGCCATTTAGCGGTGCAATTTCTCCGGGCCTGGGGCTGTGAAGTGACTGCCTTTACCTCCAGTGCCAGGAAGCAAACGGAAGTGTTGGAATTGGGCGCTCACCACATACTAGATTCCACCAATCCAGAGGCGATCGCCAGTGCGGAAGGCAAATTTGACTATATTATCTCCACTGTGAACCTGAAGCTTGACTGGAACTTATACATCAGCACCCTGGCGCCCCAGGGACATTTCCACTTTGTTGGGGTGGTGTTGGAGCCTTTGGATCTAAATCTTTTTCCCCTTTTGATGGGACAACGCTCCGTTTCTGCCTCCCCAGTGGGTAGTCCCGCCACCATTGCCACCATGTTGGACTTTGCTGTGCGCCATGACATTAAACCCGTGGTGGAACAATTTAGCTTTGATCAGATCAACGAGGCGATCGCCCATCTAGAAAGCGGCAAAGCCCATTATCGGGTAGTGCTCAGCCATAGTAAAAATTAG",
                               "GOI", False, 2, 41.0, True)
    adh3 = Component.Component("adh", "ATGCATATTAAAGCCTACGCTGCCCTGGAAGCCAACGGAAAACTCCAACCCTTTGAATACGACCCCGGTGCCCTGGGTGCTAATGAGGTGGAGATTGAGGTGCAGTATTGTGGGGTGTGCCACAGTGATTTGTCCATGATTAATAACGAATGGGGCATTTCCAATTACCCCCTAGTGCCGGGTCATGAGGTGGTGGGTACTGTGGCCGCCATGGGCGAAGGGGTGAACCATGTTGAGGTGGGGGATTTAGTGGGGCTGGGTTGGCATTCGGGCTACTGCATGACCTGCCATAGTTGTTTATCTGGCTACCACAACCTTTGTGCCACGGCGGAATCGACCATTGTGGGCCACTACGGTGGCTTTGGCGATCGGGTTCGGGCCAAGGGAGTCAGCGTGGTGAAATTACCTAAAGGCATTGACCTAGCCAGTGCCGGGCCCCTTTTCTGTGGAGGAATTACCGTTTTCAGTCCTATGGTGGAACTGAGTTTAAAGCCCACTGCAAAAGTGGCAGTGATCGGCATTGGGGGCTTGGGCCATTTAGCGGTGCAATTTCTCCGGGCCTGGGGCTGTGAAGTGACTGCCTTTACCTCCAGTGCCAGGAAGCAAACGGAAGTGTTGGAATTGGGCGCTCACCACATACTAGATTCCACCAATCCAGAGGCGATCGCCAGTGCGGAAGGCAAATTTGACTATATTATCTCCACTGTGAACCTGAAGCTTGACTGGAACTTATACATCAGCACCCTGGCGCCCCAGGGACATTTCCACTTTGTTGGGGTGGTGTTGGAGCCTTTGGATCTAAATCTTTTTCCCCTTTTGATGGGACAACGCTCCGTTTCTGCCTCCCCAGTGGGTAGTCCCGCCACCATTGCCACCATGTTGGACTTTGCTGTGCGCCATGACATTAAACCCGTGGTGGAACAATTTAGCTTTGATCAGATCAACGAGGCGATCGCCCATCTAGAAAGCGGCAAAGCCCATTATCGGGTAGTGCTCAGCCATAGTAAAAATTAG",
                               "GOI", True, 2, 41.0, True)
    
    pdc = Component.Component("pdc", "ATGCATAGTTATACTGTCGGTACCTATTTAGCGGAGCGGCTTGTCCAGATTGGTCTCAAGCATCACTTCGCAGTCGCGGGCGACTACAACCTCGTCCTTCTTGACAACCTGCTTTTGAACAAAAACATGGAGCAGGTTTATTGCTGTAACGAACTGAACTGCGGTTTCAGTGCAGAAGGTTATGCTCGTGCCAAAGGCGCAGCAGCAGCCGTCGTTACCTACAGCGTTGGTGCGCTTTCCGCATTTGATGCTATCGGTGGCGCCTATGCAGAAAACCTTCCGGTTATCCTGATCTCCGGTGCTCCGAACAACAACGACCACGCTGCTGGTCATGTGTTGCATCATGCTCTTGGCAAAACCGACTATCACTATCAGTTGGAAATGGCCAAGAACATCACGGCCGCCGCTGAAGCGATTTACACCCCGGAAGAAGCTCCGGCTAAAATCGATCACGTGATCAAAACTGCTCTTCGCGAGAAGAAGCCGGTTTATCTCGAAATCGCTTGCAACACTGCTTCCATGCCCTGCGCCGCTCCTGGACCGGCAAGTGCATTGTTCAATGACGAAGCCAGCGACGAAGCATCCTTGAATGCAGCGGTTGACGAAACCCTGAAATTCATCGCCAACCGCGACAAAGTTGCCGTCCTCGTCGGCAGCAAGCTGCGCGCTGCTGGTGCTGAAGAAGCTGCTGTTAAATTCACCGACGCTTTGGGCGGTGCAGTGGCTACTATGGCTGCTGCCAAGAGCTTCTTCCCAGAAGAAAATGCCAATTACATTGGTACCTCATGGGGCGAAGTCAGCTATCCGGGCGTTGAAAAGACGATGAAAGAAGCCGATGCGGTTATCGCTCTGGCTCCTGTCTTCAACGACTACTCCACCACTGGTTGGACGGATATCCCTGATCCTAAGAAACTGGTTCTCGCTGAACCGCGTTCTGTCGTTGTCAACGGCATTCGCTTCCCCAGCGTTCATCTGAAAGACTATCTGACCCGTTTGGCTCAGAAAGTTTCCAAGAAAACCGGTTCTTTGGACTTCTTCAAATCCCTCAATGCAGGTGAACTGAAGAAAGCCGCTCCGGCTGATCCGAGTGCTCCGTTGGTCAACGCAGAAATCGCCCGTCAGGTCGAAGCTCTTCTGACCCCGAACACGACGGTTATTGCTGAAACCGGTGACTCTTGGTTCAATGCTCAGCGCATGAAGCTCCCGAACGGTGCTCGCGTTGAATATGAAATGCAGTGGGGTCACATTGGTTGGTCCGTTCCTGCCGCCTTCGGTTATGCCGTCGGTGCTCCGGAACGTCGCAACATCCTCATGGTTGGTGATGGTTCCTTCCAGCTGACGGCTCAGGAAGTTGCTCAGATGGTTCGCCTGAAACTGCCGGTTATCATCTTCTTGATCAATAACTATGGTTACACCATCGAAGTTATGATCCATGATGGTCCGTACAACAACATCAAGAACTGGGATTATGCCGGTCTGATGGAAGTGTTCAACGGTAACGGTGGTTATGACAGCGGTGCTGCTAAAGGCCTGAAGGCTAAAACCGGTGGCGAACTGGCAGAAGCTATCAAGGTTGCTCTGGCAAACACCGACGGCCCAACCCTGATCGAATGCTTCATCGGTCGTGAAGACTGCACTGAAGAATTGGTCAAATGGGGTAAGCGCGTTGCTGCCGCCAACAGCCGTAAGCCTGTTAACAAGCTCCTCTAG",
                              "GOI", True, 3, 42.0, True)
    
    addToComps(S3, currentAllComps)
    addToComps(A, currentAllComps)
    addToComps(adh2, currentAllComps)
    addToComps(adh3, currentAllComps)
    addToComps(pdc, currentAllComps)
    
#############################################

printActions = True

currentAllComps = {"Pr" : {}, "RBS": {}, "GOI": {}, "Term": {}}

#load with some defaults
makeDefaults(currentAllComps)
makeMore(currentAllComps)

tempComp = None


@app.route("/makeComponent", methods = ["POST"], endpoint = "makeComponent")
def makeComponent():
    if(printActions):
        print("MAKING COMPONENT")

    #get form data from the web page
    stuff = request.form["bigData"]
    dataDict = leval(stuff)

    name = dataDict["componentName"]
    seq = dataDict["componentSeq"].upper() #need to transform to all caps & check if it's only ATGC
    elemType = dataDict["componentType"]
    position = int(dataDict["componentPos"])
    TM = float(dataDict["componentTM"])
        
    if(dataDict["componentTerminal"] == "true"):
        terminal = True
    else:
        terminal = False
    
    #create component
    a = Component.Component(name, seq, elemType, terminal, position, TM)

    #output text
    output = "Created:<br>" + str(a)
    output += "<br><br>Complete sequence:<br>" + a.getFullSeq()
    output += "<br>Left primer:<br>" + a.leftPrimer
    output += "<br>Right primer:<br>" + a.rightPrimer
    output = output.replace("\n", "<br>")
    
    global tempComp
    tempComp = a
    #need to store in temp. variable before it's actually confirmed
    #a.setID()
    #addToComps(a, currentAllComps) #need to store in session or something

    if(printActions):
        print("COMPONENT DONE")
        
    return jsonify({"output": output})

@app.route("/confirmCreation", methods = ["POST"])
def confirmCreation():
    global tempComp
    if(tempComp == None):
        output = "Nothing to create."
    elif(tempComp == "Done"):
        output = "Already created component."
    elif(type(tempComp) == Component.Component):
        tempComp.setID()
        addToComps(tempComp, currentAllComps)
        output = "Created component " + tempComp.idStr
        
        tempDict = {}
        tempDict[tempComp.idStr + "-LeftPrimer.fasta"] = ">" + tempComp.idStr + " " + tempComp.getLongName() + " left primer\n" + tempComp.leftPrimer
        tempDict[tempComp.idStr + "-RightPrimer.fasta"] = ">" + tempComp.idStr + " " + tempComp.getLongName() + " right primer\n" +tempComp.rightPrimer
        tempDict[tempComp.idStr + "-FullSeq.fasta"] = ">" + tempComp.idStr + " " + tempComp.getLongName() + " full sequence\n" +tempComp.getFullSeq()

        session["submissionID"] = uuid1().hex        
        session["compFiles"] = tempDict
        session.modified = True

        tempComp = "Done"

    else:
        output = "ERROR"
    
    return jsonify({"output": output})

@app.route("/domesticate", methods = ["POST", "GET"], endpoint = "domesticate")
def domesticate():
    return render_template("untitled.html")

@app.route("/assemble", methods = ["POST", "GET"])
def assemble():
    #dict of all components
    allAvailableNames = {"Pr": [], "RBS": [], "GOI": [], "Term": []}
    for key in allAvailableNames.keys():
        allAvailableNames[key] = list(currentAllComps[key].keys())
        
    #dictionary of all component names sorted by position
    allComponentsPosition = {}
    for outerKey in currentAllComps.keys():
        for innerKey in currentAllComps[outerKey].keys(): #this is Sub Ideal if mult. comps have same name      
            allComponentsPosition[innerKey] = list(currentAllComps[outerKey][innerKey].keys())
        
    #dictionary of all valid terminators
    validTerminals = {"Pr": [], "RBS": [], "GOI": [], "Term": []}
    for typeKey in currentAllComps.keys():
        for nameKey in currentAllComps[typeKey].keys():
            for positionKey in currentAllComps[typeKey][nameKey]:
                try:
                    if(currentAllComps[typeKey][nameKey][positionKey]["T"] != []):
                        validTerminals[typeKey].append(nameKey)
                except KeyError:
                    continue
        
    #list of fidelities
    fidelities = ["98.5%", "98.1%", "95.8%", "91.7%", "random"]
    fidelityLimits = {"98.5%": 2, "98.1%": 3, "95.8%": 5, "91.7%": 10, "random": 20}
    
    return render_template("assembly2.html", fidelities = fidelities,
                           fidelityLimits = fidelityLimits,
                           availableElements = allAvailableNames, 
                           componentsPosition = allComponentsPosition,
                           validTerminals = validTerminals)

@app.route("/process2", methods = ["POST"])
def process2():
    stuff = request.form["bigData"]
    dataDict = leval(stuff)
    
    print(dataDict)
    
    del dataDict["fidelity"]
    del dataDict["elemName0"]
    del dataDict["elemType0"]
    del dataDict["elemName999"]
    del dataDict["elemType999"]
    
    thingy = [] #collection of them
    for key in dataDict.keys():
        number = int(key[8:])
        
        if number > len(thingy):
            thingy.append({"position": number})
            
        if(key[0:8] == "elemType"):
            thingy[number - 1]["type"] = dataDict[key]
            
        elif(key[0:8] == "elemName"):
            thingy[number - 1]["name"] = dataDict[key]

    componentsFound = ""

    allOkay = True
    compsList = []

    for comp in thingy:
        if(comp["position"] < len(dataDict) / 2):
            terminalLetter = "M"
        else:
            terminalLetter = "T"
                        
        try:
            foundComp = currentAllComps[comp["type"]][comp["name"]][comp["position"]][terminalLetter]
            compsList.append(foundComp)
            componentsFound += "found: " + foundComp.idStr + "<br>"
        except KeyError:
            componentsFound += "could not find: " + str(comp) + "terminal letter: " + terminalLetter + "<br>"
            allOkay = False
        
    fullSeq = startEndComps[0].getFullSeq()
    
    if(allOkay):
        for comp in compsList:
            componentsFound += "<br>" + comp.idStr + ":<br>" + comp.getFullSeq()
            
            fullSeq += comp.getFullSeq()
            
    fullSeq += startEndComps[1].getFullSeq()
    
    session["submissionID"] = uuid1().hex       #used to name submission files
    session["producedFiles"] = {"fullSequence.fasta": ">Cyano'Construct Sequence\n" + fullSeq}
    session.modified = True
    
    componentsFound += "<br><br>Full sequence:<br>"  + fullSeq
    
    return jsonify({"output": componentsFound})


@app.route("/components", methods = ["GET"])
def displayComps():
    retString = "All Components:<br>"
    for comp in flattenDicts(currentAllComps):
        retString += comp.idStr + "<br>"
        retString += str(comp)
        retString += "<hr>"
    retString = retString.replace("\n", "<br>")

    return render_template("components.html", components = retString)

@app.route("/sequencesZip2.zip") #is this a good name?
def sequencesZip2():
    if(printActions):
        print("CREATING FASTA AND ZIP FILES")

    #get producedFiles
    filesDict = session["producedFiles"]
    
    #check if no files have been produced
    if(filesDict == {}):
        if(printActions):
            print("NO SEQUENCE; NO FILES CREATED")
        return render_template("noSeq.html")
    
    #paths
    filesDirPath = filePath.rsplit("/", 1)[0] + "/files"
    sessionDir = filesDirPath + "/" + session["submissionID"]    
    os.mkdir(sessionDir)
    
    print("MADE DIRECTORY: " + sessionDir)    
    
    #write files
    for filename in filesDict:
        newName = sessionDir + "/" + filename
        with open(newName, "w") as f:
            f.write(filesDict[filename])
            
    #make zip
    zipPath = filesDirPath + "/zips/" + session["submissionID"]    
    make_archive(zipPath, "zip", sessionDir)
    
    #read zip as a byte file
    with open(zipPath + ".zip", "rb") as f:  #this is likely inefficient
        data = f.readlines()
    
    #delete the session directory & zip file
    rmtree(sessionDir)
    os.remove(zipPath + ".zip")
    
    if(printActions):
        print("FINISHED CREATING FILES FOR SUBMISSION " + session["submissionID"])

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})

@app.route("/componentSequences.zip") #is this a good name?
def componentSequences():
    if(printActions):
        print("CREATING FASTA AND ZIP FILES")

    #get producedFiles
    try:
        filesDict = session["compFiles"]
    except KeyError:
        print("NO COMPONENT; NO FILES CREATED")
        return render_template("noSeq.html")
    
    #check if no files have been produced
    if(filesDict == {}):
        if(printActions):
            print("NO SEQUENCE; NO FILES CREATED")
        return render_template("noSeq.html")
    
    #paths
    filesDirPath = filePath.rsplit("/", 1)[0] + "/files"
    sessionDir = filesDirPath + "/" + session["submissionID"]    
    os.mkdir(sessionDir)
        
    #write files
    for filename in filesDict:
        newName = sessionDir + "/" + filename
        with open(newName, "w") as f:
            f.write(filesDict[filename])
            
    #make zip
    zipPath = filesDirPath + "/zips/" + session["submissionID"]    
    make_archive(zipPath, "zip", sessionDir)
    
    #read zip as a byte file
    with open(zipPath + ".zip", "rb") as f:  #this is likely inefficient
        data = f.readlines()
    
    #delete the session directory & zip file
    rmtree(sessionDir)
    os.remove(zipPath + ".zip")
    
    if(printActions):
        print("FINISHED CREATING FILES FOR SUBMISSION " + session["submissionID"])

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})

    
##



@app.route("/process", methods = ["POST"], endpoint = "process")
def process():
    if(printActions):
        print("PROCESSING DATA")

    #get form data from the web page
    stuff = request.form["bigData"]

    #transform data into a dictionary
    dataDict = leval(stuff)
    
    #process
    output, fileContents = processData(dataDict)
    
    #modify output text to display properly in HTML
    output = output.strip()
    output = output.replace("\n", "<br>")
    
    #set session data
    session["submissionID"] = uuid1().hex       #used to name submission files
    session["producedFiles"] = fileContents     #dict; keys are names of files, values are contents
    session.modified = True

    if(printActions):    
        print("FINISHED PROCESSING DATA FOR SUBMISSION " + session["submissionID"])
    return jsonify({"output": output})
    
@app.route("/index", methods = ["GET", "POST"], endpoint = "index")
@app.route("/", methods = ["GET", "POST"], endpoint = "index")
def index():
    #initialize session data
    session["submissionID"] = "none"
    session["producedFiles"] = {}
    session.modified = True
    
    #set fidelity options
    fidelities = ["98.5%", "98.1%", "95.8%", "91.7%", "random"]
    
    return render_template("indexCC.html", fidelities = fidelities)

#zip file for download
@app.route("/sequencesZip.zip") #is this a good name?
def sequencesZip():
    if(printActions):
        print("CREATING FASTA AND ZIP FILES")

    #get producedFiles
    filesDict = session["producedFiles"]
    
    #check if no files have been produced
    if(filesDict == {}):
        if(printActions):
            print("NO SEQUENCE; NO FILES CREATED")
        return render_template("noSeq.html")
    
    #paths
    filesDirPath = filePath.rsplit("/", 1)[0] + "/files"
    sessionDir = filesDirPath + "/" + session["submissionID"]    
    os.mkdir(sessionDir)
        
    #write files
    for filename in filesDict:
        newName = sessionDir + "/" + filename
        with open(newName, "w") as f:
            f.write(filesDict[filename])
            
    #make zip
    zipPath = filesDirPath + "/zips/" + session["submissionID"]    
    make_archive(zipPath, "zip", sessionDir)
    
    #read zip as a byte file
    with open(zipPath + ".zip", "rb") as f:  #this is likely inefficient
        data = f.readlines()
    
    #delete the session directory & zip file
    rmtree(sessionDir)
    os.remove(zipPath + ".zip")
    
    if(printActions):
        print("FINISHED CREATING FILES FOR SUBMISSION " + session["submissionID"])

    return Response(data, headers = {"Content-Type": "application/zip",
                                     "Condent-Disposition": "attachment; filename='sequences.zip';"})

#sets session timeout
@app.before_request
def before_request():
    #set sessions to expire 24 hours after being changed
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)
    session.modified = True
    return

#############################################

if __name__ == '__main__':
    #run
    app.run(debug=True)
