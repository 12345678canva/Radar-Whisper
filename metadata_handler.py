#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Metadata handler module for extracting and managing audio file metadata
"""

import os
import io
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from PIL import Image
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis


class MetadataHandler:
    """
    Handles metadata extraction and manipulation for audio files.
    Uses mutagen library to provide detailed metadata beyond what QMediaPlayer offers.
    """
    
    # Supported file extensions and their corresponding mutagen classes
    SUPPORTED_FORMATS = {
        '.mp3': MP3,
        '.flac': FLAC,
        '.wav': WAVE,
        '.m4a': MP4,
        '.ogg': OggVorbis,
    }
    
    def __init__(self) -> None:
        """Initialize the metadata handler."""
        self._current_file: Optional[str] = None
        self._current_metadata: Dict[str, Any] = {}
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from an audio file.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            Dict[str, Any]: Dictionary containing the extracted metadata
            
        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            # Store the current file path
            self._current_file = file_path
            
            # Clear any previous metadata
            self._current_metadata = {}
            
            # Get the appropriate mutagen class for this file type
            format_class = self.SUPPORTED_FORMATS[file_ext]
            audio = format_class(file_path)
            
            # Extract basic metadata
            metadata = self._extract_metadata(audio, file_ext)
            
            # Add file information
            metadata['file_path'] = file_path
            metadata['file_name'] = os.path.basename(file_path)
            metadata['file_size'] = os.path.getsize(file_path)
            metadata['file_extension'] = file_ext[1:]  # Remove the dot
            
            # Store the metadata
            self._current_metadata = metadata
            
            return metadata
            
        except Exception as e:
            # If there's an error, try a more generic approach
            try:
                basic_metadata = {
                    'title': os.path.splitext(os.path.basename(file_path))[0],
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_extension': file_ext[1:],
                }
                
                # Try with generic mutagen
                audio = mutagen.File(file_path)
                if audio:
                    basic_metadata['duration'] = int(audio.info.length * 1000)  # Convert to ms
                    basic_metadata['duration_str'] = self.format_duration(audio.info.length)
                    
                return basic_metadata
            except Exception as e2:
                # Return at minimum the file information
                return {
                    'title': os.path.splitext(os.path.basename(file_path))[0],
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_extension': file_ext[1:],
                    'error': str(e2)
                }
    
    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple files and extract metadata.
        
        Args:
            file_paths (List[str]): List of file paths to process
            
        Returns:
            List[Dict[str, Any]]: List of metadata dictionaries, one for each file
        """
        results = []
        for file_path in file_paths:
            try:
                metadata = self.get_metadata(file_path)
                results.append(metadata)
            except Exception as e:
                # Add error information but don't halt the batch process
                results.append({
                    'file_path': file_path,
                    'error': str(e)
                })
        
        return results
    
    def get_album_art(self, file_path: Optional[str] = None) -> Optional[bytes]:
        """
        Extract album art from an audio file.
        
        Args:
            file_path (Optional[str]): Path to the audio file. If None, uses the last processed file.
            
        Returns:
            Optional[bytes]: Album art as bytes, or None if no album art is found
        """
        if file_path:
            # Process the new file
            self.get_metadata(file_path)
        elif not self._current_file:
            # No current file
            return None
        
        file_ext = os.path.splitext(self._current_file)[1].lower()
        
        try:
            if file_ext == '.mp3':
                return self._get_mp3_album_art(self._current_file)
            elif file_ext == '.flac':
                return self._get_flac_album_art(self._current_file)
            elif file_ext == '.m4a':
                return self._get_mp4_album_art(self._current_file)
            elif file_ext == '.ogg':
                return self._get_ogg_album_art(self._current_file)
            else:
                return None
        except Exception:
            return None
    
    def save_album_art(self, file_path: str, output_path: str) -> bool:
        """
        Extract and save album art to a file.
        
        Args:
            file_path (str): Path to the audio file
            output_path (str): Path where the image should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        art_data = self.get_album_art(file_path)
        if not art_data:
            return False
        
        try:
            # Save the image data to the specified path
            with open(output_path, 'wb') as f:
                f.write(art_data)
            return True
        except Exception:
            return False
    
    def set_album_art(self, file_path: str, image_path: str) -> bool:
        """
        Set album art for an audio file.
        
        Args:
            file_path (str): Path to the audio file
            image_path (str): Path to the image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path) or not os.path.exists(image_path):
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # Read the image data
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            
            # Determine the MIME type of the image
            img = Image.open(io.BytesIO(img_data))
            mime_type = f"image/{img.format.lower()}"
            
            if file_ext == '.mp3':
                return self._set_mp3_album_art(file_path, img_data, mime_type)
            elif file_ext == '.flac':
                return self._set_flac_album_art(file_path, img_data, mime_type)
            elif file_ext == '.m4a':
                return self._set_mp4_album_art(file_path, img_data, mime_type)
            elif file_ext == '.ogg':
                return self._set_ogg_album_art(file_path, img_data, mime_type)
            else:
                return False
        except Exception:
            return False
    
    def update_tags(self, file_path: str, tags: Dict[str, Any]) -> bool:
        """
        Update tags for an audio file.
        
        Args:
            file_path (str): Path to the audio file
            tags (Dict[str, Any]): Dictionary of tags to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            return False
        
        try:
            # Get the appropriate mutagen class for this file type
            format_class = self.SUPPORTED_FORMATS[file_ext]
            audio = format_class(file_path)
            
            # Update the tags based on the file format
            if file_ext == '.mp3':
                self._update_mp3_tags(audio, tags)
            elif file_ext == '.flac':
                self._update_flac_tags(audio, tags)
            elif file_ext == '.wav':
                # WAV has limited tag support
                self._update_wav_tags(audio, tags)
            elif file_ext == '.m4a':
                self._update_mp4_tags(audio, tags)
            elif file_ext == '.ogg':
                self._update_ogg_tags(audio, tags)
            
            # Save the changes
            audio.save()
            
            # Refresh the metadata
            if self._current_file == file_path:
                self.get_metadata(file_path)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to a human-readable string.
        
        Args:
            seconds (float): Duration in seconds
            
        Returns:
            str: Formatted duration string (HH:MM:SS or MM:SS)
        """
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _extract_metadata(self, audio: Any, file_ext: str) -> Dict[str, Any]:
        """
        Extract metadata from a mutagen audio object.
        
        Args:
            audio (Any): Mutagen audio object
            file_ext (str): File extension
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata = {}
        
        # Extract duration in milliseconds and as formatted string
        if hasattr(audio.info, 'length'):
            metadata['duration'] = int(audio.info.length * 1000)  # Convert to ms
            metadata['duration_str'] = self.format_duration(audio.info.length)
        
        # Extract bitrate if available
        if hasattr(audio.info, 'bitrate'):
            metadata['bitrate'] = audio.info.bitrate
        
        # Extract sample rate if available
        if hasattr(audio.info, 'sample_rate'):
            metadata['sample_rate'] = audio.info.sample_rate
        
        # Extract channels if available
        if hasattr(audio.info, 'channels'):
            metadata['channels'] = audio.info.channels
        
        # Extract format-specific metadata
        if file_ext == '.mp3':
            return self._extract_mp3_metadata(audio, metadata)
        elif file_ext == '.flac':
            return self._extract_flac_metadata(audio, metadata)
        elif file_ext == '.wav':
            return self._extract_wav_metadata(audio, metadata)
        elif file_ext == '.m4a':
            return self._extract_mp4_metadata(audio, metadata)
        elif file_ext == '.ogg':
            return self._extract_ogg_metadata(audio, metadata)
        else:
            return metadata
    
    def _extract_mp3_metadata(self, audio: MP3, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata specific to MP3 files.
        
        Args:
            audio (MP3): Mutagen MP3 object
            metadata (Dict[str, Any]): Metadata dictionary to update
            
        Returns:
            Dict[str, Any]: Updated metadata
        """
        if audio.tags:
            # Title
            if 'TIT2' in audio.tags:
                metadata['title'] = str(audio.tags['TIT2'])
            
            # Artist
            if 'TPE1' in audio.tags:
                metadata['artist'] = str(audio.tags['TPE1'])
            
            # Album
            if 'TALB' in audio.tags:
                metadata['album'] = str(audio.tags['TALB'])
            
            # Album Artist
            if 'TPE2' in audio.tags:
                metadata['album_artist'] = str(audio.tags['TPE2'])
            
            # Year
            if 'TDRC' in audio.tags:
                metadata['year'] = str(audio.tags['TDRC'])
            
            # Track number
            if 'TRCK' in audio.tags:
                track_info = str(audio.tags['TRCK'])
                if '/' in track_info:
                    track, total = track_info.split('/')
                    metadata['track_number'] = int(track.strip())
                    metadata['total_tracks'] = int(total.strip())
                else:
                    metadata['track_number'] = int(track_info.strip())
            
            # Genre
            if 'TCON' in audio.tags:
                metadata['genre'] = str(audio.tags['TCON'])
            
            # Comment
            if 'COMM::'in audio.tags:
                metadata['comment'] = str(audio.tags['COMM::'])
        
        # Add format-specific info
        metadata['format'] = 'MP3'
        metadata['layer'] = audio.info.layer
        metadata['mode'] = audio.info.mode
        
        # Check if album art is present
        if audio.tags and any(tag.startswith('APIC') for tag in audio.tags.keys()):
            metadata['has_album_art'] = True
        
        return metadata
    
    def _extract_flac_metadata(self, audio: FLAC, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata specific to FLAC files.
        
        Args:
            audio (FLAC): Mutagen FLAC object
            metadata (Dict[str, Any]): Metadata dictionary to update
            
        Returns:
            Dict[str, Any]: Updated metadata
        """
        # Title
        if 'title' in audio:
            metadata['title'] = str(audio['title'][0])
        
        # Artist
        if 'artist' in audio:
            metadata['artist'] = str(audio['artist'][0])
        
        # Album
        if 'album' in audio:
            metadata['album'] = str(audio['album'][0])
        
        # Album Artist
        if 'albumartist' in audio:
            metadata['album_artist'] = str(audio['albumartist'][0])
        
        # Year/Date
        if 'date' in audio:
            metadata['year'] = str(audio['date'][0])
        
        # Track number
        if 'tracknumber' in audio:
            track_info = str(audio['tracknumber'][0])
            if '/' in track_info:
                track, total = track_info.split('/')
                metadata['track_number'] = int(track.strip())
                metadata['total_tracks'] = int(total.strip())
            else:
                metadata['track_number'] = int(track_info.strip())
        
        # Genre
        if 'genre' in audio:
            metadata['genre'] = str(audio['genre'][0])
        
        # Comment
        if 'comment' in audio:
            metadata['comment'] = str(audio['comment'][0])
        
        # Add format-specific info
        metadata['format'] = 'FLAC'
        
        # Check if album art is present
        if audio.pictures:
            metadata['has_album_art'] = True
        
        return metadata
    
    def _extract_wav_metadata(self, audio: WAVE, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata specific to WAV files.
        
        Args:
            audio (WAVE): Mutagen WAVE object
            metadata (Dict[str, Any]): Metadata dictionary to update
            
        Returns:
            Dict[str, Any]: Updated metadata
        """
        # WAV files have limited tag support in ID3 format
        if hasattr(audio, 'tags') and audio.tags:
            # Title
            if 'TIT2' in audio.tags:
                metadata['title'] = str(audio.tags['TIT2'])
            
            # Artist
            if 'TPE1' in audio.tags:
                metadata['artist'] = str(audio.tags['TPE1'])
            
            # Album
            if 'TALB' in audio.tags:
                metadata['album'] = str(audio.tags['TALB'])
        
        # Add format-specific info
        metadata['format'] = 'WAV'
        metadata['bits_per_sample'] = getattr(audio.info, 'bits_per_sample', None)
        
        return metadata
    
    def _extract_mp4_metadata(self, audio: MP4, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata specific to MP4/M4A files.
        
        Args:
            audio (MP4): Mutagen MP4 object
            metadata (Dict[str, Any]): Metadata dictionary to update
            
        Returns:
            Dict[str, Any]: Updated metadata
        """
        # MP4 has a different tag map
        # Title
        if '\xa9nam' in audio:
            metadata['title'] = str(audio['\xa9nam'][0])
        
        # Artist
        if '\xa9ART' in audio:
            metadata['artist'] = str(audio['\xa9ART'][0])
        
        # Album
        if '\xa9alb' in audio:
            metadata['album'] = str(audio['\xa9alb'][0])
        
        # Album Artist
        if 'aART' in audio:
            metadata['album_artist'] = str(audio['aART'][0])
        
        # Year
        if '\xa9day' in audio:
            metadata['year'] = str(audio['\xa9day'][0])
        
        # Track number
        if 'trkn' in audio:
            track, total = audio['trkn'][0]
            metadata['track_number'] = track
            if total:
                metadata['total_tracks'] = total
        
        # Genre
        if '\xa9gen' in audio:
            metadata['genre'] = str(audio['\xa9gen'][0])
        
        # Comment
        if '\xa9cmt' in audio:
            metadata['comment'] = str(audio['\xa9cmt'][0])
        
        # Add format-specific info
        metadata['format'] = 'M4A'
        
        # Check if album art is present
        if 'covr' in audio:
            metadata['has_album_art'] = True
        
        return metadata
    
    def _extract_ogg_metadata(self, audio: OggVorbis, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata specific to OGG Vorbis files.
        
        Args:
            audio (OggVorbis): Mutagen OggVorbis object
            metadata (Dict[str, Any]): Metadata dictionary to update
            
        Returns:
            Dict[str, Any]: Updated metadata
        """
        # Similar to FLAC
        # Title
        if 'title' in audio:
            metadata['title'] = str(audio['title'][0])
        
        # Artist
        if 'artist' in audio:
            metadata['artist'] = str(audio['artist'][0])
        
        # Album
        if 'album' in audio:
            metadata['album'] = str(audio['album'][0])
        
        # Album Artist
        if 'albumartist' in audio:
            metadata['album_artist'] = str(audio['albumartist'][0])
        
        # Year/Date
        if 'date' in audio:
            metadata['year'] = str(audio['date'][0])
        
        # Track number
        if 'tracknumber' in audio:
            track_info = str(audio['tracknumber'][0])
            if '/' in track_info:
                track, total = track_info.split('/')
                metadata['track_number'] = int(track.strip())
                metadata['total_tracks'] = int(total.strip())
            else:
                metadata['track_number'] = int(track_info.strip())
        
        # Genre
        if 'genre' in audio:
            metadata['genre'] = str(audio['genre'][0])
        
        # Comment
        if 'comment' in audio:
            metadata['comment'] = str(audio['comment'][0])
        
        # Add format-specific info
        metadata['format'] = 'OGG'
        
        # Check for metadata blocks that might contain album art
        if 'metadata_block_picture' in audio:
            metadata['has_album_art'] = True
        
        return metadata
    
    def _get_mp3_album_art(self, file_path: str) -> Optional[bytes]:
        """
        Extract album art from an MP3 file.
        
        Args:
            file_path (str): Path to the MP3 file
            
        Returns:
            Optional[bytes]: Album art as bytes, or None if no album art is found
        """
        try:
            audio = ID3(file_path)
            for tag in audio.keys():
                if tag.startswith('APIC'):
                    return audio[tag].data
            return None
        except Exception:
            return None
    
    def _get_flac_album_art(self, file_path: str) -> Optional[bytes]:
        """
        Extract album art from a FLAC file.
        
        Args:
            file_path (str): Path to the FLAC file
            
        Returns:
            Optional[bytes]: Album art as bytes, or None if no album art is found
        """
        try:
            audio = FLAC(file_path)
            if audio.pictures:
                # Just return the first picture
                return audio.pictures[0].data
            return None
        except Exception:
            return None
    
    def _get_mp4_album_art(self, file_path: str) -> Optional[bytes]:
        """
        Extract album art from an MP4/M4A file.
        
        Args:
            file_path (str): Path to the MP4/M4A file
            
        Returns:
            Optional[bytes]: Album art as bytes, or None if no album art is found
        """
        try:
            audio = MP4(file_path)
            if 'covr' in audio:
                return audio['covr'][0]
            return None
        except Exception:
            return None
    
    def _get_ogg_album_art(self, file_path: str) -> Optional[bytes]:
        """
        Extract album art from an OGG file.
        
        Args:
            file_path (str): Path to the OGG file
            
        Returns:
            Optional[bytes]: Album art as bytes, or None if no album art is found
        """
        try:
            audio = OggVorbis(file_path)
            if 'metadata_block_picture' in audio:
                import base64
                data = base64.b64decode(audio['metadata_block_picture'][0])
                picture = Picture(data)
                return picture.data
            return None
        except Exception:
            return None
    
    def _set_mp3_album_art(self, file_path: str, img_data: bytes, mime_type: str) -> bool:
        """
        Set album art for an MP3 file.
        
        Args:
            file_path (str): Path to the MP3 file
            img_data (bytes): Image data
            mime_type (str): Image MIME type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio = ID3(file_path)
            
            # Clear existing album art
            for tag in list(audio.keys()):
                if tag.startswith('APIC'):
                    del audio[tag]
            
            # Add the new album art
            audio['APIC'] = APIC(
                encoding=3,  # UTF-8
                mime=mime_type,
                type=3,  # Cover (front)
                desc='Cover',
                data=img_data
            )
            
            audio.save()
            return True
        except Exception:
            return False
    
    def _set_flac_album_art(self, file_path: str, img_data: bytes, mime_type: str) -> bool:
        """
        Set album art for a FLAC file.
        
        Args:
            file_path (str): Path to the FLAC file
            img_data (bytes): Image data
            mime_type (str): Image MIME type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio = FLAC(file_path)
            
            # Clear existing pictures
            audio.clear_pictures()
            
            # Create a new picture
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = mime_type
            picture.desc = 'Cover'
            picture.data = img_data
            
            # Add the picture
            audio.add_picture(picture)
            
            audio.save()
            return True
        except Exception:
            return False
    
    def _set_mp4_album_art(self, file_path: str, img_data: bytes, mime_type: str) -> bool:
        """
        Set album art for an MP4/M4A file.
        
        Args:
            file_path (str): Path to the MP4/M4A file
            img_data (bytes): Image data
            mime_type (str): Image MIME type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio = MP4(file_path)
            
            # Set the cover art
            if 'image/jpeg' in mime_type:
                audio['covr'] = [MP4.Cover(img_data, MP4.Cover.JPEG)]
            elif 'image/png' in mime_type:
                audio['covr'] = [MP4.Cover(img_data, MP4.Cover.PNG)]
            else:
                # Try to use JPEG as default
                audio['covr'] = [MP4.Cover(img_data, MP4.Cover.JPEG)]
            
            audio.save()
            return True
        except Exception:
            return False
    
    def _set_ogg_album_art(self, file_path: str, img_data: bytes, mime_type: str) -> bool:
        """
        Set album art for an OGG file.
        
        Args:
            file_path (str): Path to the OGG file
            img_data (bytes): Image data
            mime_type (str): Image MIME type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio = OggVorbis(file_path)
            
            # Create a picture object
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = mime_type
            picture.desc = 'Cover'
            picture.data = img_data
            
            # Convert to base64
            import base64
            data = picture.write()
            encoded_data = base64.b64encode(data).decode('ascii')
            
            # Set the metadata block picture
            audio['metadata_block_picture'] = [encoded_data]
            
            audio.save()
            return True
        except Exception:
            return False
    
    def _update_mp3_tags(self, audio: MP3, tags: Dict[str, Any]) -> None:
        """
        Update tags for an MP3 file.
        
        Args:
            audio (MP3): Mutagen MP3 object
            tags (Dict[str, Any]): Dictionary of tags to update
        """
        # Make sure we have ID3 tags
        if not audio.tags:
            audio.tags = ID3()
        # Map common tag names to ID3 frames
        tag_map = {
            'title': ('TIT2', lambda x: str(x)),
            'artist': ('TPE1', lambda x: str(x)),
            'album': ('TALB', lambda x: str(x)),
            'album_artist': ('TPE2', lambda x: str(x)),
            'year': ('TDRC', lambda x: str(x)),
            'genre': ('TCON', lambda x: str(x)),
            'comment': ('COMM::', lambda x: str(x)),
            'track_number': ('TRCK', lambda x: str(x)),
        }
        
        # Update each tag if it's in the provided tags dictionary
        for tag_name, (frame_id, converter) in tag_map.items():
            if tag_name in tags:
                try:
                    # Import the appropriate ID3 frame type
                    from mutagen.id3 import TIT2, TPE1, TALB, TPE2, TDRC, TCON, COMM, TRCK
                    frame_classes = {
                        'TIT2': TIT2,
                        'TPE1': TPE1,
                        'TALB': TALB,
                        'TPE2': TPE2,
                        'TDRC': TDRC,
                        'TCON': TCON,
                        'TRCK': TRCK,
                    }
                    
                    # Special case for comments
                    if frame_id == 'COMM::':
                        audio.tags.add(COMM(
                            encoding=3,  # UTF-8
                            lang='eng',
                            desc='',
                            text=converter(tags[tag_name])
                        ))
                    else:
                        frame_class = frame_classes[frame_id]
                        audio.tags.add(frame_class(
                            encoding=3,  # UTF-8
                            text=converter(tags[tag_name])
                        ))
                except Exception as e:
                    print(f"Error setting ID3 tag {tag_name}: {str(e)}")
    
    def _update_flac_tags(self, audio: FLAC, tags: Dict[str, Any]) -> None:
        """
        Update tags for a FLAC file.
        
        Args:
            audio (FLAC): Mutagen FLAC object
            tags (Dict[str, Any]): Dictionary of tags to update
        """
        # FLAC tags are stored as key-value pairs in the file's Vorbis comments
        tag_map = {
            'title': 'title',
            'artist': 'artist',
            'album': 'album',
            'album_artist': 'albumartist',
            'year': 'date',
            'genre': 'genre',
            'comment': 'comment',
            'track_number': 'tracknumber',
        }
        
        # Update each tag if it's in the provided tags dictionary
        for tag_name, vorbis_name in tag_map.items():
            if tag_name in tags:
                try:
                    # Convert the value to string and set it
                    value = str(tags[tag_name])
                    audio[vorbis_name] = [value]
                except Exception as e:
                    print(f"Error setting FLAC tag {tag_name}: {str(e)}")
    
    def _update_wav_tags(self, audio: WAVE, tags: Dict[str, Any]) -> None:
        """
        Update tags for a WAV file.
        
        Args:
            audio (WAVE): Mutagen WAVE object
            tags (Dict[str, Any]): Dictionary of tags to update
        """
        # WAV files have limited tag support through ID3
        # First make sure we have tags
        if not hasattr(audio, 'tags') or audio.tags is None:
            from mutagen.id3 import ID3
            audio.tags = ID3()
        
        # We'll reuse the MP3 tag update method since WAV uses ID3 as well
        self._update_mp3_tags(audio, tags)
    
    def _update_mp4_tags(self, audio: MP4, tags: Dict[str, Any]) -> None:
        """
        Update tags for an MP4/M4A file.
        
        Args:
            audio (MP4): Mutagen MP4 object
            tags (Dict[str, Any]): Dictionary of tags to update
        """
        # MP4 has a different tag map
        tag_map = {
            'title': '\xa9nam',
            'artist': '\xa9ART',
            'album': '\xa9alb',
            'album_artist': 'aART',
            'year': '\xa9day',
            'genre': '\xa9gen',
            'comment': '\xa9cmt',
        }
        
        # Update each tag if it's in the provided tags dictionary
        for tag_name, mp4_name in tag_map.items():
            if tag_name in tags:
                try:
                    # Convert the value to string and set it
                    value = str(tags[tag_name])
                    audio[mp4_name] = [value]
                except Exception as e:
                    print(f"Error setting MP4 tag {tag_name}: {str(e)}")
        
        # Handle track number separately since it's a tuple (track, total)
        if 'track_number' in tags:
            try:
                track = int(tags['track_number'])
                total = int(tags.get('total_tracks', 0)) if 'total_tracks' in tags else 0
                audio['trkn'] = [(track, total)]
            except Exception as e:
                print(f"Error setting MP4 track number: {str(e)}")
    
    def _update_ogg_tags(self, audio: OggVorbis, tags: Dict[str, Any]) -> None:
        """
        Update tags for an OGG Vorbis file.
        
        Args:
            audio (OggVorbis): Mutagen OggVorbis object
            tags (Dict[str, Any]): Dictionary of tags to update
        """
        # OGG Vorbis uses the same tag format as FLAC (Vorbis comments)
        tag_map = {
            'title': 'title',
            'artist': 'artist',
            'album': 'album',
            'album_artist': 'albumartist',
            'year': 'date',
            'genre': 'genre',
            'comment': 'comment',
            'track_number': 'tracknumber',
        }
        
        # Update each tag if it's in the provided tags dictionary
        for tag_name, vorbis_name in tag_map.items():
            if tag_name in tags:
                try:
                    # Convert the value to string and set it
                    value = str(tags[tag_name])
                    audio[vorbis_name] = [value]
                except Exception as e:
                    print(f"Error setting OGG tag {tag_name}: {str(e)}")
