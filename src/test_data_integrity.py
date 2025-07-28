"""
Phase 1: Unit & Integration Testing - Step 1
Data Preprocessing and Integrity Validation
"""

import json
import os
from pathlib import Path
from datetime import datetime
import unittest
from typing import Dict, List, Any

class TestDataIntegrity(unittest.TestCase):
    """Test data loading and integrity validation"""
    
    def setUp(self):
        """Set up test data paths"""
        self.project_root = Path(__file__).parent.parent
        self.assets_dir = self.project_root / 'assets'
        self.est1_metadata = self.assets_dir / 'images_EST-1.json'
        self.est2_metadata = self.assets_dir / 'images_EST-2.json'
        self.est1_images = self.assets_dir / 'images_EST-1'
        self.est2_images = self.assets_dir / 'images_EST-2'
    
    def test_file_existence(self):
        """Test that all required files exist"""
        self.assertTrue(self.est1_metadata.exists(), "Missing images_EST-1.json")
        self.assertTrue(self.est2_metadata.exists(), "Missing images_EST-2.json")
        self.assertTrue(self.est1_images.exists(), "Missing images_EST-1 directory")
        self.assertTrue(self.est2_images.exists(), "Missing images_EST-2 directory")
    
    def test_metadata_loading(self):
        """Test loading all metadata and basic structure"""
        try:
            with open(self.est1_metadata, 'r', encoding='utf-8') as f:
                est1_data = json.load(f)
            with open(self.est2_metadata, 'r', encoding='utf-8') as f:
                est2_data = json.load(f)
            
            # Check structure
            self.assertIn('images', est1_data, "EST-1 missing 'images' key")
            self.assertIn('images', est2_data, "EST-2 missing 'images' key")
            
            return est1_data, est2_data
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON format: {e}")
    
    def test_total_image_count(self):
        """Test total image count matches expected 270 (170 + 100)"""
        est1_data, est2_data = self.test_metadata_loading()
        
        est1_images = len(est1_data['images'])
        est2_images = len(est2_data['images'])
        total = est1_images + est2_images
        
        print(f"EST-1: {est1_images} images")
        print(f"EST-2: {est2_images} images")
        print(f"Total: {total} images")
        
        self.assertEqual(est1_images, 170, "EST-1 should have 170 images")
        self.assertEqual(est2_images, 100, "EST-2 should have 100 images")
        self.assertEqual(total, 270, "Total should be 270 images")
    
    def test_date_parsing(self):
        """Test date parsing for sample images"""
        est1_data, _ = self.test_metadata_loading()
        
        # Get sample images for date testing
        sample_keys = list(est1_data['images'].keys())[:10]
        print(f"Testing date parsing for sample images: {sample_keys}")
        
        for key in sample_keys:
            image_data = est1_data['images'][key]
            shooting_str = image_data.get('image_shooting', '')
            
            # Parse datetime
            try:
                dt = datetime.strptime(shooting_str, "%Y:%m:%d %H:%M:%S")
                
                # Check date range (June-July 2025)
                self.assertEqual(dt.year, 2025, f"Year should be 2025: {dt}")
                self.assertIn(dt.month, [6, 7], f"Month should be June/July 2025: {dt}")
                
                # Ensure it's not the current system date
                today = datetime.now()
                self.assertNotEqual(dt.date(), today.date(), 
                                  f"Parsed date {dt} should not be current system date")
                
            except ValueError as e:
                self.fail(f"Invalid date format for {key}: {shooting_str} - {e}")
    
    def test_detection_data_integrity(self):
        """Test detection data structure and validation"""
        est1_data, est2_data = self.test_metadata_loading()
        
        # Test sample detections
        test_cases = [
            (est1_data, "651424718_16424f3e-5e45-4fae-b5d0-82957b0badf0.jpg"),
            (est2_data, "651433349_9cfb30dd-ff00-454d-8c4c-74b4e4dea44a.jpg")
        ]
        
        for data, image_id in test_cases:
            if image_id in data['images']:
                image_data = data['images'][image_id]
                detections = image_data.get('detections', [])
                
                print(f"Testing detections for {image_id}: {len(detections)} total")
                self.assertGreater(len(detections), 0, f"Should have detections in {image_id}")
                
                for detection in detections:
                    # Validate bounding box format
                    if 'bounding_box_start_x' in detection:
                        self.assertIsInstance(detection['bounding_box_start_x'], float)
                        self.assertIsInstance(detection['bounding_box_end_x'], float)
                        self.assertIsInstance(detection['bounding_box_start_y'], float)
                        self.assertIsInstance(detection['bounding_box_end_y'], float)
                        
                        # Check bounds (0-1 normalized)
                        for coord in ['bounding_box_start_x', 'bounding_box_end_x', 
                                    'bounding_box_start_y', 'bounding_box_end_y']:
                            if coord in detection:
                                self.assertGreaterEqual(float(detection[coord]), 0)
                                self.assertLessEqual(float(detection[coord]), 1)
    
    def test_image_file_associations(self):
        """Test that all image metadata have corresponding files"""
        est1_data, est2_data = self.test_metadata_loading()
        
        # Check EST-1 - keys match filenames directly
        missing_est1 = []
        for image_filename in est1_data['images']:
            image_path = self.est1_images / image_filename
            if not image_path.exists():
                missing_est1.append(image_filename)
        
        # Check EST-2 - keys match filenames directly
        missing_est2 = []
        for image_filename in est2_data['images']:
            image_path = self.est2_images / image_filename
            if not image_path.exists():
                missing_est2.append(image_filename)
        
        print(f"Valid EST-1 files: {len(est1_data['images']) - len(missing_est1)}")
        print(f"Valid EST-2 files: {len(est2_data['images']) - len(missing_est2)}")
        print(f"Missing EST-1 files: {len(missing_est1)}")
        print(f"Missing EST-2 files: {len(missing_est2)}")
        
        # Allow up to 5% missing files due to data cleanup
        max_missing_est1 = max(1, len(est1_data['images']) * 0.05)
        max_missing_est2 = max(1, len(est2_data['images']) * 0.05)
        
        self.assertLessEqual(len(missing_est1), max_missing_est1, 
                           f"Too many missing EST-1 files: {len(missing_est1)}")
        self.assertLessEqual(len(missing_est2), max_missing_est2, 
                           f"Too many missing EST-2 files: {len(missing_est2)}")
    
    def test_metadata_key_presence(self):
        """Test required keys are present in metadata"""
        est1_data, est2_data = self.test_metadata_loading()
        
        required_keys = ['photo_id', 'image_shooting', 'detections']
        
        for dataset_name, data in [('EST-1', est1_data), ('EST-2', est2_data)]:
            image_keys = list(data['images'].keys())[:5]  # Sample first 5
            
            for image_key in image_keys:
                image_data = data['images'][image_key]
                
                for key in required_keys:
                    self.assertIn(key, image_data, 
                                f"{key} missing in {dataset_name} image {image_key}")

def run_data_integrity_tests():
    """Run all data integrity tests and report results"""
    print("🔍 SecuriSite-IA: Data Integrity Testing")
    print("=" * 50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataIntegrity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All data integrity tests passed!")
        print(f"Validated {result.testsRun} data integrity assertions")
    else:
        print(f"❌ {len(result.failures)} test failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == '__main__':
    run_data_integrity_tests()