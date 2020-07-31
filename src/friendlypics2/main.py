"""Main entry point module for the application"""
import sys

from qtpy.QtWidgets import QApplication
from friendlypics2.dialogs.main_window import MainWindow
# TODO: hook up exception handling
# TODO: set up logging (https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt)
# TODO: setup app configuration file for storing user settings
# TODO: add about box that just shows version number


def run(args):
    """Main entrypoint function

    Args:
        args (list): command line arguments to be passed to the application

    Returns:
        int: return code to report back to the shell with
    """
    app = QApplication(args)
    widget = MainWindow()
    widget.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run(sys.argv))
