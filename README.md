# playing-card-gen
Generate custom playing cards, especially for tabletop games.

The main script takes as arguments a configuration json file and a decklist file. The configuration is responsible for defining the parameters of your card design. For instance, which card type to use, the placement of the art, and from where to source your assets. The decklist is a .csv file with the columns expected for the card type. A copy of the example output is in `example/example.png`.

## Features
- Generates decklist images (usable with Tabletop Simulator) from assets and decklists in either local folders or Google drive.
- Uses flexible configuration to define card layout and other build parameters.
- Supports placing images and drawing text. So far there is an additional image layer for rendering in a line symbols mapped from text. The text layer supports wrapping, automatic font sizing, newlines, and image embeddings.
- Supports running in a Docker container to isolate dependencies.
- Generates saved object files for Tabletop Simulator.

There are two example configurations. Each generates the the same card type, but one uses local assets while the other reads them from Google drive.

## To run the local example
The flexibility of the input configuration can make it difficult to know what parameters are supported. `scripts/card_layer_factory.py` is a good source of truth for card layers, and `scripts/config_enums.py` should help with understanding appropriate parameter values. The example is already configured for a number of layer types along with other necessary build parameters.
```
python ./scripts/util/gen_local.py --config './example/example_local_config.json' --decklist './example/example.csv'
```

## To run in a Docker container - recommended
To encapsulate dependencies, there is a Flask server and Dockerfile to host the generator API in a Docker container. Note that only local assets can be used (no Google image provider).
To start the container:
```
docker run -p 8084:8084 --rm -it $(docker build -q --build-arg ASSETS_FOLDER="./example/assets/" --build-arg PORT=8084 .)
```
To call the server
```
python ./scripts/util/gen_remote.py --config "./example/example_docker_config.json" --decklist "./example/example.csv" --port 8084 --out_folder "./temp/out"
```
The output will be saved to `temp/out/example.png`.
Alternatively, you can run the server directly:
```
python ./scripts/server.py --assets_folder './example/assets/' --port 8084
```

## To run the google drive example

The example renders a card defined in a Google sheet, using images stored in Google drive. You'll need to do some set up, however, due to Google drive permissions. The app can only interact with files it created in your drive or a shared one. To get started you'll need to upload the assets to the drive.

### 1. [Create a Google app](https://console.developers.google.com/).
Download the app credentials json. The example config expects it to be in `credentials.json` (which is in the `.gitignore`), but you can change that to point anywhere.

### 2. Create the decklist
Pick a folder to upload your assets to, and grab its id from the share url. To create an empty decklist in the remote folder `<folder_id>`:
```
python ./scripts/util/google_create_csv.py --creds './credentials.json' --name 'example' --folder_id '<folder_id>'
```
This will print the Id of the created spreadsheet, `<decklist_id>`. However, you should be able to refer to the assets by name in your configuration and decklists.

The columns names in the decklist are referenced by the corresponding `CardBuilder` implementation, in this case the `ExampleCardBuilder`. Refer to `examples/assets/lists/example-local.csv` or the builder implementation itself to populate the decklist.

### 3. Upload images
To upload an image `<image_file>` in `<folder_id>`:
```
python ./scripts/util/google_upload_png.py --creds './credentials.json' --file <image_file> --name 'example_image.png' --folder_id '<folder_id>'
```
Alternatively specify `--update_id` to update an existing image. You can use the images in `example/assets/images/`.

### 4. Generate the cards
Update `example/example_google_config.json` with the names of the files you uploaded (specifying the `"google_assets_folder_id"` enables reference by name rather than id).
```
python ./main.py --config './example/example_google_config.json' --decklist '<decklist_name>'
```

## Utility scripts
- Download all decklists and `.png`s from folder on Google drive. This can be useful to get assets into a local folder to load into the Docker image.
```
python ./scripts/util/google_download_folder.py --creds 'credentials.json' --source_folder_id <folder_id> --target_folder 'temp/assets/'
```
- Generate a decklist and prepare it for Tabletop Simulator. Uploads the generated deck image to Google drive, then generates a TTS saved object `.json` pointing to that image. Copy the result file to the game's saved objects folder (on Windows, `C:\Users\<you>\Documents\My Games\Tabletop Simulator\Saves\Saved Objects\`), and load it into the game. Note that to run this example you'll need to update the Ids in `example/example_tts_config.json`.
```
python ./scripts/util/gen_and_tts.py --tts_config "./example/example_tts_config.json" --deck_config "./example/example_local_config.json" --decklist "./example/example.csv" --out_folder "./temp/out" --copy_to_tts False
```