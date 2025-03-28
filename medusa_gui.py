#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QLabel, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

VERSION = "1.0.0"

class MedusaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'Medusa Wavetable Tool v{VERSION}')
        self.setFixedSize(400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add title
        title = QLabel("Medusa Wavetable Tool")
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
        input_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Medusa Wavetable File",  # Dialog title
            "",  # Starting directory
            "Polyend Files (*.polyend)"  # File filter
        )
        if input_file:
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
        input_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing Wavetable WAV Files",  # More descriptive title
            ""
        )
        if input_dir:
            # Default output file next to the waves directory
            parent_dir = os.path.dirname(input_dir)
            default_output = os.path.join(parent_dir, "recompiled.polyend")
            
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Recompiled Wavetable File As",  # More descriptive title
                default_output,
                "Polyend Files (*.polyend)"
            )
            if output_file:
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
        input_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing WAV Files to Process",  # More descriptive title
            ""
        )
        if input_dir:
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
            "About Medusa Wavetable Tool",
            f"Medusa Wavetable Tool v{VERSION}\n\n"
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