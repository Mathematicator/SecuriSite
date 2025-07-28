"""
Test the corrected data loader with actual paths
"""

import json
from pathlib import Path
from datetime import datetime

def test_data_loading():
    """Test data loading with corrected paths"""
    print("🔍 Testing Real Dataset Data Loading")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / 'assets'
    
    print(f"Project root: {project_root}")
    print(f"Assets dir: {assets_dir}")
    
    def load_camera_data(camera_name: str):
        """Load data for a specific camera"""
        json_path = assets_dir / f'images_{camera_name}.json'
        images_dir = assets_dir / f'images_{camera_name}'
        
        print(f"\n{camera_name}:")
        print(f"  JSON exists: {json_path.exists()}")
        print(f"  Images dir exists: {images_dir.exists()}")
        
        if not json_path.exists():
            return None, None
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  Loaded entries: {len(data.get('images', {}))}")
            
            # Count valid files
            valid_files = 0
            for filename, image_data in data.get('images', {}).items():
                if (images_dir / filename).exists():
                    valid_files += 1
            print(f"  Valid files: {valid_files}")
            
            # Extract dates
            dates = []
            for filename, metadata in data.get('images', {}).items():
                try:
                    timestamp = metadata.get('image_shooting', '')
                    if timestamp:
                        fixed = timestamp.replace(':', '-', 2)
                        date = datetime.strptime(fixed, '%Y-%m-%d %H:%M:%S')
                        dates.append(date)
                except:
                    continue
            
            if dates:
                print(f"  Date range: {min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}")
            
            return data, dates
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return None, None

    # Test both cameras
    est1_data, est1_dates = load_camera_data('EST-1')
    est2_data, est2_dates = load_camera_data('EST-2')
    
    # Summary
    total_images = 0
    total_dates = set()
    
    if est1_data:
        total_images += len(est1_data.get('images', {}))
        total_dates.update(est1_dates or [])
    if est2_data:
        total_images += len(est2_data.get('images', {}))  
        total_dates.update(est2_dates or [])
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total images: {total_images}")
    print(f"   Total unique dates: {len(total_dates)}")
    print(f"   Overall date range: {min(total_dates).strftime('%Y-%m-%d')} to {max(total_dates).strftime('%Y-%m-%d')}" 
          if total_dates else "No dates found")
    
    return est1_data, est2_data

if __name__ == '__main__':
    test_data_loading()