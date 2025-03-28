#!/usr/bin/env python3

import rumps
import os
import sys
import threading
import subprocess
from pathlib import Path
import wave
import numpy as np
import struct

class MedusaWavetableApp(rumps.App):
    def __init__(self):
        super(MedusaWavetableApp, self).__init__("Medusa",
                                                title="M",  # Simple text instead of icon
                                                quit_button="Quit")
        
        # Decompile menu
        self.decompile_menu = rumps.MenuItem("Decompile Wavetable")
        self.decompile_menu.add(rumps.MenuItem("Select .polyend File...", callback=self.select_decompile_input))
        
        # Recompile menu
        self.recompile_menu = rumps.MenuItem("Recompile Wavetables")
        self.recompile_menu.add(rumps.MenuItem("Select Input Folder...", callback=self.select_recompile_input))
        
        # Process WAVs menu
        self.process_menu = rumps.MenuItem("Process Custom WAVs")
        self.process_menu.add(rumps.MenuItem("Select Input Folder...", callback=self.select_process_input))
        
        # Add menus to app
        self.menu = [
            self.decompile_menu,
            self.recompile_menu,
            self.process_menu,
            None,  # Separator
            rumps.MenuItem("About", callback=self.about)
        ]
    
    def notify(self, title, message, success=True):
        rumps.notification(
            title="Medusa Wavetable Tool",
            subtitle="Success!" if success else "Error",
            message=message
        )
    
    def select_file(self, title="Select File", file_types=None):
        from AppKit import NSOpenPanel, NSApp
        
        panel = NSOpenPanel.alloc().init()
        panel.setTitle_(title)
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(False)
        panel.setAllowsMultipleSelection_(False)
        
        if file_types:
            panel.setAllowedFileTypes_(file_types)
        
        if panel.runModal() == 1:
            return panel.URLs()[0].path()
        return None
    
    def select_directory(self, title="Select Folder"):
        from AppKit import NSOpenPanel, NSApp
        
        panel = NSOpenPanel.alloc().init()
        panel.setTitle_(title)
        panel.setCanChooseFiles_(False)
        panel.setCanChooseDirectories_(True)
        panel.setAllowsMultipleSelection_(False)
        
        if panel.runModal() == 1:
            return panel.URLs()[0].path()
        return None
    
    def select_save_file(self, title="Save As", default_name=None, file_types=None):
        from AppKit import NSSavePanel, NSApp
        
        panel = NSSavePanel.alloc().init()
        panel.setTitle_(title)
        
        if default_name:
            panel.setNameFieldStringValue_(default_name)
        
        if file_types:
            panel.setAllowedFileTypes_(file_types)
        
        if panel.runModal() == 1:
            return panel.URL().path()
        return None
    
    def decompile_wavetable(self, input_file, output_dir):
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Read the polyend file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # Extract wavetables
            wavetable_size = 16000  # 0x3E80 bytes per wavetable
            num_wavetables = len(data) // wavetable_size
            
            for i in range(num_wavetables):
                # Extract wavetable data
                start = i * wavetable_size
                end = start + wavetable_size
                wavetable_data = data[start:end]
                
                # Extract waveform data (starts at offset 0x80)
                waveform_data = wavetable_data[0x80:]
                
                # Save wavetable ID
                id_file = os.path.join(output_dir, f'wavetable_{i:02d}.id')
                with open(id_file, 'wb') as f:
                    f.write(wavetable_data[4:8])  # ID is at offset 4
                
                # Convert to WAV format
                wav_file = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
                with wave.open(wav_file, 'wb') as wav:
                    wav.setnchannels(1)  # mono
                    wav.setsampwidth(2)  # 16-bit
                    wav.setframerate(44100)  # 44.1kHz
                    wav.writeframes(waveform_data)
            
            self.notify("Success", f"Extracted {num_wavetables} wavetables")
            return True
            
        except Exception as e:
            self.notify("Error", str(e), success=False)
            return False
    
    def recompile_wavetable(self, input_dir, output_file):
        try:
            # Read all WAV files
            wavetables = []
            for i in range(64):  # Medusa expects exactly 64 wavetables
                wav_file = os.path.join(input_dir, f'wavetable_{i:02d}.wav')
                id_file = os.path.join(input_dir, f'wavetable_{i:02d}.id')
                
                if not os.path.exists(wav_file) or not os.path.exists(id_file):
                    raise Exception(f"Missing files for wavetable {i}")
                
                # Read wavetable ID
                with open(id_file, 'rb') as f:
                    wavetable_id = f.read()
                
                # Read WAV data
                with wave.open(wav_file, 'rb') as wav:
                    if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                        raise Exception(f"Invalid format in {wav_file}")
                    waveform_data = wav.readframes(wav.getnframes())
                
                # Create wavetable structure
                header = b'\x21\x00\x01\x00' if i == 0 else b'\x02\x00\x00\x3c'
                subheader = b'\x04\x00\x00\x3c'
                size = struct.pack('<H', 4)
                index = struct.pack('<H', i)
                
                # Combine all parts
                wavetable = (
                    header +
                    wavetable_id +
                    b'\x00' * (0x40 - 8) +  # Padding to 0x40
                    subheader +
                    size +
                    index +
                    b'\x00' * (0x80 - 0x48) +  # Padding to 0x80
                    waveform_data
                )
                
                wavetables.append(wavetable)
            
            # Write combined file
            with open(output_file, 'wb') as f:
                for wavetable in wavetables:
                    f.write(wavetable)
            
            self.notify("Success", "Recompiled wavetables successfully")
            return True
            
        except Exception as e:
            self.notify("Error", str(e), success=False)
            return False
    
    def select_decompile_input(self, _):
        def run():
            input_file = self.select_file(
                title="Select .polyend File",
                file_types=["polyend"]
            )
            if not input_file:
                return
            
            output_dir = self.select_directory(title="Select Output Folder")
            if not output_dir:
                return
            
            self.decompile_wavetable(input_file, output_dir)
        
        threading.Thread(target=run).start()
    
    def select_recompile_input(self, _):
        def run():
            input_dir = self.select_directory(title="Select Folder with WAV Files")
            if not input_dir:
                return
            
            output_file = self.select_save_file(
                title="Save Wavetable As",
                default_name="recompiled.polyend",
                file_types=["polyend"]
            )
            if not output_file:
                return
            
            self.recompile_wavetable(input_dir, output_file)
        
        threading.Thread(target=run).start()
    
    def select_process_input(self, _):
        def run():
            input_dir = self.select_directory(title="Select Folder with WAV Files")
            if not input_dir:
                return
            
            output_dir = self.select_directory(title="Select Output Folder")
            if not output_dir:
                return
            
            try:
                os.makedirs(output_dir, exist_ok=True)
                
                # Process WAV files
                wav_files = sorted(Path(input_dir).glob('*.wav'))[:64]
                for i, wav_path in enumerate(wav_files):
                    output_wav = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
                    output_id = os.path.join(output_dir, f'wavetable_{i:02d}.id')
                    
                    # Convert WAV file
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
                    
                    # Create ID file
                    with open(output_id, 'wb') as f:
                        f.write(i.to_bytes(4, 'little'))
                
                self.notify("Success", f"Processed {len(wav_files)} WAV files")
                
            except Exception as e:
                self.notify("Error", str(e), success=False)
        
        threading.Thread(target=run).start()
    
    @rumps.clicked("About")
    def about(self, _):
        rumps.alert(
            title="About Medusa Wavetable Tool",
            message=(
                "A tool for working with Polyend Medusa synthesizer wavetables.\n\n"
                "Features:\n"
                "• Extract wavetables from .polyend files\n"
                "• Recompile WAV files into wavetables\n"
                "• Process custom WAV files for use with Medusa\n\n"
                "© 2024 All rights reserved."
            )
        )

if __name__ == "__main__":
    MedusaWavetableApp().run()