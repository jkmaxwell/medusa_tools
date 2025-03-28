#!/usr/bin/env python3

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

class MedusaApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Medusa Wavetable Tool')
        self.root.geometry('400x300')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add title
        title = ttk.Label(main_frame, text="Medusa Wavetable Tool", font=('Helvetica', 16))
        title.grid(row=0, column=0, pady=10)
        
        # Add description
        desc = ttk.Label(main_frame, text="A tool for working with Polyend Medusa wavetables")
        desc.grid(row=1, column=0, pady=5)
        
        # Add buttons
        decompile_btn = ttk.Button(main_frame, text="Decompile .polyend File", command=self.select_decompile_input)
        decompile_btn.grid(row=2, column=0, pady=5, padx=20, sticky=tk.EW)
        
        recompile_btn = ttk.Button(main_frame, text="Recompile Wavetables", command=self.select_recompile_input)
        recompile_btn.grid(row=3, column=0, pady=5, padx=20, sticky=tk.EW)
        
        process_btn = ttk.Button(main_frame, text="Process Custom WAVs", command=self.select_process_input)
        process_btn.grid(row=4, column=0, pady=5, padx=20, sticky=tk.EW)
        
        about_btn = ttk.Button(main_frame, text="About", command=self.about)
        about_btn.grid(row=5, column=0, pady=5, padx=20, sticky=tk.EW)
    
    def select_decompile_input(self):
        input_file = filedialog.askopenfilename(
            title="Select .polyend File",
            filetypes=[("Polyend Files", "*.polyend")]
        )
        if input_file:
            result = decompile_wavetable(input_file)
            if result['success']:
                messagebox.showinfo(
                    "Success",
                    f"Extracted {result['num_wavetables']} wavetables to {result['output_dir']}"
                )
            else:
                messagebox.showerror("Error", f"Error decompiling wavetable: {result['error']}")
    
    def select_recompile_input(self):
        input_dir = filedialog.askdirectory(
            title="Select waves Directory"
        )
        if input_dir:
            # Default output file next to the waves directory
            parent_dir = os.path.dirname(input_dir)
            default_output = os.path.join(parent_dir, "recompiled.polyend")
            
            output_file = filedialog.asksaveasfilename(
                title="Save Wavetable As",
                initialfile=os.path.basename(default_output),
                defaultextension=".polyend",
                filetypes=[("Polyend Files", "*.polyend")]
            )
            if output_file:
                result = recompile_wavetable(input_dir, output_file)
                if result['success']:
                    messagebox.showinfo(
                        "Success",
                        f"Successfully recompiled {result['num_wavetables']} wavetables to {result['output_file']}"
                    )
                else:
                    messagebox.showerror("Error", f"Error recompiling wavetables: {result['error']}")
    
    def select_process_input(self):
        input_dir = filedialog.askdirectory(
            title="Select Folder with WAV Files"
        )
        if input_dir:
            # Create processed directory next to input directory
            output_dir = os.path.join(os.path.dirname(input_dir), 'processed')
            
            result = process_wavs(input_dir, output_dir)
            if result['success']:
                messagebox.showinfo(
                    "Success",
                    f"Processed {result['num_files']} WAV files to {result['output_dir']}\n"
                    "You can now use Recompile Wavetables to create a .polyend file."
                )
            else:
                messagebox.showerror("Error", f"Error processing WAVs: {result['error']}")
    
    def about(self):
        messagebox.showinfo(
            "About Medusa Wavetable Tool",
            "A tool for working with Polyend Medusa synthesizer wavetables.\n\n"
            "Features:\n"
            "• Extract wavetables from .polyend files\n"
            "• Recompile WAV files into wavetables\n"
            "• Process custom WAV files for use with Medusa\n\n"
            "© 2024 All rights reserved."
        )

def main():
    root = tk.Tk()
    app = MedusaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()