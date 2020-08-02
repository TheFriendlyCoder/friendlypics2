"""helper methods for use by GUI objects and dialogs"""
import logging
from contextlib import contextmanager
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


def generate_screen_id(screen):
    """generates a unique identifier for a screen

    Args:
        screen (QScreen):
            screen to be analysed

    Returns:
        str:
            unique ID describing the given screen
    """
    if screen.serialNumber():
        return screen.serialNumber()

    return f"screen-{screen.name()}-{int(screen.physicalDotsPerInch())}dpi"


@contextmanager
def settings_group_context(settings, group_name):
    """Context manager that starts loading settings from a specific sub-group and restores
    the original settings group once the context goes out of scope

    Code within this context will load settings from the specified sub-group

    Args:
        settings (QSettings): settings for the running app
        group_name (str): name of the settings group to invoke

    """
    settings.beginGroup(group_name)
    try:
        yield
    finally:
        settings.endGroup()


class GuiLogger(logging.Handler):
    """Custom Python log handler that redirects output to a Qt widget"""
    def __init__(self, widget):
        """
        Args:
            widget (QWidget):
                text widget to redirect log output to
        """
        super().__init__()

        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        """Displays a log message to the GUI"""
        # TODO: consider disabling log output when the UI isn't being shown
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, _):
        """Disable disk-based file access"""


if __name__ == "__main__":  # pragma: no cover
    pass
