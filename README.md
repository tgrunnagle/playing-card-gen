# playing-card-gen
Generate custom playing cards, especially for tabletop games.

With a `.json` configuration file and a `.csv` decklist file, these scripts can render images suitable for printing or use in Tabletop Simulator. The configuration defines some parameters and describes the layout of the card. The scripts will load assets from a local folder or Google drive, then render the layers and save a `.png` of the deck. Check out the `example/` folder to see what goes in and what comes out.

## Features
- Generates formatted images from assets and decklists in either local folders or Google drive.
- Uses flexible configuration to define card layout and other build parameters.
- Supports placing images and drawing text. Image placement is flexible and composable. The text layer supports wrapping, automatic font sizing, newlines, and image embeddings.
- Supports running deck generation in a Docker container to isolate dependencies.
- Generates Tabletop Simulator saved object files for quick development iterations.

There are two example configurations. Each generates the the same card type, but one uses local assets (`example/example_config.json`) while the other reads them from Google drive (`example/example_config_google.json`).

## To run the local example
```
python scripts/util/gen.py -h
```
The flexibility of the input configuration can make it difficult to know what parameters are supported. `scripts/card_layer_factory.py` is a good source of truth for card layers, and `scripts/config_enums.py` should help with understanding appropriate parameter values. The example is already configured for a number of layer types along with other necessary build parameters.
```
python ./scripts/util/gen.py --config './example/example_config.json' --decklist './example/assets/example.csv' --out_folder './temp/out/'
```

## To run in a Docker container - recommended
To encapsulate dependencies, there is a Flask server and Dockerfile to host the generator API in a Docker container. Note that only local assets can be used (no Google image provider), so the 'local' configuration is used.
To create the container and start the generator server:
```
docker run -p 8084:8084 --gpus all --rm -it $(docker build -q --tag "playing-card-gen:latest" --build-arg ASSETS_FOLDER="./example/assets/" --build-arg PORT=8084 .)
```
To call the server:
```
python ./scripts/util/gen_remote.py --config "./example/example_config.json" --decklist "./example/assets/example.csv" --port 8084 --out_folder "./temp/out"
```

## To run the google drive example
This example renders a card defined in a Google sheet using images stored in Google drive. You'll need to do some set up, however, due to Google drive permissions. The app can only interact with files it created in your drive or a shared one. To get started you'll need to upload the assets to the drive.

1. [Create a Google app](https://console.developers.google.com/).
Download the app credentials json. The example config expects it to be in `credentials.json` (which is in the `.gitignore`), but you can change that to point anywhere.

2. Upload decklist
Pick a folder to upload your assets to, and grab its id from the share url. To create an empty decklist in the remote folder `<folder_id>`:
```
python ./scripts/util/google_create_csv.py --creds './credentials.json' --name 'example.csv' --folder_id '<folder_id>'
```
    This will print the Id of the created spreadsheet, `<decklist_id>`. However, you should be able to refer to the assets by name in your configuration and decklists.

3. Upload images
To upload an image `<image_file>` in `<folder_id>`:
```
python ./scripts/util/google_upload_png.py --creds './credentials.json' --source <local_file> --target_folder '<remote_folder_id>'
```
Alternatively you can upload a folder of `.png`s:
```
python ./scripts/util/google_upload_folder.py --creds './credentials.json' --source_folder <local_folder> --target_folder '<remote_folder_id>'
```

4. Generate cards
Update `example/example_config_google.json` with the names of the files you uploaded (specifying the `"google_assets_folder_id"` enables reference by name rather than id).
```
python ./scripts/util/gen.py --config './example/example_config_google.json' --decklist '<decklist_name>' --out_folder 'temp/out/'
```

## Utility scripts
- Download all decklists and `.png`s from folder on Google drive. This can be useful to get assets into a local folder to load into the Docker image.
```
python ./scripts/util/google_download_folder.py --creds 'credentials.json' --source_folder_id <folder_id> --target_folder 'temp/assets/'
```

- Generate a decklist and prepare it for Tabletop Simulator. Uploads the generated deck image to Google drive, then generates a TTS saved object `.json` pointing to that image. Optionally copy the result file to TTS's saved objects folder (on Windows, `C:\Users\<you>\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\`). It can be loaded in game from there.

    Not having set up Google server authentication precludes this from running entirely within the Docker container, so dependencies need managed. Since it interacts with Google drive you will need to follow step 1 of running the Google example. Finally, to run this example you'll need to update the folder ids in `example/example_tts_config.json`.
```
python ./scripts/util/gen_and_tts.py --tts_config "./example/example_tts_config.json" --deck_config "./example/example_config.json" --decklist "./example/assets/example.csv" --out_folder "./temp/out" --copy_to_tts
```

- Manually generate the Tabletop Simulator object file. If you don't have Google drive integration set up, you can do the following to set up TTS
    1. Generate the deck image with local assets,
    2. Manually upload the result image, along with a back image, to a shared folder in Google drive,
    3. Grab the file ids from the share links (`https://drive.google.com/drive/folders/<file_id>?usp=share_link`),
    4. Run `gen_tts.py` with the appropriate parameters (`-h`), this assembles the saved object `.json`.
