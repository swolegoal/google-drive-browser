"""
(c)2016 Andrew M Rogers. All Rights Reserved.
"""
"""
LICENSE
This program is licensed under the GPLv2 License.  For more information consult
the included LICENSE file in the the google-drive-browser directory.

AUTHORS
Andrew M Rogers
    Email: tuxlovesyou@gmail.com

ABOUT
This is a demonstration of a graphical file browser for Google Drive using
Google's Python client API and a modified version of the easygui library.

NOTES
More documentation coming at a later (unspecified) date.
"""

import httplib2
import os
import subprocess
import csv
import shutil
import mimetypes
import module_locator

"""Google Drive API imports"""
from apiclient import discovery
from apiclient import errors

import oauth2client
from oauth2client import client
from oauth2client.file import Storage
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools

"""MY MODULES"""
from andrewgui import *

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Drive Browser Demo'
OUT_PATH = os.path.join(os.path.dirname(__file__), 'out')
if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

class DriveState(object):
    """Store state provided by Drive."""

    def __init__(self, state):
        """
        Create a new instance of drive state.
        Parse and lode the JSON state parameter.

        ARGS:
            state: state query parameter as a string."""
        state_data = json.loads(state)
        self.action = state_data['action']
        self.ids = map(str, state_data.get('ids', []))

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns :
        Credentials, the obtained credential."""

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 
            'google-drive-browser-demo.json')
    if not os.path.exists(credential_path):
        subprocess.call(['touch', credential_path])

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed for backwards-compatibility with Python <= 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

"""SETUP"""
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v2', http=http)

def getFileInfo(file_id, file_property):
    fileInfo = service.files().get(fileId=folder_id).execute()
    return fileInfo[file_property]

def breadcrumbs(folder_id, pathStr):
    """GET BREADCRUMBS"""
    parent_folder_id = folder_id
    while True:
        if folder_id == 'root':
            pathStr = 'My Drive >'
            fileInfo = service.files().get(fileId=parent_folder_id).execute()
            break
        parents = service.parents().list(fileId=parent_folder_id).execute()
        for parent in parents['items']:
            parent_folder_id = parent['id']
            fileInfo = service.files().get(fileId=parent_folder_id).execute()
            pathStr = str(fileInfo['title']) + ' > ' + pathStr
        fileInfo = service.files().get(fileId=parent_folder_id).execute()
        if parent_folder_id == 'root' or fileInfo['title'] == 'My Drive':
            break
    return pathStr

def filePicker(msg, title, fileType):
    """RETRIEVE INITIAL FILE LISTING"""
    results = service.files().list(maxResults=0).execute()
    """for i in results:
        print i"""
    items = results.get('items', [])
    fileList = [' ']
    fileListDecorated = [' ']
    pathStr = ''
    folder_id = 'root'
    children_ids = [' ']
    selectedFileId = 'root'
    choice = 'none'

    if not items:
        print 'no files found.'
        msgbox("no files found / communication error.",
                image='gui_imgs/drive_icon.png', ok_button="exit")
        quit()
    else:
        while True:
            fileInfo = service.files().get(fileId=folder_id).execute()
            pathStr = fileInfo['title']
            pathStr = breadcrumbs(folder_id, pathStr)
            param = { # Set the parameters
                'q': "\'" + folder_id + "\' in parents",
                'maxResults': 0,
            }

            """GET THE FILE LIST FOR THE CURRENT FOLDER"""
            try:
                fileListDecorated = [' ']
                fileList = [' ']
                results = service.files().list(**param).execute()
                items = results.get('items', [])
            except errors.HttpError, error:
                msgbox("A connection error occurred.  Please check your " +
                            "connection and try again later. \n(%s)" % error,
                            image='gui_imgs/drive_icon.png', ok_button='Quit')
                print 'An error occurred: %s' % error
                quit()

            #print 'FILES:'
            index = 0
            if len(items) == 0:
                fileListDecorated.append(' ..')
                fileList.append(' ')
            if not items:
                parental = service.parents().list(fileId=folder_id).execute()
                for parent in parental['items']:
                    folder_id = parent['id']
                fileInfo = service.files().get(fileId=folder_id).execute()
                fileListDecorated = [' ..']
                msgbox("This is an empty folder.",
                        image='gui_imgs/folder_open.png', ok_button='Go Back')
                pathStr = breadcrumbs(folder_id, pathStr)
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    #print '[folder] {0}'.format(item['title'])
                    fileListDecorated[index] = ' [folder] ' + item['title']
                else:
                    #print item['title']
                    fileListDecorated[index] = item['title']
                    fileList[index] = item['title']
                fileListDecorated.append(' ..')
                fileList.append(' ')
                index += 1

            fileListDecorated.append(' .')
            choice = choicebox(msg + pathStr, title, fileListDecorated,
                    ok_button='Select',  cancel_button='Back a folder')

            isFolder = False
            isFile = False
            if not choice == None and choice.startswith(' [folder] '):
                isFolder = True
                choice = choice[10:]

            if choice == ' .' and fileType == "folder":
                print folder_id
                return folder_id

            for item in items:
                if item['title'] == choice:
                    if isFolder:
                        folder_id = item['id']
                        pathStr = str(item['title'])
                        break
                    if not isFolder:
                        selectedFileId= item['id']
                        isFile = True
                        break

                if (choice == None or choice == ' ..') and not folder_id == 'root':
                    parental = service.parents().list(fileId=folder_id).execute()
                    for parent in parental['items']:
                        folder_id = parent['id']
                        fileInfo = service.files().get(fileId=folder_id).execute()
                        pathStr = fileInfo['title']
                        break

            if isFile:
                break

        """There is life after the file chooser"""
        print choice
        print selectedFileId
        return selectedFileId

def fileDownloader(selectedFileId, conversion, fileDescription):
    fileInfo = service.files().get(fileId=selectedFileId).execute()
    download_url = None
    outfile = None
    if 'exportLinks' in fileInfo and conversion in fileInfo['exportLinks']:
        outfile = os.path.join(OUT_PATH, fileInfo['title'] + '.' + conversion[-3:])
        download_url = fileInfo['exportLinks'][conversion]
    elif 'downloadUrl' in fileInfo:
        outfile = os.path.join(OUT_PATH, fileInfo['title'])
        download_url = fileInfo['downloadUrl']
    else:
        msgbox("ERROR getting " + str(fileInfo['title']) + ".  Are you sure it is a %s?"
                % fileDescription,
                image='gui_imgs/folder_open.png', ok_button='Go Back')
        return None
    if download_url:
        print "Downloading " + fileInfo['title'] + "..."
        resp, content = service._http.request(download_url)
        if resp.status == 200:
            if os.path.isfile(outfile):
                print "File %s already exists, clobbering." % outfile
            with open(outfile, 'wb') as f:
                f.write(content)
                print "Done downloading %s." % outfile
                msgbox("Done downloading %s.  Moving on to conversion."
                        % outfile, image='gui_imgs/download.png',
                        ok_button='Continue')
                return outfile
        else:
            print 'ERROR downloading %s.' % fileInfo['title']
            msgbox('ERROR downloading %s.' % fileInfo['title'],
                    image='gui_imgs/network-error.png', ok_button="OK")
            outfile = None
    outfile = None
    return outfile

def main():
    msg = "Select a file you would like to download from your Google Drive.\n\n Current path: "
    title = "Choose a file"
    fileType = "file"
    outfile = None
    while not outfile:
        selectedFileId = filePicker(msg, title, fileType)
        conversion = 'text/csv'
        fileDescription = 'spreadsheet'
        outfile = fileDownloader(selectedFileId, conversion, fileDescription)
    fileType = mimetypes.guess_type(outfile)
    print fileType[0]
    if not fileType[0] == 'text/csv':
        msgbox('Spreadsheet conversion not performed.',
                image='gui_imgs/spreadsheet.png', ok_button='Quit')
        quit()
    elif not outfile:
        msgbox('File did not download.  Either the file link is invalid'
                + ' or your connection is down.  \n\nPlease verify that your internet ' +
                'connection is working and/or that you selected a spreadsheet file and try again.',
                image='gui_imgs/network-error.png', ok_button='Quit')
        quit()
    if outfile:
        print os.path.abspath(outfile)
        infilename = outfile
        outfilename = os.path.abspath(outfile) + '.tmp'
    else:
        msgbox('Something went horribly wrong!  You should never get here!\n\n'
                + 'The file didn\'t get out!  This should\'ve been found out in'
                + ' the last check!', ok_button='Kill me!')
        quit()

if __name__ == '__main__':
    main()
