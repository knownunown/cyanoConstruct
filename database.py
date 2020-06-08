#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 16:13:01 2020

@author: Lia Thomson

cyanoConstruct database file (UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB tables)
"""

from jinja2 import Markup #for HTML display of Component
from datetime import datetime #for time in GenBank file
from time import time

from cyanoConstruct import db

EXPIRATIONSECS = 3600 #expires in an hour

class UserDataDB(db.Model):
    __tablename__ = "UserData"
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(254), unique = True)

    googleAssoc = db.Column(db.Boolean, default = False, nullable = False)
    googleID = db.Column(db.Text, unique = True)

    tempPass = db.Column(db.String(32))
    tempExp = db.Column(db.Integer)

    nextNSidPR = db.Column(db.Integer)
    nextNSidRBS = db.Column(db.Integer)
    nextNSidGOI = db.Column(db.Integer)
    nextNSidTERM = db.Column(db.Integer)
    
    def __repr__(self):
        return '<User {}>'.format(self.id)
    
    def incrementID(self, NStype):
        if(type(NStype) != str):
            raise TypeError("NStype not a str")
        
        #I'm very sorry about this
        if(NStype == "Pr"):
            self.nextNSidPR += 1
            return self.nextNSidPR
        elif(NStype == "RBS"):
            self.nextNSidRBS += 1
            return self.nextNSidRBS
        elif(NStype == "GOI"):
            self.nextNSidGOI += 1
            return self.nextNSidGOI
        else:
            self.nextNSidTERM += 1
            return self.nextNSidTERM

    #getters
    def getID(self):
        return self.id
    
    def getEmail(self):
        return self.email

    def getGoogleAssoc(self):
        return self.googleAssoc

    def getGoogleID(self):
        return self.googleID

    def getNextNSid(self):
        return {"Pr": self.nextNSidPR,
                "RBS": self.nextNSidRBS,
                "GOI": self.nextNSidGOI,
                "Term": self.nextNSidTERM}

    def getAllNamedSeqs(self):
        return NamedSequenceDB.query.filter_by(user_id = self.id)
    
    def getAllComponents(self):
        return ComponentDB.query.filter_by(user_id = self.id)

    def getAllBackbones(self):
        return BackboneDB.query.filter_by(user_id = self.id)

    #setters
    def setEmail(self, newEmail):
        self.email = newEmail

    def setGoogleAssoc(self, newValue):
        self.googleAssoc = newValue

    def setGoogleID(self, newID):
        self.googleID = newID

    def setTemp(self, temp):
        self.timeExp = int(time() + EXPIRATIONSECS)
        self.tempPass = temp

    #something
    def compareTemp(self, temp):
        if(time() > self.timeExp):
            #somehow indicate it's too late
            return False
        else:
            return self.tempPass == temp

class NamedSequenceDB(db.Model):
    __tablename__ = "NamedSequence"
    
    id = db.Column(db.Integer, primary_key = True)
    elemType = db.Column(db.String(4))
    name = db.Column(db.String(20))
    seq = db.Column(db.Text())
    nameID = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer)
    
    def __repr__(self):
        return "<NamedSequence " + str(self.getID()) +  ": " + self.getType() + "-" + str(self.getNameID()).zfill(3) + " " + self.getName() + ">"
    
    def __str__(self):
        return "NamedSequence " + self.getType() + "-" + str(self.getNameID()).zfill(3) + ": " + self.getName() + ", " + str(len(self.getAllComponents())) + " components."

    #getters
    def getID(self):
        return self.id
    
    def getUserID(self):
        return self.user_id
    
    def getAllComponents(self):
        return self.getAllComponentsQuery().all()
    
    def getAllComponentsQuery(self):
        return ComponentDB.query.filter_by(namedSequence_id = self.id)
    
    def getType(self):
        return self.elemType
        
    def getName(self):
        return self.name
    
    def getSeq(self):
        return self.seq
    
    def getNameID(self):
        return self.nameID

    def getHTMLdisplay(self):
        longNamesSingular = {"Pr": "Promoter", "RBS": "Ribosome Binding Site", "GOI": "Gene", "Term": "Terminator"}
        longName = longNamesSingular[self.getType()]

        if UserDataDB.query.get(self.getUserID()).getEmail() == "default":
            libraryName = "Default"
            isDefault = True
        else:
            libraryName = "Personal"
            isDefault = False

        retArray = []

        retArray.append("""<div class = "hideableTitle nameTitle" id = "{libraryName}{NSname}">
                    <input class = "titleLeft subtleButton" type = "button" onclick = "toggleDisplay('{libraryName}{NSname}Data'); switchToggleText(this);" value = "Name: {NSname}">
                    <span class = "titleRight monospaced">[Click to show]</span>
                </div>

                <div id = "{libraryName}{NSname}Data" class = "hideableDiv" style = "display: none">

                        <!-- info about the named sequence -->
                        <p>{longName}: {NSname}</p>

                        <p>Sequence:</p>
                        <div class = "sequence monospaced">{NSseq}</div>

                        <br>""".format(libraryName = libraryName,
                                        NSname = self.getName(),
                                        longName = longName,
                                        NSseq = self.getSeq(),
                                        ))

        allComps = self.getAllComponents()
        allComps.sort()

        for comp in allComps:
            retArray.append("""<div class = "hideableTitle compTitle" id = "{libraryName}{compNameID}">
                            <input class = "titleLeft subtleButton" type = "button" onclick = "toggleDisplay('{libraryName}{compNameID}Data'); switchToggleText(this);" value = "ID: {compNameID}">
                            <span class = "titleRight monospaced">[Click to show]</span>
                        </div>

                        <div id = "{libraryName}{compNameID}Data" class = "hideableDiv componentData" style = "display: none">

                            <p>
                                {compHTML}
                            </p>

                            <hr>

                            <p><span class = 'emphasized'>Complete Sequence:</span></p>
                            <div class = "sequence monospaced">
                                {fullSeq}
                            </div>

                            <br>

                            <input type = "button" class = "styledButton" value = "Download Sequences" onclick = "downloadComponentSequence({compID})">""".format(
                                                        libraryName = libraryName,
                                                        compNameID = comp.getNameID(),
                                                        compHTML = comp.getHTMLstr(),
                                                        fullSeq = comp.getFullSeq(),
                                                        compID = comp.getID()
                                                        ))

            if(not isDefault):
                retArray.append("""<br><hr><input type = "button" class = "styledButton" value = "Remove Component" onclick = "removeComponent({compID})">""".format(
                                                                                                compID = comp.getID()))


            retArray.append("""</div><div class = "hideableBottom"></div>""")

        if(not isDefault):
            retArray.append("""<br><hr><input type = "button" class = "styledButton" value = "Remove Sequence" onclick = "removeSequence('{NSID}')">""".format(
                NSID = self.getID()))


        retArray.append("""</div><div class = "hideableBottom"></div>""")

        retStr = "".join(retArray)

        return Markup(retStr)


    #comparisons
    def __eq__(self, other):
        return ((self.getType() == other.getType()) and (self.getNameID() == other.getNameID()))
    
    def __ne__(self, other):
        return ((self.getType() != other.getType()) or (self.getNameID() != other.getNameID()))

    def __lt__(self, other):
        typeOrder = ["Pr", "RBS" "GOI", "Term"]
        selfIndex = typeOrder.index(self.getType())
        otherIndex = typeOrder.index(other.getType())
        
        if(selfIndex == otherIndex):
            return self.getNameID() < other.getNameID()
        else:
            return selfIndex < otherIndex
    
    def __le__(self, other):
        typeOrder = ["Pr", "RBS" "GOI", "Term"]
        selfIndex = typeOrder.index(self.getType())
        otherIndex = typeOrder.index(other.getType())
        
        if(selfIndex == otherIndex):
            return self.getNameID() <= other.getNameID()
        else:
            return selfIndex <= otherIndex
    
    def __gt__(self, other):
        typeOrder = ["Pr", "RBS" "GOI", "Term"]
        selfIndex = typeOrder.index(self.getType())
        otherIndex = typeOrder.index(other.getType())
        
        if(selfIndex == otherIndex):
            return self.getNameID() > other.getNameID()
        else:
            return selfIndex > otherIndex
    
    def __ge__(self, other):
        typeOrder = ["Pr", "RBS" "GOI", "Term"]
        selfIndex = typeOrder.index(self.getType())
        otherIndex = typeOrder.index(other.getType())
        
        if(selfIndex == otherIndex):
            return self.getNameID() >= other.getNameID()
        else:
            return selfIndex >= otherIndex

class SpacerDataDB(db.Model):
    __tablename__ = "SpacerData"

    start = "GAAGAC" #enzyme recog. site?
    end = "GTCTTC"

    
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.SmallInteger)
    spacerLeft = db.Column(db.String(4))
    spacerRight = db.Column(db.String(4))
    isTerminal = db.Column(db.Boolean)
    terminalLetter = db.Column(db.String(1))
    leftNN = db.Column(db.String(2))
    rightNN = db.Column(db.String(2))

    comp_id = db.Column(db.Integer)

    def __repr__(self):
        return "<SpacerData {}>".format(self.id)
    
    def __str__(self):
        return "SpacerData: " + str(self.getPosition()) + " " + self.getTerminalLetter()

    def setCompID(self, compID):
        self.comp_id = compID

    #getters
    def getID(self):
        return self.id
    
    def getCompID(self):
        return self.comp_id
    
    def getPosition(self):
        return self.position

    def getSpacerLeft(self):
        return self.spacerLeft
    
    def getSpacerRight(self):
        return self.spacerRight
    
    def getIsTerminal(self):
        return self.isTerminal
    
    def getTerminalLetter(self):
        return self.terminalLetter

    def getLeftNN(self):
        return self.leftNN
    
    def getRightNN(self):
        return self.rightNN

    def getFullSeqLeft(self):
        return SpacerDataDB.start + self.getLeftNN() + self.getSpacerLeft()

    def getFullSeqRight(self):
        return self.getSpacerRight()  + self.getRightNN() +  SpacerDataDB.end


    #comparisons
    def __eq__(self, other):
        return ((self.getPosition() == other.getPosition()) and (self.getTerminalLetter() == other.getTerminalLetter()))
    
    def __ne__(self, other):
        return ((self.getPosition() != other.getPosition()) or (self.getTerminalLetter() != other.getTerminalLetter()))

    def __lt__(self, other):
        if(self.getPosition() == other.getPosition()):
            letterOrder = ["T", "M", "L"]
            return letterOrder.index(self.getTerminalLetter()) < letterOrder.index(other.getTerminalLetter())
        else:
            return self.getPosition() < other.getPosition()
    
    def __le__(self, other):
        if(self.getPosition() == other.getPosition()):
            letterOrder = ["T", "M", "L"]
            return letterOrder.index(self.getTerminalLetter()) <= letterOrder.index(other.getTerminalLetter())
        else:
            return self.getPosition() <= other.getPosition()
    
    def __gt__(self, other):
        if(self.getPosition() == other.getPosition()):
            letterOrder = ["T", "M", "L"]
            return letterOrder.index(self.getTerminalLetter()) > letterOrder.index(other.getTerminalLetter())
        else:
            return self.getPosition() > other.getPosition()
    
    def __ge__(self, other):
        if(self.getPosition() == other.getPosition()):
            letterOrder = ["T", "M", "L"]
            return letterOrder.index(self.getTerminalLetter()) >= letterOrder.index(other.getTerminalLetter())
        else:
            return self.getPosition() >= other.getPosition()
    

class PrimerDataDB(db.Model):
    __tablename__ = "PrimerData"
    
    id = db.Column(db.Integer, primary_key=True)
    primersFound = db.Column(db.Boolean)
    seqLeft = db.Column(db.Text) #gross
    seqRight = db.Column(db.Text)
    GCleft = db.Column(db.Float)
    GCright = db.Column(db.Float)
    TMleft = db.Column(db.Float)
    TMright = db.Column(db.Float)
    
    comp_id = db.Column(db.Integer)

    def __repr__(self):
        return "<PrimerData {}>".format(self.id)
    
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

    
    #setters
    #def setComp(self, comp):
    #    self.comp = comp
    
    def setCompID(self, compID):
        self.comp_id = compID
    
    #getters
    def getID(self):
        return self.id
    
    def getCompID(self):
        return self.comp_id
    
    
    def getPrimersFound(self):
        return self.primersFound
    
    def getSeqLeft(self):
        return self.seqLeft
    
    def getGCleft(self):
        return self.GCleft
    
    def getTMleft(self):
        return self.TMleft
    
    def getSeqRight(self):
        return self.seqRight
    
    def getGCright(self):
        return self.GCright
    
    def getTMright(self):
        return self.TMright


class ComponentDB(db.Model):
    __tablename__ = "Component"
    
    id = db.Column(db.Integer, primary_key=True)
        
    namedSequence_id = db.Column(db.Integer)
    spacerData_id = db.Column(db.Integer)
    primerData_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return "<Component " + str(self.getID()) + " " + str(self.getNameID()) + " " + self.getName() + ">"
    
    def __str__(self):
        return "Component " +  self.getNameID() + ": " + self.getName()


    #setters
    def setNamedSequenceID(self, newID):
        self.namedSequence_id = newID

    def setSpacerDataID(self, newID):
        self.spacerData_id = newID

    def setPrimerDataID(self, newID):
        self.primerData_id = newID

    def setUserID(self, newID):
        self.user_id = newID


    #complicated getters
    def getFullSeq(self):
        return self.getFullSpacerLeft() + self.getSeq() + self.getFullSpacerRight()
    
    def getLongName(self):
        retStr = self.getType() + " " + self.getName() + " Position: " + str(self.getPosition())
        if(self.getTerminal()):
            retStr += " last"
        else:
            retStr += " not last"
        
        return retStr

    def getHTMLdisplay(self):
        retStr = "ID: " + str(self.getNameID()) + "<br>"

        retStr += "Position: " + str(self.getPosition()) + "<br>"
        retStr += "Last?: " + str(self.getTerminal()) + "<br>"

        retStr += "<br><span class = 'emphasized'>Spacers:</span><br>"
        retStr += "Left: " + self.getLeftSpacer() + "<br>"
        retStr += "Right: " + self.getRightSpacer() + "<br>"
        
        retStr += "<br><span class = 'emphasized'>Primers:</span><br>"
        retStr += "Left primer:<br>GC content: " + str(round(self.getLeftGC() * 100, 4)) + "%<br>TM: " + str(round(self.getLeftTM(), 4)) + "<br>Sequence:<br>" + self.getLeftPrimer() + "<br><br>"
        retStr += "Right primer:<br>GC content: " + str(round(self.getRightGC() * 100, 4)) + "%<br>TM: " + str(round(self.getRightTM(), 4)) + "<br>Sequence:<br>" + self.getRightPrimer() + "<br>"

        return Markup(retStr)
    
    def getHTMLstr(self):
        retStr = "ID: " + str(self.getNameID()) + "<br>"

        retStr += "Position: " + str(self.getPosition()) + "<br>"
        retStr += "Last?: " + str(self.getTerminal()) + "<br>"

        retStr += "<br><span class = 'emphasized'>Spacers:</span><br>"
        retStr += "Left: " + self.getLeftSpacer() + "<br>"
        retStr += "Right: " + self.getRightSpacer() + "<br>"
        
        retStr += "<br><span class = 'emphasized'>Primers:</span><br>"
        retStr += "Left primer:<br>GC content: " + str(round(self.getLeftGC() * 100, 4)) + "%<br>TM: " + str(round(self.getLeftTM(), 4)) + "<br>Sequence:<br>" + self.getLeftPrimer() + "<br><br>"
        retStr += "Right primer:<br>GC content: " + str(round(self.getRightGC() * 100, 4)) + "%<br>TM: " + str(round(self.getRightTM(), 4)) + "<br>Sequence:<br>" + self.getRightPrimer() + "<br>"

        return retStr
    def getCompZIP(self):
        #primers and complete sequence
        retDict = {}
        
        idStr = self.getNameID()
        idStrAndName = self.getNameID() + " (" + self.getName() + ")"
        
        retDict[idStr + "-CompleteSequence.fasta"] = ">" + idStrAndName + " complete sequence\n" + self.getFullSeq()
        retDict[idStr + "-LeftPrimer.fasta"] = ">" + idStrAndName + " left primer\n" + self.getLeftPrimer()
        retDict[idStr + "-RightPrimer.fasta"] = ">" + idStrAndName + " right primer\n" + self.getRightPrimer()
        retDict[idStr + "-CompleteSequence.gb"] = self.getGenBankFile()
        
        return retDict
    
    def getGenBankFile(self):
        #lengths 
        lenSpacerL = 4  #all of these are fixed
        lenSpacerR = 4
        lenNNL = 2
        lenNNR = 2
        lenEnzymeL = 6
        lenEnzymeR = 6
        lenSeq = len(self.getSeq())
        lenTotal = lenSpacerL + lenSpacerR + lenNNL + lenNNR + lenEnzymeL + lenEnzymeR + lenSeq
    
        #date
        date = datetime.today().strftime("%d-%b-%Y")
    
        fileByLines = []
        fileByLines.append("LOCUS\t\t" + self.getNameID() + "\t" + str(lenTotal) + " bp\tDNA\tlinear\t" + date)#the date?
        fileByLines.append("DEFINITION\t" + self.getNameID() + " (" + self.getName() + ") component from CyanoConstruct.")
        fileByLines.append("FEATURES\tLocation/Qualifiers")
        
        i = 0

        #EnzymeLeft
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenEnzymeL))
        fileByLines.append("\t\t\t/note=\"enzyme recog. site (left) (BbsI)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#CFEC67")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#CFEC67")
        i += lenEnzymeL
        
        #NNleft
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenNNL))
        fileByLines.append("\t\t\t/note=\"NN (left)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#62E6D0")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#62E6D0")
        i += lenNNL
        
        #spacerLeft
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenSpacerL))
        fileByLines.append("\t\t\t/note=\"spacer (left)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#E6855F") #color only for Benchling?
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#E6855F")
        i += lenSpacerL
        
        
        #sequence
        if(self.getType() == "GOI"):
            fileByLines.append("\tgene\t\t" + str(i + 1) + ".." + str(i + lenSeq))
            fileByLines.append("\t\t\t/gene=\"" + self.getName() + "\"")
        else:
            regTypes = {"Pr": "promoter", "RBS" : "ribosome_binding_site", "Term": "terminator"}
            regName = regTypes[self.getType()]
            longTypes = {"Pr": "promoter", "RBS" : "RBS", "Term": "terminator"}
            longType = longTypes[self.getType()]
            fileByLines.append("\tregulatory\t" + str(i + 1) + ".." + str(i + lenSeq))
            fileByLines.append("\t\t\t/regulatory_class=" + regName)
            fileByLines.append("\t\t\t/note=\"" + longType + " " + self.getName() + "\"")
        
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#AB81E1")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#AB81E1")
        
        i += lenSeq

        #spacerRight
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenSpacerR))
        fileByLines.append("\t\t\t/note=\"spacer (right)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#E6855F")
        i += lenSpacerL

        #NNright
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenNNR))
        fileByLines.append("\t\t\t/note=\"NN (right)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#62E6D0")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#62E6D0")
        i += lenNNL

        #EnzymeRight
        fileByLines.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + lenEnzymeR))
        fileByLines.append("\t\t\t/note=\"enzyme recog. site (right) (BbsI)\"")
        fileByLines.append("\t\t\t/ApEinfo_fwdcolor=#CFEC67")
        fileByLines.append("\t\t\t/ApEinfo_revcolor=#CFEC67")
        i += lenEnzymeL

        
        #the sequence
        fileByLines.append("ORIGIN")
        
        i = 0 #re-use of i
        
        seq = self.getFullSeq().lower()
        
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
    
            fileByLines.append(line)
    
            i += 1
            
        remainder = len(seq) % 60
        if(remainder != 0): #is not zero
            
            line = str(i * 60 + 1).rjust(9, " ") + " "
            for j in range(remainder):
                line += seq[i * 60 + j]
                if((j + 1) % 10 == 0):
                    line += " "
            
            fileByLines.append(line)
            
        
        #finish file
        fileByLines.append("//")
        
        return "\n".join(fileByLines)
        
    
    #basic getters    
    def getNameID(self):
        nameID = self.getNamedSequence().getNameID()
        retStr = self.getType() + "-" + str(nameID).zfill(3) + "-" + str(self.getPosition()).zfill(3) + self.getTerminalLetter()
        return retStr


    #getters
    def getID(self):
        return self.id
    
    def getNamedSeqID(self):
        return self.namedSequence_id
    
    def getUserID(self):
        return self.user_id



    def getNamedSequence(self):
        return NamedSequenceDB.query.get(self.getNamedSeqID())
    
    def getName(self):
        return self.getNamedSequence().getName()
    
    def getSeq(self):
        return self.getNamedSequence().getSeq()
    
    def getType(self):
        return self.getNamedSequence().getType()



    def getSpacerData(self):
        return SpacerDataDB.query.get(self.spacerData_id)
    
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
        return PrimerDataDB.query.get(self.primerData_id)
        
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

    #comparisons
    def __eq__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() == other.getSpacerData()
        else:
            return False
    
    def __ne__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() != other.getSpacerData()
        else:
            return True

    def __lt__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() < other.getSpacerData()
        else:
            return self.getNamedSequence() < other.getNamedSequence()
    
    def __le__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() <= other.getSpacerData()
        else:
            return self.getNamedSequence() <= other.getNamedSequence()
    
    def __gt__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() > other.getSpacerData()
        else:
            return self.getNamedSequence() > other.getNamedSequence()
        
    def __ge__(self, other):
        if(self.getNamedSequence() == other.getNamedSequence()):
            return self.getSpacerData() >= other.getSpacerData()
        else:
            return self.getNamedSequence() >= other.getNamedSequence()

class BackboneDB(db.Model):
    __tablename__ = "Backbone"

    #gross
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    seq = db.Column(db.Text())

    user_id = db.Column(db.Integer)

    def __repr__(self):
        return "<Backbone {ID} {Name}".format(ID = self.getID(), Name = self.getName())
    
    def __str__(self):
        return "Backbone {Name}".format(Name = self.getName())


    def setUserID(self, newID):
        self.user_id = newID        

    #getters
    def getID(self):
        return self.id
    
    def getUserID(self):
        return self.user_id

    def getName(self):
        return self.name
    
    def getSeq(self):
        return self.seq

    def getHTMLdisplay(self):
        if UserDataDB.query.get(self.getUserID()).getEmail() == "default":
            libraryName = "Default"
            isDefault = True
        else:
            libraryName = "Personal"
            isDefault = False

        retArray = []

        retArray.append("""<div class = "hideableTitle nameTitle" id = "{libraryName}{BBname}Backbone">
                    <input class = "titleLeft subtleButton" type = "button" onclick = "toggleDisplay('{libraryName}{BBname}BackboneData'); switchToggleText(this);" value = "Name: {BBname}">
                    <span class = "titleRight monospaced">[Click to show]</span>
                </div>

                <div id = "{libraryName}{BBname}BackboneData" class = "hideableDiv" style = "display: none">

                        <!-- info about the named sequence -->
                        <p>Backbone: {BBname}</p>

                        <p>Sequence:</p>
                        <div class = "sequence monospaced">{BBseq}</div>

                        <br>""".format(libraryName = libraryName,
                                        BBname = self.getName(),
                                        BBseq = self.getSeq(),
                                        ))


        if(not isDefault):
            retArray.append("""<br><hr><input type = "button" class = "styledButton" value = "Remove Backbone" onclick = "removeBackbone('{BBID}')">""".format(
                BBID = self.getID()))

        retArray.append("""</div><div class = "hideableBottom"></div>""")

        retStr = "".join(retArray)

        return Markup(retStr)

    #comparisons
    def __eq__(self, other):
        return self.getName() == other.getName()

    def __ne__(self, other):
        return self.getName() != other.getName()

    def __lt__(self, other):
        return self.getName() < other.getName()

    def __le__(self, other):
        return self.getName() <= other.getName()
    
    def __gt__(self, other):
        return self.getName() > other.getName()
        
    def __ge__(self, other):
        return self.getName() >= other.getName()
