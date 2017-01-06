from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import time
from subprocess import call, check_call, check_output
from googleapiclient.http import MediaFileUpload

PREFIX = 'https://www.googleapis.com/auth/'
SCOPES = ['drive', 'drive.file', 'drive.metadata.readonly']

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


def calculateFolderSize(drive, folder_id):
    q = "'{}' in parents".format(folder_id)
    folder = drive.files().list(q=q, fields='files(size)').execute()
    x = sum([int(gFile['size']) for gFile in folder['files']])
    print('Folder Size:')
    print('{} b'.format(x))
    print('{} kB'.format(round(x / 1024.0)))
    print('{} MB'.format(round(x / 1024.0 ** 2)))
    print('{} GB'.format(round(x / 1024.0 ** 3)))

for i in range(len(SCOPES)):
    SCOPES[i] = PREFIX + SCOPES[i]
creds = authorizeUser()
drive = createService('drive', creds)
folder_id = input("Folder ID? ")
calculateFolderSize(drive, folder_id)
