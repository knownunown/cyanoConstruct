#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: Lia Thomson

cyanoConstruct __init__ file
"""
printActions = True
__version__ = "0.4.4"

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
from cyanoConstruct.misc import printIf, checkType
import cyanoConstruct.enumsExceptions
from cyanoConstruct.database import UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, BackboneDB
db.create_all()
from cyanoConstruct.component import NamedSequence, SpacerData, PrimerData, inverseSeq
nullPrimerData = PrimerData.makeNull()
maxPosition = SpacerData.getMaxPosition()
from cyanoConstruct.users import UserData

try:
    defaultUser = UserData.load("default")
except UserNotFoundError:
    defaultUser = UserData.new("default")

import cyanoConstruct.routesFuncs
from cyanoConstruct.routes import *