#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFileDialog, QMessageBox, QButtonGroup,
                              QRadioButton)
from PySide6.QtCore import Qt
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

VERSION = "1.0.0"
APP_NAME = "Medusa Wavetable Utility"

class MedusaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{APP_NAME} v{VERSION}')
        self.setFixedSize(400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add title
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        desc = QLabel("A tool for working with Polyend Medusa wavetables")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Add spacing
        layout.addSpacing(20)
        
        # Create from Audio Files section
        create_section = QWidget()
        create_layout = QVBoxLayout(create_section)
        create_layout.setSpacing(5)
        
        create_btn = QPushButton("Create from Audio Files")
        create_btn.clicked.connect(self.select_create_input)
        create_btn.setToolTip("Create wavetable bank directly from audio files")
        create_layout.addWidget(create_btn)
        
        # Selection mode radio buttons
        mode_group = QWidget()
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.setContentsMargins(20, 0, 0, 0)  # Add left margin for indentation
        
        self.selection_group = QButtonGroup(self)
        alpha_radio = QRadioButton("Alphanumeric")
        random_radio = QRadioButton("Random")
        alpha_radio.setChecked(True)  # Default to alphanumeric
        
        self.selection_group.addButton(alpha_radio)
        self.selection_group.addButton(random_radio)
        
        mode_layout.addWidget(alpha_radio)
        mode_layout.addWidget(random_radio)
        mode_layout.addStretch()
        
        create_layout.addWidget(mode_group)
        layout.addWidget(create_section)
        
        # Add spacing after the create section
        layout.addSpacing(10)
        
        decompile_btn = QPushButton("Decompile .polyend File")
        decompile_btn.clicked.connect(self.select_decompile_input)
        decompile_btn.setToolTip("Extract wavetables from a .polyend file to WAV files")
        layout.addWidget(decompile_btn)
        
        recompile_btn = QPushButton("Recompile Wavetables")
        recompile_btn.clicked.connect(self.select_recompile_input)
        recompile_btn.setToolTip("Create .polyend file from processed WAV files")
        layout.addWidget(recompile_btn)
        
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.about)
        about_btn.setToolTip("Show information about this application")
        layout.addWidget(about_btn)
    
    def select_decompile_input(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Medusa Wavetable File")
        dialog.setNameFilter("Polyend Files (*.polyend)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            input_file = dialog.selectedFiles()[0]
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
    
    def select_recompile_input(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Directory Containing Wavetable WAV Files")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            input_dir = dialog.selectedFiles()[0]
            
            # Default output file next to the waves directory
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
    
    def select_create_input(self):
        # First select input directory
        input_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing Audio Files",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not input_dir:
            return
            
        # Get selection mode from radio buttons
        random_mode = self.selection_group.checkedButton().text() == "Random"
        
        # Get output file location
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Wavetable Bank As",
            "wavetables.polyend",
            "Polyend Files (*.polyend)"
        )
        
        if not output_file:
            return
            
        # Create the wavetable bank
        result = medusa_core.create_wavetable_bank(
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
    
    def about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{VERSION}\n\n"
            "A tool for working with Polyend Medusa synthesizer wavetables.\n\n"
            "Features:\n"
            "• Extract wavetables from .polyend files\n"
            "• Create wavetable banks from audio files\n"
            "• Support for random or alphabetical file selection\n\n"
            "© 2024 All rights reserved."
        )

def main():
    app = QApplication(sys.argv)
    window = MedusaApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()