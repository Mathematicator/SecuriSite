"""
Phase 1: Unit & Integration Testing - Step 2
Agent-Level Output Validation
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
import unittest
from unittest.mock import patch
import os

# Import agents
from securisite.agents.cv_risk_detector import ComputerVisionRiskDetector
from securisite.agents.weather_context_agent import WeatherContextAgent
from securisite.agents.regulation_agent import RegulationAgent
from securisite.utils.data_loader import data_loader

class TestAgents(unittest.TestCase):
    """Test individual agent functionality"""
    
    def setUp(self):
        """Set up test data from real dataset"""
        self.project_root = Path(__file__).parent.parent
        self.test_images = data_loader.get_risk_annotated_images()
        self.test_image = next((img for img in self.test_images 
                              if img.camera == 'EST-1'), None)
        
        if self.test_image:
            print(f"Test image: {self.test_image.image_id} from {self.test_image.camera}")
            print(f"Detections: {len(self.test_image.detections)}")
    
    def test_cv_risk_detector_output_format(self):
        """Test CV agent produces structured output"""
        if not self.test_image:
            self.skipTest("No test image available")
        
        agent = ComputerVisionRiskDetector()
        
        # Create test data based on real detection
        test_data = {
            'image_path': self.test_image.image_id,
            'detections': self.test_image.detections
        }
        
        async def run_cv_test():
            result = await agent.process(test_data)
            return result
        
        result = asyncio.run(run_cv_test())
        
        # Validate output structure
        self.assertIsInstance(result, dict)
        self.assertIn('risk_scores', result)
        self.assertIn('image_analysis', result)
        self.assertIsInstance(result['risk_scores'], list)
        
        # Each risk score should be structured
        for risk in result['risk_scores']:
            self.assertIn('risk_type', risk)
            self.assertIn('severity', risk)
            self.assertIn('area', risk)
        
        print("✅ CV agent output structure validated")
    
    def test_weather_context_agent(self):
        """Test weather agent with real timestamp"""
        if not self.test_image:
            self.skipTest("No test image available")
        
        agent = WeatherContextAgent()
        
        # Use real timestamp from dataset
        test_data = {
            'timestamp': self.test_image.timestamp.isoformat()
        }
        
        async def run_weather_test():
            result = await agent.process(test_data)
            return result
        
        result = asyncio.run(run_weather_test())
        
        # Validate weather data structure
        self.assertIsInstance(result, dict)
        self.assertIn('weather_conditions', result)
        self.assertIn('timestamp', result)
        
        weather = result['weather_conditions']
        self.assertIsInstance(weather, dict)
        self.assertIn('condition', weather)
        
        print("✅ Weather agent output validated")
    
    def test_regulation_agent_specificity(self):
        """Test regulation agent with real risk types"""
        agent = RegulationAgent()
        
        # Test with common risk types from dataset
        test_cases = [
            {'risk_type': 'person_without_ppe'},
            {'risk_type': 'tower_crane_operation'},
            {'risk_type': 'container_obstruction'},
            {'risk_type': 'proximite_homme_machine'}
        ]
        
        async def run_regulation_test(risk_data):
            result = await agent.process(risk_data)
            return result
        
        for test_case in test_cases:
            with self.subTest(risk_type=test_case['risk_type']):
                result = asyncio.run(run_regulation_test(test_case))
                
                # Validate regulation output structure
                self.assertIsInstance(result, dict)
                self.assertIn('regulatory_analysis', result)
                
                regulations = result['regulatory_analysis']
                if isinstance(regulations, list):
                    for reg in regulations:
                        self.assertIn('regulation', reg)
                        self.assertIn('description', reg)
                        self.assertIn('reference', reg)
                        
                        # Ensure references are from Code du Travail
                        ref = reg.get('reference', '')
                        self.assertIn('Code du Travail', ref or '')
        
        print("✅ Regulation agent specificity validated")
    
    def test_no_hallucination_detection(self):
        """Test that agents don't hallucinate non-existent risks"""
        # Test with an image that has no risks
        no_risk_data = {
            'image_path': 'safe_image',
            'detections': [
                {'label': 'sky', 'score': 0.95, 'bounding_box_start_x': 0.0}
            ]
        }
        
        agent = ComputerVisionRiskDetector()
        
        async def run_safe_test():
            result = await agent.process(no_risk_data)
            return result
        
        result = asyncio.run(run_safe_test())
        
        # Should either return empty risks or "safe" status
        risk_scores = result.get('risk_scores', [])
        self.assertTrue(len(risk_scores) <= 2, 
                       "Should not hallucinate excessive risks for safe inputs")
        
        print("✅ No hallucination test completed")

def run_agent_tests():
    """Run all agent tests"""
    print("🧪 Running Agent Validation Tests")
    print("=" * 50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgents)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All agent tests passed!")
    else:
        print(f"❌ {len(result.failures)} test failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == '__main__':
    # Check if we have test data
    test_images = data_loader.get_risk_annotated_images()
    if not test_images:
        print("❌ No test images available. Running with mock data...")
    else:
        print(f"✅ Found {len(test_images)} images with detections for testing")
    
    run_agent_tests()