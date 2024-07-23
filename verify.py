import yt_dlp

playlist_url = "https://youtube.com/playlist?list=PLxCzCOWd7aiFM9Lj5G9G_76adtyb4ef7i&si=NkkIw3EnK9HoEqjj"

def fetch_playlist_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Extract video URLs only
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            print(f"Playlist title: {info.get('title', 'N/A')}")
            print('Videos in playlist:')
            for entry in info['entries']:
                print(f"- {entry['url']}")
        else:
            print("No entries found.")

fetch_playlist_info(playlist_url)
