#!/usr/bin/python


import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=False,
                        default='credentials.json',
                        help='Google app credentials json file')
    parser.add_argument('--source', type=str, required=True, help='Local file')
    parser.add_argument('--target_folder', type=str, required=False,
                        help='Id of remote folder')
    parser.add_argument('--name', type=str, required=False,
                        default=None, help='Remote name')
    args = parser.parse_args()

    client = GoogleDriveClient(args.creds)

    id = client.create_or_update_png(args.source, args.target_folder, args.name)
    print('Result file ' + id)
