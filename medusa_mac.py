#!/usr/bin/env python3

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
import wave
import struct
import numpy as np
from pathlib import Path

WAVETABLE_SIZE = 16000  # 0x3E80 bytes per wavetable
DATA_OFFSET = 0x80  # Fixed offset where waveform data starts

def show_error(message):
    """Show error dialog"""
    QMessageBox.critical(None, "Error", str(message))

class MedusaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        try:
            # Set window properties
            self.setWindowTitle('Medusa Wavetable Tool')
            self.setMinimumWidth(400)
            
            # Create central widget and layout
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            
            # Add title
            title = QLabel("Medusa Wavetable Tool")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Add description
            desc = QLabel("A tool for working with Polyend Medusa wavetables")
            desc.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc)
            
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
            
        except Exception as e:
            show_error(e)
    
    def decompile_wavetable(self, input_file):
        try:
            # Create waves directory next to the input file
            input_dir = os.path.dirname(input_file)
            output_dir = os.path.join(input_dir, 'waves')
            os.makedirs(output_dir, exist_ok=True)
            
            # Save a copy of the original file for reference
            with open(input_file, 'rb') as f:
                data = f.read()
                with open(os.path.join(output_dir, 'original.polyend'), 'wb') as out:
                    out.write(data)
            
            # Extract wavetables
            num_wavetables = len(data) // WAVETABLE_SIZE
            
            for i in range(num_wavetables):
                # Extract wavetable data
                start = i * WAVETABLE_SIZE
                end = start + WAVETABLE_SIZE
                wavetable_data = data[start:end]
                
                # Extract waveform data (starts at offset 0x80)
                waveform_data = wavetable_data[DATA_OFFSET:]
                
                # Convert to WAV format
                wav_file = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
                with wave.open(wav_file, 'wb') as wav:
                    wav.setnchannels(1)  # mono
                    wav.setsampwidth(2)  # 16-bit
                    wav.setframerate(44100)  # 44.1kHz
                    wav.writeframes(waveform_data)
            
            QMessageBox.information(
                None,
                "Success",
                f"Extracted {num_wavetables} wavetables to {output_dir}"
            )
            
        except Exception as e:
            show_error(f"Error decompiling wavetable: {str(e)}")
    
    def recompile_wavetable(self, input_dir, output_file):
        try:
            wavetables = []
            
            for i in range(64):
                wav_file = os.path.join(input_dir, f'wavetable_{i:02d}.wav')
                if not os.path.exists(wav_file):
                    raise Exception(f"Missing wavetable_{i:02d}.wav")
                
                with wave.open(wav_file, 'rb') as wav:
                    if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                        raise Exception(f"Invalid format in {wav_file}")
                    waveform_data = wav.readframes(wav.getnframes())
                
                header = b'\x21\x00\x01\x00' if i == 0 else b'\x02\x00\x00\x3c'
                subheader = b'\x04\x00\x00\x3c'
                size = struct.pack('<H', 4)
                index = struct.pack('<H', i)
                identifier = b'\x00\x00\x00\x00'  # Default identifier
                
                wavetable = (
                    header +
                    identifier +
                    b'\x00' * (0x40 - 8) +
                    subheader +
                    size +
                    index +
                    b'\x00' * (0x80 - 0x48) +
                    waveform_data
                )
                
                wavetables.append(wavetable)
            
            with open(output_file, 'wb') as f:
                for wavetable in wavetables:
                    f.write(wavetable)
            
            QMessageBox.information(
                None,
                "Success",
                f"Successfully recompiled wavetables to {output_file}"
            )
            
        except Exception as e:
            show_error(f"Error recompiling wavetables: {str(e)}")
    
    def select_decompile_input(self):
        try:
            input_file, _ = QFileDialog.getOpenFileName(
                self,
                "Select .polyend File",
                "",
                "Polyend Files (*.polyend)"
            )
            if input_file:
                self.decompile_wavetable(input_file)
            
        except Exception as e:
            show_error(e)
    
    def select_recompile_input(self):
        try:
            input_dir = QFileDialog.getExistingDirectory(
                self,
                "Select waves Directory"
            )
            if not input_dir:
                return
            
            # Default output file next to the waves directory
            parent_dir = os.path.dirname(input_dir)
            default_output = os.path.join(parent_dir, "recompiled.polyend")
            
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Wavetable As",
                default_output,
                "Polyend Files (*.polyend)"
            )
            if output_file:
                self.recompile_wavetable(input_dir, output_file)
            
        except Exception as e:
            show_error(e)
    
    def select_process_input(self):
        try:
            input_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Folder with WAV Files"
            )
            if not input_dir:
                return
            
            # Create processed directory next to input directory
            output_dir = os.path.join(os.path.dirname(input_dir), 'processed')
            os.makedirs(output_dir, exist_ok=True)
            
            # Get all WAV files from input directory
            wav_files = sorted(Path(input_dir).glob('*.wav'))[:64]  # Limit to 64 files
            if not wav_files:
                raise Exception("No WAV files found in input directory")
            
            for i, wav_path in enumerate(wav_files):
                output_wav = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
                
                # Process WAV file
                with wave.open(str(wav_path), 'rb') as wav_in:
                    # Read audio data
                    frames = wav_in.readframes(wav_in.getnframes())
                    
                    # Convert to mono if stereo
                    if wav_in.getnchannels() == 2:
                        data = np.frombuffer(frames, dtype=np.int16)
                        data = data.reshape(-1, 2)
                        data = np.mean(data, axis=1, dtype=np.int16)
                        frames = data.tobytes()
                    
                    # Write processed WAV
                    with wave.open(output_wav, 'wb') as wav_out:
                        wav_out.setnchannels(1)
                        wav_out.setsampwidth(2)
                        wav_out.setframerate(44100)
                        wav_out.writeframes(frames)
            
            QMessageBox.information(
                None,
                "Success",
                f"Processed {len(wav_files)} WAV files to {output_dir}\n"
                "You can now use Recompile Wavetables to create a .polyend file."
            )
            
        except Exception as e:
            show_error(f"Error processing WAVs: {str(e)}")
    
    def about(self):
        try:
            QMessageBox.information(
                None,
                "About Medusa Wavetable Tool",
                "A tool for working with Polyend Medusa synthesizer wavetables.\n\n"
                "Features:\n"
                "• Extract wavetables from .polyend files\n"
                "• Recompile WAV files into wavetables\n"
                "• Process custom WAV files for use with Medusa\n\n"
                "© 2024 All rights reserved."
            )
        except Exception as e:
            show_error(e)

def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Medusa Wavetable Tool")
        medusa = MedusaApp()
        medusa.show()
        sys.exit(app.exec())
    except Exception as e:
        if QApplication.instance():
            show_error(e)
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()