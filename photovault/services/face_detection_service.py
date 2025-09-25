# photovault/services/face_detection_service.py

import logging
import os
from typing import List, Dict, Tuple, Optional
from photovault.models import Photo, Person, PhotoPerson, db

logger = logging.getLogger(__name__)

class FaceDetectionService:
    """
    Face detection service for PhotoVault
    Provides face detection and recognition capabilities
    """
    
    def __init__(self):
        self._available = False
        try:
            # Check if OpenCV is available for face detection
            import cv2
            self._cv2 = cv2
            self._available = True
            logger.info("Face detection service is available")
        except ImportError:
            logger.warning("OpenCV not available, face detection disabled")
    
    def is_available(self) -> bool:
        """Check if face detection is available"""
        return self._available
    
    def get_face_detection_stats(self, user_id: int) -> Dict:
        """
        Get face detection statistics for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with face detection statistics
        """
        try:
            # Get statistics from database
            total_photos = Photo.query.filter_by(user_id=user_id).count()
            photos_with_faces = db.session.query(Photo).join(PhotoPerson).filter(
                Photo.user_id == user_id
            ).distinct().count()
            
            verified_tags = PhotoPerson.query.join(Photo).filter(
                Photo.user_id == user_id,
                PhotoPerson.verified == True
            ).count()
            
            unverified_tags = PhotoPerson.query.join(Photo).filter(
                Photo.user_id == user_id,
                PhotoPerson.verified == False
            ).count()
            
            unique_people = Person.query.filter_by(user_id=user_id).count()
            
            return {
                'total_photos': total_photos,
                'photos_with_faces': photos_with_faces,
                'verified_tags': verified_tags,
                'unverified_tags': unverified_tags,
                'unique_people': unique_people,
                'detection_available': self._available
            }
        except Exception as e:
            logger.error(f"Error getting face detection stats: {str(e)}")
            return {
                'total_photos': 0,
                'photos_with_faces': 0,
                'verified_tags': 0,
                'unverified_tags': 0,
                'unique_people': 0,
                'detection_available': False,
                'error': str(e)
            }
    
    def detect_faces_in_photo(self, photo_path: str) -> List[Dict]:
        """
        Detect faces in a photo
        
        Args:
            photo_path: Path to the photo file
            
        Returns:
            List of face detection results
        """
        if not self._available:
            return []
        
        try:
            # Load the image
            image = self._cv2.imread(photo_path)
            if image is None:
                logger.warning(f"Could not load image: {photo_path}")
                return []
            
            # Convert to grayscale for face detection
            gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
            
            # Load face classifier (using Haar cascades)
            face_cascade_path = self._cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = self._cv2.CascadeClassifier(face_cascade_path)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Convert to list of dictionaries
            face_results = []
            for i, (x, y, w, h) in enumerate(faces):
                face_results.append({
                    'id': i,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 0.8  # Placeholder confidence
                })
            
            logger.info(f"Detected {len(face_results)} faces in {photo_path}")
            return face_results
            
        except Exception as e:
            logger.error(f"Error detecting faces in {photo_path}: {str(e)}")
            return []
    
    def process_photo_for_faces(self, photo_id: int) -> bool:
        """
        Process a photo to detect and store face data
        
        Args:
            photo_id: ID of the photo to process
            
        Returns:
            True if processing was successful
        """
        if not self._available:
            return False
        
        try:
            photo = Photo.query.get(photo_id)
            if not photo:
                logger.warning(f"Photo {photo_id} not found")
                return False
            
            # Get the photo file path
            photo_path = photo.file_path
            if not os.path.exists(photo_path):
                logger.warning(f"Photo file not found: {photo_path}")
                return False
            
            # Detect faces
            faces = self.detect_faces_in_photo(photo_path)
            
            if faces:
                # Store face detection results
                for face in faces:
                    # Check if this face region already exists
                    existing = PhotoPerson.query.filter_by(
                        photo_id=photo_id,
                        face_x=face['x'],
                        face_y=face['y'],
                        face_width=face['width'],
                        face_height=face['height']
                    ).first()
                    
                    if not existing:
                        # Create new face detection record
                        photo_person = PhotoPerson(
                            photo_id=photo_id,
                            person_id=None,  # Will be filled when user identifies
                            face_x=face['x'],
                            face_y=face['y'],
                            face_width=face['width'],
                            face_height=face['height'],
                            confidence=face['confidence'],
                            verified=False
                        )
                        db.session.add(photo_person)
                
                db.session.commit()
                logger.info(f"Processed {len(faces)} faces for photo {photo_id}")
                return True
            
            return True  # No faces found, but processing was successful
            
        except Exception as e:
            logger.error(f"Error processing photo {photo_id} for faces: {str(e)}")
            db.session.rollback()
            return False
    
    def tag_face(self, photo_person_id: int, person_id: int) -> bool:
        """
        Tag a detected face with a person
        
        Args:
            photo_person_id: ID of the PhotoPerson record
            person_id: ID of the Person to tag
            
        Returns:
            True if tagging was successful
        """
        try:
            photo_person = PhotoPerson.query.get(photo_person_id)
            if not photo_person:
                return False
            
            photo_person.person_id = person_id
            photo_person.verified = True
            db.session.commit()
            
            logger.info(f"Tagged face {photo_person_id} with person {person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tagging face {photo_person_id}: {str(e)}")
            db.session.rollback()
            return False

# Create singleton instance
face_detection_service = FaceDetectionService()