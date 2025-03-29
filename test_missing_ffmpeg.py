#!/usr/bin/env python3

import sys
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

class TestMessageBox(QMessageBox):
    """Custom QMessageBox that prints its content."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Print content right after creation
        QTimer.singleShot(0, self._print_content)
    
    def _print_content(self):
        print("\nDialog Content:")
        print(f"Title: {self.windowTitle()}")
        print(f"Text: {self.text()}")
        print(f"Informative Text: {self.informativeText()}")
        print(f"Detailed Text: {self.detailedText()}")
        print("\nPlease click Close to exit the application.")

def test_missing_ffmpeg():
    """Test that app shows error dialog when ffmpeg is missing."""
    print("Testing ffmpeg missing scenario...")
    print("You should see an error dialog.")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Replace QMessageBox with our test version in the medusa_gui module
    with patch('medusa_gui.QMessageBox', TestMessageBox), \
         patch('shutil.which', return_value=None), \
         patch('subprocess.run', side_effect=FileNotFoundError("No such file or directory: 'ffmpeg'")):
        from medusa_gui import main
        main()

if __name__ == '__main__':
    test_missing_ffmpeg()