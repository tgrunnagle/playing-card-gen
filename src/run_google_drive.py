#!/usr/bin/python
import argparse
from enum import StrEnum
import os

from google.google_drive_client import GoogleDriveClient

# TODO upload csv
class Actions(StrEnum):
    CREATE_CSV = "create_csv"
    UPLOAD_PNG = "upload_png"
    UPLOAD_FOLDER = "upload_folder"
    DOWNLOAD_FOLDER = "download_folder"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=[a.value for a in Actions],
        help="Action to perform.",
    )
    parser.add_argument(
        "--source_folder",
        type=str,
        required=False,
        help="Source folder path or ID",
    )
    parser.add_argument(
        "--target_folder", type=str, required=False, help="Target folder path or ID"
    )
    parser.add_argument("--source", type=str, required=False, help="Content source")
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="Content name",
    )
    parser.add_argument(
        "--creds_file",
        type=str,
        default="../credentials.json",
    )
    args = parser.parse_args()

    if not args.creds_file:
        raise Exception("--creds_file required.")
    client = GoogleDriveClient(args.creds_file)

    if args.action == Actions.CREATE_CSV:
        if not args.name or not args.target_folder:
            raise Exception("--name and --target_folder required.")
        client.create_csv(args.name, args.target_folder)
    elif args.action == Actions.UPLOAD_PNG:
        if not args.source or not args.target_folder:
            raise Exception("--source and --target_folder required.")
        client.create_or_update_png(args.source, args.target_folder, args.name)
    elif args.action == Actions.DOWNLOAD_FOLDER:
        if not args.source_folder or not args.target_folder:
            raise Exception("--source_folder and --target_folder required.")
        client.download_folder(args.source_folder, args.target_folder)
    elif args.action == Actions.UPLOAD_FOLDER:
        if not args.source_folder or not args.target_folder:
            raise Exception("--source_folder and --target_folder required.")
        for f in os.listdir(args.source_folder):
            if f.endswith(".png"):
                client.create_or_update_png(
                    os.path.join(args.source_folder, f), args.target_folder
                )
            elif f.endswith(".json"):
                client.create_or_update_json(
                    os.path.join(args.source_folder, f), args.target_folder
                )
    else:
        raise Exception("Unsupported action: " + args.action)
