#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:32:02 2020

@author: Lia Thomson

cyanoConstruct __init__ file
"""
__version__ = "0.4.4"

# import statements
from flask import Flask, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from cyanoconstruct.database import db
from os import environ

import importlib


# Flask app
app = Flask(__name__)
migrate = Migrate()


try:
    config = {
        "SECRET_KEY": environ["SECRET_KEY"],
        "SQLALCHEMY_DATABASE_URI": environ["SQLALCHEMY_DATABASE_URI"],
    }
except KeyError:
    config = importlib.import_module("cyanoconstruct.config")

app.config.update(config)
db.init_app(app)
migrate.init_app(app, db, render_as_batch=True)

with app.app_context():
    # db.create_all()
    # import for the side effects, init the default user.
    import cyanoconstruct.users

# import modules
from cyanoconstruct.misc import printIf, checkType
import cyanoconstruct.enumsExceptions

from cyanoconstruct.component import NamedSequence, SpacerData, PrimerData, inverseSeq

maxPosition = SpacerData.getMaxPosition()

from cyanoconstruct.routes import app as base
from cyanoconstruct.routes import login_manager

login_manager.init_app(app)
app.register_blueprint(base)
