import os
import sys
import uuid
import re
import time
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QFont, QIcon, QImage, QTextDocument, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QStatusBar, QToolBar, QAction, QFileDialog, QFontComboBox, QComboBox, QMessageBox, QLabel, QSplashScreen
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtPrintSupport import QPrintDialog

# Create massives for K#DS
FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
IMAGE_EXTENSIONS = ['.jpg', '.png', '.bmp']
HTML_EXTENSIONS = ['.htm', '.html']

def hexuuid():
    return uuid.uuid4().hex

def splitext(p):
    return os.path.splitext(p)[1].lower()

class WeLanguageInterpreter:
    def __init__(self):
        self.variables = {}
        self.commands = {}
        self.debug_mode = True
        self.eip = 0  # Emulate an instruction pointer
        self.program = []  # Store program instructions

    def parse_and_execute(self, content):
        self.program = content.splitlines()
        self.eip = 0

        while self.eip < len(self.program):
            line = self.program[self.eip].strip()
            self.eip += 1  # Move to the next line

            if line.startswith(';') or not line:
                continue

            if line.startswith('var.create '):
                self.handle_variable_declaration(line)
            elif line.startswith('var.set '):
                self.handle_variable_definition(line)
            elif line.startswith('!set command = '):
                self.handle_command_definition(line)
            elif line.startswith('mov '):
                self.handle_mov(line)
            elif line.startswith('add '):
                self.handle_add(line)
            elif line.startswith('mod '):
                self.handle_mod(line)
            elif line.startswith('!cr '):
                self.handle_command_execution(line)
            elif line.startswith('input '):
                self.handle_input(line)

    def handle_variable_declaration(self, line):
        match = re.match(r"var.create (\w+)", line)
        if match:
            var_name = match.group(1)
            self.variables[var_name] = 0
            if self.debug_mode:
                print(f"Variable {var_name} declared.")

    def handle_variable_definition(self, line):
        match = re.match(r"var.set (\w+) = '(.+)'", line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            if var_name in self.variables:
                self.variables[var_name] = var_value
                if self.debug_mode:
                    print(f"Variable {var_name} set to '{var_value}'")
            else:
                if self.debug_mode:
                    print(f"Error: Variable '{var_name}' not declared.")

    def handle_command_definition(self, line):
        match = re.match(r"!set command = '(.+)'", line)
        if match:
            command_name = match.group(1)
            if self.variables:
                last_var_name = list(self.variables.keys())[-1]
                self.commands[command_name] = last_var_name
                if self.debug_mode:
                    print(f"Command '{command_name}' assigned to variable '{last_var_name}'")

    def handle_command_execution(self, line):
        match = re.match(r"!cr (\w+)", line)
        if match:
            var_name = match.group(1)
            if var_name in self.variables:
                print(self.variables[var_name])
            else:
                if self.debug_mode:
                    print(f"Variable '{var_name}' not found.")

    def handle_mov(self, line):
        match = re.match(r"mov (\w+), (\d+)", line)
        if match:
            var_name = match.group(1)
            value = int(match.group(2))
            self.variables[var_name] = value
            if self.debug_mode:
                print(f"Set: {var_name} = {value}")

    def handle_add(self, line):
        match = re.match(r"add (\w+), (\d+)", line)
        if match:
            var_name = match.group(1)
            value = int(match.group(2))
            if var_name in self.variables:
                self.variables[var_name] += value
                if self.debug_mode:
                    print(f"Added: {var_name} += {value}")

    def handle_mod(self, line):
        match = re.match(r"mod (.+)", line)
        if match:
            mod_value = match.group(1)
            self.debug_mode = mod_value != 'x023x'
            if self.debug_mode:
                print(f"Modifier set: {mod_value}")

    def handle_input(self, line):
        match = re.match(r"input (\w+)", line)
        if match:
            var_name = match.group(1)
            if var_name in self.variables:
                user_input = input(f"Enter value for {var_name}: ")
                self.variables[var_name] = user_input
                if self.debug_mode:
                    print(f"Variable {var_name} set to '{user_input}'")
            else:
                print(f"Error: Variable '{var_name}' not declared.")

class TextEdit(QTextEdit):
    def canInsertFromMimeData(self, source):
        return source.hasImage() or super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        cursor = self.textCursor()
        document = self.document()

        if source.hasUrls():
            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())
                else:
                    break
            else:
                return

        elif source.hasImage():
            image = source.imageData()
            uuid = hexuuid()
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            return

        super(TextEdit, self).insertFromMimeData(source)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.editor = TextEdit()
        self.editor.selectionChanged.connect(self.update_format)
        font = QFont('Hack', 12)
        self.editor.setFont(font)
        self.path = None
        layout.addWidget(self.editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        def load_icon(filename):
            path = os.path.join('images', filename)
            if not os.path.exists(path):
                print(f'Error: file {path} not found.')
            return QIcon(path)

        open_file_action = QAction(load_icon('blue-folder-open-document.png'), "Open Project...", self)
        open_file_action.setStatusTip("Open WeLang project")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(load_icon('disk.png'), "Save", self)
        save_file_action.setStatusTip("Save current WeLang project")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        saveas_file_action = QAction(load_icon('disk--pencil.png'), "Save As...", self)
        saveas_file_action.setStatusTip("Save current WeLang project to a specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        print_action = QAction(load_icon('printer.png'), "Print...", self)
        print_action.setStatusTip("Print WeLang program code")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit program (save project before exit)")
        file_menu.addAction(exit_action)

        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(load_icon('arrow-curve-180-left.png'), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(load_icon('arrow-curve.png'), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(load_icon('scissors.png'), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(load_icon('document-copy.png'), "Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(load_icon('clipboard-paste-document-text.png'), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(load_icon('selection-input.png'), "Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.setShortcut(QKeySequence.SelectAll)
        select_action.triggered.connect(self.editor.selectAll)
        edit_toolbar.addSeparator()
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(load_icon('arrow-continue.png'), "Wrap text to window", self)
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        debug_toolbar = QToolBar("Debug")
        debug_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(debug_toolbar)
        debug_menu = self.menuBar().addMenu("&Debug")

        run_action = QAction(load_icon('play.png'), "Run File", self)
        run_action.setStatusTip("Run WeLang Project")
        run_action.triggered.connect(self.run_file)
        debug_menu.addAction(run_action)

        self.interpreter = WeLanguageInterpreter()

        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.editor.setCurrentFont)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])

        self.create_help_menu()

        self.update_format()
        self.update_title()
        self.show()

    def create_help_menu(self):
        help_menu = self.menuBar().addMenu("&Help")

        documentation_action = QAction("Documentation", self)
        documentation_action.setStatusTip("View documentation for WeLang commands")
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)

        about_action = QAction("About K# Studio", self)
        about_action.setStatusTip("View information about program")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("About program")
        dlg.setText(
            "K# Developer Studio\n\n"
            "Version 2.4\n"
            "(c) WeLang Community, 2024\n"
        )
        dlg.exec_()

    def show_documentation(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Documentation")
        dlg.setText(
            "WeLang commands:\n"
            "var.create var_name - Creates a new variable\n"
            "var.set var_name = 'value' - Assigns a value to a variable\n"
            "mov var_name, value - Sets an integer value to a variable\n"
            "add var_name, value - Adds a value to a variable\n"
            "mod value - Modifies the debug mode\n"
            "!set command = 'command' - Maps a command to a variable\n"
            "!cr var_name - Executes a command, printing the variable value\n"
            "input var_name - Reads an input from the console into a variable\n"
        )
        dlg.exec_()

    def block_signals(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def update_format(self):
        pass

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open project", "",
            "WeLang Program (*.wel);;WeLang Program Alternative (*.wla);;All files (*.*)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.path = path
            self.editor.setText(text)
            self.update_title()
            self.status.showMessage("File opened", 2000)

    def file_save(self):
        if self.path is None:
            return self.file_saveas()

        text = self.editor.toHtml() if splitext(self.path) in HTML_EXTENSIONS else self.editor.toPlainText()
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.status.showMessage("File saved", 2000)

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save project", "",
            "WeLang Program (*.wel);;WeLang Program Alternative (*.wla);;All files (*.*)"
        )
        if not path:
            return

        text = self.editor.toHtml() if splitext(path) in HTML_EXTENSIONS else self.editor.toPlainText()

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.path = path
            self.update_title()
            self.status.showMessage("File saved as", 2000)

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle(
            "%s - WeLang Developer Studio 2.31" % (os.path.basename(self.path) if self.path else "Untitled")
        )

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    def run_file(self):
        code = self.editor.toPlainText()
        self.interpreter.parse_and_execute(code)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("K# Developer Studio 2.31")

    # Load the splash image
    splash_pix = QPixmap('Boeing.png')  # Replace with your image path

    # Create and display the splash screen
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()

    # Allow some time for the splash screen to be visible
    time.sleep(2)  # Optional, but provides a better user experience

    # Initialize and show the main window
    window = MainWindow()
    window.show()

    # Close the splash screen after the main window is fully initialized
    splash.finish(window)

    # Start the application event loop
    app.exec_()
