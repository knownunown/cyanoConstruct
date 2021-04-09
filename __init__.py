#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: Lia Thomson

cyanoConstruct __init__ file
"""
__version__ = "0.4.4"

#import statements
from flask import Flask, session
from flask_login import current_user, login_user, logout_user, login_required

from config import Config

#Flask app
app = Flask(__name__)

app.config.update(Config)

from flask_migrate import Migrate

# database
from database import db
db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push() # HACK: refactor out and use `with`
db.create_all()

#import modules
from misc import printIf, checkType
import enumsExceptions

from component import NamedSequence, SpacerData, PrimerData, inverseSeq
maxPosition = SpacerData.getMaxPosition()

from routes import app as base
from routes import login_manager
login_manager.init_app(app)
app.register_blueprint(base)
