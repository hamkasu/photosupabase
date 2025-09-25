# photovault/services/app_storage_service.py

import os
import logging
from typing import Tuple, Optional, BinaryIO

logger = logging.getLogger(__name__)

class AppStorageService:
    """
    App Storage service for PhotoVault
    Provides a fallback mechanism when Replit Object Storage is not available
    """
    
    def __init__(self):
        self._available = False
        try:
            # Check if replit-object-storage is available
            import replit_object_storage
            self._storage = replit_object_storage
            self._available = True
            logger.info("Replit Object Storage is available")
        except ImportError:
            logger.info("Replit Object Storage not available, using local fallback")
    
    def is_available(self) -> bool:
        """Check if app storage is available"""
        return self._available
    
    def upload_file(self, file: BinaryIO, filename: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Upload file to app storage
        
        Args:
            file: File-like object to upload
            filename: Name of the file
            user_id: Optional user ID for organizing files
            
        Returns:
            Tuple of (success, path_or_error_message)
        """
        if not self._available:
            return False, "App storage not available"
        
        try:
            # Create storage path
            if user_id:
                storage_path = f"users/{user_id}/{filename}"
            else:
                storage_path = f"uploads/{filename}"
            
            # Upload to Replit Object Storage
            self._storage.upload_file(file, storage_path)
            return True, storage_path
        except Exception as e:
            logger.error(f"Failed to upload file to app storage: {str(e)}")
            return False, str(e)
    
    def download_file(self, file_path: str) -> Tuple[bool, bytes]:
        """
        Download file from app storage
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            Tuple of (success, file_content_or_error_message)
        """
        if not self._available:
            return False, b"App storage not available"
        
        try:
            content = self._storage.download_file(file_path)
            return True, content
        except Exception as e:
            logger.error(f"Failed to download file from app storage: {str(e)}")
            return False, str(e).encode()
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete file from app storage
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            Tuple of (success, error_message_or_empty)
        """
        if not self._available:
            return False, "App storage not available"
        
        try:
            self._storage.delete_file(file_path)
            return True, ""
        except Exception as e:
            logger.error(f"Failed to delete file from app storage: {str(e)}")
            return False, str(e)
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists in app storage
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            True if file exists, False otherwise
        """
        if not self._available:
            return False
        
        try:
            return self._storage.file_exists(file_path)
        except Exception as e:
            logger.error(f"Failed to check file existence in app storage: {str(e)}")
            return False
    
    def create_thumbnail(self, file_path: str, thumbnail_size: Tuple[int, int] = (150, 150)) -> Tuple[bool, str]:
        """
        Create thumbnail for image in app storage
        
        Args:
            file_path: Path to the source image
            thumbnail_size: Size of the thumbnail (width, height)
            
        Returns:
            Tuple of (success, thumbnail_path_or_error_message)
        """
        if not self._available:
            return False, "App storage not available"
        
        try:
            # For now, we'll implement a basic version
            # In a full implementation, this would download the image, create thumbnail, and upload it back
            thumbnail_path = file_path.replace('.', f'_thumb_{thumbnail_size[0]}x{thumbnail_size[1]}.')
            # This is a placeholder - actual implementation would create the thumbnail
            return True, thumbnail_path
        except Exception as e:
            logger.error(f"Failed to create thumbnail in app storage: {str(e)}")
            return False, str(e)
    
    def get_image_info(self, file_path: str) -> Tuple[bool, dict]:
        """
        Get image information from app storage
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Tuple of (success, image_info_dict_or_error_message)
        """
        if not self._available:
            return False, {"error": "App storage not available"}
        
        try:
            # This would typically get image metadata
            # For now, return basic info
            return True, {
                "path": file_path,
                "available": True
            }
        except Exception as e:
            logger.error(f"Failed to get image info from app storage: {str(e)}")
            return False, {"error": str(e)}

# Create singleton instance
app_storage = AppStorageService()