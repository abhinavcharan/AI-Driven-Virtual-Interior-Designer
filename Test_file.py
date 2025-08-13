# tests/__init__.py
"""Test package for AI Interior Design Assistant"""

# tests/test_app.py
import pytest
import streamlit as st
from PIL import Image
import numpy as np
import sys
import os

# Add the parent directory to the path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import process_image, safe_multiply_uint8, add_furniture_overlay, FURNITURE_DATA, COLOR_PALETTES

class TestImageProcessing:
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        # Create a simple test image
        self.test_image = Image.new('RGB', (100, 100), color='white')
        
    def test_safe_multiply_uint8(self):
        """Test safe multiplication function."""
        img_array = np.array([100, 200, 50], dtype=np.uint8)
        result = safe_multiply_uint8(img_array, 1.5)
        
        assert result.dtype == np.uint8
        assert result[0] == 150  # 100 * 1.5
        assert result[1] == 255  # 200 * 1.5 clipped to 255
        assert result[2] == 75   # 50 * 1.5
        
    def test_process_image_modern_style(self):
        """Test image processing for Modern style."""
        result = process_image(self.test_image, "Modern")
        
        assert isinstance(result, Image.Image)
        assert result.size == self.test_image.size
        
    def test_process_image_all_styles(self):
        """Test image processing for all available styles."""
        styles = ["Modern", "Traditional", "Industrial", "Scandinavian", "Bohemian", "Minimalist"]
        
        for style in styles:
            result = process_image(self.test_image, style)
            assert isinstance(result, Image.Image)
            assert result.size == self.test_image.size
            
    def test_add_furniture_overlay(self):
        """Test furniture overlay functionality."""
        furniture_items = ["🛋 Test sofa", "📚 Test shelf", "💡 Test lamp"]
        result = add_furniture_overlay(self.test_image, furniture_items, "Modern")
        
        assert isinstance(result, Image.Image)
        assert result.size == self.test_image.size

class TestDataStructures:
    
    def test_furniture_data_structure(self):
        """Test that FURNITURE_DATA has correct structure."""
        expected_styles = ["Modern", "Traditional", "Industrial", "Scandinavian", "Bohemian", "Minimalist"]
        
        assert list(FURNITURE_DATA.keys()) == expected_styles
        
        for style, items in FURNITURE_DATA.items():
            assert isinstance(items, list)
            assert len(items) > 0
            for item in items:
                assert isinstance(item, str)
                assert len(item) > 0
                
    def test_color_palettes_structure(self):
        """Test that COLOR_PALETTES has correct structure."""
        expected_styles = ["Modern", "Traditional", "Industrial", "Scandinavian", "Bohemian", "Minimalist"]
        
        assert list(COLOR_PALETTES.keys()) == expected_styles
        
        for style, colors in COLOR_PALETTES.items():
            assert isinstance(colors, list)
            assert len(colors) > 0
            for hex_color, name in colors:
                assert isinstance(hex_color, str)
                assert hex_color.startswith('#')
                assert len(hex_color) == 7  # #RRGGBB format
                assert isinstance(name, str)
                assert len(name) > 0

class TestUtilityFunctions:
    
    def test_hex_to_rgb_conversion(self):
        """Test hex color to RGB conversion logic."""
        hex_color = "#FF5733"
        # Simulate the conversion logic from add_furniture_overlay
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        
        assert rgb == (255, 87, 51)
        assert all(0 <= c <= 255 for c in rgb)

# tests/test_image_processing.py
import pytest
import numpy as np
from PIL import Image
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import process_image, safe_multiply_uint8

class TestAdvancedImageProcessing:
    
    def setup_method(self):
        """Setup more complex test images."""
        # Create test images with different characteristics
        self.white_image = Image.new('RGB', (200, 200), color='white')
        self.black_image = Image.new('RGB', (200, 200), color='black')
        self.colored_image = Image.new('RGB', (200, 200), color=(100, 150, 200))
        
    def test_industrial_style_processing(self):
        """Test Industrial style processing creates grayscale effect."""
        result = process_image(self.colored_image, "Industrial")
        result_array = np.array(result)
        
        # Industrial style should create a grayish image
        assert isinstance(result, Image.Image)
        # Check that the image has been modified
        original_array = np.array(self.colored_image)
        assert not np.array_equal(result_array, original_array)
        
    def test_scandinavian_style_brightness(self):
        """Test Scandinavian style increases brightness."""
        dark_image = Image.new('RGB', (100, 100), color=(50, 50, 50))
        result = process_image(dark_image, "Scandinavian")
        
        original_brightness = np.mean(np.array(dark_image))
        result_brightness = np.mean(np.array(result))
        
        # Should be brighter
        assert result_brightness > original_brightness
        
    def test_minimalist_saturation_reduction(self):
        """Test Minimalist style reduces saturation."""
        # Create a highly saturated image
        saturated_image = Image.new('RGB', (100, 100), color=(255, 0, 0))  # Pure red
        result = process_image(saturated_image, "Minimalist")
        
        # Convert to HSV to check saturation
        original_hsv = saturated_image.convert('HSV')
        result_hsv = result.convert('HSV')
        
        original_sat = np.array(original_hsv)[:, :, 1].mean()
        result_sat = np.array(result_hsv)[:, :, 1].mean()
        
        # Saturation should be reduced
        assert result_sat < original_sat
        
    def test_edge_cases(self):
        """Test edge cases for image processing."""
        # Very small image
        tiny_image = Image.new('RGB', (1, 1), color='white')
        result = process_image(tiny_image, "Modern")
        assert result.size == (1, 1)
        
        # Large multiplication factor
        test_array = np.array([100], dtype=np.uint8)
        result = safe_multiply_uint8(test_array, 10.0)
        assert result[0] == 255  # Should be clipped
        
    def test_blur_effects(self):
        """Test that certain styles apply blur effects."""
        # Create an image with sharp edges
        sharp_image = Image.new('RGB', (100, 100), color='white')
        # Add some black squares to create edges
        pixels = sharp_image.load()
        for i in range(20, 40):
            for j in range(20, 40):
                pixels[i, j] = (0, 0, 0)
                
        # Test styles that should apply blur
        blur_styles = ["Modern", "Traditional", "Bohemian"]
        
        for style in blur_styles:
            result = process_image(sharp_image, style)
            assert isinstance(result, Image.Image)
            # The test passes if no exceptions are raised

if __name__ == "__main__":
    pytest.main([__file__])
