#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: liathomson
"""

#__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from cyanoConstruct.config import Config



app = Flask(__name__)
#login = LoginManager(app)

app.config.from_object(Config)

db = SQLAlchemy(app, session_options={"expire_on_commit": False})
#migrate = Migrate(app, db)

from cyanoConstruct.EnumsExceptions import AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, NotLoggedInError
from cyanoConstruct.ok import UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB
db.create_all()
from cyanoConstruct.ComponentDatabaseVersion import NamedSequence, SpacerData, PrimerData, Component, checkType
from cyanoConstruct.SessionUsers2 import SessionData, UserData
from cyanoConstruct.routes2 import *

#from cyanoConstruct import CyanoConstructMod
#from cyanoConstruct import Component
#from cyanoConstruct import SessionUsers
#from cyanoConstruct import CCDatabase

__version__ = "0.3"