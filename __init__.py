#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: Lia Thomson

cyanoConstruct __init__ file
"""

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate

from cyanoConstruct.config import Config

app = Flask(__name__)
login = LoginManager(app)

app.config.from_object(Config)

db = SQLAlchemy(app, session_options = {"expire_on_commit": False})
migrate = Migrate(app, db)

from cyanoConstruct.enumsExceptions import AlreadyExistsError, SequenceMismatchError, SequenceNotFoundError, ComponentNotFoundError, UserNotFoundError, NotLoggedInError
from cyanoConstruct.database import UserDataDB, NamedSequenceDB, SpacerDataDB, PrimerDataDB, ComponentDB
db.create_all()
from cyanoConstruct.component import NamedSequence, SpacerData, PrimerData, Component, checkType
from cyanoConstruct.sessionUsers import SessionData, UserData, Globals

from cyanoConstruct.routes import *


__version__ = "0.3.1"