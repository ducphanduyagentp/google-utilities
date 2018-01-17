from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from subprocess import call, check_call, check_output
from googleapiclient.http import MediaFileUpload

import time
import datetime
import math

PREFIX = 'https://www.googleapis.com/auth/'
SCOPES = ['drive', 'drive.file', 'drive.metadata.readonly']
sizeSuffix = ['B', 'kB', 'MB', 'GB', 'TB']
def authorizeUser():
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return creds


def createService(service, creds):
    SERVICE = discovery.build(service, 'v3', http=creds.authorize(Http()))
    return SERVICE

def getFolderInfo(drive, folderID):
    q = "'{}' in parents".format(folderID)
    gdriveFolder = drive.files().list(q=q, fields='nextPageToken, files', pageSize=1000).execute()

    subFolders = []
    files = []
    nFiles = 0
    nFolders = 0
    folderSize = 0

    while True:
        subFolders += [entry['id'] for entry in gdriveFolder['files'] if 'folder' in entry['mimeType']]
	files += [entry for entry in gdriveFolder['files'] if 'folder' not in entry['mimeType']]
        if 'nextPageToken' not in gdriveFolder:
            break
        gdriveFolder = drive.files().list(q=q, pageToken=gdriveFolder['nextPageToken'], fields='nextPageToken, files', pageSize=1000).execute()
    nFolders += len(subFolders)
    nFiles += len(files)
    folderSize += sum([int(entry['size']) for entry in files if 'size' in entry])
    for folder in subFolders:
        cFiles, cFolders, cFolderSize = getFolderInfo(drive, folder)
        nFiles += cFiles
        nFolders += cFolders
        folderSize += cFolderSize

    return (nFiles, nFolders, folderSize)

for i in range(len(SCOPES)):
    SCOPES[i] = PREFIX + SCOPES[i]
creds = authorizeUser()
drive = createService('drive', creds)
while True:
	folderID = str(raw_input("Folder ID? "))
	a, b, c = getFolderInfo(drive, folderID)
	idx = int(math.log(c, 1024))
	print('{} files, {} folders, {:.2f} {}'.format(a, b, c / (1024.0 ** idx), sizeSuffix[idx]))
