#!/usr/bin/python
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--create_csv",
        action="store_true",
        help="Create a .csv file in google drive. Requires --config, --name, and --dest."
    )
    parser.add_argument(
        "--upload_png",
        action="store_true",
        help="Uploads a .png to google drive. Requires --config, --src, and --dest."
    )
    parser.add_argument(
        "--upload_folder",
        action="store_true",
        help="Uploads a folder to google drive. Requires --config, --src, and --dest."
    )
    parser.add_argument(
        "--download_folder",
        action="store_true",
        help="Downloads a folder from google drive. Requires --config, --src, and --dest."
    )