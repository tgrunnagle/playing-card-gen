#!/usr/bin/python
from typing import Optional
import os
from abc import ABC, abstractmethod

import PIL.Image
from google_drive_client import GoogleDriveClient
from config_enums import ImageProviderType


class ImageProvider(ABC):

    @abstractmethod
    def get_image(id: str) -> PIL.Image.Image:
        pass


class ImageProviderFactory(ABC):

    _DEFAULT_PROVIDER = ImageProviderType.LOCAL

    @staticmethod
    def build(config: dict) -> ImageProvider:
        p: ImageProviderType = config.get(
            'image_provider') or ImageProviderFactory._DEFAULT_PROVIDER

        if p == ImageProviderType.LOCAL:
            return LocalImageProvider(
                config.get('local_image_folder'))
        elif p == ImageProviderType.GOOGLE:
            return GoogleDriveImageProvider(
                config.get('google_secrets_path'),
                config.get('google_assets_folder_id'),
                config.get('google_temp_folder'))
        else:
            raise Exception(
                'Unsupported image provider type "' + p + '"')


class GoogleDriveImageProvider(ImageProvider):

    _TEMP_FOLDER = './temp/google/'

    def __init__(
            self,
            secrets_path: str,
            folder_id: Optional[str],
            temp_folder: Optional[str]
    ):
        self._temp_folder = temp_folder or GoogleDriveImageProvider._TEMP_FOLDER
        if not os.path.exists(self._temp_folder):
            os.makedirs(self._temp_folder)
        self._folder_id = folder_id
        self._client = GoogleDriveClient(secrets_path)

    def get_image(self, id: str) -> PIL.Image.Image:
        file_name = self._get_local_file_name(id)
        if not os.path.exists(file_name):
            self._client.download_png(id, file_name, self._folder_id)
        # dont cache Image objects so callers can manage lifecycle
        img = PIL.Image.open(file_name)

        return img

    def _get_local_file_name(self, id: str) -> str:
        name = id if id.endswith('.png') else id + '.png'
        return os.path.join(self._temp_folder, name)


class LocalImageProvider(ImageProvider):
    def __init__(self, folder: str):
        self._folder = folder

    def get_image(self, id: str) -> PIL.Image.Image:
        return PIL.Image.open(os.path.join(self._folder, id))
