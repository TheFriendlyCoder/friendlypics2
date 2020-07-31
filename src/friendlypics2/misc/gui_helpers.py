"""helper methods for use by GUI objects and dialogs"""
from qtpy import uic
from pkg_resources import resource_filename

PACKAGE_NAME = "friendlypics2"


def load_ui(file, parent):
    """Loads a UI interface file from disk

    Args:
        file (str):
            path to the UI file to load. Must be relative to the data/ui folder.
        parent (object):
            reference to the Qt dialog object associated with the UI file
    """
    ui_file = resource_filename(PACKAGE_NAME, "data/ui/" + file)
    uic.loadUi(ui_file, parent)


if __name__ == "__main__":  # pragma: no cover
    pass
