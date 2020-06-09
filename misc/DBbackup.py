#cyanoConstruct backup databse
#https://www.pythoncircle.com/post/360/how-to-backup-database-periodically-on-pythonanywhere-server/

import os
from datetime import datetime
from zipfile import ZipFile
from time import time

DIR = os.path.join(os.path.expanduser("~"), "cyanoDBbackups")
FILE_PREFIX = "cyanoConstructDB"
FILE_SUFFIX_DATE_FORMAT = "%Y-%m-%d-%H:%MUTC"
USERNAME = "cyanogate"
DBNAME = USERNAME + "$cyanoconstruct"
DAYS_TO_KEEP = 2 #results in 3 files stored at any given time

#make today's backup
timestamp = datetime.now().strftime(FILE_SUFFIX_DATE_FORMAT)
backup_filename = os.path.join(DIR, FILE_PREFIX + timestamp + ".sql")

os.system("mysqldump -u " + USERNAME + " -h " + USERNAME + ".mysql.pythonanywhere-services.com '" + DBNAME +"'  > "+ backup_filename)

#make into zip
zip_filename = os.path.join(DIR, FILE_PREFIX + timestamp + ".zip")
with ZipFile(zip_filename, 'w') as zip:
    zip.write(backup_filename, os.path.basename(backup_filename))

#remove .sql file
os.remove(backup_filename)

#remove old backups
for filename in os.listdir(DIR):
	completePath = os.path.join(DIR, filename)
	secLastMod = time() - os.stat(completePath).st_mtime
	if(secLastMod > DAYS_TO_KEEP * 86400):
		print("REMOVING: " + completePath)
		os.remove(completePath)