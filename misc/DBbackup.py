#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup the database.

Uses code from: https://www.pythoncircle.com/post/360/how-to-backup-database-periodically-on-pythonanywhere-server/

@author: Lia Thomson
"""

import os
from datetime import datetime
from zipfile import ZipFile
from time import time

DAYS_TO_KEEP = 3  # results in 3 files being stored at any given time

# other variables
DIR = os.path.join(os.path.expanduser("~"), "cyanoDBbackups")
FILE_PREFIX = "cyanoConstructDB"
FILE_SUFFIX_DATE_FORMAT = "%Y-%m-%d-%H:%MUTC"
USERNAME = "cyanogate"
DBNAME = USERNAME + "$cyanoconstruct"

# make today's backup
# file name
timestamp = datetime.now().strftime(FILE_SUFFIX_DATE_FORMAT)
backup_filename = os.path.join(DIR, FILE_PREFIX + timestamp + ".sql")
# create the .sql backup using the file name
os.system(
    "mysqldump -u "
    + USERNAME
    + " -h "
    + USERNAME
    + ".mysql.pythonanywhere-services.com '"
    + DBNAME
    + "'  > "
    + backup_filename
)

# make the .sql file into a .zip
zip_filename = os.path.join(DIR, FILE_PREFIX + timestamp + ".zip")
with ZipFile(zip_filename, "w") as zip:
    zip.write(backup_filename, os.path.basename(backup_filename))

# remove the .sql file
os.remove(backup_filename)

# remove old backups
for filename in os.listdir(DIR):
    completePath = os.path.join(DIR, filename)
    secLastMod = time() - os.stat(completePath).st_mtime
    if secLastMod > DAYS_TO_KEEP * (86400 - 600):
        print("REMOVING: " + completePath)
        os.remove(completePath)
