#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions that are used by the routes file.

@author: Lia Thomson
"""

# design
from enumsExceptions import (
    SequenceMismatchError,
    SequenceNotFoundError,
    BackboneNotFoundError,
)
from users import UserData, defaultUser
from misc import checkType, printIf
from string import ascii_letters, digits

from component import SpacerData

maxPosition = SpacerData.getMaxPosition()

# assembly
from datetime import datetime, timedelta
import re

# zips
import os
from shutil import rmtree, make_archive
from uuid import uuid1, uuid4
import random

validCharacters = ascii_letters + digits + "_-:;.,[]{}()<>=+?@^~|/#$*&`! "
specialChars = {"&quot;": '"', "&#039;": "'"}

#################################### MISC #####################################
def boolJS(b):
    """Translates "true" and "false" strings into boolean counterparts.
    Used for translating JavaScript data from the site to Python data.

    PARAMETER:
            b: string that is "true" or "false"

    RETURNS:
            Boolean counterpart of b
    """

    if b == "true":
        return True
    elif b == "false":
        return False
    else:
        if type(b) != str:
            raise TypeError("b not a boolean")
        else:
            raise ValueError("b not true or false")


def extractSequence(originSeq):
    """Remove all numbers and whitespace from a string."""
    seq = re.sub("\s|\d", "", originSeq)
    return seq


# temporary passwords or something
def makePass():
    """Return 32-character long string of random letters and numbers.

    NOTE:
            For possible future generation of temporary, random passwords.
            Not currently in use."""
    temp = uuid4().hex + uuid4().hex

    characters = "{letters}{digits}{d1}{d2}".format(
        letters=ascii_letters,
        digits=digits,
        d1=digits[random.randrange(10)],
        d2=digits[random.randrange(10)],
    )

    password = []

    for i in range(0, 64, 2):
        index1 = int(temp[i : i + 2], 16)
        index = (int)(index1 / 4)

        password.append(characters[index])

    return "".join(password)


################################# DESIGN PAGE #################################
def validateNewNS(newNSType, newNSName, newNSSeq):
    """Validates the input from creating a new NamedSequence on the design page.

    PARAMETERS:
            newNSType: string type for the named sequence ("Pr", "RBS", "GOI", or "Term")
            newNSName: string name for the named sequence
            newNSSeq: string sequence for the named sequence

    RETURNS:
            validInput: boolean. True if all input is valid, False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
    """
    validInput = True
    outputStr = ""

    #####   TYPE CHECKING   #####
    if type(newNSType) != type(newNSName) != type(newNSSeq) != str:
        validInput = False
        outputStr += "ERROR: input received not all strings.<br>"

    try:
        checkType(newNSType, "newNSType")
    except ValueError:
        validInput = False
        outputStr += "ERROR: '" + newNSType + "' is not a valid type.<br>"

        #####   VALIDATE NAME   #####
    # length
    if len(newNSName) < 1 or len(newNSName) > 20:
        validInput = False
        outputStr += "ERROR: Sequence name must be 1-20 characters.<br>"

    # whether it already exists in default:
    longNames = {
        "Pr": "promoter",
        "RBS": "ribosome binding site",
        "GOI": "gene",
        "Term": "terminator",
    }
    for elemType in ["Pr", "RBS", "GOI", "Term"]:
        try:
            defaultUser.findNamedSequenceNoSeq(elemType, newNSName)

            validInput = False
            outputStr += (
                "ERROR: {newNSName} already exists in the default "
                "library as a {longName}.<br>"
            ).format(newNSName=newNSName, longName=longNames[elemType])
            break
        except SequenceMismatchError:
            validInput = False
            outputStr += (
                "ERROR: {newNSName} already exists in the default "
                "library as a {longName}, and with a different sequence.<br>"
            ).format(newNSName=newNSName, longName=longNames[elemType])
            break
        except SequenceNotFoundError:
            pass

    # characters
    for special in specialChars:
        newNSName = newNSName.replace(special, specialChars[special])

    invalidCharactersName = []

    for character in newNSName:
        if (character not in validCharacters) and (
            character not in invalidCharactersName
        ):
            validInput = False
            outputStr += (
                "ERROR: '" + character + "' is not allowed in a sequence's name.<br>"
            )
            invalidCharactersName.append(character)

            #####   VALIDATE SEQUENCE       #####
    # length
    if (
        len(newNSSeq) < 1 or len(newNSSeq) > 99999
    ):  # I don't know what limits should be used
        validInput = False
        outputStr += "ERROR: Sequence must be 1-99999 nucleotides.<br>"

    # characters
    validNucleotides = "AGTCBDHKMNRSVWY"

    invalidCharactersSeq = []

    # check special Chars first:
    for special in specialChars:
        if special in newNSSeq:
            validInput = False
            outputStr += (
                "ERROR: {char} is not allowed in a sequence's name.<br>".format(
                    char=specialChars[special]
                )
            )
            invalidCharactersSeq.append(specialChars[special])

    for character in newNSSeq:
        if (character not in validNucleotides) and (
            character not in invalidCharactersSeq
        ):
            validInput = False
            outputStr += "ERROR: '" + character + "' is not an allowed nucleotide.<br>"
            invalidCharactersSeq.append(character)

    return (validInput, outputStr)


def validateSpacers(newPosStr, newTerminalStr):
    """Validates the input to create a new SpacerData on the design page.

    PARAMETERS:
            newPosStr: string of an integer for the position of the component
            newTerminalStr: string of a boolean for if the component is terminal

    RETURNS:
            validInput: boolean. True if all input is valid, False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
            newPos: newPos as an integer
            isTerminal: isTerminal as a boolean
    """
    validInput = True
    outputStr = ""

    ####   VALIDATE POSITION   ####
    # turn into integer
    try:
        newPos = int(newPosStr)
    except Exception:
        validInput = False
        outputStr += "ERROR: position not an integer.<br>"

    # ensure its within range
    if validInput:
        # if it is not within range
        if (newPos < 0) or (newPos > maxPosition):
            # if newPos is not 999 (if it is 999, it is at position T)
            if newPos != 999:
                validInput = False
                outputStr += (
                    "ERROR: Position must be in range 1-{maxPosition}.<br>".format(
                        maxPosition=maxPosition
                    )
                )

                ####   VALIDATE ISTERMINAL   ####
    # turn into boolean
    try:
        isTerminal = boolJS(newTerminalStr)
    except Exception:
        validInput = False
        outputStr += "ERROR: Last element value not valid.<br>"

    # if the position is the maximum allowed position, it must be terminal
    if validInput and (newPos == maxPosition) and (not isTerminal):
        validInput = False
        outputStr += "ERROR: {newPos} is the last allowed position, so it must be terminal.<br>".format(
            newPos=newPos
        )

    return (validInput, outputStr, newPos, isTerminal)


def validatePrimers(TMstr, rangeStr):
    """Validates the input to create a new PrimerData on the design page.
    Specifically, when determining primers for a new component.

    PARAMETERS:
            TMstr: string of a number that is the ideal TM, in Celsius
            rangeStr: string of a number that is deviance allowed from the ideal TM

    RETURNS:
            validInput: boolean. True if all input is valid, False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
            TMnum: ideal TM as a float
            rangeNum: range as a float
    """
    validInput = True
    outputStr = ""

    # type checking
    # TM
    try:
        TMnum = float(TMstr)
    except Exception:
        validInput = False
        outputStr += "ERROR: TM not a number.<br>"

    # range
    try:
        rangeNum = float(rangeStr)
    except Exception:
        validInput = False
        outputStr += "ERROR: TM range not a number.<br>"

    # ensure the values are within the allowed ranges
    if validInput:
        # TM
        if TMnum < 20 or TMnum > 80:  # I don't know what to actually limit it by
            validInput = False
            outputStr += "ERROR: Melting point out of range 20-80<br>"

        # range
        if rangeNum < 1 or rangeNum > 10:
            validInput = False
            outputStr += "ERROR: Range for melting point must be in range 1-10.<br>"

    return (validInput, outputStr, TMnum, rangeNum)


def validateBackbone(newName, newDesc, newSeq, newType, newFeatures):
    """Validates the input from creating a new backbone on the design page.

    PARAMETERS:
            newName: string name of the new backbone
            newDesc: string description for the backbone
            newSeq: string for the sequence of the backbone
            newType: string for the type of the backbone. Valid values are "i" and "r"
                    for integrative and replicative, respectively.
            newFeatures: string for the features of the backbone. Formatted as it
                    will appear in a .gb file.

    RETURNS:
            validInput: boolean. True if all input is valid, False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
    """
    validInput = True
    outputStr = ""

    #####   TYPE CHECKING   #####
    if (
        (type(newName) != type(newDesc) != type(newSeq) != str)
        != type(newType)
        != type(newFeatures)
    ):
        validInput = False
        outputStr += "ERROR: input received not all strings.<br>"

        #####   VALIDATE NAME   #####
    # length
    if len(newName) < 1 or len(newName) > 20:
        validInput = False
        outputStr += "ERROR: Backbone name must be 1-20 characters.<br>"

        # whether it already exists in default:
        try:
            defaultUser.findBackbone(newName)

            validInput = False
            outputStr += "ERROR: Backbone {name} already exists in the default library.<br>".format(
                name=newName
            )

        except BackboneNotFoundError:
            pass

    # characters
    invalidCharactersName = []

    for special in specialChars:
        newName = newName.replace(special, specialChars[special])

    for character in newName:
        if (character not in validCharacters) and (
            character not in invalidCharactersName
        ):
            validInput = False
            outputStr += (
                "ERROR: '{character}' is not allowed in a backbone's name.<br>".format(
                    character=character
                )
            )
            invalidCharactersName.append(character)

            #####   VALIDATE DESCRIPTION    #####
    if len(newDesc) < 1 or len(newDesc) > 128:
        validInput = False
        outputStr += "ERROR: Description must be 1-128 characters long.<br>"

    for special in specialChars:
        newDesc = newDesc.replace(special, specialChars[special])

        #####   VALIDATE SEQUENCE       #####
    # length
    # 999,999 chosen arbitrarily, because I think SOME limit is necessary
    if len(newSeq) < 1 or len(newSeq) > 999999:
        validInput = False
        outputStr += "ERROR: Sequence must be 1-999999 nucleotides.<br>"

    # characters
    validNucleotides = "AGTCBDHKMNRSVWYagtcbdhkmnrsvwy"

    for special in specialChars:
        newSeq = newSeq.replace(special, specialChars[special])

    invalidCharactersSeq = []
    for character in newSeq:
        if (character not in validNucleotides) and (
            character not in invalidCharactersSeq
        ):
            validInput = False
            outputStr += (
                "ERROR: '{character}' is not an allowed nucleotide.<br>".format(
                    character=character
                )
            )
            invalidCharactersSeq.append(character)

            #####   VALIDATE TYPE   #####
    if newType != "i" and newType != "r":
        validInput = False
        outputStr += "ERROR: Invalid backbone type received.<br>"

        #####   VALIDATE Features       #####
    # currently assumes the feature section is formatted properly
    # ?! change? check what?

    return (validInput, outputStr)


def searchBackbone(seq):
    """Search a backbone sequence for the patterns to the left and right of the
    insertion site.
    Called by validateSearchBackbone().

    PARAMETER:
            seq: string sequence to search.

    RETURNS:
            sitesL: list of integer indices for where the left pattern begins
            sitesR: list of integer indices for where the right pattern begins
    """
    # make seq uppercase
    seq = seq.upper()

    # set the left and right patterns to search for
    patternL = "{spacerL}\w\w{start}".format(spacerL="AGGA", start="GTCTTC")
    patternR = "{end}\w\w{spacerR}".format(end="GAAGAC", spacerR="TACA")

    # search the the linear sequence
    sitesL = [m.start() for m in re.finditer(patternL, seq)]
    sitesR = [m.start() for m in re.finditer(patternR, seq)]

    # search the very end and beginning, combined (since it's circular)

    loopLen = 11  # length of the pattern (spacer-4 bp, NN-2 bp, recog.-6 bp) - 1

    # merge the very end and very beginning of seq, to search for the patterns
    veryEnd = seq[-loopLen:] + seq[0:loopLen]

    # search for the left pattern
    matchL = re.search(patternL, veryEnd)
    if matchL:
        # adjust the index to apply to the complete sequence, not just veryEnd
        index = matchL.start()
        if index < loopLen:
            index = len(seq) - (loopLen - index)
        else:
            index -= loopLen

        sitesL.append(index)

    # search for the right pattern
    matchR = re.search(patternR, veryEnd)
    if matchR:
        # adjust the index to apply to the complete sequence, not just veryEnd
        index = matchR.start()
        if index < loopLen:
            index = len(seq) - (loopLen - index)
        else:
            index -= loopLen

        sitesR.append(index)

    return (sitesL, sitesR)


def validateSearchBackbone(outputStr, seq):
    """Validate backbone sequence has one of each of the left and right patterns
    around the insertion location. (Patterns are AGGANNGTCTTC and GAAGACNNTACA.)
    Called by readBackboneGB().
    Calls searchBackbone().

    PARAMETERS:
            outputStr: string of HTML to output to the website. Added onto if errors are found.
            seq: string sequence of backbone to search for the patterns.

    RETURNS:
            validInput: boolean. True if sequence has exactly one of each pattern.
                    False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
    """
    validInput = True
    sitesL, sitesR = searchBackbone(seq)

    if len(sitesL) == 0:
        validInput = False
        sitesL.append(None)
        outputStr += (
            "ERROR: No match found for the <span class = 'monospaced'>"
            "AGGANNGTCTTC</span> pattern.<br>"
        )
    elif len(sitesL) > 1:
        validInput = False
        outputStr += (
            "ERROR: Multiple matches found for the <span class = "
            "'monospaced'>AGGANNGTCTTC</span> pattern.<br>"
        )

    if len(sitesR) == 0:
        validInput = False
        sitesR.append(None)
        outputStr += (
            "ERROR: No match found for the <span class = 'monospaced'>"
            "GAAGACNNTACA</span> pattern.<br>"
        )
    elif len(sitesL) > 1:
        validInput = False
        outputStr += (
            "ERROR: Multiple matches found for the <span class = "
            "'monospaced'>GAAGACNNTACA</span> pattern.<br>"
        )

    return (validInput, outputStr, sitesL[0], sitesR[0])


def readBackboneGB(dataBytes, outputStr):
    """Read a backbone .gb file, validate it as a properly formatted .gb file,
    and extract relevant information about the backbone.

    PARAMETERS:
            dataBytes: the .gb file in byte form
            outputStr: string of HTML to output to the website. Errors will be added to it.

    RETURNS:
            outputStr: string of HTML to output to the website. Displays all errors.
            validInput: boolean. True if the .gb file is valid, False otherwise.
            a dictionary of information extracted from the file, with the following keys
                    name: backbone name
                    molType: backbone's molecule type (e.g. "DNA")
                    division: backbone's division (e.g. "SYN")
                    definition: backbone's definition (i.e. description)
                    features: backbone's features section [words]
                    sequence: backboene's sequence
    """
    validInput = True

    features = None
    definition = None
    name = None
    molType = None
    seq = None
    division = None

    try:
        backboneData = dataBytes.splitlines(keepends=True)

        for i in range(len(backboneData)):
            backboneData[i] = backboneData[i].decode()

    except Exception as e:
        validInput = False
        print(e)
        outputStr += "ERROR: Invalid input received."

    if validInput:
        # look at the first line
        try:
            header = backboneData[0].split()

            if header[0] != "LOCUS":
                raise Exception("no LOCUS")

            lengthIndex = -1

            # find the length
            for i in range(len(header) - 1):
                if header[i + 1][-2:] == "bp":
                    if header[i + 1][-3:-2] == "-":
                        try:
                            length = int(header[i + 1][0:-3])
                            lengthIndex = i + 1
                        except Exception:
                            pass
                    else:
                        try:
                            length = int(header[i + 1][0:-2])
                            lengthIndex = i + 1
                        except Exception:
                            pass
                else:
                    try:
                        length = int(header[i + 1])
                        lengthIndex = i + 1
                    except Exception:
                        pass

            if lengthIndex == -1:
                raise Exception("Could not find length of sequence.")

            # remove "bp" if it's there
            if header[lengthIndex + 1] == "bp":
                header.pop(lengthIndex + 1)

            if len(header) < lengthIndex + 3:
                raise Exception(
                    (
                        "First line is too short."
                        "It must have the format: LOCUS locus_name sequence_length "
                        "molecule_type (optional: circular or linear) (optional: GenBank_division) "
                        "modification_date"
                    )
                )
            elif len(header) > lengthIndex + 5:
                raise Exception(
                    (
                        "First line is too long."
                        "It must have the format: LOCUS locus_name sequence_length "
                        "molecule_type (optional: circular or linear) (optional: GenBank_division) "
                        "modification_date"
                    )
                )

            # name
            name = " ".join(header[1:lengthIndex])

            # sequence type (molecule type) & division
            molType = header[lengthIndex + 1]
            if molType.find("DNA") == -1:
                raise Exception("Sequence must be a DNA sequence.")

            if header[lengthIndex + 2] == "linear":
                raise Exception("Sequence must be circular, not linear.")
            elif header[lengthIndex + 2] == "circular":
                if len(header) == 6:
                    division = ""
                else:
                    division = header[lengthIndex + 3]
            else:  # assume it is the division
                if len(header) == 7:
                    raise Exception(
                        "Unexpected word: {}".format(header[lengthIndex + 2])
                    )
                else:
                    if (
                        len(header) == 5
                    ):  # it is not the division, but the modification date
                        division = ""
                    else:
                        division = header[lengthIndex + 2]  # it is the division

            # the modification date will be dropped

            # definition
            defRow = backboneData[1].split(maxsplit=1)

            if defRow[0] != "DEFINITION":
                raise Exception("No DEFINITION")

            if len(defRow) == 1:
                definition = ""
            else:
                definition = defRow[1].rstrip()

            # IGNORES other information like Accession, Source, Journal, etc.

            # search for the relevant regions: the FEATURES and the ORIGIN
            featureIndex = -1
            originIndex = -1
            originEnd = -1

            for i in range(len(backboneData) - 2):
                if backboneData[i + 2][0:6] == "ORIGIN":
                    originIndex = i + 2
                elif backboneData[i + 2][0:8] == "FEATURES":
                    featureIndex = i + 2
                elif backboneData[i + 2][0:2] == "//":
                    originEnd = i + 2

            if featureIndex == -1:
                raise Exception("No FEATURE section found.")
            if originIndex == -1:
                raise Exception("No ORIGIN section found.")
            if originEnd == -1:
                raise Exception("No end of .gb (//) found.")
            if originIndex < featureIndex:
                raise Exception("Origin section should not be before feature section.")
            if originEnd < originIndex:
                raise Exception("End of .gb should be after Origin section.")

            # first look at the origin
            seq = extractSequence("\n".join(backboneData[originIndex + 1 : originEnd]))

            if len(seq) != length:
                raise Exception(
                    (
                        "Length of sequence declared in the first line "
                        "({firstLine} bp) and of the actual sequence in "
                        "the ORIGIN section ({originSec} bp) are inconsistent."
                    ).format(firstLine=length, originSec=len(seq))
                )

            # replace spacing of the FEATURES section with tabs
            for i in range(featureIndex + 1, originIndex):
                if backboneData[i].lstrip()[0] != "/":
                    row = backboneData[i].split(maxsplit=1)

                    if len(row) == 2:
                        if len(row[0]) <= 6:
                            backboneData[i] = "\t{row1}\t\t{row2}".format(
                                row1=row[0], row2=row[1]
                            )
                        else:
                            backboneData[i] = "\t{row1}\t{row2}".format(
                                row1=row[0], row2=row[1]
                            )
                    else:
                        backboneData[i] = "\t{row}".format(row=row[0])
                else:
                    backboneData[i] = "\t\t\t{row}\n".format(
                        row=backboneData[i].strip()
                    )

            features = "".join(backboneData[featureIndex + 1 : originIndex])

        except Exception as e:
            validInput = False
            outputStr += "ERROR: {}".format(e)

    return (
        outputStr,
        validInput,
        {
            "name": name,
            "molType": molType,
            "division": division,
            "definition": definition,
            "features": features,
            "sequence": seq,
        },
    )


def processGBfeatures(seq, features, outputStr):
    """Process a backbone's sequence and features for storage as a Backbone in the database.
    FINISH ANNOTATING THIS, IT IS A VERY COMPLICATED AND CONFUSING FUNCTION
    Calls validateSearchBackbone()

    PARAMETERS:
            seq: string sequence of the backbone
            features: string features
            outputStr: string of HTML to output to the website. Errors will be added to it.

    RETURNS:
            validInput: boolean. True if input is valid, False otherwise.
            outputStr: HTML string to output to the website so errors are displayed.
            a dictionary of information for creating a new Backbone, with keys:
                    seqBefore: string sequence of the backbone before the insertion region
                    seqAfter: string sequence of the backbone after the insertion region
                    featureSection: string of the features, formatted for a .gb file
                            Has stylistic modifications (e.g. tabs instead of spaces) and
                            "[AddLength]"s, for use during assembly.
    """
    sequenceBefore = None
    sequenceAfter = None
    featureSection = None

    # get the indices for the start of the left and right pattern
    # if there are only one of each
    validInput, outputStr, siteL, siteR = validateSearchBackbone(outputStr, seq)

    length = len(seq)

    printIf("siteL {} siteR {}".format(siteL, siteR))

    if validInput:
        try:
            # Apologies in advance if this entire section does not make sense.
            # I barely understood how it worked when I wrote it, and have since
            # forgotten.

            # insL is the leftmost index of the insertion region, i.e. the first
            # nucleotide to be removed.
            # it uses the numbering of the .gb file, which counts from 1 NOT 0
            # which is why it is calculated with + 5, not + 4
            if siteL + 4 >= length:
                insL = 5 - (length - siteL)
            else:
                insL = siteL + 5

            # relatedly, insR is the rightmost index of the insertion region, i.e.
            # the last nucleotide to be removed
            # I THINK???????
            # ?!
            if siteR + 7 >= length:
                insR = 8 - (length - siteR)
            else:
                insR = siteR + 8

            printIf((insL, insR))

            if insR >= insL:
                insertionAdjustment = (insR - insL) + 1
                rightmost = insR
            else:  # if the insertion region wraps back around
                insertionAdjustment = insR
                rightmost = length + 1

            printIf(
                "insertionAdjustment {} rightmost {}".format(
                    insertionAdjustment, rightmost
                )
            )

            deleteNextLine = False

            # go through every line of the features
            for i in range(len(features)):
                # remove whitespace on the left of the line
                features[i] = features[i].lstrip()

                # do nothing if there's nothing in this line
                if not features[i]:
                    continue

                # if the line does NOT begin with "/", so it is a feature key
                # that says what type the feature is
                if features[i][0] != "/":
                    # split the line into row, which splits the type (?) and location
                    # so "gene 5..10" turns into ["gene", "5..10"]
                    row = features[i].split(maxsplit=1)

                    printIf(features[i])

                    # if there is a range/location for the feature
                    if len(row) > 1:
                        # should have numbers in the string of the format NUMBER..NUMBER
                        rowElements = re.split("(\d+..\d+)", row[1])
                        # determine if it's formatted like join(5..10, 15..20)
                        if rowElements[0] == "join(":
                            isJoin = True
                        else:
                            isJoin = False

                        pairsRemove = 0

                        print(rowElements)
                        # every other element in the list should be a number pair
                        # the other elements will be "join(" etc.
                        for j in range(1, len(rowElements), 2):
                            removeFeature = False

                            # get the start and end index of the range
                            startIndex, endIndex = rowElements[j].split("..")
                            newStart = int(startIndex)
                            newEnd = int(endIndex)

                            # make sure the indices are less than the length
                            # if they loop around
                            if newStart > length:
                                newStart -= length

                            if newEnd > length:
                                newEnd -= length

                            printIf(
                                "newStart {} newEnd {} \t insL {} insR {}".format(
                                    newStart, newEnd, insL, insR
                                )
                            )

                            # if the insertion region is in the middle of the sequence
                            # it does NOT loop around at the end
                            if insR >= insL:
                                # if newStart is within the insertion region
                                if newStart >= insL and newStart <= insR:
                                    # if newEnd is within the insertion region
                                    if newEnd >= insL and newEnd <= insR:
                                        # need to remove the feature
                                        removeFeature = True

                                        printIf("need to remove the entire thing")

                                    # otherwise, shove newStart to insR + 1
                                    # so the range begins at the end of the
                                    # insertion region
                                    else:
                                        newStart = insR + 1

                                        if newStart > length:
                                            newStart = newStart - length
                                # if newEnd is within the insertion region
                                # (but newStart is not)
                                elif newEnd > insL and newEnd <= insR:
                                    # shove newEnd insL - 1
                                    # so the range ends at the beginning of the
                                    # insertion region
                                    newEnd = insL - 1

                                    if newEnd < 1:
                                        newEnd = length + newEnd

                                insR2 = insR

                            # otherwise the insertion region DOES loop around
                            else:
                                # if newStart is within the insertion region
                                if newStart <= insR:
                                    # if newEnd is also within the insertion region
                                    if newEnd <= insR:
                                        # need to remove the entire feature
                                        removeFeature = True

                                        printIf("need to remove the entire thing")

                                    else:
                                        # shove newStart to the end of the
                                        # insertion region
                                        newStart = insR + 1

                                        if newStart > length:
                                            newStart = newStart - length
                                # if newEnd is within the insertion region
                                if newEnd >= insL:
                                    # end within insertion region
                                    if newStart >= insL:
                                        # rneed to remove the entire feature
                                        removeFeature = True

                                        printIf("need to remove the entire thing")
                                    else:
                                        # shove newEnd to the beginning of the
                                        # insertion region
                                        newEnd = insL - 1

                                        if newEnd < 1:
                                            newEnd = length + newEnd

                                printIf(
                                    "newStart {} newEnd {} insR {}".format(
                                        newStart, newEnd, insR
                                    )
                                )

                                printIf("newStart -= insR; newEnd -= insR")

                                # finally, subtract insR from newStart and newEnd
                                # to account for the removal of the insertion region
                                newStart -= insR
                                newEnd -= insR

                                insR2 = length - insR

                            # normally, rightmost = insR
                            # looping, rightmost = length + 1

                            # normally, insR2 = insR
                            # looping, insR2 = length - insR

                            # ?!!!! what is going on

                            # I have previously stated I do not remember how this
                            # section works. So I'm not really sure what insR and
                            # rightmost represent, nor why these if statments are
                            # used. I only know that they work.

                            # dealing with newStart
                            if newStart >= insR2:
                                # if newStart is to the right of the insertion region
                                if newStart >= rightmost:
                                    # [AddLength]NUMBER[AddLength] indicates the
                                    # number must have the length of the inserted
                                    # sequence added to it in the final sequence
                                    startStr = "[AddLength]{}[AddLength]".format(
                                        newStart - insertionAdjustment
                                    )
                                else:
                                    startStr = str(newStart - insertionAdjustment)
                            else:
                                startStr = str(newStart)

                            # dealing with newEnd
                            if newEnd >= insR2:
                                # if newEnd is to the right of the insertion region
                                if newEnd >= rightmost:
                                    endStr = "[AddLength]{}[AddLength]".format(
                                        newEnd - insertionAdjustment
                                    )
                                else:
                                    endStr = str(newEnd - insertionAdjustment)
                            else:
                                endStr = str(newEnd)

                            # finally, update rowElements[j]
                            if removeFeature:
                                rowElements[j] = ""
                                pairsRemove += 1
                            else:
                                rowElements[j] = "{start}..{end}".format(
                                    start=startStr, end=endStr
                                )
                        # end of "for(j in range..." loop
                        # i.e. have gone through all number pairs

                        # proceed to deal with the line as a whole

                        printIf(
                            (
                                "isJoin = {} \tpairsRemove = {} \t"
                                "int(len(rowElements) / 2) - 1) = {}"
                            ).format(isJoin, pairsRemove, int(len(rowElements) / 2) - 1)
                        )

                        # if the entire feature needs to be removed
                        if pairsRemove == int(len(rowElements) / 2):
                            deleteNextLine = True
                            features[i] = ""
                        # otherwise, the feature stays
                        else:
                            deleteNextLine = False

                            # replace the row with the properly formatted one
                            # if row[0] is 3 characters or shorter
                            if len(row[0]) <= 3:
                                # two tabs are needed to look right
                                features[i] = "\t{row1}\t\t{row2}".format(
                                    row1=row[0], row2="".join(rowElements)
                                )
                            # if row[0] is longer than 3 characters
                            else:
                                # only one tab is needed
                                features[i] = "\t{row1}\t{row2}".format(
                                    row1=row[0], row2="".join(rowElements)
                                )

                        # remove empty numbers in a join
                        if isJoin:
                            while features[i].find(",,") != -1:
                                features[i] = features[i].replace(",,", ",")
                            features[i] = features[i].replace("(,", "(")
                            features[i] = features[i].replace(",)", ")")
                            features[i] = features[i].replace("( ", "(")
                            features[i] = features[i].replace(" )", ")")

                            # remove the join() if there's only one set of numbers remaining
                            if pairsRemove == int(len(rowElements) / 2) - 1:
                                features[i] = features[i].replace("join(", "")
                                features[i] = features[i].replace(")", "")

                        printIf(features[i])
                        printIf("===")

                # if this is a qualifier of a feature, e.g. /organism="Saccharomyces cerevisiae"
                # so there are no numbers to adjust
                else:
                    # add three tabs to the beginning
                    features[i] = "\t\t\t" + features[i]

                # clear the line if deleteNextLine is true
                # i.e. the feature needs to be deleted
                if deleteNextLine:
                    features[i] = ""

            featureSection = "".join(features)

            # remove the insertion region by setting sequenceBefore and sequenceAfter
            if insL <= insR:
                sequenceBefore = seq[0 : insL - 1]
                sequenceAfter = seq[insR:]
            else:
                sequenceBefore = seq[insR : insL - 1]
                sequenceAfter = ""

        except Exception as e:
            outputStr += "ERROR: {}".format(e)
            validInput = False

    return (
        outputStr,
        validInput,
        {
            "seqBefore": sequenceBefore,
            "seqAfter": sequenceAfter,
            "featureSection": featureSection,
        },
    )


################################ ASSEMBLY PAGE ################################


def addSpacerAssemblyGB(spacer, features, i):
    """Add a spacer to the features. Modifies the features list to do so.
    Called when constructing the .zip of an assembled sequence.

    PARAMETERS:
            spacer: string spacer sequence to add
            features: list of strings, each a line for the .gb file's FEATURES section
            i: integer length of the total assembled sequence so far

    RETURNS:
            new integer length of the total assembled sequence
    """
    lenSpacer = len(spacer)

    # add the appropriate lines to the features
    features.append(
        "\tmisc_feature\t{start}..{end}".format(start=i + 1, end=i + lenSpacer)
    )
    features.append('\t\t\t/note="spacer"')
    # the following lines are only used by Benchling? and aren't standard for .gb files
    features.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
    features.append("\t\t\t/ApEinfo_revcolor=#E6855F")

    return i + lenSpacer


def addCompAssemblyGB(comp, features, i):
    """Add feature of component for a .gb file. Modifies the features list to do so.

    PARAMETERS:
            spacer: Component (ComponentDB?) to add
            features: list of strings, each a line for the .gb file's FEATURES section
            i: integer length of the total assembled sequence so far

    RETURNS:
            new integer length of the total assembled sequence
    """
    lenSeq = len(comp.getSeq())

    # if the component is a GOI, format as a gene
    if comp.getType() == "GOI":
        features.append("\tgene\t\t{start}..{end}".format(start=i + 1, end=i + lenSeq))
        features.append('\t\t\t/gene="{name}"'.format(name=comp.getName()))
    # otherwise, the component is regulatory
    else:
        regTypes = {
            "Pr": "promoter",
            "RBS": "ribosome_binding_site",
            "Term": "terminator",
        }
        regName = regTypes[comp.getType()]
        longTypes = {"Pr": "promoter", "RBS": "RBS", "Term": "terminator"}
        longType = longTypes[comp.getType()]

        features.append(
            "\tregulatory\t{start}..{end}".format(
                start=i + 1, end=i + lenSeq if comp.getType() != "GOI" else lenSeq - 2
            )
        )  # leave room for the RBS padding
        features.append("\t\t\t/regulatory_class=" + regName)
        features.append(
            '\t\t\t/note="{longType} {name}"'.format(
                longType=longType, name=comp.getName()
            )
        )

    # append the GG padding annotation for the RBS. In practice, this should
    # probably be a part of the "spacer", but the spacer GenBank annotation function doesn't have
    # the context to determine whether or not the component is a RBS.
    i += lenSeq
    if comp.getType() == "RBS":
        features.append("\tmisc_feature\t" + str(i + 1) + ".." + str(i + 2))
        features.append('\t\t\t/note="RBS padding"')
        features.append("\t\t\t/ApEinfo_fwdcolor=#E6855F")
        features.append("\t\t\t/ApEinfo_revcolor=#E6855F")
        i += 2

    return i


def finishCompAssemblyGB(features, fullSeq, offset, backboneName):
    """Make the head and ORIGIN section of the .gb file, then join all parts together into a single string.

    PARAMETERS:
            features: list of strings, each string being one line in the FEATURES section
            fullSeq: string of the complete assembled sequence
            offset: integer number of minutes the user's timezone is off from UTC
            backboneName: string name of the backbone being used.

    RETURNS:
            fileString: string of final formatted .gb file
    """
    # file head
    # get date, modifying for the user's timezone, and then format it into a string
    dateObject = datetime.utcnow() - timedelta(minutes=offset)
    date = dateObject.strftime("%d-%b-%Y").upper()

    # start completeFile, where each string is its own line, with the first three lines:
    # the header, the definition, and "FEATURES              Location/Qualifiers"
    completeFile = [
        "LOCUS\t\tAssembled_sequence\t{length} bp\tDNA\tcircular\tSYN\t{date}".format(
            length=len(fullSeq), date=date
        ),
        "DEFINITION\tSequence assembled from CyanoConstruct using backbone {name}.".format(
            name=backboneName
        ),
        "FEATURES\t\tLocation/Qualifiers",
    ]

    # process sequence for ORIGIN section
    seq = fullSeq.lower()

    i = 0
    # start origin with the first line being "ORIGIN"
    origin = ["ORIGIN"]

    # add most lines (60 nucleotides per line)
    while i < (len(seq) // 60):
        i60 = i * 60
        # format the line with the index
        # then 6 blocks of 10 nucleotides separated by spaces
        line = "{number} {block1} {block2} {block3} {block4} {block5} {block6}".format(
            number=str(i60 + 1).rjust(9, " "),
            block1=seq[i60 : i60 + 10],
            block2=seq[i60 + 10 : i60 + 20],
            block3=seq[i60 + 20 : i60 + 30],
            block4=seq[i60 + 30 : i60 + 40],
            block5=seq[i60 + 40 : i60 + 50],
            block6=seq[i60 + 50 : i60 + 60],
        )

        # add the line to the origin section
        origin.append(line)

        i += 1

    # if the final line has <60 nucleotides, it needs to be added in a different way
    remainder = len(seq) % 60
    if remainder != 0:
        line = str(i * 60 + 1).rjust(9, " ") + " "
        for j in range(remainder):
            line += seq[i * 60 + j]
            if (j + 1) % 10 == 0:
                line += " "

        origin.append(line)

    # merge file head, features, and origin sections
    completeFile.extend(features)
    completeFile.extend(origin)
    completeFile.append("//")

    # merge into a single string
    fileString = "\n".join(completeFile)

    return fileString


################################ ZIP FUNCTIONS ################################
def makeZIP(filesDict):
    """Make and return a .zip file.

    PARAMETER:
            filesDict: dictionary of files; the keys are string file names,
                    while the values are the file contents

    RETURNS:
            data: byte data of the complete .zip file
    """
    # type checking
    if type(filesDict) != dict:
        raise TypeError("filesDict not a dict")

    # check if there are no files to create
    if filesDict == {}:
        printIf("NO SEQUENCE; NO FILES CREATED")

        return None

    # make a random and unique submission ID for the folder
    submissionID = uuid1().hex

    # paths for folders
    # get the path for the "files" folder in cyanoConstruct
    filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    # get the path for the folder that will be created to store the files
    sessionDir = os.path.join(filesDirPath, submissionID)
    # create said folder
    os.mkdir(sessionDir)

    printIf("MADE DIRECTORY: " + sessionDir)

    # write files to the folder
    for fileName in filesDict:
        newName = os.path.join(sessionDir, fileName)
        with open(newName, "w") as f:
            f.write(filesDict[fileName])

    # make zip and write it to the zips folder
    zipPath = os.path.join(os.path.join(filesDirPath, "zips"), submissionID)
    make_archive(zipPath, "zip", sessionDir)

    # read zip as a byte file and store it as data
    with open(zipPath + ".zip", "rb") as f:
        data = f.readlines()

    # delete the session directory & zip file
    rmtree(sessionDir)
    os.remove(zipPath + ".zip")

    printIf("FINISHED CREATING FILES FOR SESSION " + submissionID)

    return data


def makeAllLibraryZIP(user, offset):
    """Create a .zip file of all components of a user.

    PARAMETER:
            user: a UserData whose library will be turned into a .zip
            offset: integer number of minutes the user's timezone is off from UTC

    RETURNS:
            data: byte data of the completed .zip file
    """
    # type checking
    # if(type(user) != UserData):
    #       raise TypeError("user not a UserData")

    # directories and paths
    filesDirPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    sessionDir = os.path.join(filesDirPath, uuid1().hex)
    libraryDir = os.path.join(sessionDir, user.getEmail() + "Library")

    # make the directories needed
    try:
        os.mkdir(sessionDir)
    except OSError:  # if it exists
        pass
    os.mkdir(libraryDir)

    printIf("MADE DIRECTORY: " + libraryDir)

    # do this.
    # ?! DOES THIS RETURN BACKBONES, ACTUALLY?
    # get the named sequences, sorted
    sortedNS = user.getSortedNS()
    # go through each type (e.g. RBS)
    for typeKey in sortedNS:
        # do nothing if the folder would be empty
        if sortedNS[typeKey] == []:
            continue

        # make folder for the type
        typeDir = os.path.join(libraryDir, typeKey)
        os.mkdir(typeDir)

        # for each named sequence of that type
        for ns in sortedNS[typeKey]:
            # get the components derived from the sequence
            nsComps = ns.getAllComponents()

            # do nothing if the folder would be empty
            if nsComps == []:
                continue

            # make folder for the sequence
            nameDir = os.path.join(typeDir, ns.getName())
            os.mkdir(nameDir)

            # sort the components
            nsComps.sort()

            # for each component derived from the sequence
            for comp in nsComps:
                # make folder for the component
                compDir = os.path.join(nameDir, comp.getNameID())
                os.mkdir(compDir)

                # get info. for the component (dict of file names and contents)
                compZIP = comp.getCompZIP(offset)

                # write the files for the component
                for fileName in compZIP:
                    filePath = os.path.join(compDir, fileName)

                    with open(filePath, "w") as f:
                        f.write(compZIP[fileName])

    # make the .zip
    zipPath = os.path.join(sessionDir, "libraryZIP")
    make_archive(zipPath, "zip", libraryDir)

    # read zip as a byte file
    with open(zipPath + ".zip", "rb") as f:
        data = f.readlines()

    # delete all folders and files created earlier in this function
    rmtree(sessionDir)

    printIf("FINISHED CREATING LIBRARY ZIP FOR USER " + user.getEmail())

    return data
