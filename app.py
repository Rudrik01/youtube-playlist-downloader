from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import yt_dlp
import os
import zipfile
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
DOWNLOAD_FOLDER = 'static/downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Function to strip ANSI codes
def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def my_hook(d):
    if d['status'] == 'downloading':
        progress = {
            'percent': strip_ansi_codes(d['_percent_str']).strip(),
            'speed': strip_ansi_codes(d.get('_speed_str', 'N/A')).strip(),
            'eta': strip_ansi_codes(d.get('_eta_str', 'N/A')).strip()
        }
        socketio.emit('progress', progress)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    playlist_url = request.form['playlist_url']
    
    ydl_opts = {
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': 'bestvideo/best',
        'progress_hooks': [my_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=True)
            if 'entries' not in info:
                return "No videos found in the playlist. Please check the URL and try again."
            video_files = [os.path.join(DOWNLOAD_FOLDER, f"{entry['title']}.mp4") for entry in info['entries']]
    except Exception as e:
        return f"Failed to retrieve or download videos: {e}"

    zip_path = os.path.join(DOWNLOAD_FOLDER, 'playlist_videos.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in video_files:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
