#!/usr/bin/python


import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=True,
                        help='Google app credentials json file')
    parser.add_argument('--file', type=str, required=True, help='Local file')
    parser.add_argument('--update_id', type=str, required=False,
                        help='To update: Id of the remote file')
    parser.add_argument('--folder_id', type=str, required=False,
                        help='To create: Id of remote folder')
    parser.add_argument('--name', type=str, required=False,
                        help='To create: Remote file name')
    args = parser.parse_args()

    if (args.update_id is None) == (args.folder_id is None):
        raise Exception(
            'Exactly one of --update_id (update) or --folder_id (create) must be specified')

    client = GoogleDriveClient(args.creds)

    if args.update_id is not None:
        client.update_png(args.file, args.update_id)
    else:
        target_name = args.name or os.path.split(args.file)[1]
        id = client.create_png(args.file, target_name, args.folder_id)
        print('New image id is ' + id)
