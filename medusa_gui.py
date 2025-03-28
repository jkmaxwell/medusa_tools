#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QLabel, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

VERSION = "1.0.0"
APP_NAME = "Medusa Waveform Utility"

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
        
        # Add buttons
        decompile_btn = QPushButton("Decompile .polyend File")
        decompile_btn.clicked.connect(self.select_decompile_input)
        layout.addWidget(decompile_btn)
        
        recompile_btn = QPushButton("Recompile Wavetables")
        recompile_btn.clicked.connect(self.select_recompile_input)
        layout.addWidget(recompile_btn)
        
        process_btn = QPushButton("Process Custom WAVs")
        process_btn.clicked.connect(self.select_process_input)
        layout.addWidget(process_btn)
        
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.about)
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
    
    def select_process_input(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Directory Containing WAV Files to Process")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            input_dir = dialog.selectedFiles()[0]
            # Create processed directory next to input directory
            output_dir = os.path.join(os.path.dirname(input_dir), 'processed')
            
            result = process_wavs(input_dir, output_dir)
            if result['success']:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Processed {result['num_files']} WAV files to {result['output_dir']}\n"
                    "You can now use Recompile Wavetables to create a .polyend file."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error processing WAVs: {result['error']}"
                )
    
    def about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{VERSION}\n\n"
            "A tool for working with Polyend Medusa synthesizer wavetables.\n\n"
            "Features:\n"
            "• Extract wavetables from .polyend files\n"
            "• Recompile WAV files into wavetables\n"
            "• Process custom WAV files for use with Medusa\n\n"
            "© 2024 All rights reserved."
        )

def main():
    app = QApplication(sys.argv)
    window = MedusaApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()