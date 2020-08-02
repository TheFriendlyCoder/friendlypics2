"""Logic for the application about box"""
import logging
from qtpy.QtWidgets import QDialog, QLabel, QPushButton
from qtpy.QtCore import Slot, QSettings
from friendlypics2.version import __version__
from friendlypics2.misc.gui_helpers import load_ui
from friendlypics2.misc.app_helpers import is_mac_app_bundle, is_pyinstaller_bundle


class AboutDialog(QDialog):
    """Logic for managing about box"""
    def __init__(self, parent):
        super().__init__(parent)
        self._log = logging.getLogger(__name__)
        self.setWindowTitle("About...")
        self.setModal(True)
        self.settings = QSettings()
        self._load_ui()
        # Flag indicating whether the user has requested the GUI settings to be reset.
        # If so, the caller should disable any further settings recording logic
        self.cleared = False

    def _load_ui(self):
        """Internal helper method that configures the UI for the main window"""
        load_ui("about_dlg.ui", self)

        self.title_label = self.findChild(QLabel, "title_label")
        self.title_label.setText(f"Friendly Pics 2 v{__version__}")

        self.runtime_env_label = self.findChild(QLabel, "runtime_env_label")
        if is_mac_app_bundle():
            self.runtime_env_label.setText("Running as MacOS app bundle")
        elif is_pyinstaller_bundle():
            self.runtime_env_label.setText("Running as a pyinstaller binary")
        else:
            self.runtime_env_label.setText("Running under conventional Python environment")

        self.gui_settings_label = self.findChild(QLabel, "gui_settings_label")
        self.gui_settings_label.setText(f"<b>GUI Settings:</b> {self.settings.fileName()}")

        self.gui_settings_clear_button = self.findChild(QPushButton, "gui_settings_clear_button")
        self.gui_settings_clear_button.clicked.connect(self._clear_gui_settings)

        # Center the about box on the parent window
        parent_geom = self.parent().geometry()
        self.move(parent_geom.center() - self.rect().center())

    @Slot()
    def _clear_gui_settings(self):
        """Callback for when user selects the clear gui settings button"""
        self.settings.clear()
        self.settings.sync()
        self.gui_settings_clear_button.setEnabled(False)
        self.cleared = True
