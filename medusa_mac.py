#!/usr/bin/env python3

import rumps
import os
import sys
import threading
import subprocess
from pathlib import Path

class MedusaWavetableApp(rumps.App):
    def __init__(self):
        super(MedusaWavetableApp, self).__init__("Medusa", icon="🎹")
        
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
    
    def run_command(self, cmd, callback=None):
        def _run():
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    rumps.notification(
                        title="Medusa Wavetable Tool",
                        subtitle="Success!",
                        message="Operation completed successfully"
                    )
                    if callback:
                        callback(True)
                else:
                    rumps.notification(
                        title="Medusa Wavetable Tool",
                        subtitle="Error",
                        message=stderr or "Operation failed"
                    )
                    if callback:
                        callback(False)
            except Exception as e:
                rumps.notification(
                    title="Medusa Wavetable Tool",
                    subtitle="Error",
                    message=str(e)
                )
                if callback:
                    callback(False)
        
        thread = threading.Thread(target=_run)
        thread.start()
    
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
    
    def select_decompile_input(self, _):
        input_file = self.select_file(
            title="Select .polyend File",
            file_types=["polyend"]
        )
        if not input_file:
            return
        
        output_dir = self.select_directory(title="Select Output Folder")
        if not output_dir:
            return
        
        cmd = [
            sys.executable,
            "medusa_wavetable_tool.py",
            "decompile",
            input_file,
            "--output",
            output_dir
        ]
        self.run_command(cmd)
    
    def select_recompile_input(self, _):
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
        
        cmd = [
            sys.executable,
            "medusa_wavetable_tool.py",
            "recompile",
            input_dir,
            "--output",
            output_file
        ]
        self.run_command(cmd)
    
    def select_process_input(self, _):
        input_dir = self.select_directory(title="Select Folder with WAV Files")
        if not input_dir:
            return
        
        output_dir = self.select_directory(title="Select Output Folder")
        if not output_dir:
            return
        
        cmd = [
            sys.executable,
            "medusa_wav_preprocessor.py",
            input_dir,
            output_dir
        ]
        self.run_command(cmd)
    
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