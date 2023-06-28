#!/usr/bin/python
import os
from abc import ABC, abstractmethod

import PIL.Image

from google.google_drive_client import GoogleDriveClient
from param.config_enums import ImageProviderType
from util.helpers import Helpers


class ImageProvider(ABC):
    @abstractmethod
    def get_image(self, name: str) -> PIL.Image.Image:
        pass

    @abstractmethod
    def save_image(self, name: str, img: PIL.Image.Image) -> str:
        pass


class ImageProviderFactory(ABC):
    _DEFAULT_PROVIDER = ImageProviderType.LOCAL

    @staticmethod
    def build(config: dict) -> ImageProvider:
        p: ImageProviderType = (
            Helpers.dont_require(config, "image_provider")
            or ImageProviderFactory._DEFAULT_PROVIDER
        )

        if p == ImageProviderType.LOCAL:
            return LocalImageProvider(
                Helpers.require(config, "assets/folder"),
                Helpers.require(config, "output/folder"),
            )
        elif p == ImageProviderType.GOOGLE:
            return GoogleDriveImageProvider(
                Helpers.require(config, "google_secrets_path"),
                Helpers.require(config, "assets/folder"),
                Helpers.require(config, "output/folder"),
                Helpers.dont_require(config, "output/temp_folder"),
            )
        else:
            raise Exception('Unsupported image provider type "' + p + '"')


class GoogleDriveImageProvider(ImageProvider):
    _TEMP_FOLDER = "../example/temp/google/"

    def __init__(
        self,
        secrets_path: str,
        asset_folder_id: str,
        output_folder_id: str,
        temp_folder: str | None,
    ):
        self._temp_folder = temp_folder or GoogleDriveImageProvider._TEMP_FOLDER
        if not os.path.exists(self._temp_folder):
            os.makedirs(self._temp_folder)
        self._asset_folder_id = asset_folder_id
        self._output_folder_id = output_folder_id
        self._client = GoogleDriveClient(secrets_path)

    def get_image(self, name: str) -> PIL.Image.Image:
        temp_file = os.path.join(self._temp_folder, name)
        self._client.download_file(name, temp_file, self._asset_folder_id)
        # dont cache Image objects so callers can manage lifecycle
        img = PIL.Image.open(temp_file)
        return img

    def save_image(self, name: str, img: PIL.Image.Image):
        if not os.path.exists(self._temp_folder):
            os.makedirs(self._temp_folder)
        temp_file = os.path.join(self._temp_folder, name)
        img.save(temp_file, format=name.split(".")[-1] if "." in name else "png")
        id = self._client.create_or_update_png(temp_file, self._output_folder_id, name)
        return GoogleDriveClient.DOWNLOAD_URL_FORMAT.format(id)


class LocalImageProvider(ImageProvider):
    def __init__(self, asset_folder: str, output_folder):
        self._asset_folder = asset_folder
        self._output_folder = output_folder

    def get_image(self, name: str) -> PIL.Image.Image:
        return PIL.Image.open(os.path.join(self._asset_folder, name))

    def save_image(self, name: str, img: PIL.Image.Image):
        if not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)
        output_file = os.path.join(self._output_folder, name)
        img.save(
            output_file,
            format=name.split(".")[-1] if "." in name else "png",
        )
        return output_file
