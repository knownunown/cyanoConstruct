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
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from config import Config

#Flask app
app = Flask(__name__)
login = LoginManager(app)

app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#database
db = SQLAlchemy(app, session_options={"expire_on_commit": False})
migrate = Migrate(app, db)

#import modules
from misc import printIf, checkType
import enumsExceptions
from database import UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB, BackboneDB
db.create_all()
from component import NamedSequence, SpacerData, PrimerData, inverseSeq
nullPrimerData = PrimerData.makeNull()
maxPosition = SpacerData.getMaxPosition()
from users import UserData

try:
    defaultUser = UserData.load("default")
except enumsExceptions.UserNotFoundError:
    defaultUser = UserData.new("default")

import routesFuncs
from routes import *
