import os
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Union, List

import requests
import validators
from pytube import YouTube, Playlist


class PytubeFunction:
    CREATION_FLAGS = 0x08000000  # hides ffmpeg console

    def __init__(self, output_dir: str, progress_callback: any, complete_callback: any,
                 all_complete_callback: any):
        """
        A class to handle various operations related to YouTube videos.
        :param output_dir: The directory where the downloaded files will be stored.
        :param progress_callback: The callback function to handle download progress.
        :param complete_callback: The callback function to handle download completion.
        :param all_complete_callback: The callback function to handle process completion.
        """
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback
        self.all_complete_callback = all_complete_callback
        self.download_path = Path.home() / "Downloads"

    def download_thumbnail(self, thumbnail_url: str) -> str:
        if self.validate_url(thumbnail_url):
            response = requests.get(thumbnail_url)

            if response.status_code == 200:
                rand_filename = str(uuid.uuid4()) + '.jpg'
                output = self.download_path / rand_filename
                with open(output, 'wb') as file:
                    file.write(response.content)
                return str(output)

    def download_audio(self, url: str) -> None:
        if self.validate_url(url):
            yt_obj = YouTube(url, self.progress_callback, self.complete_callback)

            video_title = yt_obj.title
            title = self.rename_title(video_title)
            output_file = Path(self.output_dir) / f"{title}.mp3"

            audio_stream = yt_obj.streams.filter(only_audio=True).order_by('abr').desc().first()

            audio_path = audio_stream.download(output_path=str(self.download_path), filename='audio')

            subprocess.run(['ffmpeg', '-y', '-i', audio_path, '-c:a', 'libmp3lame', output_file],
                           creationflags=self.CREATION_FLAGS)

            # Clean up temp files
            self.remove_files(str(audio_path))

            # Process complete
            self.all_complete_callback()

    def download_video(self, url: str) -> None:
        if self.validate_url(url):
            yt_obj = YouTube(url, self.progress_callback, self.complete_callback)

            video_title = yt_obj.title
            title = self.rename_title(video_title)
            output_file = Path(self.output_dir) / f"{title}.mp4"

            video_stream = yt_obj.streams.filter(progressive=False, adaptive=True).order_by(
                'resolution').desc().first()
            audio_stream = yt_obj.streams.filter(only_audio=True).order_by('abr').desc().first()

            video_path = video_stream.download(output_path=str(self.download_path), filename='video')
            audio_path = audio_stream.download(output_path=str(self.download_path), filename='audio')

            video = self.download_path / "video.mp4"
            audio = self.download_path / "audio.mp3"

            subprocess.run(['ffmpeg', '-y', '-i', video_path, '-c:v', 'copy', video], creationflags=self.CREATION_FLAGS)
            subprocess.run(['ffmpeg', '-y', '-i', audio_path, '-c:a', 'libmp3lame', audio],
                           creationflags=self.CREATION_FLAGS)
            subprocess.run(['ffmpeg', '-y', '-i', video, '-i', audio, '-c:v', 'copy', '-c:a', 'aac', output_file],
                           creationflags=self.CREATION_FLAGS)

            # Clean up temp files
            self.remove_files([str(audio), str(audio_path), str(video), str(video_path)])

            # Process complete
            self.all_complete_callback()

    def search_playlist(self, url: str):
        if self.validate_url(url):
            p = Playlist(url)
            title = p.title
            owner = p.owner
            videos = f"{p.length} videos"
            views = self.format_view_count(p.views)
            updated = self.format_publish_date(p.last_updated)

            video_details = []
            video_urls = []

            for video_url in p.video_urls:
                video_urls.append(video_url)
                video_detail = self.quick_search(video_url)
                video_details.append(video_detail)

            return {"title": title, "owner": owner, "videos": videos, "views": views, "last_updated": updated,
                    "video_info": video_details, "video_urls": video_urls}

    def quick_search(self, url: str) -> dict:
        if self.validate_url(url):
            yt_obj = YouTube(url)
            title = yt_obj.title
            owner = yt_obj.author
            channel_url = yt_obj.channel_url
            thumbnail_url = yt_obj.thumbnail_url
            thumbnail_path = self.download_thumbnail(thumbnail_url)
            views = self.format_view_count(yt_obj.views)
            publish_date = self.format_publish_date(yt_obj.publish_date)

            return {"title": title, "owner": owner, "channel_url": channel_url, "thumbnail_url": thumbnail_url,
                    "thumbnail_path": thumbnail_path,
                    "views": views,
                    "publish_date": publish_date}

    def remove_files(self, paths: Union[str, List[str]]) -> None:
        if isinstance(paths, list):
            for path in paths:
                self.remove_file(path)
        else:
            self.remove_file(paths)

    @staticmethod
    def remove_file(path: str) -> None:
        if os.path.isfile(path):
            os.remove(path)

    @staticmethod
    def format_publish_date(publish_date: datetime) -> str:
        current_date = datetime.now()

        years_diff = current_date.year - publish_date.year
        months_diff = current_date.month - publish_date.month

        total_months_diff = years_diff * 12 + months_diff

        if total_months_diff > 12:
            years = total_months_diff // 12
            return f"{years} years ago"
        else:
            return f"{total_months_diff} months ago"

    @staticmethod
    def format_view_count(views: int) -> str:
        suffixes = {6: 'M', 3: 'K', 0: ''}
        for power, suffix in sorted(suffixes.items(), reverse=True):
            if views >= 10 ** power:
                views /= 10 ** power
                return f'{views:.1f}{suffix} views'
        return f'{views} views'

    @staticmethod
    def rename_title(title: str) -> str:
        """
        Removes special characters from video title to be a valid filename
        :param title: video title to be renamed
        :return: new title
        """
        title = re.sub(r'[\\/*?:"<>|.]', '', title).strip()
        title = title.replace(" ", "_")
        return title

    @staticmethod
    def validate_url(url: str) -> bool:
        return validators.url(url)


# Callback
def on_progress_callback(stream, _, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = int(bytes_downloaded / total_size * 100)

    print(f'{percentage_of_completion}%')


def on_complete_callback(_, file_path):
    print(f'Processing file... {file_path}')


def all_done_callback():
    print('Download Complete!')


# Usage
if __name__ == "__main__":
    download_folder = str(Path.home() / "Downloads")
    # 2min 4K video
    video_url = 'https://youtu.be/bON-KPiiNCk?si=o8MN5OEtmSH7iVsb'
    # 5 videos playlist
    playlist_url = 'https://youtube.com/playlist?list=PL4KX3oEgJcfeyz484TYEQULx99yFWudTN&si=NaBge2OwI7xk6S72'
    downloader = PytubeFunction(download_folder, on_progress_callback, on_complete_callback,
                                all_done_callback)

    # downloader.download_video(video_url)  # Download the highest resolution video
    # downloader.download_audio(video_url)  # Download audio only (.mp3)
    # playlist_details = downloader.search_playlist(playlist_url)  # Get playlist details same as quick_search function

    # video_details = downloader.quick_search(video_url)  # Get details about video such as: title, owner, channel_url,
    # thumbnail_url, thumbnail_path, views and publish date

    # downloader.download_thumbnail(thumbnail_url)  # Download video thumbnail
    # downloader.validate_url(video_url)  # Validate video url, return True if valid otherwise False
