"""Logic for the application settings UI"""
import logging
import json
from qtpy.QtWidgets import QDialog
from qtpy.QtCore import Slot, QAbstractItemModel, QModelIndex, Qt
from friendlypics2.misc.gui_helpers import load_ui

# TODO: fix pylint warnings with this class - it's only used internally by the model below
class SettingsItem:
    """Interface to a single application setting or group of application settings

    Loosely based on example code found
    `here <https://github.com/pyside/Examples/blob/master/examples/itemviews/simpletreemodel/simpletreemodel.py>`__
    """
    def __init__(self, data, parent=None):
        """
        Args:
            data (tuple):
                fields associated with this setting, providing data for each column in the view
            parent (SettingsItem):
                parent setting that owns this one. Set to None to indicate this item is a root
                setting with no parent
        """
        self._log = logging.getLogger(__name__)
        self._parent_item = parent
        self._item_data = data
        self._child_items = list()

    def __str__(self):
        return json.dumps(self._item_data, indent=4)

    def set_data(self, value):
        """Modifies the data value for this setting

        Args:
            value (str):
                new value for this setting
        """
        self._item_data = (self._item_data[0], value)

    @property
    def child_items(self):
        """list (SettingsItem): list of children owned by this item"""
        return self._child_items

    def appendChild(self, item):  # pylint: disable=invalid-name
        """Adds a new child element to this setting in the tree

        Args:
            item (SettingsItem):
                child item related to this one
        """
        self._child_items.append(item)

    def child(self, row):
        """Gets a specific child item from this parent

        Args:
            row (int):
                index of the child item to retrieve

        Returns:
            SettingsItem: child item with the given index
        """
        return self._child_items[row]

    def childCount(self):  # pylint: disable=invalid-name
        """int: number of children contained within this item"""
        return len(self._child_items)

    def columnCount(self):  # pylint: disable=invalid-name
        """int: number of columns or fields associated with this item"""
        return len(self._item_data)

    def data(self, column):
        """str: data associated with this item for the given field / column.
        May be None if no data for the specified column exists."""
        if column > len(self._item_data):
            return None
        return self._item_data[column]

    def parent(self):
        """SettingItem: parent object that owns this item, or None if this is a root item"""
        return self._parent_item

    def row(self):
        """int: gets the relative offset of this item with respect to its siblings"""
        if self._parent_item:
            return self._parent_item.child_items.index(self)

        return 0


class AppSettingsModel(QAbstractItemModel):
    """Interface for rendering application settings stored in a hierarchical format

    Loosely based on example code found
    `here <https://github.com/pyside/Examples/blob/master/examples/itemviews/simpletreemodel/simpletreemodel.py>`__
    """
    def __init__(self, data):
        """
        Args:
            data (AppSettings):
                reference to the application settings to be managed by this dialog
        """
        super().__init__(None)
        self._log = logging.getLogger(__name__)
        self._settings = data
        self._root_item = SettingsItem(("Setting", "Value"))
        self._setup_model_data(self._settings.data, self._root_item)

    @property
    def root_item(self):
        """SettingsItem: gets the root node of our settings tree"""
        return self._root_item

    def _setup_model_data(self, data, parent):
        """Helper method used to populate our model data

        Args:
            data (dict):
                dictionary of settings to be managed by our model
                nodes in the dictionary that contain nested dictionaries are assumed to be settings groups,
                and all other nodes are assumed to be simple settings / data values
            parent (SettingsItem):
                reference to the parent item that will own all child items defined by the given data block
        """
        for cur_key, cur_val in data.items():
            if isinstance(cur_val, dict):
                temp = SettingsItem((cur_key, ""), parent)
            else:
                temp = SettingsItem((cur_key, cur_val), parent)

            parent.appendChild(temp)
            if isinstance(cur_val, dict):
                self._setup_model_data(cur_val, temp)

    def columnCount(self, parent):  # pylint: disable=invalid-name
        """retrieves the number of fields associated with a given item

        Args:
            parent (QModelIndex):
                index of the item to retrieve information for
                contains a reference to the SettingsItem it manages

        Returns:
            int: number of fields associated with the given item
        """
        if parent.isValid():
            return parent.internalPointer().columnCount()

        return self._root_item.columnCount()

    def data(self, index, role):  # pylint: disable=no-self-use
        """retrieves data for a specific setting given a specific role

        Args:
            index (QModelIndex):
                index for the setting to query
            role:
                `ItemDataRole <https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum>`__
                of the role within the view where the data will be used

        Returns:
            str:
                data for the specified setting within the given context, or None if no
                data suitable for the given role can be found
        """
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def setData(self, index, value, role):  # pylint: disable=invalid-name
        """Modifies the value of a settings

        Loosely based on example code found
        `here <https://doc.qt.io/qtforpython/overviews/model-view-programming.html#an-editable-model>`__

        Args:
            index (QModelIndex):
                index of the app setting to modify
            value (str):
                new data value for the setting
            role:
                `ItemDataRole <https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum>`__
                of the role within the view where the data is being edited

        Returns:
            bool: True if the data was successfully modified, False if not
        """
        if not index.isValid() or role != Qt.EditRole:
            return False

        item = index.internalPointer()
        item.set_data(value)

        # resync the data in the view
        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):  # pylint: disable=no-self-use
        """gets bit-field describing how a given setting should be rendered

        Args:
            index (QModelIndex):
                index of the setting to be analysed

        Returns:
            int: bit-field encoded set of flags describing how the given item should be displayed
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):  # pylint: disable=invalid-name
        """Gets column header text for the view

        Args:
            section (int):
                id of the field / column to retrieve the header for
            orientation:
                `Orientation <https://doc.qt.io/qt-5/qt.html#Orientation-enum>`__
                of the text direction for the headers
            role:
                `ItemDataRole <https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum>`__
                of the role within the view where the data will be used

        Returns:
            str: header text for the given section / column
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_item.data(section)

        return None

    def index(self, row, column, parent):
        """Gets the index for a given element in the data managed by the model

        Args:
            row (int):
                row of the data set to query
                within our context, this is the ID of the setting to query
            column (int):
                column of the data set to query
                within our context, this is the ID of the field of a specific setting to query
            parent (QModelIndex):
                index of the node / setting containing the children to query

        Returns:
            QModelIndex: reference to the setting associated with the given context
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        """Gets the index of the parent item for a given setting

        Args:
            index (QModelIndex):
                index of the setting to query

        Returns:
            QModelIndex:
                reference to the setting owning the given item, or an empty index if the
                given item has no parent
        """
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent):  # pylint: disable=invalid-name
        """Number of direct children owned by a given index

        Args:
            parent (QModelIndex):
                reference to the setting to query

        Returns:
            int: number of children owned by this parent
        """
        if parent.column() > 0:
            self._log.debug(f"Returning default for {parent.internalPointer()}")
            return 0

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.childCount()


class SettingsDialog(QDialog):
    """Logic for managing application settings dialog"""
    def __init__(self, parent, settings):
        """
        Args:
            parent (QWidget):
                Parent widget / dialog that owns the settings dialog
            settings (AppSettings):
                reference to the application settings to be managed by this dialog
        """
        super().__init__(parent)
        self._settings = settings
        self._log = logging.getLogger(__name__)
        self._load_ui()

    def _load_ui(self):
        """Internal helper method that configures the UI for the dialog"""
        load_ui("settings_dlg.ui", self)

        self.cancel_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self._save_clicked)

        model = AppSettingsModel(self._settings)
        self.settings_view.setModel(model)

        # Center the about box on the parent window
        parent_geom = self.parent().geometry()
        self.move(parent_geom.center() - self.rect().center())

    def _load_data(self, item):
        """helper method that dumps the raw data from the settings data model to a dictionary

        Args:
            item(SettingsItem):
                reference to the item to retrieve settings data from. Data will be generated
                recursively for all children owned by the settings item.

        Returns:
            dict: updated settings data loaded from the data model
        """
        retval = dict()
        for cur_child in item.child_items:
            if cur_child.child_items:
                temp_data = self._load_data(cur_child)
            else:
                temp_data = cur_child.data(1)
            retval[cur_child.data(0)] = temp_data
        return retval

    @Slot()
    def _save_clicked(self):
        """Callback for when the user clicks the save button"""
        new_data = self._load_data(self.settings_view.model().root_item)
        self._settings.data = new_data
        self._settings.save()
        self.close()
