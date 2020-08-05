"""Interface for persisting application settings"""
import logging
from pathlib import Path
import json
from copy import deepcopy

import yaml
from appdirs import user_config_dir
from friendlypics2.version import __version__
from friendlypics2.misc.app_settings_services.pinterest import PinterestSettings


class AppSettings:
    """Interface for accessing and persisting application settings"""
    def __init__(self):
        self._log = logging.getLogger(__name__)
        temp = user_config_dir("Friendly Pics 2", "The Friendly Coder", __version__)
        self._filename = Path(temp).joinpath("appsettings.yml")
        self._log.debug(self._filename)

        if self._filename.exists():
            self._data = yaml.safe_load(self._filename.read_text())
        else:
            self._data = dict()
        self._data["file_version"] = "1.0"

    def __str__(self):
        return json.dumps(self._data, indent=4)

    @property
    def _supported_services(self):
        # TODO: dynamically generate this list
        retval = {
            PinterestSettings.service_name: PinterestSettings
        }
        return retval

    @property
    def data(self):
        """dict: reference to the raw settings data managed by this object.
        Used exclusively for the settings dialog"""
        return self._data

    @data.setter
    def data(self, value):
        self._data = deepcopy(value)

    @property
    def path(self):
        """Location of the config file managed by this class"""
        return self._filename

    @property
    def file_version(self):
        """str: gets the schema version for the config file"""
        assert "file_version" in self._data
        return self._data.get("file_version")

    def save(self):
        """Saves the current contents of the app settings for later reference"""
        self._filename.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self._filename.open("w") as config_file:
            yaml.safe_dump(self._data, config_file)

    @property
    def supported_service_names(self):
        return self._supported_services.keys()

    def get_service(self, service_name):
        """Gets settings associated with a specific service

        Args:
            service_name (str):
                name of the service to load the settings for
                for a list of services supported by the app, see supported_service_names property

        Returns:
            class that manages the service-specific settings
        """
        if service_name not in self._supported_services.keys():
            raise NotImplemented(f"Service {service_name} not supported by the app")
        if "services" not in self._data:
            self._data["services"] = dict()
        if service_name not in self._data["services"]:
            self._data["services"][service_name] = dict()
        return self._supported_services[service_name](self._data["services"][service_name])
