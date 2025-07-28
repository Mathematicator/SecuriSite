"""
SecuriSite-IA Web Application with Real Dataset Integration
Uses actual construction site data from June-July 2025
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import io
import os
from typing import Dict, List, Any

from .utils.data_loader import SecuriSiteDataLoader
from .evaluation.evaluator import PerformanceEvaluator

app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize data loaders
dataloader = SecuriSiteDataLoader()

class RealDataWebApp:
    """Web application serving real construction site safety data"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.assets_dir = self.project_root / 'assets'
        self.load_real_data()
    
    def load_real_data(self):
        """Load real data from June-July 2025"""
        try:
            self.all_images = dataloader.get_image_data()
            self.risky_images = [img for img in self.all_images if img.detections and len(img.detections) > 0]
            self.dates = sorted(list(set(img.date_str for img in self.all_images if img.detection_packages>0)))
            
            print(f"✅ Loaded {len(self.all_images)} total images")
            print(f"✅ {len(self.risky_images)} images with risks")
            print(f"✅ Date range: {min(self.dates) if self.dates else 'none'} to {max(self.dates) if self.dates else 'none'}")
            
        except Exception as e:
            print(f"❌ Error loading real data: {e}")
            self.all_images = []
            self.risky_images = []
            self.dates = []
    
    def analyze_real_risks(self, image_data: Any) -> Dict[str, Any]:
        """Analyze real risks from detection data"""
        if not image_data:
            return {
                "image_analysis": {},
                "risk_scores": []
            }
        
        # Analyze real detections for risk factors
        risk_scores = []
        image_analysis = {
            "image_id": image_data.image_id,
            "timestamp": image_data.timestamp.isoformat(),
            "camera": image_data.camera,
            "filename": image_data.filename
        }
        
        # Count person detections and check for PPE
        persons = [d for d in image_data.detections if d.get('label') == 'person'] 
        ppe_detections = []
        
        if persons:
            no_ppe_count = 0
            for person in persons:
                attributes = person.get('attributes', {})
                if attributes.get('no_ppe', 0) > 0.7:
                    no_ppe_count += 1
            
            if no_ppe_count > 0:
                risk_scores.append({
                    "risk_type": f"person_without_ppe_{no_ppe_count}",
                    "severity": min(10, 5 + no_ppe_count * 2),
                    "area": f"personnel_zone_{len(persons)}",
                    "equipment_involved": ["person"] * no_ppe_count
                })
        
        # Check for machinery risks
        machinery = [d for d in image_data.detections if any(label in str(d.get('label', '')).lower() for label in ['tower_crane', 'excavator', 'dumper'])]
        if machinery:
            risk_scores.append({
                "risk_type": "machinery_operation",
                "severity": 6,
                "area": "equipment_zone",
                "equipment_involved": [m.get('label', 'unknown') for m in machinery]
            })
        
        # Check for container issues
        containers = [d for d in image_data.detections if d.get('label') == 'container']
        if containers:
            risk_scores.append({
                "risk_type": "container_obstruction",
                "severity": 5,
                "area": "storage_zone",
                "equipment_involved": ["container"] * len(containers)
            })
        
        return {
            "image_analysis": image_analysis,
            "risk_scores": risk_scores,
            "summary": {
                "status": "risk_detected" if risk_scores else "safe",
                "total_risks": len(risk_scores),
                "max_severity": max([r["severity"] for r in risk_scores], default=0)
            }
        }

real_app = RealDataWebApp()

@app.route('/')
def dashboard():
    """Main dashboard with real data"""
    selected_date = request.args.get('date')
    today = datetime(2025, 7, 17).strftime("%Y-%m-%d")  # Latest date from dataset
    
    # Get relevant images
    if selected_date and selected_date in [d for d in real_app.dates if d]:
        relevant_images = [img for img in real_app.risky_images if img.date_str == selected_date]
    else:
        relevant_images = real_app.risky_images[:20]  # Show first 20 risks by default
    
    # Process real risks
    risks = []
    for img in relevant_images:
        analysis = real_app.analyze_real_risks(img)
        if analysis["risk_scores"]:
            for risk in analysis["risk_scores"]:
                risks.append({
                    "id": img.image_id,
                    "title": risk["risk_type"].replace("_", " ").title(),
                    "severity": risk["severity"],
                    "location": f"{img.camera}: {img.filename}",
                    "timestamp": img.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "image_path": img.filename,
                    "description": f"{risk['area']}: {len(risk['equipment_involved'])} detections found",
                    "detections": img.detections,
                    "camera": img.camera,
                    "date": img.date_str
                })
    
    # Calculate risk score
    if risks:
        avg_severity = sum(r['severity'] for r in risks) / len(risks)
        risk_level = "RISQUE ÉLEVÉ" if avg_severity >= 7 else "RISQUE MODÉRÉ" if avg_severity >= 5 else "RISQUE FAIBLE"
        risk_color = "#D32F2F" if avg_severity >= 7 else "#F57C00" if avg_severity >= 5 else "#388E3C"
    else:
        avg_severity = 0
        risk_level = "AUCUN RISQUE"
        risk_color = "#388E3C"
        risks = []
    
    all_dates = [d for d in real_app.dates if d]  
    
    return render_template('dashboard.html',
                         risks=risks,
                         risk_score=avg_severity,
                         risk_level=risk_level,
                         risk_color=risk_color,
                         selected_date=selected_date or today,
                         current_date_display=datetime.strptime(selected_date or today, "%Y-%m-%d").strftime("%d %B %Y"),
                         all_dates=all_dates)

@app.route('/r/<image_id>')
def risk_detail(image_id):
    """Detailed view of specific image with real data"""
    image_data = next((img for img in real_app.risky_images if img.image_id == image_id), None)
    
    if not image_data:
        return "Risk non trouvé", 404
    
    # Generate risk analysis from real data
    analysis = real_app.analyze_real_risks(image_data)
    
    # Map to risk structure for template
    risk = {
        "id": image_data.image_id,
        "title": next((r["risk_type"].replace("_", " ").title() for r in analysis["risk_scores"]), "Analyse Sécurité"),
        "severity": next((r["severity"] for r in analysis["risk_scores"]), 1),
        "location": f"{image_data.camera}: {image_data.filename}",
        "timestamp": image_data.timestamp.strftime("%Y-%m-%d %H:%M"),
        "image_path": image_data.filename,
        "description": f"Analyse des détections de sécurité sur {image_data.camera}",
        "weather": {
            "condition": "Données météo",
            "wind": "Variables",
            "visibility": "Rapport conditions"
        },
        "regulation": {
            "reference": "Code du Travail",
            "rule": "Analyse basée sur détections réelles"
        },
        "annotations": self._generate_annotations(image_data.detections),
        "detections": image_data.detections
    }
    
    return render_template('risk_detail.html', risk=risk)

def _generate_annotations(self, detections: List[Dict]):
    """Generate simple annotations for real data"""
    annotations = []
    for i, detection in enumerate(detections):
        if detection.get('label') in ['person', 'tower_crane', 'container']:
            bbox = {
                'bbox_start_x': detection.get('bounding_box_start_x', 0),
                'bbox_start_y': detection.get('bounding_box_start_y', 0),
                'bbox_end_x': detection.get('bounding_box_end_x', 0.2),
                'bbox_end_y': detection.get('bounding_box_end_y', 0.2)
            }
            
            annotations.append({
                "type": "box",
                "x1": bbox['bbox_start_x'],
                "y1": bbox['bbox_start_y'],
                "x2": bbox['bbox_end_x'],
                "y2": bbox['bbox_end_y'],
                "color": "#FF0000"
            })
    return annotations

@app.route('/api/images/<image_filename>')
def serve_image(image_filename):
    """Serve actual images from dataset"""
    for folder in ['images_EST-1', 'images_EST-2']:
        image_path = Path('assets') / folder / image_filename
        if image_path.exists():
            return send_file(str(image_path), mimetype='image/jpeg')
    
    return "Image non trouvée", 404

@app.route('/api/timeline')
def api_timeline():
    """API endpoint for timeline data"""
    try:
        daily_counts = {}
        for img in real_app.risky_images:
            date = img.date_str
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        return jsonify({
            "dates": list(daily_counts.keys()),
            "counts": list(daily_counts.values()),
            "date_range": f"{min(daily_counts.keys())} to {max(daily_counts.keys())}" if daily_counts else "none"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 SecuriSite-IA - REAL DATA MODE")
    print("=" * 50)
    
    # Load and display real dataset info
    try:
        real_app.load_real_data()
        print("✅ Real dataset loaded successfully")
        print(f"📅 Available dates: {len(real_app.dates)}")
        if real_app.dates:
            print(f"🗓️  Range: {min(real_app.dates)} to {max(real_app.dates)}")
        print(f"📸 Images with risks: {len(real_app.risky_images)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🌐 Access the web interface:")
    print("   http://localhost:5000 (main dashboard)")
    print("   http://localhost:5000/api/timeline (dates API)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)