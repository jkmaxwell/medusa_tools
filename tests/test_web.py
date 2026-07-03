import io
import os
import struct
import time
import wave

import pytest

flask = pytest.importorskip("flask")

import web_app
from web_app import app, cleanup_temp_files, UPLOAD_FOLDER


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def wav_bytes(value=1000, n_frames=1000):
    """Build an in-memory 16-bit mono WAV."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(struct.pack('<h', value) * n_frames)
    buf.seek(0)
    return buf


def test_cleanup_removes_stale_files():
    stale = os.path.join(UPLOAD_FOLDER, 'stale.txt')
    with open(stale, 'w') as f:
        f.write('old')
    two_hours_ago = time.time() - 7200
    os.utime(stale, (two_hours_ago, two_hours_ago))

    cleanup_temp_files()
    assert not os.path.exists(stale)


def test_cleanup_keeps_fresh_files():
    fresh = os.path.join(UPLOAD_FOLDER, 'fresh.txt')
    with open(fresh, 'w') as f:
        f.write('new')
    try:
        cleanup_temp_files()
        assert os.path.exists(fresh)
    finally:
        if os.path.exists(fresh):
            os.remove(fresh)


def test_create_sanitizes_output_filename(client):
    """A traversal attempt in output_filename must not escape the upload dir."""
    escape_target = os.path.abspath(os.path.join(UPLOAD_FOLDER, '..', 'evil.polyend'))
    assert not os.path.exists(escape_target)

    resp = client.post('/create', data={
        'files': (wav_bytes(), 'a.wav'),
        'output_filename': '../../evil',
    }, content_type='multipart/form-data')

    assert resp.status_code == 200
    assert not os.path.exists(escape_target)


def test_create_from_single_file(client):
    """One uploaded file is enough to build a full 64-slot bank."""
    resp = client.post('/create', data={
        'files': (wav_bytes(), 'a.wav'),
        'output_filename': 'bank.polyend',
    }, content_type='multipart/form-data')

    assert resp.status_code == 200
    from medusa_core import TOTAL_FILE_SIZE
    assert len(resp.data) == TOTAL_FILE_SIZE


def test_api_status(client):
    resp = client.get('/api/status')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'running'
