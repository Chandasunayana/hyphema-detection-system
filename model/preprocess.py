import cv2
import numpy as np
from PIL import Image
import tensorflow as tf

class ImagePreprocessor:
    
    @staticmethod
    def preprocess_image(image_path, target_size=(224, 224)):
        """
        Preprocess image for model input
        """
        # Read image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply preprocessing steps
        img = ImagePreprocessor.resize_image(img, target_size)
        img = ImagePreprocessor.enhance_contrast(img)
        img = ImagePreprocessor.denoise_image(img)
        img = ImagePreprocessor.normalize_image(img)
        
        return img
    
    @staticmethod
    def resize_image(img, target_size):
        """Resize image to target size"""
        return cv2.resize(img, target_size)
    
    @staticmethod
    def enhance_contrast(img):
        """Apply contrast enhancement for better feature detection"""
        # Convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge back
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    @staticmethod
    def denoise_image(img):
        """Apply denoising"""
        return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    @staticmethod
    def normalize_image(img):
        """Normalize pixel values to [0, 1]"""
        return img.astype(np.float32) / 255.0
    
    @staticmethod
    def extract_eye_region(img):
        """
        Extract eye region using basic eye detection
        Note: In production, use more sophisticated eye detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Use Viola-Jones detector (simplified)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(eyes) > 0:
            # Get the largest eye detected
            x, y, w, h = max(eyes, key=lambda rect: rect[2] * rect[3])
            return img[y:y+h, x:x+w]
        
        return img  # Return original if no eye detected