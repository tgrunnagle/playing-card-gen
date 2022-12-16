#!/usr/bin/python


import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa

# copies contents of a local folder to a remote folder
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=False,
                        default='credentials.json',
                        help='Google app credentials json file')
    parser.add_argument('--source_folder', type=str, required=True, help='Local folder')
    parser.add_argument('--target_folder', type=str, required=False,
                        help='Id of the remote folder')
    args = parser.parse_args()

    client = GoogleDriveClient(args.creds)

    for file in os.listdir(args.source_folder):
        if file.split('.')[-1] != 'png':
            continue
        client.create_or_update_png(os.path.join(args.source_folder, file), args.target_folder)
