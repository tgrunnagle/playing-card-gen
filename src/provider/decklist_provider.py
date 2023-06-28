#!/usr/bin/python
import os
from abc import ABC, abstractmethod
from csv import DictReader
from typing import Optional

from google.google_drive_client import GoogleDriveClient
from param.config_enums import DecklistProviderType
from util.helpers import Helpers


class DecklistProvider(ABC):
    @abstractmethod
    def get_list(self, id: str) -> list[dict[str, str]]:
        pass


class DecklistProviderFactory(ABC):
    _DEFAULT_PROVIDER = DecklistProviderType.LOCAL

    def build(config: dict) -> DecklistProvider:
        p: DecklistProviderType = (
            Helpers.dont_require(config, "decklist_provider")
            or DecklistProviderFactory._DEFAULT_PROVIDER
        )
        if p == DecklistProviderType.LOCAL:
            return LocalDecklistProvider(Helpers.require(config, "assets/folder"))
        elif p == DecklistProviderType.GOOGLE:
            return GoogleDriveDecklistProvider(
                Helpers.require(config, "google_secrets_path"),
                Helpers.require(config, "assets/folder"),
            )
        else:
            raise Exception('Unsupported decklist provider type "' + p + '"')


class GoogleDriveDecklistProvider(DecklistProvider):
    def __init__(self, secrets_path: str, asset_folder_id: Optional[str]):
        self._client = GoogleDriveClient(secrets_path)
        self._asset_folder_id = asset_folder_id

    def get_list(self, name: str) -> list[dict[str, str]]:
        return list(self._client.download_csv(name, self._asset_folder_id))


class LocalDecklistProvider(DecklistProvider):
    def __init__(self, asset_folder: str):
        self._asset_folder = asset_folder

    def get_list(self, name: str) -> list[dict[str, str]]:
        with open(os.path.join(self._asset_folder, name), "r", newline="\r\n") as file:
            return list(DictReader(file.readlines(), delimiter=","))
