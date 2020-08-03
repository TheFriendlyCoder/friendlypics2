"""GUI dialog defining behavior of main application window"""
import logging
from pathlib import Path
from qtpy.QtWidgets import QMainWindow, QApplication, QFileDialog
from qtpy.QtCore import Slot, QSettings, QPoint, QSize, QRect, QModelIndex, QAbstractListModel, Qt
from qtpy.QtGui import QKeySequence, QIcon

from friendlypics2.misc.gui_helpers import load_ui, generate_screen_id, settings_group_context
from friendlypics2.misc.app_helpers import is_mac_app_bundle
from friendlypics2.dialogs.about_dlg import AboutDialog
from friendlypics2.misc.app_settings import AppSettings
from friendlypics2.dialogs.settings_dlg import SettingsDialog


class ImageItem:
    """Abstraction around an image that appears in the main list view"""
    def __init__(self, file_path):
        """
        Args:
            file_path (pathlib.Path):
                path to the file managed by this instance
        """
        self._log = logging.getLogger(__name__)
        self._file_path = file_path
        self._thumbnail = None

    @property
    def thumbnail(self):
        """QIcon: thumbnail representation of the image, lazy loaded when needed"""
        if self._thumbnail:
            return self._thumbnail
        self._thumbnail = QIcon(str(self._file_path))
        return self._thumbnail

    @property
    def file_name(self):
        """str: name of the file managed by this object, excluding the path"""
        return self._file_path.name


class ImageModel(QAbstractListModel):
    """Qt model that manages a list of images"""
    def __init__(self, folder):
        """
        Args:
            folder (pathlib.Path):
                path containing images to be presented to the user
        """
        super().__init__(None)
        self._log = logging.getLogger(__name__)
        self._folder = folder
        self._cache_size = 50  # only load the first 50 image thumbnails to reduce load times
        self._data = self._setup_model_data()

    @property
    def max_count(self):
        """int: gets the total number of images managed by this model"""
        return len(self._data)

    def data(self, index, role):
        """retrieves data for a specific image given a specific role

        Args:
            index (QModelIndex):
                index for the image to query
            role:
                `ItemDataRole <https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum>`__
                of the role within the view where the data will be used

        Returns:
            str or QIcon:
                returns the name of the file when using the Display role, and returns
                the image thumbnail when using the Decoration role
        """
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.DecorationRole):
            return None

        if index.row() > len(self._data):
            return None

        if role == Qt.DecorationRole:
            return self._data[index.row()].thumbnail
        return self._data[index.row()].file_name

    def rowCount(self, _):  # pylint: disable=invalid-name
        """int: number of images in the model, lazy loaded as needed"""
        return self._cache_size

    def canFetchMore(self, parent):  # pylint: disable=invalid-name
        """Is there more data to load from our model

        Used for lazy loading image thumbnails only when needed

        Args:
            parent (QModelIndex):
                reference to the parent item containing the images to load

        Returns:
            bool: True if there is more data to load from our model, False if not
        """
        if parent.isValid():
            return False
        retval = self._cache_size < len(self._data)
        return retval

    def fetchMore(self, parent):  # pylint: disable=invalid-name
        """Lazily loads more image data when needed

        Triggered by the view class when the user scrolls below the current end of
        the viewable data

        Args:
            parent (QModelIndex):
                reference to the parent item containing the images to load
        """
        if parent.isValid():
            return
        remainder = len(self._data) - self._cache_size
        next_batch = min(10, remainder)
        if next_batch <= 0:
            return
        self.beginInsertRows(QModelIndex(), self._cache_size, self._cache_size + next_batch - 1)
        self._cache_size += next_batch
        self.endInsertRows()

    def _setup_model_data(self):
        """list (ImageItem): Loads image metadata for all images in the model"""
        retval = list()
        for cur_file in sorted(self._folder.glob("*")):
            if not cur_file.is_file():
                continue
            if not cur_file.suffix:
                continue
            retval.append(ImageItem(cur_file))
        return retval


class MainWindow(QMainWindow):
    """Main window interface"""
    def __init__(self):
        super().__init__(parent=None)
        # Initialize private properties
        self._log = logging.getLogger(__name__)
        self._disable_window_save = False
        self._last_path = None

        # Initialize app settings
        self._app_settings = AppSettings()

        # Initialize window
        self._log.debug("Initializing main window...")
        self.setWindowTitle("Friendly Pics")
        self.statusBar().showMessage('Ready')

        self._settings = QSettings()
        self._load_ui()
        self._load_window_state()
        self._log.debug("Main window initialized")

    def _find_default_screen(self):
        """Screen: loads the screen ID for the screen where the application window should appear by default

        NOTE: this helper method assumes that the caller has already changed the active context of
        the self.settings object to point to the window we need to process
        """
        groups = self._settings.childGroups()
        default_group_id = self._settings.value("LastScreen")

        all_screens = dict()
        for cur_screen in QApplication.screens():
            all_screens[generate_screen_id(cur_screen)] = cur_screen

        # Favor the last used screen if it is still available
        if default_group_id in all_screens.keys():
            self._log.debug(f"Loading layout for previously used screen {default_group_id}")
            return all_screens[default_group_id]

        # if last used screen is not found, see if we have any cached screen details
        # that map to one of our available screen
        cached_screen_ids = set(all_screens.keys()).intersection(set(groups))

        # If so, return the first match
        if cached_screen_ids:
            return all_screens[cached_screen_ids[0]]

        # If all else fails and there are no defaults to be found, return the default screen
        default_screen_id = generate_screen_id(QApplication.screens()[0])
        self._log.debug("Loading a default screen layout")
        return all_screens[default_screen_id]

    def _load_ui(self):
        """Internal helper method that configures the UI for the main window"""
        load_ui("main_window.ui", self)

        self.file_open_menu.triggered.connect(self.file_open_click)
        self.file_open_menu.setShortcut(QKeySequence.Open)
        self.file_settings_menu.triggered.connect(self.file_settings_click)

        self.window_debug_menu.triggered.connect(self.window_debug_click)

        self.help_about_menu.triggered.connect(self.help_about_click)

        # Hack: for testing on MacOS we convert menu bar to non native
        #       works around the bug where native menu bar on Mac is read only on app launch
        #       problem is non existent when running app from a .app package
        #       (ie: as generated by pyinstaller)
        if not is_mac_app_bundle():
            self.menuBar().setNativeMenuBar(False)

    def _load_window_state(self):
        """Restores window layout to it's previous state. Must be called after _load_ui"""
        # Load all settings for this specific window
        with settings_group_context(self._settings, self.objectName()):
            target_screen = self._find_default_screen()

            # by default, scale our window to half the target screen's size
            default_width = int(target_screen.geometry().width() / 2)
            default_height = int(target_screen.geometry().height() / 2)
            default_size = QSize(default_width, default_height)

            # by default, center the window within the target screen
            geom = QRect(QPoint(0, 0), default_size)
            geom.moveCenter(target_screen.geometry().center())
            default_pos = geom.topLeft()

            with settings_group_context(self._settings, generate_screen_id(target_screen)):
                # TODO: do some additional sanity checking to make sure the target position and size
                #       lie within the screen boundaries and if not, fallback to defaults
                self.resize(self._settings.value("size", default_size))
                self.move(self._settings.value("pos", default_pos))

            if self._settings.value("window_debug", False):
                self.debug_dock.show()
                self.window_debug_menu.setChecked(True)
            else:
                self.debug_dock.hide()
                self.window_debug_menu.setChecked(False)
        self._last_path = self._settings.value("last_path", None)
        if self._last_path:
            model = ImageModel(self._last_path)
            self.thumbnail_view.setModel(model)
            self.statusBar().showMessage(f"Loaded {model.max_count} images")

    def _save_window_state(self):
        """Saves the current window state so it can be restored on next run"""
        # Save settings just for this window
        with settings_group_context(self._settings, self.objectName()):
            # Save window layout for the currently used screen
            cur_screen_id = generate_screen_id(self.screen())
            self._settings.setValue("LastScreen", cur_screen_id)
            with settings_group_context(self._settings, cur_screen_id):
                self._settings.setValue("size", self.size())
                self._settings.setValue("pos", self.pos())
            self._settings.setValue("window_debug", self.window_debug_menu.isChecked())
        if self._last_path:
            self._settings.setValue("last_path", self._last_path)
        self._settings.sync()

    @Slot()
    def file_open_click(self):
        """callback for file-open menu"""
        temp_path = self._last_path or Path("~").expanduser()
        new_path = QFileDialog.getExistingDirectory(self, "Select folder...", str(temp_path))
        if not new_path:
            return
        self._last_path = Path(new_path)
        model = ImageModel(self._last_path)
        self.thumbnail_view.setModel(model)
        self.statusBar().showMessage(f"Loaded {model.max_count} images")

    @Slot()
    def help_about_click(self):
        """callback for the help-about menu"""
        dlg = AboutDialog(self, self._app_settings)
        dlg.exec_()
        self._disable_window_save = dlg.cleared

    @Slot()
    def window_debug_click(self):
        """event handler for when the window->debug menu is clicked"""
        if self.window_debug_menu.isChecked():
            self.debug_dock.show()
        else:
            self.debug_dock.hide()

    @Slot()
    def file_settings_click(self):
        """event handler for when the file->settings menu is clicked"""
        dlg = SettingsDialog(self, self._app_settings)
        dlg.exec_()

    def closeEvent(self, event):  # pylint: disable=invalid-name
        """event handler called when the application is about to close

        Args:
            event (QCloseEvent):
                reference to the event object being raised
        """
        self._log.debug("Shutting down")
        if not self._disable_window_save:
            self._save_window_state()
        self._app_settings.save()
        event.accept()


if __name__ == "__main__":  # pragma: no cover
    pass
