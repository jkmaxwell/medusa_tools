#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFileDialog, QMessageBox, QButtonGroup,
                              QRadioButton, QMenuBar, QMenu, QGroupBox, QStatusBar)
from PySide6.QtCore import Qt, QSize
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs, create_wavetable_bank
from version import __version__ as VERSION, __app_name__ as APP_NAME

class MedusaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{APP_NAME} v{VERSION}')
        self.setFixedSize(450, 400)
        
        # Load Windows 95 style
        style_file = os.path.join(os.path.dirname(__file__), "styles/win95.qss")
        with open(style_file) as f:
            self.setStyleSheet(f.read())
        
        # Create menu bar
        menubar = QMenuBar()
        self.setMenuBar(menubar)
        
        # File menu
        file_menu = QMenu("&File", self)
        menubar.addMenu(file_menu)
        file_menu.addAction("E&xit", self.close)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        menubar.addMenu(help_menu)
        help_menu.addAction("&About", self.about)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add title
        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        desc = QLabel("A tool for working with Polyend Medusa wavetables")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create wavetable group
        create_group = QGroupBox("Create Wavetable")
        create_layout = QVBoxLayout(create_group)
        
        create_btn = QPushButton("Create from Audio Files")
        create_btn.clicked.connect(self.select_create_input)
        create_btn.setToolTip("Create wavetable bank directly from audio files")
        create_layout.addWidget(create_btn)
        
        # Selection mode radio buttons
        mode_group = QWidget()
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.setContentsMargins(20, 0, 0, 0)
        
        self.selection_group = QButtonGroup(self)
        alpha_radio = QRadioButton("Alphanumeric")
        random_radio = QRadioButton("Random")
        alpha_radio.setChecked(True)
        
        self.selection_group.addButton(alpha_radio)
        self.selection_group.addButton(random_radio)
        
        mode_layout.addWidget(alpha_radio)
        mode_layout.addWidget(random_radio)
        mode_layout.addStretch()
        
        create_layout.addWidget(mode_group)
        layout.addWidget(create_group)
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        decompile_btn = QPushButton("Decompile .polyend File")
        decompile_btn.clicked.connect(self.select_decompile_input)
        decompile_btn.setToolTip("Extract wavetables from a .polyend file to WAV files")
        tools_layout.addWidget(decompile_btn)
        
        recompile_btn = QPushButton("Recompile Wavetables")
        recompile_btn.clicked.connect(self.select_recompile_input)
        recompile_btn.setToolTip("Create .polyend file from processed WAV files")
        tools_layout.addWidget(recompile_btn)
        
        layout.addWidget(tools_group)
        
        # Add status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")
    
    def update_status(self, message):
        """Update status bar message."""
        self.statusBar().showMessage(message)
    
    def select_decompile_input(self):
        self.update_status("Selecting file to decompile...")
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Medusa Wavetable File")
        dialog.setNameFilter("Polyend Files (*.polyend)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            input_file = dialog.selectedFiles()[0]
            self.update_status(f"Decompiling {os.path.basename(input_file)}...")
            result = decompile_wavetable(input_file)
            if result['success']:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Extracted {result['num_wavetables']} wavetables to {result['output_dir']}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error decompiling wavetable: {result['error']}"
                )
        self.update_status("Ready")
    
    def select_recompile_input(self):
        self.update_status("Selecting files to recompile...")
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Directory Containing Wavetable WAV Files")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            input_dir = dialog.selectedFiles()[0]
            
            parent_dir = os.path.dirname(input_dir)
            default_output = os.path.join(parent_dir, "recompiled.polyend")
            
            save_dialog = QFileDialog(self)
            save_dialog.setWindowTitle("Save Recompiled Wavetable File As")
            save_dialog.setNameFilter("Polyend Files (*.polyend)")
            save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            save_dialog.setDirectory(parent_dir)
            save_dialog.selectFile("recompiled.polyend")
            
            if save_dialog.exec() == QFileDialog.DialogCode.Accepted:
                output_file = save_dialog.selectedFiles()[0]
                self.update_status("Recompiling wavetables...")
                result = recompile_wavetable(input_dir, output_file)
                if result['success']:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Successfully recompiled {result['num_wavetables']} wavetables to {result['output_file']}"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error recompiling wavetables: {result['error']}"
                    )
        self.update_status("Ready")
    
    def select_create_input(self):
        self.update_status("Selecting audio files...")
        input_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing Audio Files",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not input_dir:
            self.update_status("Ready")
            return
            
        random_mode = self.selection_group.checkedButton().text() == "Random"
        
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Wavetable Bank As",
            "wavetables.polyend",
            "Polyend Files (*.polyend)"
        )
        
        if not output_file:
            self.update_status("Ready")
            return
            
        self.update_status("Creating wavetable bank...")
        result = create_wavetable_bank(
            input_dir,
            output_file,
            random_order=random_mode
        )
        
        if result['success']:
            QMessageBox.information(
                self,
                "Success",
                f"Successfully created wavetable bank:\n"
                f"- Output file: {result['output_file']}\n"
                f"- Number of wavetables: {result['num_wavetables']}\n"
                f"- Source files: {len(result['source_files'])}"
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Error creating wavetable bank: {result['error']}"
            )
        self.update_status("Ready")
    
    def about(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle(f"About {APP_NAME}")
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            f"<h3>{APP_NAME} v{VERSION}</h3>"
            "<p>A tool for working with Polyend Medusa synthesizer wavetables.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Extract wavetables from .polyend files</li>"
            "<li>Create wavetable banks from audio files</li>"
            "<li>Support for random or alphabetical file selection</li>"
            "</ul>"
            "<p>© 2024 All rights reserved.</p>"
        )
        about_box.setStyleSheet(self.styleSheet())
        about_box.exec()

def main():
    app = QApplication(sys.argv)
    window = MedusaApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()