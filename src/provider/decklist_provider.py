#!/usr/bin/python
from abc import ABC, abstractmethod
from csv import DictReader
from typing import Optional

from google.google_drive_client import GoogleDriveClient
from param.config_enums import DecklistProviderType


class DecklistProvider(ABC):
    @abstractmethod
    def get_list(self, id: str) -> list[dict[str, str]]:
        pass


class DecklistProviderFactory(ABC):
    _DEFAULT_PROVIDER = DecklistProviderType.LOCAL

    def build(config: dict) -> DecklistProvider:
        p: DecklistProviderType = (
            config.get("decklist_provider") or DecklistProviderFactory._DEFAULT_PROVIDER
        )
        if p == DecklistProviderType.LOCAL:
            return LocalDecklistProvider()
        elif p == DecklistProviderType.GOOGLE:
            return GoogleDriveDecklistProvider(
                config.get("google_secrets_path"), config.get("google_assets_folder_id")
            )
        else:
            raise Exception('Unsupported decklist provider type "' + p + '"')


class GoogleDriveDecklistProvider(DecklistProvider):
    def __init__(self, secrets_path: str, folder_id: Optional[str]):
        self._client = GoogleDriveClient(secrets_path)
        self._folder_id = folder_id

    def get_list(self, id: str) -> list[dict[str, str]]:
        return list(self._client.download_csv(id, self._folder_id))


class LocalDecklistProvider(DecklistProvider):
    def __init__(self):
        return

    def get_list(self, id: str) -> list[dict[str, str]]:
        with open(id, "r", newline="\r\n") as file:
            return list(DictReader(file.readlines(), delimiter=","))
