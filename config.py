"""
Configuration file for Computer Vision Detection System
Centralized configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for detection system"""
    
    # Default paths
    IMAGES_DIR = "images"
    OUTPUT_DIR = "results"
    OUTPUT_IMAGES_DIR = "output_images"
    LOGS_DIR = "logs"
    
    # Detection thresholds
    PERSON_CONFIDENCE_THRESHOLD = 0.3
    TEXT_CONFIDENCE_THRESHOLD = 0.1
    MIN_TEXT_SIZE = (10, 10)  # (width, height) in pixels
    
    # Model configuration
    PERSON_MODEL = "yolov8n.pt"  # Options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    TEXT_LANGUAGES = ['en']  # Add more languages as needed
    USE_GPU = False  # Set to True if GPU available
    
    # Image processing
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    MAX_IMAGE_SIZE = (4096, 4096)  # Skip larger images
    MIN_IMAGE_SIZE = (100, 100)
    
    # Output configuration
    SAVE_ANNOTATED_IMAGES = True
    SAVE_JSON_RESULTS = True
    SAVE_STATISTICS = True
    JSON_INDENT = 2  # Pretty print JSON
    
    # Visualization colors (BGR format)
    PERSON_BOX_COLOR = (255, 0, 0)  # Blue
    TEXT_BOX_COLOR = (0, 255, 0)    # Green
    BOX_THICKNESS = 2
    FONT_SCALE = 0.5
    FONT_THICKNESS = 1
    
    # Logging configuration
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = "detection.log"
    
    # Performance settings
    BATCH_SIZE = 1
    NUM_WORKERS = 0
    
    @classmethod
    def load_from_file(cls, filepath: str) -> None:
        """Load configuration from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
                for key, value in config_dict.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
    
    @classmethod
    def save_to_file(cls, filepath: str) -> None:
        """Save current configuration to JSON file"""
        config_dict = {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and isinstance(getattr(cls, key), (str, int, float, bool, list, dict, tuple))
        }
        
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration values"""
        errors = []
        
        if not 0.0 <= cls.PERSON_CONFIDENCE_THRESHOLD <= 1.0:
            errors.append("PERSON_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if not 0.0 <= cls.TEXT_CONFIDENCE_THRESHOLD <= 1.0:
            errors.append("TEXT_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if not cls.PERSON_MODEL.endswith('.pt'):
            errors.append("PERSON_MODEL must be a .pt file")
        
        if not cls.TEXT_LANGUAGES:
            errors.append("TEXT_LANGUAGES must not be empty")
        
        if cls.BOX_THICKNESS < 1:
            errors.append("BOX_THICKNESS must be >= 1")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True


# Preset configurations
class PresetConfig:
    """Preset configurations for different use cases"""
    
    @staticmethod
    def high_accuracy() -> Dict[str, Any]:
        """High accuracy configuration (slower, fewer false positives)"""
        return {
            "PERSON_CONFIDENCE_THRESHOLD": 0.5,
            "TEXT_CONFIDENCE_THRESHOLD": 0.3,
            "PERSON_MODEL": "yolov8m.pt",
            "USE_GPU": True,
        }
    
    @staticmethod
    def high_speed() -> Dict[str, Any]:
        """High speed configuration (faster, more false positives)"""
        return {
            "PERSON_CONFIDENCE_THRESHOLD": 0.2,
            "TEXT_CONFIDENCE_THRESHOLD": 0.05,
            "PERSON_MODEL": "yolov8n.pt",
            "USE_GPU": False,
        }
    
    @staticmethod
    def balanced() -> Dict[str, Any]:
        """Balanced configuration (default)"""
        return {
            "PERSON_CONFIDENCE_THRESHOLD": 0.3,
            "TEXT_CONFIDENCE_THRESHOLD": 0.1,
            "PERSON_MODEL": "yolov8n.pt",
            "USE_GPU": False,
        }
    
    @staticmethod
    def gpu_enabled() -> Dict[str, Any]:
        """GPU-enabled configuration"""
        return {
            "PERSON_CONFIDENCE_THRESHOLD": 0.3,
            "TEXT_CONFIDENCE_THRESHOLD": 0.1,
            "PERSON_MODEL": "yolov8s.pt",
            "USE_GPU": True,
        }
    
    @staticmethod
    def apply_preset(preset_name: str) -> None:
        """Apply a preset configuration to Config class"""
        presets = {
            "high_accuracy": PresetConfig.high_accuracy(),
            "high_speed": PresetConfig.high_speed(),
            "balanced": PresetConfig.balanced(),
            "gpu_enabled": PresetConfig.gpu_enabled(),
        }
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")
        
        preset = presets[preset_name]
        for key, value in preset.items():
            setattr(Config, key, value)


if __name__ == "__main__":
    # Example usage
    print("Configuration System")
    print("=" * 50)
    
    # Show default configuration
    print("\nDefault Configuration:")
    for key, value in Config.get_all().items():
        print(f"  {key}: {value}")
    
    # Validate configuration
    print("\nValidating configuration...")
    if Config.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
    
    # Save configuration
    Config.save_to_file("default_config.json")
    print("\nConfiguration saved to: default_config.json")
    
    # Apply presets
    print("\n" + "=" * 50)
    print("Available Presets:")
    for preset in ["high_accuracy", "high_speed", "balanced", "gpu_enabled"]:
        print(f"  - {preset}")
