#!/usr/bin/python

import argparse
from google_drive_client import GoogleDriveClient

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', type=str, required=True,
                        help='Google app credentials json file')
    parser.add_argument('--source_folder_id', type=str, required=True)
    parser.add_argument('--target_folder', type=str, required=True)
    args = parser.parse_args()

    client = GoogleDriveClient(args.creds)
    client.download_folder(args.source_folder_id, args.target_folder)
