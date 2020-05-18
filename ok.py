#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 16:13:01 2020

@author: liathomson
"""

from jinja2 import Markup #for HTML display of Component

from cyanoConstruct import db

class UserDataDB(db.Model):
    __tablename__ = "UserData"
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True)
    nextNSidPR = db.Column(db.Integer)
    nextNSidRBS = db.Column(db.Integer)
    nextNSidGOI = db.Column(db.Integer)
    nextNSidTERM = db.Column(db.Integer)
    
    #allNamedSeqs = db.relationship("NamedSequenceDB", backref = "userNS", lazy = "joined")
    #allComponents = db.relationship("ComponentDB", backref = "userC", lazy = "joined")

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
    
    def getNextNSid(self):
        return {"Pr": self.nextNSidPR,
                "RBS": self.nextNSidRBS,
                "GOI": self.nextNSidGOI,
                "Term": self.nextNSidTERM}

    def getAllNamedSeqs(self):
        return NamedSequenceDB.query.filter_by(user_id = self.id)
        #print(self.allNamedSeqs)
        #return self.allNamedSeqs
    
    def getAllComponents(self):
        return ComponentDB.query.filter_by(user_id = self.id)
        #return self.allComponents

class NamedSequenceDB(db.Model):
    __tablename__ = "NamedSequence"
    
    id = db.Column(db.Integer, primary_key = True)
    elemType = db.Column(db.String(4))
    name = db.Column(db.String(20))
    seq = db.Column(db.Text())
    nameID = db.Column(db.Integer)
    
    #user_id = db.Column(db.Integer, db.ForeignKey("UserData.id"))
    user_id = db.Column(db.Integer)

    #components = db.relationship("ComponentDB", backref = "namedSeq", lazy = "joined")
    #misc
    #nextTotalID = {"default": 1}
    
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
    spacerLeft = db.Column(db.String(4)) #4? or bump it up in case?
    spacerRight = db.Column(db.String(4))
    isTerminal = db.Column(db.Boolean)
    terminalLetter = db.Column(db.String(1))
    leftNN = db.Column(db.String(2))
    rightNN = db.Column(db.String(2))

    #uhhhhh
    #comp_id = db.Column(db.Integer, db.ForeignKey("Component.id"))
    comp_id = db.Column(db.Integer)

    def __repr__(self):
        return "<SpacerData {}>".format(self.id)
    
    def __str__(self):
        return "SpacerData: " + str(self.getPosition()) + " " + self.getTerminalLetter()

    #setters
    #def setComp(self, comp):
    #    self.comp = comp

    def setCompID(self, compID):
        self.comp_id = compID

    #them getters
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
        return self.getSpacerLeft() + self.getLeftNN() + SpacerDataDB.start

    def getFullSeqRight(self):
        return SpacerDataDB.end + self.getRightNN() + self.getSpacerRight() #except the complementary probably


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
    
    #comp_id = db.Column(db.Integer, db.ForeignKey("Component.id"))
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
    
    #namedSequence_id = db.Column(db.Integer, db.ForeignKey("NamedSequence.id"))
    #spacerData = db.relationship("SpacerDataDB", uselist = False, backref = "comp")
    #primerData = db.relationship("PrimerDataDB", uselist = False, backref = "comp")

    #the user is just... the user of the named sequence, no?
    #user_id = db.Column(db.Integer, db.ForeignKey("UserData.id"))
    
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
            retStr += " terminal"
        else:
            retStr += " non-terminal"
        
        return retStr

    def getHTMLdisplay(self):
        retStr = "ID: " + str(self.getNameID()) + "<br>"

        retStr += "Position: " + str(self.getPosition()) + "<br>"
        retStr += "Terminal?: " + str(self.getTerminal()) + "<br>"

        retStr += "<br><span class = 'emphasized'>Spacers:</span><br>"
        retStr += "Left: " + self.getLeftSpacer() + "<br>"
        retStr += "Right: " + self.getRightSpacer() + "<br>"
        
        retStr += "<br><span class = 'emphasized'>Primers:</span><br>"
        retStr += "Left primer:<br>GC content: " + str(round(self.getLeftGC() * 100, 4)) + "%<br>TM: " + str(round(self.getLeftTM(), 4)) + "<br>Sequence:<br>" + self.getLeftPrimer() + "<br><br>"
        retStr += "Right primer:<br>GC content: " + str(round(self.getRightGC() * 100, 4)) + "%<br>TM: " + str(round(self.getRightTM(), 4)) + "<br>Sequence:<br>" + self.getRightPrimer() + "<br>"

        return Markup(retStr)
    
    def getCompZIP(self):
        #primers and complete sequence
        retDict = {}
        
        idStr = self.getNameID()
        idStrAndName = self.getNameID() + " (" + self.getName() + ")"
        
        retDict[idStr + "-CompleteSequence.fasta"] = ">" + idStrAndName + " complete sequence\n" + self.getFullSeq()
        retDict[idStr + "-LeftPrimer.fasta"] = ">" + idStrAndName + " left primer\n" + self.getLeftPrimer()
        retDict[idStr + "-RightPrimer.fasta"] = ">" + idStrAndName + " right primer\n" + self.getRightPrimer()
        
        return retDict
    
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
        return self.user_id #could just redirect to the namedSequence.user_id



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