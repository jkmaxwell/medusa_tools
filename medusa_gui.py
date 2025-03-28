#!/usr/bin/env python3

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import queue
import subprocess

class MedusaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Medusa Wavetable Tool")
        self.root.geometry("600x500")
        
        # Queue for thread-safe GUI updates
        self.queue = queue.Queue()
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Styles
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Section.TLabel", font=("Helvetica", 12, "bold"))
        
        # Header
        ttk.Label(main_frame, text="Medusa Wavetable Tool", style="Header.TLabel").grid(column=0, row=0, columnspan=3, pady=10)
        
        # Decompile section
        ttk.Label(main_frame, text="Decompile Wavetable", style="Section.TLabel").grid(column=0, row=1, columnspan=3, pady=(20,5), sticky=tk.W)
        
        ttk.Label(main_frame, text="Input .polyend file:").grid(column=0, row=2, sticky=tk.W)
        self.decompile_input = ttk.Entry(main_frame, width=50)
        self.decompile_input.grid(column=1, row=2, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_decompile_input).grid(column=2, row=2)
        
        ttk.Label(main_frame, text="Output folder:").grid(column=0, row=3, sticky=tk.W)
        self.decompile_output = ttk.Entry(main_frame, width=50)
        self.decompile_output.grid(column=1, row=3, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_decompile_output).grid(column=2, row=3)
        
        ttk.Button(main_frame, text="Decompile", command=self.decompile).grid(column=0, row=4, columnspan=3, pady=10)
        
        # Recompile section
        ttk.Label(main_frame, text="Recompile Wavetables", style="Section.TLabel").grid(column=0, row=5, columnspan=3, pady=(20,5), sticky=tk.W)
        
        ttk.Label(main_frame, text="Input folder:").grid(column=0, row=6, sticky=tk.W)
        self.recompile_input = ttk.Entry(main_frame, width=50)
        self.recompile_input.grid(column=1, row=6, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_recompile_input).grid(column=2, row=6)
        
        ttk.Label(main_frame, text="Output .polyend file:").grid(column=0, row=7, sticky=tk.W)
        self.recompile_output = ttk.Entry(main_frame, width=50)
        self.recompile_output.grid(column=1, row=7, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_recompile_output).grid(column=2, row=7)
        
        ttk.Button(main_frame, text="Recompile", command=self.recompile).grid(column=0, row=8, columnspan=3, pady=10)
        
        # Process Custom WAVs section
        ttk.Label(main_frame, text="Process Custom WAVs", style="Section.TLabel").grid(column=0, row=9, columnspan=3, pady=(20,5), sticky=tk.W)
        
        ttk.Label(main_frame, text="Input folder:").grid(column=0, row=10, sticky=tk.W)
        self.process_input = ttk.Entry(main_frame, width=50)
        self.process_input.grid(column=1, row=10, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_process_input).grid(column=2, row=10)
        
        ttk.Label(main_frame, text="Output folder:").grid(column=0, row=11, sticky=tk.W)
        self.process_output = ttk.Entry(main_frame, width=50)
        self.process_output.grid(column=1, row=11, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_process_output).grid(column=2, row=11)
        
        ttk.Button(main_frame, text="Process WAVs", command=self.process_wavs).grid(column=0, row=12, columnspan=3, pady=10)
        
        # Status area
        self.status_text = tk.Text(main_frame, height=6, width=60)
        self.status_text.grid(column=0, row=13, columnspan=3, pady=10)
        self.status_text.config(state=tk.DISABLED)
        
        # Start checking queue
        self.check_queue()
    
    def browse_decompile_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Polyend files", "*.polyend")])
        if filename:
            self.decompile_input.delete(0, tk.END)
            self.decompile_input.insert(0, filename)
    
    def browse_decompile_output(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.decompile_output.delete(0, tk.END)
            self.decompile_output.insert(0, dirname)
    
    def browse_recompile_input(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.recompile_input.delete(0, tk.END)
            self.recompile_input.insert(0, dirname)
    
    def browse_recompile_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".polyend",
                                              filetypes=[("Polyend files", "*.polyend")])
        if filename:
            self.recompile_output.delete(0, tk.END)
            self.recompile_output.insert(0, filename)
    
    def browse_process_input(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.process_input.delete(0, tk.END)
            self.process_input.insert(0, dirname)
    
    def browse_process_output(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.process_output.delete(0, tk.END)
            self.process_output.insert(0, dirname)
    
    def update_status(self, message):
        self.queue.put(message)
    
    def check_queue(self):
        while True:
            try:
                message = self.queue.get_nowait()
                self.status_text.config(state=tk.NORMAL)
                self.status_text.insert(tk.END, message + "\n")
                self.status_text.see(tk.END)
                self.status_text.config(state=tk.DISABLED)
            except queue.Empty:
                break
        self.root.after(100, self.check_queue)
    
    def run_command(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.update_status(output.strip())
        rc = process.poll()
        return rc
    
    def decompile(self):
        if not self.decompile_input.get() or not self.decompile_output.get():
            messagebox.showerror("Error", "Please select input file and output folder")
            return
        
        def run():
            cmd = [
                sys.executable,
                "medusa_wavetable_tool.py",
                "decompile",
                self.decompile_input.get(),
                "--output",
                self.decompile_output.get()
            ]
            rc = self.run_command(cmd)
            if rc == 0:
                self.update_status("Decompile completed successfully")
            else:
                self.update_status("Error during decompile")
        
        threading.Thread(target=run, daemon=True).start()
    
    def recompile(self):
        if not self.recompile_input.get() or not self.recompile_output.get():
            messagebox.showerror("Error", "Please select input folder and output file")
            return
        
        def run():
            cmd = [
                sys.executable,
                "medusa_wavetable_tool.py",
                "recompile",
                self.recompile_input.get(),
                "--output",
                self.recompile_output.get()
            ]
            rc = self.run_command(cmd)
            if rc == 0:
                self.update_status("Recompile completed successfully")
            else:
                self.update_status("Error during recompile")
        
        threading.Thread(target=run, daemon=True).start()
    
    def process_wavs(self):
        if not self.process_input.get() or not self.process_output.get():
            messagebox.showerror("Error", "Please select input and output folders")
            return
        
        def run():
            cmd = [
                sys.executable,
                "medusa_wav_preprocessor.py",
                self.process_input.get(),
                self.process_output.get()
            ]
            rc = self.run_command(cmd)
            if rc == 0:
                self.update_status("WAV processing completed successfully")
            else:
                self.update_status("Error during WAV processing")
        
        threading.Thread(target=run, daemon=True).start()

def main():
    root = tk.Tk()
    app = MedusaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()