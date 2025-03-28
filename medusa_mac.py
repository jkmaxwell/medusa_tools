#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import wave
import numpy as np
import struct
from pathlib import Path

class WorkerThread(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(True, "Operation completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))

class MedusaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Medusa Wavetable Tool')
        self.setMinimumWidth(400)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add title
        title = QLabel("Medusa Wavetable Tool")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        desc = QLabel("A tool for working with Polyend Medusa wavetables")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
    
    def notify(self, title, message, success=True):
        if success:
            QMessageBox.information(None, title, message)
        else:
            QMessageBox.warning(None, title, message)
    
    def select_decompile_input(self):
        try:
            input_file, _ = QFileDialog.getOpenFileName(
                self,
                "Select .polyend File",
                "",
                "Polyend Files (*.polyend)"
            )
            if not input_file:
                return
            
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Folder"
            )
            if not output_dir:
                return
            
            self.worker = WorkerThread(self.decompile_wavetable, input_file, output_dir)
            self.worker.finished.connect(self.on_operation_complete)
            self.worker.start()
            
        except Exception as e:
            self.notify("Error", str(e), False)
    
    def select_recompile_input(self):
        try:
            input_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Folder with WAV Files"
            )
            if not input_dir:
                return
            
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Wavetable As",
                "recompiled.polyend",
                "Polyend Files (*.polyend)"
            )
            if not output_file:
                return
            
            self.worker = WorkerThread(self.recompile_wavetable, input_dir, output_file)
            self.worker.finished.connect(self.on_operation_complete)
            self.worker.start()
            
        except Exception as e:
            self.notify("Error", str(e), False)
    
    def select_process_input(self):
        try:
            input_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Folder with WAV Files"
            )
            if not input_dir:
                return
            
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Folder"
            )
            if not output_dir:
                return
            
            self.worker = WorkerThread(self.process_wavs, input_dir, output_dir)
            self.worker.finished.connect(self.on_operation_complete)
            self.worker.start()
            
        except Exception as e:
            self.notify("Error", str(e), False)
    
    def on_operation_complete(self, success, message):
        self.notify("Medusa Wavetable Tool", message, success)
    
    def decompile_wavetable(self, input_file, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        with open(input_file, 'rb') as f:
            data = f.read()
        
        wavetable_size = 16000
        num_wavetables = len(data) // wavetable_size
        
        for i in range(num_wavetables):
            start = i * wavetable_size
            end = start + wavetable_size
            wavetable_data = data[start:end]
            waveform_data = wavetable_data[0x80:]
            
            id_file = os.path.join(output_dir, f'wavetable_{i:02d}.id')
            with open(id_file, 'wb') as f:
                f.write(wavetable_data[4:8])
            
            wav_file = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            with wave.open(wav_file, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(44100)
                wav.writeframes(waveform_data)
        
        return True
    
    def recompile_wavetable(self, input_dir, output_file):
        wavetables = []
        
        for i in range(64):
            wav_file = os.path.join(input_dir, f'wavetable_{i:02d}.wav')
            id_file = os.path.join(input_dir, f'wavetable_{i:02d}.id')
            
            if not os.path.exists(wav_file) or not os.path.exists(id_file):
                raise Exception(f"Missing files for wavetable {i}")
            
            with open(id_file, 'rb') as f:
                wavetable_id = f.read()
            
            with wave.open(wav_file, 'rb') as wav:
                if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                    raise Exception(f"Invalid format in {wav_file}")
                waveform_data = wav.readframes(wav.getnframes())
            
            header = b'\x21\x00\x01\x00' if i == 0 else b'\x02\x00\x00\x3c'
            subheader = b'\x04\x00\x00\x3c'
            size = struct.pack('<H', 4)
            index = struct.pack('<H', i)
            
            wavetable = (
                header +
                wavetable_id +
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
        
        return True
    
    def process_wavs(self, input_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        wav_files = sorted(Path(input_dir).glob('*.wav'))[:64]
        for i, wav_path in enumerate(wav_files):
            output_wav = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            output_id = os.path.join(output_dir, f'wavetable_{i:02d}.id')
            
            with wave.open(str(wav_path), 'rb') as wav_in:
                frames = wav_in.readframes(wav_in.getnframes())
                
                if wav_in.getnchannels() == 2:
                    data = np.frombuffer(frames, dtype=np.int16)
                    data = data.reshape(-1, 2)
                    data = np.mean(data, axis=1, dtype=np.int16)
                    frames = data.tobytes()
                
                with wave.open(output_wav, 'wb') as wav_out:
                    wav_out.setnchannels(1)
                    wav_out.setsampwidth(2)
                    wav_out.setframerate(44100)
                    wav_out.writeframes(frames)
            
            with open(output_id, 'wb') as f:
                f.write(i.to_bytes(4, 'little'))
        
        return True
    
    def about(self):
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

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Medusa Wavetable Tool")
    medusa = MedusaApp()
    medusa.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()