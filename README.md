# playing-card-gen
Generate custom playing cards, especially for tabletop games.

With `json` configuration files and a `csv` decklist file, these scripts will render images suitable for printing (e.g. at [MPC](makeplayingcards.com)) and/or use in Tabletop Simulator. The configuration describes the layout of the card and details of the generation process. The scripts will load assets, render cards based on the configurations and decklist, and save the results in `png` files. Check out the `example/` folder for example assets and configurations.

## Features
- Generates formatted images from assets and decklists in either local folders or Google drive.
- Uses flexible configuration to define card layout and other build parameters.
- Includes rendering features such as static and card-specific text and images, and embedded symbols in text.
- Generates Tabletop Simulator saved object files for quick development iterations.

There are two example generation configurations, which describe how assets are retrieved and how and where results are saved. `example/example_config_local.json` uses local assets while `example/example_config_google.json` leverages Google drive. `example/deck_config.json` describes the card layout and other card-specific features.

## To initialize the python virtual environment
```
python -m venv env

# on macOS
source env/bin/activate

# on windows (in powershell, Set-ExecutionPolicy RemoteSigned)
.\env\Scripts\activate

# exit venv
deactivate
```

2. Install dependencies
```
pip install -r requirements.txt
```

## To run the generator using local assets
```
cd src
python .\run_gen.py -h
python .\run_gen.py --gen_config "..\example\gen_config_local.json" --deck_config "..\example\deck_config.json" --decklist "example.csv"
```

See `example/deck_config.json` for an example of how card formats are described in configuration. Most importantly, each type of card is a list of layers, which can be:
- Text: static (same on each card) or card-specific text, supporting vertical and horizontal alignment settings, colors, font size, and embedded symbols.
- Image: static or card-specific images.
- Symbol rows: an array of images with a specific orientation, for e.g. describing the costs or suits of a card.

The example exhibits many of the layer configurations and can be adapted as needed. Check out `src/layer/card_layer_factory.py` for the source of truth on the layer types and parameters.

## To run the generator against google drive
1. [Create a Google app](https://console.cloud.google.com)

Once you have created your app, navigate to the `APIs and Services` dashboard. From the `Enabled APIs & services` tab, enable the `Google Drive API` and `Google Sheets API` APIs.

From the `Credentials` tab, click `+ CREATE CREDENTIALS` and select `OAuth Client ID`. Select `Desktop App` from the dropdown and create the credentials. You will have an opportunity to download a `json` file containing the client ID and secret. You can also do so from the `Credentials` tab in the dashboard. Save the `json` file somewhere; the example configurations look for `credentials.json` in the root of the repo. Note `credentials.json` is in the `.gitignore`.

2. Use the `run_google_drive.py` helper script to initialize assets

Since the google client can only interact with files it created, use the `run_google_drive.py` helper script to
- Create an empty spreadsheet,
- Upload image assets

See the script parameters by running the following. You can find the folder IDs from google drive in the last segment of the URL path when browsing `https://drive.google.com`. 

```
python .\run_google_drive.py -h
```

3. Generate cards

Update `example/example_config_google.json` `input/folder` with the ID of the drive folder you uploaded assets to in step 3. Create an output folder and update `output/folder` with its ID. Then generate the cards pointing to `gen_config_google.json`.
```
python .\run_gen.py --gen_config "..\example\gen_config_google.json" --deck_config "..\example\deck_config.json" --decklist "example.csv"
```

## To generate a Tabletop Simulator object
If you've generated the cards and uploaded the results to Google drive (`output/type` is `google`), you can automatically generate a "saved object file" for use with Tabletop Simulator. Add the `--tts` parameter to `run_gen.py` to create the `json` object file. The script will also attempt to copy the file to the TTS saved objects folder so it can be easily loaded into the game (update `output/tts/saved_objects_folder` if the default path doesn't work for you).

```
python .\run_gen.py --gen_config "..\example\gen_config_google.json" --deck_config "..\example\deck_config.json" --decklist "example.csv" --tts
```
