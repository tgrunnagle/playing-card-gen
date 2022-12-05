# playing-card-gen
Generate custom playing cards, especially for tabletop games.

With a simple `.json` configuration file and a deck list in a `.csv` file, these scripts can render images suitable for use in Tabletop Simulator. The configuration defines some parameters and describes the layout of the card. The scripts will load assets from a local folder or Google drive, then render the layers and save a `.png` of the deck. Check out the `example/` folder to see what goes in and what comes out.

## Features
- Generates decklist images (usable with Tabletop Simulator) from assets and decklists in either local folders or Google drive.
- Uses flexible configuration to define card layout and other build parameters.
- Supports placing images and drawing text. Image placement is flexible and composable. The text layer supports wrapping, automatic font sizing, newlines, and image embeddings.
- Supports running deck generation in a Docker container to isolate dependencies.
- Generates Tabletop Simulator saved object files for quick development iterations.

There are two example configurations. Each generates the the same card type, but one uses local assets while the other reads them from Google drive.

## To run the local example
The flexibility of the input configuration can make it difficult to know what parameters are supported. `scripts/card_layer_factory.py` is a good source of truth for card layers, and `scripts/config_enums.py` should help with understanding appropriate parameter values. The example is already configured for a number of layer types along with other necessary build parameters.
```
python ./scripts/util/gen_local.py --config './example/example_local_config.json' --decklist './example/example.csv' --out_folder './temp/out/'
```

## To run in a Docker container - recommended
To encapsulate dependencies, there is a Flask server and Dockerfile to host the generator API in a Docker container. Note that only local assets can be used (no Google image provider), so the 'local' configuration is used.
To create the container and start the generator server:
```
docker run -p 8084:8084 --rm -it $(docker build -q --build-arg ASSETS_FOLDER="./example/assets/" --build-arg PORT=8084 .)
```
To call the server:
```
python ./scripts/util/gen_remote.py --config "./example/example_local_config.json" --decklist "./example/example.csv" --port 8084 --out_folder "./temp/out"
```
Alternatively, you can run the server locally:
```
python ./scripts/server.py --assets_folder './example/assets/' --port 8084
```

## To run the google drive example
The example renders a card defined in a Google sheet, using images stored in Google drive. You'll need to do some set up, however, due to Google drive permissions. The app can only interact with files it created in your drive or a shared one. To get started you'll need to upload the assets to the drive.

### 1. [Create a Google app](https://console.developers.google.com/).
Download the app credentials json. The example config expects it to be in `credentials.json` (which is in the `.gitignore`), but you can change that to point anywhere.

### 2. Upload decklist
Pick a folder to upload your assets to, and grab its id from the share url. To create an empty decklist in the remote folder `<folder_id>`:
```
python ./scripts/util/google_create_csv.py --creds './credentials.json' --name 'example' --folder_id '<folder_id>'
```
This will print the Id of the created spreadsheet, `<decklist_id>`. However, you should be able to refer to the assets by name in your configuration and decklists.

### 3. Upload images
To upload an image `<image_file>` in `<folder_id>`:
```
python ./scripts/util/google_upload_png.py --creds './credentials.json' --file <image_file> --name 'example_image.png' --folder_id '<folder_id>'
```
Alternatively specify `--update_id` to update an existing image. You can use the images in `example/assets/images/`.

### 4. Generate cards
Update `example/example_google_config.json` with the names of the files you uploaded (specifying the `"google_assets_folder_id"` enables reference by name rather than id).
```
python ./scripts/util/gen_local.py --config './example/example_google_config.json' --decklist '<decklist_name>' --output_folder 'temp/out/'
```

## Utility scripts
- Download all decklists and `.png`s from folder on Google drive. This can be useful to get assets into a local folder to load into the Docker image.
```
python ./scripts/util/google_download_folder.py --creds 'credentials.json' --source_folder_id <folder_id> --target_folder 'temp/assets/'
```

- Generate a decklist and prepare it for Tabletop Simulator. Uploads the generated deck image to Google drive, then generates a TTS saved object `.json` pointing to that image. Copy the result file to the game's saved objects folder (on Windows, `C:\Users\<you>\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\`), and load it into the game.

    Not having set up Google server authentication precludes this from running entirely within the Docker container, so dependencies need managed. The card generation can still happen in the container, but the interaction with Google drive to upload the result and determine file Ids can't. WIP.
    
    Note that to run this example you'll need to update the Ids in `example/example_tts_config.json`.
```
python ./scripts/util/gen_and_tts.py --tts_config "./example/example_tts_config.json" --deck_config "./example/example_local_config.json" --decklist "./example/example.csv" --out_folder "./temp/out" --copy_to_tts False --remote True
```