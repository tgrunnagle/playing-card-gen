#!/usr/bin/python

from google_drive_client import GoogleDriveClient
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=True,
                        help='Google app credentials json file')
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--folder_id', type=str, required=True)
    args = parser.parse_args()

    client = GoogleDriveClient(args.creds)

    id = client.create_csv(args.name, args.folder_id)
    print('New sheet id is ' + id)
