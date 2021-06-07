#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes file, which is used to load website pages and process input from the site.

@author: Lia Thomson
"""

from misc import printIf
from users import UserData, defaultUser
from component import SpacerData, PrimerData, nullPrimerData
from database import NamedSequenceDB, UserDataDB, ComponentDB, BackboneDB
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask import Blueprint, session
import routesFuncs as rf
import enumsExceptions as ee

# flask
from flask import request, render_template, jsonify, Response, redirect

# Google Login stuff
from google.oauth2 import id_token
from google.auth.transport import requests

# misc.
from werkzeug.urls import url_parse  # for redirect parsing

##########################################################################################

CLIENT_ID = "431868350398-t0st3dhimv5i7rc3laka2lv2864kt4pd.apps.googleusercontent.com"

##############################   USER-RELATED   ##############################

app = Blueprint("routes", __name__, template_folder="templates/")
login_manager = LoginManager()

# logging in & current user
@login_manager.user_loader
def load_user(user_id):
    try:
        return UserData.load(user_id)
    except Exception:
        return None


login_manager.login_view = "routes.login"  # for redirecting if not logged in


def checkLoggedIn():
    return not getCurrUser().is_anonymous


def getCurrUser():
    return current_user


# check permissions to see if the current user can use a component/backbone/etc.
# This is done by checking if the component/backbone/etc. is in the current
# user's library OR the default library.
# These functions are called for various aspects of the site.
def checkPermission(comp):
    """Check if the current user has permission to use the component.

    PARAMETER:
            comp: component of type ComponentDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if comp is not a ComponentDB
            AccessError: is raised if the user does not have permission
    """
    if type(comp) != ComponentDB:
        raise TypeError("comp not a ComponentDB")

    if (
        comp.getUserID() != current_user.getID()
        and comp.getUserID() != defaultUser.getID()
    ):
        raise ee.AccessError("Do not have permission to access component.")


def checkPermissionNS(ns):
    """Check if the current user has permission to use the named sequence.

    PARAMETER:
            ns: named sequence of type NamedSequenceDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if ns is not a NamedSequenceDB
            AccessError: is raised if the user does not have permission
    """
    if type(ns) != NamedSequenceDB:
        raise TypeError("ns not a NamedSequenceDB")

    if ns.getUserID() != current_user.getID() and ns.getUserID() != defaultUser.getID():
        raise ee.AccessError("Do not have permission to access sequence.")


def checkPermissionBB(bb):
    """Check if the current user has permission to use the backbone.

    PARAMETER:
            bb: backbone of type BackboneDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if bb is not a BackboneDB
            AccessError: is raised if the user does not have permission
    """
    if type(bb) != BackboneDB:
        raise TypeError("bb not a BackboneDB")

    if bb.getUserID() != current_user.getID() and bb.getUserID() != defaultUser.getID():
        raise ee.AccessError("Do not have permission to access this backbone.")


# check permissions to see if the current user can modify a component/backbone/etc.
# This is done by checking if the component/backbone/etc. is in the current
# user's library.
# These functions are called when the user tries to delete a component/etc.
def permissionOwnComp(comp):
    """Check if the current user has permission to modify the component.

    PARAMETER:
            comp: component of type ComponentDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if comp is not a ComponentDB
            AccessError: is raised if the user does not have permission
    """
    if type(comp) != ComponentDB:
        raise TypeError("comp not a ComponentDB")

    if comp.getUserID() != current_user.getID():
        raise ee.AccessError("Do not have permission to access component.")


def permissionOwnNS(ns):
    """Check if the current user has permission to modify the name sequence.

    PARAMETER:
            ns: backbone of type NamedSequenceDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if ns is not a NamedSequenceDB
            AccessError: is raised if the user does not have permission
    """
    if type(ns) != NamedSequenceDB:
        raise TypeError("ns not a NamedSequenceDB")

    if ns.getUserID() != current_user.getID():
        raise ee.AccessError("Do not have permission to modify this sequence.")


def permissionOwnBB(bb):
    """Check if the current user has permission to modify the backbone.

    PARAMETER:
            bb: backbone of type BackboneDB

    RETURNS:
            None

    ERRORS:
            TypeError: is raised if bb is not a BackboneDB
            AccessError: is raised if the user does not have permission
    """
    if type(bb) != BackboneDB:
        raise TypeError("bb not a BackboneDB")

    if bb.getUserID() != current_user.getID():
        raise ee.AccessError("Do not have permission to access this backbone.")


# get selected objects (for designing components)
# The selected sequences, spacers, and primers are stored in the session
# object, as a cookie. This is why they are not methods of the current user.
def getSelectedNS():
    """Return the selected named sequence from session.

    RETURNS
            The selected NamedSequenceDB if found.
            None if not found.
    """
    try:
        NSID = session["selectedNS"]

        return NamedSequenceDB.query.get(NSID)

    except KeyError:
        return None


def getSelectedSD():
    """Return the selected spacer data from session.

    RETURNS:
            The selected spacer data, in JSON format, if found.
            None if not found.
    """
    try:
        return session["selectedSD"]
    except KeyError:
        return None


def getSelectedPD():
    """Return the selected primer data from session.

    RETURNS:
            The selected primer data, in JSON format, if found.
            None if not found.
    """
    try:
        return session["selectedPD"]
    except KeyError:
        return None


def getAllSelected():
    """Return whether there is a selected named sequence, spacer data, and primer data."""
    return (
        (getSelectedNS() is not None)
        and (getSelectedSD() is not None)
        and (getSelectedPD() is not None)
    )


def addToSelected(newSelected):
    """Set a named sequence, spacer data, or primer data as selected.

    PARAMETER:
            newSelected: object of type NamedSequenceDB, SpacerData, or PrimerData.

    ERRORS:
            TypeError: is raised if newSelected is not of correct type.
    """
    if type(newSelected) == NamedSequenceDB:
        session["selectedNS"] = newSelected.getID()
    elif type(newSelected) == SpacerData:
        session["selectedSD"] = newSelected.toJSON()
    elif type(newSelected) == PrimerData:
        session["selectedPD"] = newSelected.toJSON()
    else:
        raise TypeError("can't add item of type " + type(newSelected))

    session.modified = True


def clearSelected():
    """Clear all selected objects from the session."""
    for key in ["selectedNS", "selectedSD", "selectedPD"]:
        try:
            session.pop(key)
        except Exception:
            pass


##################################   ERRORS ################################
###############################################################################


@app.errorhandler(404)
def error404(error):
    """Handle a 404 error (page not found) with a redirect."""
    printIf("404 error: " + str(error))
    return render_template("404.html")


@app.errorhandler(500)
def error500(error):
    """Handle a 500 error (database error) with a redirect and database rollback."""
    printIf("500 eror: " + str(error))
    # roll back the database somehow, because this is invoked by database errors
    return render_template("500.html")


def errorZIP(error):
    """Handle an error related to downloading a ZIP file."""
    return render_template(
        "noSeq.html", errorMessage=str(error), loggedIn=checkLoggedIn()
    )


##################################   LOG IN ################################
###############################################################################


@app.route("/login", methods=["POST", "GET"])
def login():
    """Route for /login"""
    # redirect if already logged in
    if checkLoggedIn():
        return redirect("/index")

    # get all "emails" for testing
    allEmails = []
    for user in UserDataDB.query.order_by(UserDataDB.email).all():
        allEmails.append(user.getEmail())

    # get returnURL
    returnURL = request.args.get("next")
    if not returnURL or (url_parse(returnURL).netloc != ""):
        returnURL = "/index"

    return render_template(
        "login.html", returnURL=returnURL, allEmails=allEmails, loggedIn=checkLoggedIn()
    )


@app.route("/loginProcess", methods=["POST"])
def loginProcess():
    """Process email login information.

    NOTES:
            This function will probably not be used in the final site.
    """
    validInput = False
    outputStr = ""
    succeeded = False

    # get information (email & remember me) from the page's form
    try:
        email = request.form["email"]

        try:
            remember = rf.boolJS(request.form["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        validInput = True
    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"

    # log the user in on the server, if valid input has been retrieved
    if validInput:
        try:
            user = UserData.load(email)

            login_user(user, remember=remember)

            clearSelected()

            # indicate success
            outputStr = "Successfully logged in as " + email + ".<br>"
            succeeded = True

        except Exception as e:
            outputStr = "ERROR: " + str(e) + "<br>"

    # return information for the web page to use and display.
    return jsonify({"output": outputStr, "succeeded": succeeded})


@app.route("/loginGoogle", methods=["POST"])
def loginGoogle():
    """Log a user in using Google Sign-In."""
    succeeded = False
    outputStr = ""

    # get information from the page
    try:
        token = request.form["IDtoken"]
        email = request.form["email"]
        try:
            remember = rf.boolJS(request.form["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        # check token

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo["sub"]

        # actually log in OR register
        try:
            # log in
            user = UserData.load(email)

            if user.getGoogleAssoc():
                # check if the Google User ID & email match
                # This may cause an issue if someone changes their email address
                # but logs in using the same Google account. Will this ever happen?
                if user.getGoogleID() != userid:
                    raise Exception("User ID and Email do not match.")
                else:
                    login_user(user, remember=remember)
                    outputStr = "Successfully logged in as {email}.".format(email=email)
            else:
                raise Exception(
                    "Account with this email already exists, not associated with Google."
                )

        except ee.UserNotFoundError:
            # register
            user = UserData.new(email)

            # set user up with Google-related info.
            user.setGoogleAssoc(True)
            user.setGoogleID(userid)

            login_user(user, remember=remember)

            clearSelected()

            outputStr = "Successfully created account as {email}.".format(email=email)

        succeeded = True

    except ValueError:
        # is raised if there is an invalid token.
        outputStr = "ERROR: Invalid input."

    # handle any other errors by transforming them into an error message
    except Exception as e:
        outputStr = "ERROR: {}".format(e)
        printIf(e)

    return jsonify({"succeeded": succeeded, "output": outputStr})


@app.route("/logout", methods=["POST", "GET"])
def logoutProcess():
    """Log the current user out."""
    logout_user()
    clearSelected()

    return redirect("/index")


@app.route("/registerProcess", methods=["POST"])
def registerProcess():
    """Register a user using an email.

    NOTE:
            This function should not be called upon in the final site.
    """
    validInput = False
    outputStr = ""
    succeeded = False

    # get information from the page's form
    try:
        email = request.form["email"]
        try:
            remember = rf.boolJS(request.form["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        validInput = True

    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"

    # try to register a new account
    if validInput:
        try:
            user = UserData.new(email)
            login_user(user, remember=remember)

            clearSelected()

            # indicate success
            outputStr += "Successfully registered and logged in as {email}.<br>".format(
                email=email
            )
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"

    return jsonify({"output": outputStr, "succeeded": succeeded})


###############################  USER PAGE   ###############################
###############################################################################


@app.route("/account", methods=["POST", "GET"])
@login_required
def accountInfo():
    """Route for /account"""
    currUser = getCurrUser()
    email = currUser.getEmail()

    googleAssoc = currUser.getEntry().getGoogleAssoc()

    return render_template(
        "account.html", email=email, googleAssoc=googleAssoc, loggedIn=checkLoggedIn()
    )


@app.route("/googleConnect", methods=["POST"])
def googleConnect():
    """Connect a server account with their Google account.

    NOTE:
            This should not be needed once all accounts are associated with a Google
            account, and cannot be created independently.
    """
    outputStr = ""
    succeeded = False

    # get information
    try:
        token = request.form["IDtoken"]
        email = request.form["email"]

        # check token

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo["sub"]

        u = UserData.load(email)

        if u.getGoogleAssoc():
            raise Exception("Already connected Google account with this email.")
        else:
            if u.getEmail() != email:
                raise Exception("Emails don't match.")
            else:
                u.setGoogleAssoc(True)
                u.setGoogleID(userid)

                outputStr = (
                    "Successfully connected {email} with Google account.".format(
                        email=email
                    )
                )

                succeeded = True

    except ValueError:
        # raised if the token is invalid.
        outputStr = "ERROR: Invalid input."

    except Exception as e:
        outputStr = "ERROR: {}".format(e)
        print(e)

    return jsonify({"output": outputStr, "succeeded": succeeded})


############################### DESIGN  #################################
###############################################################################
@app.route("/design", methods=["POST", "GET"])
@login_required
def design():
    """Route for /design"""
    # get the NamedSequences of the current user and the default user
    userNamedSequences = getCurrUser().getSortedNS()
    defaultNamedSequences = defaultUser.getSortedNS()

    # make the named sequences more friendly to javascript
    NSNamesJSONifiable = {}  # dict of lists, one list for each type of sequence
    # (e.g. RBS). The lists are lists of dicts.
    # Each dictionary represents a named sequence, with
    # values for its name and ID

    NSSequencesJSONifiable = {}  # dict of named sequence IDs, which are the keys
    # and sequences, which are the values

    defaultNames = []  # list of names from the default user. When going through
    # the user-made named sequences, the sequence will not be
    # added if its name is already in defaultNames.

    # first, json-ify the default named sequences
    for typeKey in defaultNamedSequences.keys():
        NSNamesJSONifiable[typeKey] = []

        for ns in defaultNamedSequences[typeKey]:
            NSNamesJSONifiable[typeKey].append({"name": ns.getName(), "id": ns.getID()})

            NSSequencesJSONifiable[ns.getID()] = ns.getSeq()

            defaultNames.append(ns.getName())

        # second, the user-made named sequences
        for ns in userNamedSequences[typeKey]:
            # check if the named sequence has already been added from default
            if ns.getName() not in defaultNames:
                NSNamesJSONifiable[typeKey].append(
                    {"name": ns.getName(), "id": ns.getID()}
                )

                NSSequencesJSONifiable[ns.getID()] = ns.getSeq()

    return render_template(
        "design.html",
        namedSequencesNames=NSNamesJSONifiable,
        namedSequencesSequences=NSSequencesJSONifiable,
        loggedIn=checkLoggedIn(),
    )


###############################  Component   ###############################


@app.route("/findNamedSeq", methods=["POST"])
def findNamedSeq():
    """Find a named sequence to select it for the session."""

    try:
        # get data
        nsID = request.form["NSid"]

        # get named sequence, ns, from database
        ns = NamedSequenceDB.query.get(nsID)

        if ns is None:
            outputStr = "ERROR: Sequence does not exist."
        else:
            try:
                # select the named sequence if the user has permission
                checkPermissionNS(ns)

                addToSelected(ns)

                outputStr = ""
                succeeded = True

            except ee.AccessError:
                outputStr = "ERROR: You do not have permission to access this sequence."

            except Exception as e:
                outputStr = str(e)

    except Exception:
        outputStr = "ERROR: Bad input."

    return jsonify({"output": outputStr, "succeeded": succeeded})


@app.route("/findSpacers", methods=["POST"])
def findSpacers():
    """Create a SpacerData and select it for the session."""
    # validation
    validInput = True
    succeeded = False

    # get data
    try:
        newPosStr = request.form["componentPos"]
        newTerminalStr = request.form["isTerminal"]
    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    # validate the spacer information
    if validInput:
        validInput, outputStr, newPos, isTerminal = rf.validateSpacers(
            newPosStr, newTerminalStr
        )

    # obtain the actual spacers
    if validInput:
        try:
            # make the SpacerData
            newSpacerData = SpacerData.makeNew(newPos, isTerminal)

            # add to outputStr
            if newPos == 999:
                outputStr += "Spacers found for position T"
            else:
                outputStr += "Spacers found for position " + str(newPos)

            if isTerminal:
                outputStr += " last element:"
            else:
                outputStr += " not last element:"
            outputStr += "<br>Left spacer: {left}<br>Right spacer: {right}".format(
                left=newSpacerData.getSpacerLeft(), right=newSpacerData.getSpacerRight()
            )
            # select it
            addToSelected(newSpacerData)

            succeeded = True

        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"

    if not succeeded:
        outputStr += "Spacers not found."

    return jsonify({"output": outputStr, "succeeded": succeeded})


@app.route("/findPrimers", methods=["POST"])
def findPrimers():
    """Create PrimerData and select it for the session."""
    outputStr = ""
    validInput = True
    succeeded = False

    # get form data
    try:
        TMstr = request.form["meltingPoint"]
        rangeStr = request.form["meltingPointRange"]
        skipStr = request.form["skipPrimers"]
        skipPrimers = rf.boolJS(skipStr)

    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received."

    # skip primers if that box was checked
    if skipPrimers:
        outputStr += "Chose not to make primers.<br>"
        addToSelected(nullPrimerData)

        succeeded = True

    elif validInput:
        # that thrilling data validation
        if validInput:
            validInput, outputStr, TMnum, rangeNum = rf.validatePrimers(TMstr, rangeStr)

        if validInput:
            # get selected spacers, to use for the primers
            selectedSpacers = getSelectedSD()
            # check if spacers have been selected yet
            if selectedSpacers is None:
                validInput = False
                outputStr += "ERROR: No spacers selected.<br>"

            selectedSpacers = SpacerData.fromJSON(selectedSpacers)

        if validInput:
            # get selected named sequence, to use for the primers
            selectedNS = getSelectedNS()
            # check if sequence has been selected yet
            if selectedNS is None:
                validInput = False
                outputStr += "ERROR: No sequence selected.<br>"

            seqToEvaluate = selectedNS.getSeq()

        # find the primers
        if validInput:
            try:
                # create the PrimerData
                newPrimerData = PrimerData.makeNew(seqToEvaluate, TMnum, rangeNum)
                newPrimerData.addSpacerSeqs(selectedSpacers)

                if newPrimerData.getPrimersFound():
                    # add information about the PrimerData to outputStr
                    outputStr += str(newPrimerData).replace("\n", "<br>")

                    # add to selected
                    addToSelected(newPrimerData)

                    succeeded = True

                else:
                    outputStr += (
                        "Couldn't find primers for the specified "
                        "sequence, melting point, and range.<br>"
                    )

            except Exception as e:
                outputStr += "ERROR: " + str(e) + "<br>"

        if not succeeded:
            outputStr += "Primers not found."

    return jsonify({"output": outputStr, "succeeded": succeeded})


@app.route("/finishComponent", methods=["POST"])
def finishComponent():
    """Create a component and add it to the current user's library."""
    # validation
    validInput = getAllSelected()
    succeeded = False
    newID = -1

    outputStr = ""

    if validInput:
        try:
            # get info. to use later
            currUser = getCurrUser()
            selectedNS = getSelectedNS()
            # get spacers & primers, which were stored in the session in JSON
            # format, so they need to be re-created using fromJSON()
            selectedSpacers = SpacerData.fromJSON(getSelectedSD())
            selectedPrimers = PrimerData.fromJSON(getSelectedPD())

            # check if it already exists in defaults
            try:
                defaultUser.findComponent(
                    selectedNS.getType(),
                    selectedNS.getName(),
                    selectedSpacers.getPosition(),
                    selectedSpacers.getTerminalLetter(),
                )

                # if no error has been raised, the component was found in default
                raise ee.AlreadyExistsError(
                    "Component already exists as a default component."
                )
            except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                # the component was not found in default
                pass

            # check if it already exists in personal library
            try:
                getCurrUser().findComponent(
                    selectedNS.getType(),
                    selectedNS.getName(),
                    selectedSpacers.getPosition(),
                    selectedSpacers.getTerminalLetter(),
                )

                # if no error has been raised, the component was found in the
                # current user's library.
                raise ee.AlreadyExistsError(
                    "Component already exists as a user-made component."
                )
            except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                # the component was not found in the current user
                pass

            # add NS to personal library if it's not from the personal library
            try:
                tempNS = currUser.addNSDB(selectedNS)
                selectedNS = tempNS
            except ee.AlreadyExistsError:
                pass

            # create the component
            newComponent = currUser.createComp(
                selectedNS, selectedSpacers, selectedPrimers
            )

            # modify output string
            libraryName = "Personal"
            outputStr = (
                "<a target = '_blank' href = '/library#{libraryName}{nameID}'>"
                "{nameID}</a> created."
            ).format(libraryName=libraryName, nameID=newComponent.getNameID())

            # get the ID of the new component, for the ZIP download link/button
            newID = newComponent.getID()

            succeeded = True

        except Exception as e:
            outputStr = "ERROR: " + str(e)

    else:
        outputStr += "ERROR: invalid input."

    return jsonify({"output": outputStr, "succeeded": succeeded, "newID": newID})


@app.route("/newComponent.zip")
def newCompZIP():
    """Download ZIP file from the design step."""
    try:
        # get information from the request
        newCompID = request.args.get("id")
        offset = int(request.args.get("timezoneOffset"))

        # get the requested component's ZIP file
        comp = ComponentDB.query.get(newCompID)
        checkPermission(comp)
        compZIP = comp.getCompZIP(offset)

        # make the ZIP into a byte file
        data = rf.makeZIP(compZIP)

    except Exception as e:
        printIf("FAILED TO CREATE ZIP BECAUSE: {}".format(e))
        return errorZIP(e)

    if data is None:
        return errorZIP("No/invalid component to create a ZIP from.")

    return Response(
        data,
        headers={
            "Content-Type": "application/zip",
            "Condent-Disposition": "attachment; filename='sequences.zip';",
        },
    )


###############################  Sequence       ###############################
@app.route("/newNamedSeq", methods=["POST"])
def newNamedSeq():
    """Create a new named sequence and add it to the current user's library."""
    outputStr = ""
    validInput = True
    succeeded = False

    # get data from web form
    try:
        newNSType = request.form["NStype"]
        newNSName = request.form["NSname"]
        newNSSeq = request.form["NSseq"].upper()

    except Exception:
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    # validation
    if validInput:
        validInput, outputStr = rf.validateNewNS(newNSType, newNSName, newNSSeq)

    # create the sequence
    if validInput:
        try:
            getCurrUser().createNS(newNSType, newNSName, newNSSeq)

            # outputStr
            libraryName = "Personal"
            outputStr += (
                "Successfully created <a target = '_blank' href = '/library#"
                "{libraryName}{NSname}'>{NSname}</a>."
            ).format(libraryName=libraryName, NSname=newNSName)

            succeeded = True

        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"

    if not succeeded:
        outputStr += "Sequence not created."

    return jsonify({"output": outputStr, "succeeded": succeeded})


###############################  Backbone       ###############################
@app.route("/newBackbone", methods=["POST"])
def newBackbone2():
    """Create a new backbone and add it to the current user's library."""
    outputStr = ""
    validInput = True
    succeeded = False

    # get information from the web form
    try:
        BBname = request.form["backboneName"]
        BBdesc = request.form["backboneDesc"]
        BBseq = request.form["backboneSeq"]
        BBtype = request.form["backboneType"]
        BBfeatures = request.form["backboneFeatures"]

    except Exception as e:
        printIf(e)
        validInput = False
        outputStr = "ERROR: invalid input received.<br>"

    # check if it exists in the personal library
    if validInput:
        try:
            getCurrUser().findBackbone(BBname)
            outputStr = "ERROR: Backbone {name} already exists in your personal library.".format(
                name=BBname
            )
            validInput = False
        except ee.BackboneNotFoundError:
            pass

    # general validation. Includes checking if the backbone is in the default library.
    if validInput:
        validInput, outputStr = rf.validateBackbone(
            BBname, BBdesc, BBseq, BBtype, BBfeatures
        )

    # validation of the sequence & features
    if validInput:
        outputStr, validInput, BBdata = rf.processGBfeatures(
            BBseq, BBfeatures.splitlines(keepends=True), outputStr
        )

        seqBefore = BBdata["seqBefore"]
        seqAfter = BBdata["seqAfter"]
        features = BBdata["featureSection"]

    # create the backbone
    if validInput:
        try:
            getCurrUser().createBackbone(
                BBname, BBtype, BBdesc, seqBefore, seqAfter, features
            )

            # outputStr
            libraryName = "Personal"
            outputStr += (
                "Successfully created <a target = '_blank' href = '/library#"
                "{libraryName}{BBname}Backbone'>{BBname}</a>."
            ).format(libraryName=libraryName, BBname=BBname)
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: {}<br>".format(e)

    return jsonify({"output": outputStr, "succeeded": succeeded})


@app.route("/backbonePreview", methods=["POST"])
def backbonePreview():
    """Process user-designed features and turn them into .gb file format.

    NOTES:
            This is called when the user creates their own features on the backbone
            design form. It returns a string that the web page will display as part
            of the features for the backbone in process.
    """
    outputStr = ""
    validInput = True
    succeeded = False

    featureStr = ""

    # get data
    try:
        numFeatures = int(request.form["numFeatures"])

        printIf(request.form)

    except Exception as e:
        validInput = False
        printIf(e)
        outputStr = "ERROR: Invalid input received.<br>"

    # make features
    if validInput:
        allMolTypes = {
            "genomicDNA": "genomic DNA",
            "genomicRNA": "genomic RNA",
            "mRNA": "mRNA",
            "tRNA": "tRNA",
            "rRNA": "rRNA",
            "otherRNA": "other RNA",
            "otherDNA": "other DNA",
            "transcribedRNA": "transcribed RNA",
            "viralcRNA": "viral cRNA",
            "unassignedDNA": "unassigned DNA",
            "unassignedRNA": "unassigned RNA",
        }
        try:
            # go through each feature
            for key in range(numFeatures):
                featType = request.form["featureType{}".format(key)]

                # get locations
                # if there is just locus: the origin
                if featType == "none":
                    continue
                elif featType == "origin":
                    locOrig = int(request.form["locationOrigin{}".format(key)])
                    if locOrig < 1:
                        validInput = False
                        outputStr += "ERROR: origin location must be at least 1.<br>"
                # all other feature types have a start and end location
                else:
                    locStart = int(request.form["locationStart{}".format(key)])
                    locEnd = int(request.form["locationEnd{}".format(key)])

                    if locStart < 1 or locEnd < 1:
                        outputStr += "ERROR: locations for feature #{} must be at least 1.<br>".format(
                            key
                        )

                    if locStart > locEnd:
                        validInput = False
                        outputStr += (
                            "ERROR: start location for feature #{} "
                            "is greater than its end location.<br>"
                        ).format(key)

                # add to featureStr, format depending on the type of the feature
                if featType == "origin":
                    featureStr += "\trep_origin\t{orig}\n".format(orig=locOrig)

                    # get the direction of the origin
                    direction = False

                    try:
                        direction = request.form["direction{}".format(key)]
                    except Exception:
                        pass

                    # if there is a direction, add it to the string
                    if direction:
                        if direction == "none":
                            pass
                        elif direction not in ["left", "right", "both"]:
                            raise Exception("invalid direction {}".format(direction))
                        else:
                            featureStr += "\t\t\t/direction={direction}\n".format(
                                direction=direction
                            )

                elif featType == "source":
                    organism = request.form["organism{}".format(key)]
                    molType = request.form["molType{}".format(key)]

                    if len(organism) > 64:
                        validInput = False
                        outputStr += "ERROR: organism name must be at most 64 characters long.<br>"

                    molLong = allMolTypes[molType]

                    featureStr += (
                        '\tsource\t\t{start}..{end}\n\t\t\t/organism="{organism}"\n'
                        '\t\t\t/mol_type="{molLong}"\n'
                    ).format(
                        start=locStart, end=locEnd, organism=organism, molLong=molLong
                    )

                elif featType == "CDS":
                    gene = request.form["geneName{}".format(key)]

                    if len(gene) > 64:
                        validInput = False
                        outputStr += (
                            "ERROR: gene name must be at most 64 characters long.<br>"
                        )

                    featureStr += (
                        '\tCDS\t\t{start}..{end}\n\t\t\t/gene="{geneName}"\n'.format(
                            start=locStart, end=locEnd, geneName=gene
                        )
                    )

                elif featType == "misc":
                    note = request.form["miscNote{}".format(key)]

                    if len(note) > 1024:
                        validInput = False
                        outputStr += (
                            "ERROR: note must be at most 1024 characters long.<br>"
                        )

                    featureStr += (
                        '\tmisc_feature\t{start}..{end}\n\t\t\t/note="{note}"\n'.format(
                            start=locStart, end=locEnd, note=note
                        )
                    )

                else:
                    raise Exception("invalid featType {}".format(featType))
            # end for loop going through the features

        except Exception as e:
            validInput = False
            printIf(e)
            outputStr = "ERROR: Invalid input received.<br>"

        if validInput:
            succeeded = True
            printIf(featureStr)

    return jsonify(
        {"output": outputStr, "succeeded": succeeded, "featureStr": featureStr}
    )


@app.route("/backboneFileProcess", methods=["POST"])
def backboneFile():
    """Parse through a backbone .gb file to auto-fill most of the backbone design form."""
    outputStr = ""
    validInput = True
    succeeded = False
    featureSection = ""
    sequenceOutput = ""
    definition = ""
    name = ""

    # get data from web page
    try:
        backboneData = request.data
        size = int(request.args.get("size"))
    except Exception as e:
        validInput = False
        printIf(e)
        outputStr = "ERROR: Invalid input received."

    if validInput:
        try:
            # check the size of the data received & size of the data sent are the same
            if len(backboneData) != size:
                raise Exception(
                    "File was not completely uploaded to server. Please try again."
                )

            # otherwise, process the .gb file using readBackboneGB()
            outputStr, validInput, fileData = rf.readBackboneGB(backboneData, outputStr)

            name = fileData["name"]
            definition = fileData["definition"]
            featureSection = fileData["features"]
            sequenceOutput = fileData["sequence"]

            succeeded = True

        except Exception as e:
            validInput = False
            printIf(e)
            outputStr = "ERROR: {}".format(e)

    return jsonify(
        {
            "output": outputStr,
            "succeeded": succeeded,
            "featureStr": featureSection,
            "sequence": sequenceOutput,
            "definition": definition,
            "name": name,
        }
    )


#################################   ASSEMBLY  #################################
###############################################################################

# the page for assembly
@app.route("/assemble", methods=["POST", "GET"])
@login_required
def assemble():
    """Route for /assemble"""
    allDefaultNS = defaultUser.getSortedNS()
    allSessionNS = getCurrUser().getSortedNS()

    # dict of all components
    allAvailableNames = {}
    posTerminalComb = {}

    for typeKey in allDefaultNS.keys():
        allAvailableNames[typeKey] = []

        # default library
        for ns in allDefaultNS[typeKey]:
            allAvailableNames[typeKey].append(ns.getName())  # add names

            posTerminalComb[ns.getName()] = []

            for comp in ns.getAllComponents():
                # the combination
                posTermCombRow = {
                    "position": comp.getPosition(),
                    "terminalLetter": comp.getTerminalLetter(),
                }
                if posTermCombRow not in posTerminalComb[ns.getName()]:
                    posTerminalComb[ns.getName()].append(posTermCombRow)

        # user-made library
        for ns in allSessionNS[typeKey]:
            if (
                ns.getName() not in allAvailableNames[typeKey]
            ):  # add user-made sequences if not already there
                allAvailableNames[typeKey].append(ns.getName())

                if ns.getName() not in posTerminalComb:
                    posTerminalComb[ns.getName()] = []

            for comp in ns.getAllComponents():

                # that combination
                posTermCombRow = {
                    "position": comp.getPosition(),
                    "terminalLetter": comp.getTerminalLetter(),
                }
                if posTermCombRow not in posTerminalComb[ns.getName()]:
                    posTerminalComb[ns.getName()].append(posTermCombRow)

    # list of fidelities
    fidelities = ["98.5%", "98.1%", "95.8%", "91.7%"]

    fidelityLimits = {
        "98.5%": SpacerData.max985,
        "98.1%": SpacerData.max981,
        "95.8%": SpacerData.max958,
        "91.7%": SpacerData.max917,
    }

    # list of backbones & IDs
    availableBackbones = {"i": [], "r": []}
    backboneDescs = {}
    for BB in defaultUser.getSortedBB():
        availableBackbones[BB.getType()].append([BB.getID(), BB.getName()])
        backboneDescs[BB.getID()] = BB.getDesc()
    for BB in getCurrUser().getSortedBB():
        availableBackbones[BB.getType()].append([BB.getID(), BB.getName()])
        backboneDescs[BB.getID()] = BB.getDesc()

    seqElements = [
        ["Pr", "Promoter"],
        ["RBS", "RBS"],
        ["GOI", "Gene"],
        ["Term", "Terminator"],
    ]

    return render_template(
        "assembly.html",
        fidelities=fidelities,
        fidelityLimits=fidelityLimits,
        availableElements=allAvailableNames,
        posTermComb=posTerminalComb,
        availableBackbones=availableBackbones,
        backboneDescs=backboneDescs,
        seqElements=seqElements,
        loggedIn=checkLoggedIn(),
    )


# process assembly
@app.route("/processAssembly", methods=["POST"])
def processAssembly():
    """Create an assembled sequence using information from the /assemble page."""
    outputStr = ""
    validInput = True
    succeeded = True

    # get info.
    try:
        # get basic info.
        offset = int(request.form["timezoneOffset"])
        bbID = request.form["backbone"]
        numMidElem = int(request.form["numMidElements"])

    except Exception as e:
        printIf(e)
        validInput = False
        succeeded = False
        outputStr = "ERROR: bad input."

    # insert more validation?

    if validInput:
        outputStr = "Backbone:<br>"

        try:
            # store timezone offset as a cookie
            # this is used so the .gb file has a date that is accurate to
            # the user's timezone.
            session["timezoneOffset"] = offset

            # get the backbone
            # bbID = int(dataDict["backbone"])
            bb = BackboneDB.query.get(bbID)

            # check if the backbone exists.
            if bb is None:
                validInput = False
                succeeded = False
                outputStr = "ERROR: Could not find backbone."
            else:
                try:
                    # ensure the user has permission to use the backbone
                    checkPermissionBB(bb)

                    # get info. about the backbone for outputStr
                    user = UserDataDB.query.get(bb.getUserID())

                    if user.getEmail() == "default":
                        libraryName = "Default"
                    else:
                        libraryName = "Personal"

                    outputStr += (
                        "Found:  <a target = '_blank' href = '/library#"
                        "{libraryName}{BBname}Backbone'>{BBname}</a><br>"
                    ).format(BBname=bb.getName(), libraryName=libraryName)

                    # save the backbone to the session
                    session["assemblyBackbone"] = bb.getID()

                except ee.AccessError:
                    validInput = False
                    succeeded = False
                    outputStr += (
                        "ERROR: You do not have permission to use this backbone.<br>"
                    )
        except Exception as e:
            validInput = False
            succeeded = False
            printIf(e)

        # gather the components
        if validInput:
            outputStr += "<br>Components:<br>"

            # allPositions stores the positions of all of the elements that were submitted
            allPositions = [0]
            allPositions.extend([x for x in range(1, numMidElem + 1)])
            allPositions.append(999)

            # compsList stores all of the components found
            compsList = []

            # for each position, find the corresponding component
            for pos in allPositions:
                # get the type and name from the request
                elemType = request.form["elemType{}".format(pos)]
                elemName = request.form["elemName{}".format(pos)]

                # get the terminalLetter, to be used for searching for components
                if pos == 0:
                    terminalLetter = "S"
                elif pos == 999:
                    terminalLetter = "T"
                elif pos < numMidElem:
                    terminalLetter = "M"
                else:
                    terminalLetter = "L"

                # finally search for the component
                try:
                    # search default library
                    try:
                        foundComp = defaultUser.findComponent(
                            elemType, elemName, pos, terminalLetter
                        )
                        libraryName = "Default"
                    # if not found in the default, search user library
                    except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                        foundComp = getCurrUser().findComponent(
                            elemType, elemName, pos, terminalLetter
                        )
                        libraryName = "Personal"

                    # add the found component
                    compsList.append(foundComp.getID())

                    outputStr += (
                        "Found: <a target = '_blank' href ='/library#"
                        "{libraryName}{nameID}'>{nameID}</a><br>"
                    ).format(libraryName=libraryName, nameID=foundComp.getNameID())
                except (ee.SequenceNotFoundError, ee.ComponentNotFoundError):
                    # if a component was not found
                    outputStr += (
                        "Could not find:<br>Type: {type}<br>Name: {name}"
                        "<br>Position: {pos}<br>"
                        "Terminal letter: {terminalLetter}<br>"
                    ).format(
                        type=elemType,
                        name=elemName,
                        pos=pos,
                        terminalLetter=terminalLetter,
                    )

                    succeeded = False

    # proceed if succeeded, or if everything was found
    if succeeded:
        # save the component IDs to the session
        session["assemblyCompIDs"] = compsList
        outputStr += "<br>Full sequence can be downloaded."

    else:
        outputStr += (
            "<br>Errors in finding components are often due to not having"
            "a component with the right terminal letter.<br>Sequence not created."
        )

    return jsonify({"output": outputStr, "succeeded": succeeded})


# get the zip for the assembled sequence
@app.route("/assembledSequence.zip")
def assemblyZIP():
    """Create and send a .zip for an assembled sequence."""
    # get info. about the assembled sequence
    try:
        compsList = session["assemblyCompIDs"]
        bbID = session["assemblyBackbone"]
        offset = session["timezoneOffset"]
    except KeyError:
        return errorZIP("No assembled sequence.")

    packageComps = request.args.get("components") is not None

    # gather the backbone and components from the session
    try:
        # get the backbone & see if the user has permission to use it
        bb = BackboneDB.query.get(bbID)
        checkPermissionBB(bb)

        # start the fullSeq with the part of the backbone that is before the insertion
        fullSeq = bb.getSeqBefore()
        # index (starting at zero) of the fullSeq to add at
        i = len(fullSeq)

        # get features from the backbone
        features = bb.getFeatures().splitlines()

        files = {}

        # go through each saved component
        for compNum, compID in enumerate(compsList):
            # get the component & see if the user has permission to use it
            comp: ComponentDB = ComponentDB.query.get(compID)
            checkPermission(comp)

            if packageComps:
                files[f"{compNum}_{comp.getNameID()}.gb"] = comp.getGenBankFile(offset)

            # add the component to the assembly
            # if the component is element 0, (a promoter)
            if comp.getPosition() == 0:
                # add to fullSeq and i
                fullSeq += comp.getSeq()
                i = rf.addCompAssemblyGB(comp, features, i)
                printIf("adding {compID} seq".format(compID=comp.getNameID()))
            # if the component is any non-0 element
            else:
                # ?! why IS it like this
                fullSeq += comp.getLeftSpacer() + comp.getSeq()
                i = rf.addSpacerAssemblyGB(comp.getLeftSpacer(), features, i)
                printIf(
                    "adding {compID} left spacer: {spacer}".format(
                        compID=comp.getNameID(), spacer=comp.getLeftSpacer()
                    )
                )

                # HACK(tny): GenBank annotations and sequences should be less ad-hoc.
                if comp.getType() == "RBS":
                    fullSeq += "GG"
                i = rf.addCompAssemblyGB(comp, features, i)
                printIf("adding {compID} seq".format(compID=comp.getNameID()))

        # get the length of the inserted sequence
        lengthInsertion = i - len(bb.getSeqBefore())

        # process the features
        # go through each feature
        for j in range(len(features)):
            # split the features by [AddLength]
            # the features are formatted like "blah blah [AddLength]20[AddLength] blah blah"
            # so splitting by [AddLength] will separate out 20
            # the length of the insertion can be then added to 20
            featRow = features[j].split("[AddLength]")

            if len(featRow) > 1:
                # get every number that is sandwiched by two "[AddLength]"s
                for k in range(1, len(featRow), 2):
                    # replace the number with the original index + the insertion's length
                    origIndex = int(featRow[k])
                    featRow[k] = str(origIndex + lengthInsertion)

                # merge the feature row
                features[j] = "".join(featRow)

        # finish the assembly
        fullSeq += bb.getSeqAfter()

        fileGB = rf.finishCompAssemblyGB(features, fullSeq, offset, bb.getName())
        fileFASTA = ">CyanoConstruct assembled sequence\n" + fullSeq
        print(
            f"assemblyZIP: sequence is of len {len(fullSeq)}, remaining in frame: {len(fullSeq) % 3}"
        )

        # make the .zip
        files = {
            **files,
            **{"fullSequence.fasta": fileFASTA, "fullSequence.gb": fileGB},
        }
        data = rf.makeZIP(files)

    except Exception as e:
        return errorZIP(e)

    if data is None:
        return errorZIP("No assembled sequence.")

    return Response(
        data,
        headers={
            "Content-Type": "application/zip",
            "Condent-Disposition": "attachment; filename='sequences.zip';",
        },
    )


#################################   LIBRARY   #################################
###############################################################################
@app.route("/components", methods=["GET"])
def displayComps():
    """Redirects to /library; can be removed."""
    return redirect("/library")


@app.route("/library", methods=["GET"])
@login_required
def displayCompLib():
    """Route for /library"""

    currUser = getCurrUser()

    # get the HTML code for displaying the library
    allNSandBB = {
        "Default": defaultUser.getSortedNS(),
        "Personal": currUser.getSortedNS(),
    }

    # add backbone display HTML to allNSandBB
    allNSandBB["Default"]["BB"] = defaultUser.getSortedBB()
    allNSandBB["Personal"]["BB"] = currUser.getSortedBB()

    # longNames is used for formatting on the page
    longNames = {
        "Pr": "Promoters",
        "RBS": "Ribosome Binding Sites",
        "GOI": "Genes of Interest",
        "Term": "Terminators",
        "BB": "Backbones",
    }

    return render_template(
        "library.html",
        allNSandBB=allNSandBB,
        longNames=longNames,
        loggedIn=checkLoggedIn(),
    )


@app.route("/componentZIP.zip")
def getComponentZIP():
    """Create and send the .zip for a component."""
    try:
        # get info. from request
        comp = ComponentDB.query.get(request.args.get("id"))
        offset = int(request.args.get("timezoneOffset"))

        checkPermission(comp)

        # make the .zip file
        compZIP = comp.getCompZIP(offset)
        data = rf.makeZIP(compZIP)

    except Exception as e:
        return errorZIP(e)

    if data is None:
        return errorZIP("No/invalid sequence to create a ZIP from.")

    else:
        return Response(
            data,
            headers={
                "Content-Type": "application/zip",
                "Condent-Disposition": "attachment; filename='componentZIP.zip';",
            },
        )


@app.route("/removeComponent", methods=["POST"])
def removeComponent():
    """Delete a component from the database."""
    succeeded = False
    errorMessage = ""

    try:
        # get component
        compID = request.form["compID"]
        comp = ComponentDB.query.get(compID)

        if comp is None:
            errorMessage = "Component does not exist."

        else:
            try:
                # remove the component if the user has permission to remove it
                permissionOwnComp(comp)

                getCurrUser().removeFoundComponent(comp)

                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this component."

            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."

    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})


@app.route("/removeSequence", methods=["POST"])
def removeSequence():
    """Delete a named sequence from the database.
    This will also delete all components using the named sequence."""
    succeeded = False
    errorMessage = ""

    try:
        # get named sequence
        nsID = request.form["sequenceID"]
        ns = NamedSequenceDB.query.get(nsID)

        if ns is None:
            errorMessage = "Sequence does not exist."
        else:
            try:
                # remove the named sequence if the user has permission
                permissionOwnNS(ns)

                getCurrUser().removeFoundSequence(ns)

                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this sequence."

            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."

    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})


@app.route("/removeBackbone", methods=["POST"])
def removeBackbone():
    """Delete a backbone from the database."""
    succeeded = False
    errorMessage = ""

    try:
        # get backbone
        bbID = request.form["backboneID"]
        bb = BackboneDB.query.get(bbID)

        if bb is None:
            errorMessage = "Backbone does not exist."
        else:
            try:
                # remove the backbone if the user has permission
                permissionOwnBB(bb)

                getCurrUser().removeBackbone(bbID)

                succeeded = True

            except ee.AccessError:
                errorMessage = "You do not have permission to modify this backbone."

            except Exception as e:
                errorMessage = str(e)

    except Exception:
        errorMessage = "Bad input."

    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})


@app.route("/downloadLibrary", methods=["POST"])
def downloadLibrary():
    """Called upon by the website to establish which library the user is downloading."""
    libraryName = request.form["libraryName"]

    succeeded = False

    if libraryName == "Default":
        session["libraryName"] = "Default"

        succeeded = True
        errorMessage = ""
    elif libraryName == "Personal":
        session["libraryName"] = "Personal"

        succeeded = True
        errorMessage = ""
    else:
        errorMessage = "Can't find " + libraryName + " library."

    return jsonify({"succeeded": succeeded, "errorMessage": errorMessage})


@app.route("/library.zip")
def libraryZIP():
    """Create and send a .zip containing the components and backbones of a user."""
    succeeded = False
    try:
        # get info. (set by downloadLibrary())
        libraryName = session["libraryName"]
        offset = int(request.args.get("timezoneOffset"))

        if libraryName == "Default":
            try:
                # make the .zip from the default library
                data = rf.makeAllLibraryZIP(defaultUser, offset)
                succeeded = True
            except Exception as e:
                errorMessage = str(e)
        elif libraryName == "Personal":
            try:
                # make the .zip from the current user
                data = rf.makeAllLibraryZIP(getCurrUser(), offset)
                succeeded = True
            except Exception as e:
                errorMessage = str(e)

    except KeyError:
        succeeded = False
        errorMessage = "Library not found."

    if succeeded:
        return Response(
            data,
            headers={
                "Content-Type": "application/zip",
                "Condent-Disposition": "attachment; filename='library.zip';",
            },
        )
    else:
        return errorZIP(errorMessage)


################################# BASIC PAGES #################################
###############################################################################


@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    """Route for /index and /. The homepage."""
    # set the logInMessage the user sees on the homepage.
    if checkLoggedIn():
        logInMessage = "Logged in as: {email}.".format(email=current_user.getEmail())
    else:
        logInMessage = "Not logged in."

    return render_template(
        "index.html", logInMessage=logInMessage, loggedIn=checkLoggedIn()
    )


@app.route("/privacy")
def privacyPolicy():
    """Route for /privacy. The privacy policy."""
    return render_template("privacy.html", loggedIn=checkLoggedIn())


@app.route("/about")
def about():
    """Route for /about. The information page."""
    return render_template("about.html", loggedIn=checkLoggedIn())
