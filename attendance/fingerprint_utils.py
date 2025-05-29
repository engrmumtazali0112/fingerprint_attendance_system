import base64
import numpy as np
import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fingerprint_processor')

class FingerprintProcessor:
    """Utility class for processing fingerprint images and matching"""
    
    @staticmethod
    def process_fingerprint_image(fingerprint_data):
        """
        Process fingerprint data received from scanner
        
        Args:
            fingerprint_data (str): Base64 encoded fingerprint data
            
        Returns:
            bytes: Processed fingerprint template suitable for storage
        """
        try:
            # Decode the base64 fingerprint data
            if not fingerprint_data:
                logger.error("Empty fingerprint data received")
                raise ValueError("No fingerprint data received")
                
            # Decode base64 data
            try:
                binary_data = base64.b64decode(fingerprint_data)
            except Exception as e:
                logger.error(f"Base64 decode error: {str(e)}")
                raise ValueError(f"Invalid fingerprint data format: {str(e)}")
            
            # Convert to numpy array for OpenCV processing
            try:
                # First try to convert to image
                nparr = np.frombuffer(binary_data, np.uint8)
                
                # Check if array is empty
                if nparr.size == 0:
                    logger.error("Decoded fingerprint data is empty")
                    raise ValueError("Empty fingerprint data after decoding")
                
                # Convert to image - if this is image data
                try:
                    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                    
                    # Check if image was properly decoded
                    if img is None or img.size == 0:
                        logger.warning("Could not decode as image, treating as raw template data")
                        # Just use the binary data as-is if it's not a valid image
                        return binary_data
                        
                    # Process the image
                    logger.info(f"Processing fingerprint image of shape {img.shape}")
                    
                    # Apply preprocessing - this is where the error was happening
                    # Ensure img is not empty before applying GaussianBlur
                    if img.size > 0:
                        # Apply Gaussian blur to reduce noise
                        img = cv2.GaussianBlur(img, (5, 5), 0)
                        
                        # Apply thresholding to enhance fingerprint ridges
                        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                    cv2.THRESH_BINARY_INV, 11, 2)
                        
                        # Extract features (simplified feature extraction)
                        # In real implementation, this would use specialized fingerprint algorithms
                        # For now, we'll just compress the image and return it
                        processed_data = cv2.imencode('.png', img)[1].tobytes()
                        
                        logger.info("Fingerprint processed successfully")
                        return processed_data
                    else:
                        logger.error("Empty image after decoding")
                        raise ValueError("Empty fingerprint image")
                        
                except Exception as e:
                    logger.warning(f"Image processing error, using raw data: {str(e)}")
                    # Fall back to using the raw binary data
                    return binary_data
                    
            except Exception as e:
                logger.error(f"Error processing fingerprint: {str(e)}")
                raise ValueError(f"Failed to process fingerprint: {str(e)}")
                
        except Exception as e:
            logger.error(f"Fingerprint processing error: {str(e)}")
            raise ValueError(f"Error processing fingerprint: {str(e)}")
    
    @staticmethod
    def match_fingerprint(fingerprint_data):
        """
        Match a fingerprint against the database
        
        Args:
            fingerprint_data (bytes): Processed fingerprint template to match
            
        Returns:
            tuple: (is_match, student_id, fingerprint_id)
        """
        from .models import FingerPrint
        
        try:
            # Get all fingerprints from the database
            all_fingerprints = FingerPrint.objects.all()
            
            # This is a simplified matching algorithm
            # In a real application, you would use a proper fingerprint matching algorithm
            
            # For demonstration, we'll use a simple hash comparison
            # In reality, you should use a specialized fingerprint matching library
            
            # Convert incoming fingerprint to a hash for comparison
            import hashlib
            incoming_hash = hashlib.md5(fingerprint_data).hexdigest()
            
            logger.info(f"Attempting to match fingerprint with hash: {incoming_hash[:8]}...")
            
            # Try to find a match
            for fp in all_fingerprints:
                stored_hash = hashlib.md5(fp.fingerprint_data).hexdigest()
                
                # Simple hash comparison (NOT how real fingerprint matching works!)
                # In a real implementation, you would:
                # 1. Extract features from both fingerprints
                # 2. Compare the features using a specialized algorithm
                # 3. Determine if they match based on a similarity threshold
                
                # For demo purposes, we'll just check if the hashes are similar
                # (first 8 chars match - this is ONLY for demo purposes)
                if incoming_hash[:8] == stored_hash[:8]:
                    logger.info(f"Found matching fingerprint for student {fp.student.id}")
                    return True, fp.student.id, fp.id
            
            logger.warning("No matching fingerprint found")
            return False, None, None
            
        except Exception as e:
            logger.error(f"Error matching fingerprint: {str(e)}")
            raise ValueError(f"Failed to match fingerprint: {str(e)}")