import os
from apiclient.errors import ResumableUploadError
from apiclient.http import MediaFileUpload
from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials


def createDriveService(client_email, key_file_path, user):
    """Create drive service.

        :param string client_email: Email used to gather the credentials.
        :param string key_file_path: Path of the credentials key file.
        :param string user: User to impersonate.
        :return: Authorized Drive API service instance.
    """

    # Read the private key
    with open(key_file_path, 'rb') as f:
        private_key = f.read()

    # Get the credentials and authorize the app
    credentials = SignedJwtAssertionCredentials(
        client_email, private_key,
        'https://www.googleapis.com/auth/drive.file',
        sub=user)

    http = Http()
    credentials.authorize(http)

    # Build and return the service object for the Drive API
    return build('drive', 'v2', http=http)


def insertFile(service, filename, title,
               mime_type, description='', parent_id=None):
    """Insert new file.

        :param object service: Drive API service instance.
        :param string title: Title of the file to insert with the extension.
        :param string description: Description of the file to insert.
        :param string parent_id: Parent folder's ID.
        :param string mime_type: MIME type of the file to insert.
        :param filename: Filename of the file to insert.
        :return: Inserted file metadata if successful, None otherwise.
    """

    media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)

    body = {
        'title': title,
        'description': description,
        'mimeType': mime_type
    }

    # Set the parent folder.
    if parent_id:
        body['parents'] = [{'id': parent_id}]

    request = service.files().insert(
        body=body,
        media_body=media_body)

    response = None
    try:
        while response is None:
            status, response = request.next_chunk(num_retries=2)
            if status:
                print('Uploaded %d%%.' % int(status.progress() * 100))
    except:
        raise ResumableUploadError('Failed to upload the file.')
    return response


def doUpload(
        client_email, keyfile, user, filename, mimetype,
        title=None, description=None, parent_id=None):

    if title is None:
        title = os.path.basename(filename)
    if description is None:
        description = ''

    service = createDriveService(client_email, keyfile, user)
    _file_metadata = insertFile(
        service, filename, title,
        mimetype, description=description, parent_id=parent_id)
