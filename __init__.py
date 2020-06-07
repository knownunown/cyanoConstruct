#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: Lia Thomson

cyanoConstruct __init__ file
"""
printActions = True
__version__ = "0.4.2"

#import statements
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate

from cyanoConstruct.config import Config

#Flask app
app = Flask(__name__)
login = LoginManager(app)

app.config.from_object(Config)

#database
db = SQLAlchemy(app, session_options = {"expire_on_commit": False})
migrate = Migrate(app, db)


#import modules
from cyanoConstruct.enumsExceptions import AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, BackboneNotFoundError, NotLoggedInError, AccessError
from cyanoConstruct.database import UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, BackboneDB
db.create_all()
from cyanoConstruct.component import NamedSequence, SpacerData, PrimerData, Component, checkType, nullPrimerData, inverseSeq
maxPosition = SpacerData.getMaxPosition()
from cyanoConstruct.sessionUsers import UserData

try:
    defaultUser = UserData.load("default")
except UserNotFoundError:
    defaultUser = UserData.new("default")

from cyanoConstruct.routesFuncs import boolJS, validateNewNS, validateSpacers, validatePrimers, validateBackbone, addCompAssemblyGB, finishCompAssemblyGB, makeZIP, makeAllLibraryZIP
from cyanoConstruct.routes import *

##yeah
"""for user in UserDataDB.query.all():
	if(user.googleAssoc is None):
		user.googleAssoc = False"""