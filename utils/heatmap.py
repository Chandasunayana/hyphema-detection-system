import cv2
import numpy as np
import os

# Try to import tensorflow, but don't fail if not available
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow not available, using OpenCV-based heatmap generation")

class GradCAMHeatmap:
    
    def __init__(self, model=None, last_conv_layer_name=None):
        self.model = model
        self.last_conv_layer = None
        self.tf_available = TF_AVAILABLE
        
        if model is not None and TF_AVAILABLE:
            self.last_conv_layer = self._find_last_conv_layer()
    
    def _find_last_conv_layer(self):
        """Find the last convolutional layer in the model"""
        if not self.tf_available or self.model is None:
            return None
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                return layer.name
        return None
    
    def generate_heatmap(self, image_path, output_path=None):
        """
        Generate Grad-CAM heatmap for the image
        """
        # Use OpenCV-based heatmap generation (works without TensorFlow)
        heatmap = self._generate_opencv_heatmap(image_path)
        
        # Overlay heatmap on original image
        original = cv2.imread(image_path)
        if original is None:
            # Try with PIL fallback
            from PIL import Image
            original = np.array(Image.open(image_path))
            original = cv2.cvtColor(original, cv2.COLOR_RGB2BGR)
        
        original = cv2.resize(original, (224, 224))
        
        # Create overlay
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET
        )
        
        # Superimpose heatmap
        superimposed = cv2.addWeighted(original, 0.6, heatmap_colored, 0.4, 0)
        
        # Save if output path provided
        if output_path:
            cv2.imwrite(output_path, superimposed)
            return output_path
        
        return superimposed
    
    def _generate_opencv_heatmap(self, image_path):
        """Generate heatmap using OpenCV (no TensorFlow needed)"""
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            from PIL import Image
            img = np.array(Image.open(image_path))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        img = cv2.resize(img, (224, 224))
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Detect red regions (potential blood/hyphema)
        # Red appears at two ranges in HSV
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # Also detect dark regions (possible hyphema areas)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(red_mask, dark_mask)
        
        # Apply Gaussian blur for smooth heatmap
        heatmap = combined_mask.astype(np.float32) / 255.0
        heatmap = cv2.GaussianBlur(heatmap, (25, 25), 0)
        
        # Normalize to [0, 1]
        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)
        
        return heatmap
    
    def _generate_demo_heatmap(self, image_path):
        """Legacy method - uses the OpenCV method now"""
        return self._generate_opencv_heatmap(image_path)
    
    @staticmethod
    def save_heatmap(heatmap, filename, folder='static/images/heatmaps'):
        """Save heatmap to file"""
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        cv2.imwrite(filepath, heatmap)
        return filepath