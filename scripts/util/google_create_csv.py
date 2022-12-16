#!/usr/bin/python

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from google_drive_client import GoogleDriveClient  # noqa

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=False,
                        default='credentials.json',
                        help='Google app credentials json file')
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--folder_id', type=str, required=True)
    args = parser.parse_args()

    client = GoogleDriveClient(args.creds)
    existing_ids = client.get_ids(args.name, args.folder_id)
    if len(existing_ids) > 0:
        raise Exception('Sheet already exists')

    id = client.create_csv(args.name, args.folder_id)
    print('Created file ' + id)
