from os.path import split as split_pathname
from os.path import exists as is_file_exists
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from .menu.menu_bar import MenuBar
from .files_bar import FilesBar
from .new_file import NewFile
from .find_and_replace import FindAndReplace


class Editor(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Editor")
        self.resize(800, 600)

        self._menu_bar = MenuBar()
        self.files_tabs = FilesBar()
        self.status_bar = self.statusBar()

        self.init_ui()
        self.confSignals()

    def init_ui(self):
        self._menu_bar.disable_editing()
        self.setMenuBar(self._menu_bar)
        self.setCentralWidget(self.files_tabs)

    def readSettings(self):
        pass

    def confSignals(self):
        self._menu_bar.new_file.connect(self.new_file)
        self._menu_bar.save_file.connect(self.save_file)
        self._menu_bar.save_file_as.connect(self.save_file_as)
        self._menu_bar.open_file.connect(self.open_file)
        self._menu_bar.close_tab.connect(self.files_tabs.close_tab)
        self._menu_bar.close_program.connect(self.quit)

        self._menu_bar.undo.connect(self.files_tabs.undo)
        self._menu_bar.redo.connect(self.files_tabs.redo)
        self._menu_bar.cut.connect(self.files_tabs.cut)
        self._menu_bar.copy.connect(self.files_tabs.copy)
        self._menu_bar.paste.connect(self.files_tabs.paste)
        self._menu_bar.replace_in_file.connect(self.replace_in_file)

        self._menu_bar.about.connect(self.show_about)

        self.files_tabs.new_tab.connect(self._menu_bar.enable_editing)
        self.files_tabs.nothing_open.connect(self._menu_bar.disable_editing)

    def replace_in_file(self):
        FindAndReplace(self)

    def new_file(self):
        dialog = NewFile(self)
        dialog.exec_()
        if dialog.is_create_clicked():
            self.files_tabs.open_tab(dialog.name.text())

    @staticmethod
    def __save(path: str, text: str) -> bool:
        try:
            with open(path, 'w') as f:
                f.write(text)
        except Exception as e:
            print(e)
            return False
        return True

    def save_file(self):
        if not self.files_tabs.is_open_something():
            return
        if self.files_tabs.is_current_path():
            return self.save_file_as()

        data = self.files_tabs.get_current_text()
        path = self.files_tabs.get_current_path()
        file_name = self.files_tabs.get_current_name()
        full_path = path + "/" + file_name

        if not is_file_exists(full_path):
            return self.save_file_as()

        is_saved = self.__save(full_path, data)

        if not is_saved:
            # show error on status bar
            return

    def save_file_as(self):
        if not self.files_tabs.is_open_something():
            return

        file_name = QFileDialog.getSaveFileName(
            self, "Save as...",
            self.files_tabs.get_current_name(),
            "All Files (*.*)"
        )[0]

        if file_name == '':
            return

        data = self.files_tabs.get_current_text()
        is_saved = self.__save(file_name, data)
        if not is_saved:
            # show error on status bar
            return

        new_path, new_name = split_pathname(file_name)
        self.files_tabs.update_name(new_name)
        self.files_tabs.update_path(new_path)

    @staticmethod
    def __open(path: str) -> str:
        try:
            with open(path, 'r') as f:
                text = f.read()
        except Exception as e:
            print(e)
            return
        return text

    def open_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Open file")[0]

        if file_path == "":
            return

        path, name = split_pathname(file_path)
        text = self.__open(file_path)
        if text is None:
            # show error on status bar
            return
        self.files_tabs.open_tab(name, text, path)

    def show_about(self):
        from src import about
        about.show()

    def quit(self):
        retval = QMessageBox.Yes
        if self.files_tabs.is_modified():
            ask = QMessageBox()
            ask.setIcon(QMessageBox.Question)
            ask.setWindowTitle("Exit")
            ask.setText("You have unsaved files!")
            ask.setInformativeText("Do you really want to exit?")
            ask.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ask.setDefaultButton(QMessageBox.No)
            retval = ask.exec_()

        if retval == QMessageBox.Yes:
            QApplication.quit()
