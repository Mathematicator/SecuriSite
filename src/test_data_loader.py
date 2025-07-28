"""
Test the improved data loader with real dataset
"""

from securisite.utils.data_loader import data_loader

def test_data_loader():
    """Test the data loader with real data"""
    print("🧪 Testing SecuriSite Data Loader with Real Data")
    print("=" * 60)
    
    # Test basic loading
    try:
        images = data_loader.get_image_data()
        risky_images = data_loader.get_risk_annotated_images()
        available_dates = data_loader.get_available_dates(risky_images)
        
        print(f"✅ Data map validation:")
        print(f"   Total images mapped: {len(images)}")
        print(f"   Images with detections: {len(risky_images)}")
        print(f"   Available dates: {len(available_dates)}")
        
        if images:
            min_date = min(img.timestamp for img in images)
            max_date = max(img.timestamp for img in images)
            print(f"   Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            
            print("\n📅 Real dates from dataset (first 10):")
            for date in available_dates[:10]:
                count = len([img for img in risky_images if img.date_str == date])
                print(f"   {date}: {count} images")
        
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

if __name__ == '__main__':
    test_data_loader()