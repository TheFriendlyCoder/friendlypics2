"""Interface for persisting application settings"""
import logging
from pathlib import Path
import json

import yaml
from appdirs import user_config_dir
from friendlypics2.version import __version__


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
    def data(self):
        """dict: reference to the raw settings data managed by this object.
        Used exclusively for the settings dialog"""
        return self._data

    @property
    def path(self):
        """Location of the config file managed by this class"""
        return self._filename

    @property
    def pinterest_user(self):
        """str: user to authenticate with to Pinterest"""
        return self._data.get("services", dict()).get("pinterest", dict()).get("username")

    @pinterest_user.setter
    def pinterest_user(self, value):
        # TODO: consider saving config data every time a setter is accessed
        if "services" not in self._data:
            self._data["services"] = dict()
        if "pinterest" not in self._data["services"]:
            self._data["services"]["pinterest"] = dict()

        self._data["services"]["pinterest"]["username"] = value

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
