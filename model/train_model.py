"""
Training script that works with your existing folder structure
Your structure: datasets/normal_eye_images/
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from sklearn.model_selection import train_test_split
import cv2
from PIL import Image
import random

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 30
NUM_CLASSES = 5
CLASS_NAMES = ['normal', 'mild', 'moderate', 'severe', 'critical']

def create_augmented_dataset_from_normal():
    """
    Create augmented variations from normal eye images to simulate different severity levels
    This creates synthetic hyphema images for training
    """
    
    print("📁 Creating augmented dataset from your normal eye images...")
    
    normal_dir = 'datasets/normal_eye_images'
    
    if not os.path.exists(normal_dir):
        print("❌ Please add your eye images to: datasets/normal_eye_images/")
        return False
    
    # Get all normal images
    normal_images = []
    for file in os.listdir(normal_dir):
        if file.endswith(('.jpg', '.png', '.jpeg')):
            normal_images.append(os.path.join(normal_dir, file))
    
    if len(normal_images) == 0:
        print("❌ No images found in datasets/normal_eye_images/")
        return False
    
    print(f"✅ Found {len(normal_images)} normal eye images")
    
    # Create directories for each severity
    for class_name in CLASS_NAMES:
        os.makedirs(f'datasets/{class_name}', exist_ok=True)
    
    # Copy normal images to normal folder
    for i, img_path in enumerate(normal_images):
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, IMG_SIZE)
            cv2.imwrite(f'datasets/normal/normal_{i:03d}.jpg', img)
    
    print("✅ Copied normal images to datasets/normal/")
    
    # Create synthetic hyphema images for other classes
    print("\n🎨 Creating synthetic hyphema images for training...")
    
    for severity, class_name in enumerate(['mild', 'moderate', 'severe', 'critical'], start=1):
        severity_level = severity  # 1=mild, 2=moderate, 3=severe, 4=critical
        red_intensity = severity_level * 0.25  # 0.25, 0.5, 0.75, 1.0
        
        print(f"   Creating {class_name} images (intensity: {red_intensity})...")
        
        for i, normal_img_path in enumerate(normal_images[:20]):  # Use first 20 normal images
            img = cv2.imread(normal_img_path)
            if img is None:
                continue
            
            img = cv2.resize(img, IMG_SIZE)
            
            # Add red overlay to simulate hyphema
            # Blood typically pools at the bottom of the eye
            h, w = img.shape[:2]
            blood_height = int(h * 0.3 * red_intensity)
            
            for y in range(h - blood_height, h):
                for x in range(w):
                    # Add red tint with gradient
                    intensity = 1.0 - (y - (h - blood_height)) / blood_height if blood_height > 0 else 0
                    img[y, x] = [
                        min(255, img[y, x, 0] + int(80 * intensity * red_intensity)),
                        max(0, img[y, x, 1] - int(40 * intensity * red_intensity)),
                        max(0, img[y, x, 2] - int(40 * intensity * red_intensity))
                    ]
            
            # Save synthetic image
            cv2.imwrite(f'datasets/{class_name}/{class_name}_{i:03d}.jpg', img)
    
    print("\n✅ Dataset creation complete!")
    return True

def load_dataset():
    """Load and prepare dataset from your folder structure"""
    
    X = []  # Images
    y = []  # Labels
    
    # Map folder names to labels
    folder_to_label = {
        'normal': 0,
        'mild': 1,
        'moderate': 2,
        'severe': 3,
        'critical': 4
    }
    
    for folder_name, label in folder_to_label.items():
        folder_path = os.path.join('datasets', folder_name)
        
        if not os.path.exists(folder_path):
            print(f"⚠️ Folder not found: {folder_path}")
            continue
        
        images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        for img_file in images:
            img_path = os.path.join(folder_path, img_file)
            try:
                img = cv2.imread(img_path)
                if img is None:
                    continue
                img = cv2.resize(img, IMG_SIZE)
                img = img.astype(np.float32) / 255.0
                X.append(img)
                y.append(label)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
    
    return np.array(X), np.array(y)

def create_model():
    """Create CNN model for hyphema detection"""
    
    model = models.Sequential([
        # First Convolutional Block
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Second Convolutional Block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Third Convolutional Block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Fourth Convolutional Block
        layers.Conv2D(256, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.25),
        
        # Fully Connected Layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    return model

def train_model():
    """Main training function"""
    
    print("=" * 60)
    print("🚀 Hyphema Detection Model Training")
    print("=" * 60)
    
    # Step 1: Create augmented dataset from your normal images
    print("\n📊 Step 1: Preparing dataset...")
    success = create_augmented_dataset_from_normal()
    
    if not success:
        print("\n❌ Please add your eye images to: datasets/normal_eye_images/")
        print("   Then run this script again.")
        return
    
    # Step 2: Load the dataset
    print("\n📊 Step 2: Loading dataset...")
    X, y = load_dataset()
    
    if len(X) == 0:
        print("❌ No images loaded!")
        return
    
    print(f"✅ Loaded {len(X)} images")
    
    # Count images per class
    unique, counts = np.unique(y, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"   {CLASS_NAMES[label]}: {count} images")
    
    # Step 3: Split data
    print("\n📊 Step 3: Splitting data...")
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)
    print(f"   Training: {len(X_train)} images")
    print(f"   Validation: {len(X_val)} images")
    
    # Step 4: Create model
    print("\n📊 Step 4: Creating model...")
    model = create_model()
    model.summary()
    
    # Step 5: Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Step 6: Train model
    print("\n📊 Step 5: Training model...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1
    )
    
    # Step 7: Save model
    os.makedirs('model', exist_ok=True)
    model.save('model/hyphema_model.h5')
    print("\n✅ Model saved to model/hyphema_model.h5")
    
    # Step 8: Print results
    print("\n" + "=" * 60)
    print("📈 Training Results:")
    print("=" * 60)
    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    print(f"Final Training Accuracy: {final_train_acc:.4f}")
    print(f"Final Validation Accuracy: {final_val_acc:.4f}")
    
    # Step 9: Test prediction on a sample
    print("\n📊 Step 6: Testing model...")
    test_idx = random.randint(0, len(X_val) - 1)
    test_img = X_val[test_idx:test_idx+1]
    true_label = y_val[test_idx]
    
    prediction = model.predict(test_img, verbose=0)
    predicted_class = np.argmax(prediction[0])
    confidence = np.max(prediction[0])
    
    print(f"\n🎯 Test Prediction:")
    print(f"   True Label: {CLASS_NAMES[true_label]}")
    print(f"   Predicted: {CLASS_NAMES[predicted_class]}")
    print(f"   Confidence: {confidence:.2%}")
    
    return model, history

def test_single_image(image_path):
    """Test a single image with the trained model"""
    
    if not os.path.exists('model/hyphema_model.h5'):
        print("❌ Model not found. Please train first!")
        return
    
    # Load model
    model = tf.keras.models.load_model('model/hyphema_model.h5')
    
    # Load and preprocess image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not load image: {image_path}")
        return
    
    img = cv2.resize(img, IMG_SIZE)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Predict
    prediction = model.predict(img, verbose=0)
    predicted_class = np.argmax(prediction[0])
    confidence = np.max(prediction[0])
    
    severity_labels = {
        0: {"label": "Normal", "color": "green", "description": "Eye appears healthy"},
        1: {"label": "Mild", "color": "yellow", "description": "Minor bleeding detected"},
        2: {"label": "Moderate", "color": "orange", "description": "Moderate bleeding visible"},
        3: {"label": "Severe", "color": "red", "description": "Significant bleeding detected"},
        4: {"label": "Critical", "color": "darkred", "description": "Emergency - Immediate attention required"}
    }
    
    print("\n" + "=" * 50)
    print("🔍 PREDICTION RESULT")
    print("=" * 50)
    print(f"Prediction: {'Hyphema Detected' if predicted_class > 0 else 'Normal Eye'}")
    print(f"Severity Grade: {predicted_class} - {severity_labels[predicted_class]['label']}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Description: {severity_labels[predicted_class]['description']}")
    print("=" * 50)
    
    return predicted_class, confidence

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("👁️  Hyphema Detection System - Training Module")
    print("=" * 60)
    
    # Train the model
    model, history = train_model()
    
    # Optional: Test on a sample image
    print("\n💡 To test on your own image, run:")
    print("   from train_with_your_structure import test_single_image")
    print("   test_single_image('path/to/your/eye_image.jpg')")