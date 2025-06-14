#!/usr/bin/env python3
"""
Web interface for Medusa Wavetable Utility
Provides browser-based access to wavetable creation and manipulation tools.
"""

import os
import tempfile
import shutil
import zipfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from medusa_core import create_wavetable_bank, decompile_wavetable, recompile_wavetable
from version import __version__, __app_name__

app = Flask(__name__)

# Configuration - use environment variables in production
app.secret_key = os.environ.get('SECRET_KEY', 'medusa-wavetable-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', tempfile.mkdtemp(prefix='medusa_web_'))
ALLOWED_EXTENSIONS = {'wav', 'aif', 'aiff', 'mp3', 'ogg', 'polyend'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_temp_files():
    """Clean up old temporary files"""
    try:
        for item in os.listdir(UPLOAD_FOLDER):
            item_path = os.path.join(UPLOAD_FOLDER, item)
            if os.path.isfile(item_path):
                # Delete files older than 1 hour
                if os.path.getmtime(item_path) < (os.time.time() - 3600):
                    os.remove(item_path)
            elif os.path.isdir(item_path):
                # Delete directories older than 1 hour
                if os.path.getmtime(item_path) < (os.time.time() - 3600):
                    shutil.rmtree(item_path)
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.route('/')
def index():
    cleanup_temp_files()
    return render_template('index.html', version=__version__, app_name=__app_name__)

@app.route('/create', methods=['GET', 'POST'])
def create_wavetable():
    if request.method == 'GET':
        return render_template('create.html')
    
    # Handle file upload
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        flash('No files selected')
        return redirect(request.url)
    
    # Get options
    random_order = request.form.get('random_order') == 'on'
    output_filename = request.form.get('output_filename', 'wavetables.polyend')
    if not output_filename.endswith('.polyend'):
        output_filename += '.polyend'
    
    try:
        # Create temporary directory for this upload
        temp_dir = tempfile.mkdtemp(dir=UPLOAD_FOLDER, prefix='create_')
        input_dir = os.path.join(temp_dir, 'input')
        os.makedirs(input_dir)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(input_dir, filename)
                file.save(file_path)
                saved_files.append(filename)
        
        if not saved_files:
            flash('No valid audio files uploaded')
            return redirect(request.url)
        
        # Create wavetable bank
        output_file = os.path.join(temp_dir, output_filename)
        result = create_wavetable_bank(input_dir, output_file, random_order=random_order)
        
        if result['success']:
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/octet-stream'
            )
        else:
            flash(f'Error creating wavetable: {result["error"]}')
            return redirect(request.url)
            
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(request.url)

@app.route('/decompile', methods=['GET', 'POST'])
def decompile_wavetable_route():
    if request.method == 'GET':
        return render_template('decompile.html')
    
    # Handle file upload
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if not (file and file.filename.lower().endswith('.polyend')):
        flash('Please upload a .polyend file')
        return redirect(request.url)
    
    try:
        # Create temporary directory for this upload
        temp_dir = tempfile.mkdtemp(dir=UPLOAD_FOLDER, prefix='decompile_')
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_file = os.path.join(temp_dir, filename)
        file.save(input_file)
        
        # Decompile wavetables
        output_dir = os.path.join(temp_dir, 'waves')
        result = decompile_wavetable(input_file, output_dir)
        
        if result['success']:
            # Create zip file with all extracted WAV files
            zip_filename = filename.replace('.polyend', '_waves.zip')
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for wav_file in result['files']:
                    zipf.write(wav_file, os.path.basename(wav_file))
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )
        else:
            flash(f'Error decompiling wavetable: {result["error"]}')
            return redirect(request.url)
            
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(request.url)

@app.route('/recompile', methods=['GET', 'POST'])
def recompile_wavetable_route():
    if request.method == 'GET':
        return render_template('recompile.html')
    
    # Handle file upload
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        flash('No files selected')
        return redirect(request.url)
    
    # Get output filename
    output_filename = request.form.get('output_filename', 'recompiled.polyend')
    if not output_filename.endswith('.polyend'):
        output_filename += '.polyend'
    
    try:
        # Create temporary directory for this upload
        temp_dir = tempfile.mkdtemp(dir=UPLOAD_FOLDER, prefix='recompile_')
        input_dir = os.path.join(temp_dir, 'input')
        os.makedirs(input_dir)
        
        # Save uploaded WAV files
        saved_files = []
        for file in files:
            if file and file.filename.lower().endswith('.wav'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(input_dir, filename)
                file.save(file_path)
                saved_files.append(filename)
        
        if not saved_files:
            flash('No valid WAV files uploaded')
            return redirect(request.url)
        
        # Recompile wavetables
        output_file = os.path.join(temp_dir, output_filename)
        result = recompile_wavetable(input_dir, output_file)
        
        if result['success']:
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/octet-stream'
            )
        else:
            flash(f'Error recompiling wavetables: {result["error"]}')
            return redirect(request.url)
            
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(request.url)

@app.route('/api/status')
def api_status():
    """API endpoint for status checks"""
    return jsonify({
        'status': 'running',
        'version': __version__,
        'app_name': __app_name__
    })

if __name__ == '__main__':
    import os
    
    # Use environment variable or default to port 5001 (avoiding macOS AirPlay on 5000)
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Starting {__app_name__} Web Interface v{__version__}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Server starting on: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print("💡 Try a different port:")
            print(f"   PORT=5002 python web_app.py")
            print("   or")
            print(f"   python web_app.py --port 5002")
        else:
            print(f"❌ Error starting server: {e}")
    except KeyboardInterrupt:
        print("\n👋 Server stopped") 