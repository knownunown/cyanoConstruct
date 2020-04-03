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
sysPath.append(filePath.rsplit("/",2)[0])

#import cyanoConstruct stuff
from cyanoConstruct import CyanoConstructMod as ccm
from cyanoConstruct import app

#flask
from flask import request, render_template, jsonify, Response, session

#session stuff
from uuid import uuid1
from datetime import timedelta

#misc.
from ast import literal_eval as leval
from shutil import rmtree, make_archive

"""
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

#############################################

printActions = True

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
