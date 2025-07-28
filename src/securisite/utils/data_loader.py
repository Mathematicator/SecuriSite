"""
Robust data loader for SecuriSite-IA
Handles date parsing, validation, and data integrity
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ImageData:
    """Structured image data with provenance tracking"""
    image_id: str
    filename: str
    timestamp: datetime
    camera: str
    detections: List[Dict[str, Any]]
    file_path: Path
    
    @property
    def date_str(self) -> str:
        """Return date in YYYY-MM-DD format"""
        return self.timestamp.strftime('%Y-%m-%d')

class SecuriSiteDataLoader:
    """Reliable data loader with full integrity validation"""
    
    def __init__(self, project_root: Path = None):
        """Initialize with correct path calculation"""
        if project_root:
            self.project_root = project_root
        else:
            # Go up from src/securisite/utils to project root
            self.project_root = Path(__file__).parent.parent.parent
        
        self.assets_dir = self.project_root / 'assets'
        
    def load_est1_metadata(self) -> Dict[str, Any]:
        """Load EST-1 metadata with date parsing"""
        return self._load_metadata(self.assets_dir / 'images_EST-1.json')
    
    def load_est2_metadata(self) -> Dict[str, Any]:
        """Load EST-2 metadata with date parsing"""
        return self._load_metadata(self.assets_dir / 'images_EST-2.json')
    
    def _load_metadata(self, json_path: Path) -> Dict[str, Any]:
        """Load and parse metadata with full validation"""
        if not json_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {json_path}")
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'images' not in data:
                data = {'images': data}  # Handle flat structure
                
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {json_path}: {e}")
    
    def get_image_data(self) -> List[ImageData]:
        """Get all image data with full validation"""
        images = []
        
        # Load EST-1 data
        est1_data = self.load_est1_metadata()
        est1_images = self._process_camera_images(
            est1_data, 'EST-1', self.assets_dir / 'images_EST-1'
        )
        images.extend(est1_images)
        
        # Load EST-2 data  
        est2_data = self.load_est2_metadata()
        est2_images = self._process_camera_images(
            est2_data, 'EST-2', self.assets_dir / 'images_EST-2'
        )
        images.extend(est2_images)
        
        return images
    
    def _process_camera_images(self, metadata: Dict[str, Any], 
                               camera_name: str, images_dir: Path) -> List[ImageData]:
        """Process images for a specific camera with full validation"""
        images = []
        
        # Ensure we're using the correct directory
        if not images_dir.exists():
            print(f"Warning: Directory {images_dir} does not exist")
            return images
            
        image_metadata = metadata.get('images', metadata)
        
        for filename, image_data in image_metadata.items():
            try:
                # The key IS the filename (e.g., '651424718_16424f3e...jpg')
                file_path = images_dir / filename
                
                # Extract image_id from filename without extension
                image_id = filename.replace('.jpg', '')
                
                # Parse date with correct format
                timestamp_str = image_data.get('image_shooting', '')
                if not timestamp_str:
                    continue
                    
                # Fix date format: YYYY:MM:DD → YYYY-MM-DD
                fixed_timestamp = timestamp_str.replace(':', '-', 2)
                timestamp = datetime.strptime(fixed_timestamp, '%Y-%m-%d %H:%M:%S')
                
                # Validate file exists (optional for testing)
                exists = file_path.exists()
                if not exists:
                    print(f"⚠️  Warn: Image file missing: {filename}")
                
                # Process detections
                detections = image_data.get('detections', [])
                
                images.append(ImageData(
                    image_id=image_id,
                    filename=filename,
                    timestamp=timestamp,
                    camera=camera_name,
                    detections=detections,
                    file_path=file_path
                ))
                
            except Exception as e:
                print(f"Error processing image {filename}: {e}")
                continue
                
        return images
    
    def get_risk_annotated_images(self, min_confidence: float = 0.5) -> List[ImageData]:
        """Get images with actual detections for risk analysis"""
        all_images = self.get_image_data()
        
        # Filter images with actual detections
        risky_images = []
        for img in all_images:
            if img.detections and len(img.detections) > 0:
                risky_images.append(img)
                
        print(f"Found {len(risky_images)} images with detections")
        return risky_images
    
    def get_available_dates(self, images: List[ImageData]) -> List[str]:
        """Get unique dates from actual dataset"""
        dates = set(img.date_str for img in images)
        return sorted(list(dates))

# Initialize global data loader
data_loader = SecuriSiteDataLoader()

if __name__ == '__main__':
    """Standalone test of data loader"""
    print("🧪 Testing SecuriSite Data Loader")
    print("=" * 50)
    
    try:
        # Load all image data
        images = data_loader.get_image_data()
        risky_images = data_loader.get_risk_annotated_images()
        available_dates = data_loader.get_available_dates(images)
        
        print(f"Total images loaded: {len(images)}")
        print(f"Images with detections: {len(risky_images)}")
        print(f"Available dates: {len(available_dates)}")
        print("\nDate range:")
        if images:
            min_date = min(img.timestamp for img in images)
            max_date = max(img.timestamp for img in images)
            print(f"  From: {min_date.strftime('%Y-%m-%d')}")
            print(f"  To: {max_date.strftime('%Y-%m-%d')}")
        
        print("\nSample dates with data:")
        for date in available_dates[:5]:
            count = len([img for img in risky_images if img.date_str == date])
            print(f"  {date}: {count} images with detections")
            
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        import traceback
        traceback.print_exc()