import os
from db.operations import getUsersData
from export.csv import writefile
from upload.upload_file import doUpload
from tempfile import mkstemp

HEADER = ['ID', 'Partner Name', 'Login',
          'Last Login', 'Active']


def run(host, main_db, user, password, role, client_email, keyfile_path,
        drive_user, mimetype, parent_id):
    data = getUsersData(host, main_db, user, password, role)
    for db in data.keys():
        file_fd, file_path = mkstemp(suffix='.csv', prefix=db)
        writefile(file_path, HEADER, data[db])
        os.close(file_fd)
        title = db + '.csv'
        doUpload(
            client_email, keyfile_path, drive_user, file_path, mimetype,
            title=title, description=db, parent_id=parent_id)
        os.remove(file_path)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Export users to '
                                     'google drive')
    parser.add_argument('host', help='Database host address')
    parser.add_argument('main_db', help='Main database to connect')
    parser.add_argument('user', help='Database user to connect')
    parser.add_argument('password', help='Database password used to connect')
    parser.add_argument('role', help='Database role owner of the databases '
                        'to be exported')
    parser.add_argument('client_email', help='Client email for the '
                        'service account')
    parser.add_argument('keyfile_path', help='Path to the key file provided '
                        'by Google App Engine')
    parser.add_argument('drive_user', help='Email of the user to impersonate')
    parser.add_argument('mimetype', help='File mimetype')
    parser.add_argument('--parent', nargs='?',
                        help='Parent folder to store the uploaded file')

    args = parser.parse_args()
    run(args.host, args.main_db, args.user, args.password, args.role,
        args.client_email, args.keyfile_path, args.drive_user,
        args.mimetype, args.parent)


if __name__ == '__main__':
    main()
