
# Pytube Function

Powered by Pytube, this YouTube downloader function is capable of downloading videos at the highest available resolution, including 4K. It also offers the option to download only the audio file. Additionally, it provides detailed information about individual videos and playlists.




## Features

- Powered by Pytube: Utilizes the Pytube library, a lightweight, dependency-free Python library for downloading YouTube Videos.
- High-Resolution Downloads: Capable of downloading videos at the highest available resolution, including 4K.
- Audio-Only Downloads: Provides the option to download only the audio file from a YouTube video.
- Video Details: Retrieves detailed information about individual videos.
- Playlist Details: Can also fetch information about YouTube playlists.
- FFmpeg Integration for High-Quality Videos: The function uses FFmpeg, a powerful multimedia framework, to merge video and audio files. This ensures that the downloaded videos maintain high quality, even when the video and audio are stored in separate files on YouTube. This is particularly useful for high-resolution videos where the audio and video are often separated.
## Installation

- Python 3.7-3.12 (tested on 3.12)
- FFmpeg

```bash
  git clone https://github.com/rudymohammadbali/pytube_function.git
  cd pytube_function
  pip install -r requirements.txt
```
## Usage/Examples

```python
from pytube_function import PytubeFunction

download_folder = str(Path.home() / "Downloads")
video_url = 'https://youtu.be/bON-KPiiNCk?si=o8MN5OEtmSH7iVsb' # 2min 4K video
playlist_url = 'https://youtube.com/playlist?list=PL4KX3oEgJcfeyz484TYEQULx99yFWudTN&si=NaBge2OwI7xk6S72' # 5 videos playlist

downloader = PytubeFunction(download_folder, on_progress_callback, on_complete_callback, all_done_callback)

# downloader.download_video(video_url)  # Download the highest resolution video
# downloader.download_audio(video_url)  # Download audio only (.mp3)
# playlist_details = downloader.search_playlist(playlist_url)  # Get playlist details same as quick_search function

# video_details = downloader.quick_search(video_url)  # Get details about video such as: title, owner, channel_url, thumbnail_url, thumbnail_path, views and publish date

# downloader.download_thumbnail(thumbnail_url)  # Download video thumbnail
# downloader.validate_url(video_url)  # Validate video url, return True if valid otherwise False
``` 


## Contributing

Contributions are always welcome!

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

If you want to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

