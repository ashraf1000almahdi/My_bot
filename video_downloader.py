import os
import logging
import yt_dlp
from urllib.parse import urlparse
from config import Config

class VideoDownloader:
    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        self.max_file_size = Config.MAX_FILE_SIZE
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        
    def get_video_info(self, url):
        """Extract video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'platform': info.get('extractor', 'Unknown'),
                    'thumbnail': info.get('thumbnail'),
                    'formats': self._extract_formats(info.get('formats', [])),
                    'filesize': info.get('filesize', 0)
                }
        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            return None
    
    def _extract_formats(self, formats):
        """Extract available formats and qualities"""
        available_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none':  # Video formats
                available_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': fmt.get('height', 'Unknown'),
                    'filesize': fmt.get('filesize', 0)
                })
        
        return available_formats
    
    def download_video(self, url, format_type='mp4', quality='best', user_id=None):
        """Download video with specified format and quality"""
        try:
            # Generate unique filename
            filename = f"{user_id}_{int(os.urandom(4).hex(), 16)}"
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, f'{filename}.%(ext)s'),
                'format': self._get_format_selector(format_type, quality),
                'noplaylist': True,
                'extractaudio': format_type == 'mp3',
                'audioformat': 'mp3' if format_type == 'mp3' else None,
                'embed_subs': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            # Add file size limit
            if self.max_file_size:
                ydl_opts['max_filesize'] = self.max_file_size
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                # Check file size
                filesize = info.get('filesize', 0)
                if filesize and filesize > self.max_file_size:
                    return {
                        'success': False,
                        'error': f'File size ({filesize / 1024 / 1024:.1f}MB) exceeds limit ({self.max_file_size / 1024 / 1024:.1f}MB)'
                    }
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = None
                for file in os.listdir(self.download_path):
                    if file.startswith(filename):
                        downloaded_file = os.path.join(self.download_path, file)
                        break
                
                if downloaded_file and os.path.exists(downloaded_file):
                    return {
                        'success': True,
                        'file_path': downloaded_file,
                        'title': info.get('title', 'Unknown'),
                        'filesize': os.path.getsize(downloaded_file),
                        'duration': info.get('duration', 0)
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Downloaded file not found'
                    }
                    
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_format_selector(self, format_type, quality):
        """Get format selector string for yt-dlp"""
        if format_type == 'mp3':
            return 'bestaudio/best'
        elif quality == 'best':
            return 'best'
        else:
            # Try to get specific quality
            quality_num = quality.replace('p', '')
            return f'best[height<={quality_num}]'
    
    def is_supported_url(self, url):
        """Check if URL is supported"""
        try:
            parsed = urlparse(url)
            supported_domains = [
                'youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com',
                'twitter.com', 'facebook.com', 'vimeo.com', 'dailymotion.com'
            ]
            
            return any(domain in parsed.netloc.lower() for domain in supported_domains)
        except:
            return False
    
    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old downloaded files"""
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.download_path):
                file_path = os.path.join(self.download_path, filename)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_hours * 3600:  # Convert hours to seconds
                    os.remove(file_path)
                    logging.info(f"Cleaned up old file: {filename}")
                    
        except Exception as e:
            logging.error(f"Error cleaning up files: {e}")
