import logging


class PinterestSettings:
    service_name = "pinterest"

    def __init__(self, data):
        self._data = data
        self._log = logging.getLogger(__name__)

    @property
    def user(self):
        """str: user to authenticate with to Pinterest"""
        # TODO: add a validate method that requires the username to be defined
        #       need to still provide a way to construct an instance of the object the first time
        #       maybe with a factory method
        return self._data.get("username")

    @user.setter
    def user(self, value):
        # TODO: consider saving config data every time a setter is accessed
        self._data["username"] = value