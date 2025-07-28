"""
SecuriSite-IA Web Application
Interface utilisateur pour l'analyse des risques de chantier
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
from flask_cors import CORS

# Add current directory to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(project_root))

from .orchestrator import SecuriSiteOrchestrator

app = Flask(__name__)
CORS(app)

# Initialize orchestrator
orchestrator = SecuriSiteOrchestrator()

def load_real_data():
    """Load real data from assets folder"""
    try:
        # Load EST-1 data
        est1_path = project_root / "assets" / "images_EST-1.json"
        est2_path = project_root / "assets" / "images_EST-2.json"
        weather_path = project_root / "assets" / "weather_info.json"
        
        all_images = {}
        
        if est1_path.exists():
            with open(est1_path, 'r', encoding='utf-8') as f:
                est1_data = json.load(f)
                all_images.update(est1_data.get('images', {}))
        
        if est2_path.exists():
            with open(est2_path, 'r', encoding='utf-8') as f:
                est2_data = json.load(f)
                all_images.update(est2_data.get('images', {}))
        
        weather_data = {}
        if weather_path.exists():
            with open(weather_path, 'r', encoding='utf-8') as f:
                weather_data = json.load(f)
        
        return all_images, weather_data
    except Exception as e:
        print(f"Error loading real data: {e}")
        return {}, {}

def analyze_real_risks(images_data, weather_data):
    """Analyze real risks from actual detection data"""
    risks = []
    
    for image_filename, image_data in images_data.items():
        detections = image_data.get('detections', [])
        timestamp = image_data.get('image_shooting', '')
        photo_id = image_data.get('photo_id', '')
        
        # Convert timestamp to datetime for filtering
        try:
            if timestamp:
                # Parse format "2025:07:14 14:20:07"
                dt = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d")
            else:
                continue
        except:
            continue
        
        # Analyze detections for safety risks
        risk_analysis = analyze_detections_for_risks(detections, image_filename, timestamp, photo_id, weather_data)
        
        if risk_analysis:
            risks.extend(risk_analysis)
    
    return risks

def analyze_detections_for_risks(detections, image_filename, timestamp, photo_id, weather_data):
    """Analyze detections and create risk assessments"""
    risks = []
    
    # Group detections by type
    persons = [d for d in detections if d.get('label') == 'person']
    tower_cranes = [d for d in detections if d.get('label') == 'tower_crane']
    excavators = [d for d in detections if d.get('label') == 'excavator']
    containers = [d for d in detections if d.get('label') == 'container']
    
    dt = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
    date_str = dt.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M")
    risk_id_base = f"risk_{photo_id}"
    
    # Risk 1: Person without PPE
    for i, person in enumerate(persons):
        attributes = person.get('attributes', {})
        no_ppe = attributes.get('no_ppe', 0)
        
        if no_ppe > 0.7:  # High confidence of no PPE
            severity = min(int(no_ppe * 10), 9)
            risks.append({
                "id": f"{risk_id_base}_ppe_{i}",
                "title": "Absence d'EPI - Casque",
                "severity": severity,
                "location": "Zone de construction active",
                "timestamp": f"{date_str} {time_str}",
                "image_path": image_filename,
                "description": f"Personne détectée sans équipement de protection individuelle (casque de sécurité). Confiance de détection: {no_ppe:.1%}",
                "weather": get_weather_for_date(date_str, weather_data),
                "regulation": {
                    "reference": "Code du Travail, Art. R4534-1",
                    "rule": "Le port du casque de protection est obligatoire sur tous les chantiers."
                },
                "annotations": [
                    {
                        "type": "circle",
                        "x": (person['bounding_box_start_x'] + person['bounding_box_end_x']) / 2,
                        "y": (person['bounding_box_start_y'] + person['bounding_box_end_y']) / 2,
                        "radius": 0.03,
                        "color": "#D32F2F"
                    }
                ]
            })
    
    # Risk 2: Tower crane operation risks
    for i, crane in enumerate(tower_cranes):
        if crane.get('score', 0) > 0.5:
            # Check if crane is near people
            crane_risk = False
            proximity_persons = []
            
            for person in persons:
                # Calculate distance between crane and person
                crane_center_x = (crane['bounding_box_start_x'] + crane['bounding_box_end_x']) / 2
                crane_center_y = (crane['bounding_box_start_y'] + crane['bounding_box_end_y']) / 2
                person_center_x = (person['bounding_box_start_x'] + person['bounding_box_end_x']) / 2
                person_center_y = (person['bounding_box_start_y'] + person['bounding_box_end_y']) / 2
                
                distance = ((crane_center_x - person_center_x)**2 + (crane_center_y - person_center_y)**2)**0.5
                
                if distance < 0.3:  # Close proximity
                    crane_risk = True
                    proximity_persons.append(person)
            
            if crane_risk:
                risks.append({
                    "id": f"{risk_id_base}_crane_{i}",
                    "title": "Proximité dangereuse avec grue",
                    "severity": 7,
                    "location": "Zone de grutage",
                    "timestamp": f"{date_str} {time_str}",
                    "image_path": image_filename,
                    "description": f"Personnel détecté dans la zone d'évolution de la grue. {len(proximity_persons)} personne(s) concernée(s).",
                    "weather": get_weather_for_date(date_str, weather_data),
                    "regulation": {
                        "reference": "Code du Travail, Art. R4323-55",
                        "rule": "Une distance de sécurité doit être respectée autour des engins en mouvement."
                    },
                    "annotations": [
                        {
                            "type": "box",
                            "x1": crane['bounding_box_start_x'],
                            "y1": crane['bounding_box_start_y'],
                            "x2": crane['bounding_box_end_x'],
                            "y2": crane['bounding_box_end_y'],
                            "color": "#FF9800"
                        }
                    ] + [
                        {
                            "type": "circle",
                            "x": (p['bounding_box_start_x'] + p['bounding_box_end_x']) / 2,
                            "y": (p['bounding_box_start_y'] + p['bounding_box_end_y']) / 2,
                            "radius": 0.025,
                            "color": "#D32F2F"
                        } for p in proximity_persons
                    ]
                })
    
    # Risk 3: Excavator proximity risks
    for i, excavator in enumerate(excavators):
        if excavator.get('score', 0) > 0.7:
            # Check for people near excavator
            proximity_persons = []
            
            for person in persons:
                exc_center_x = (excavator['bounding_box_start_x'] + excavator['bounding_box_end_x']) / 2
                exc_center_y = (excavator['bounding_box_start_y'] + excavator['bounding_box_end_y']) / 2
                person_center_x = (person['bounding_box_start_x'] + person['bounding_box_end_x']) / 2
                person_center_y = (person['bounding_box_start_y'] + person['bounding_box_end_y']) / 2
                
                distance = ((exc_center_x - person_center_x)**2 + (exc_center_y - person_center_y)**2)**0.5
                
                if distance < 0.2:  # Very close proximity
                    proximity_persons.append(person)
            
            if proximity_persons:
                risks.append({
                    "id": f"{risk_id_base}_excavator_{i}",
                    "title": "Proximité dangereuse avec excavatrice",
                    "severity": 8,
                    "location": "Zone d'excavation",
                    "timestamp": f"{date_str} {time_str}",
                    "image_path": image_filename,
                    "description": f"Personnel détecté à proximité immédiate de l'excavatrice en fonctionnement. {len(proximity_persons)} personne(s) à risque.",
                    "weather": get_weather_for_date(date_str, weather_data),
                    "regulation": {
                        "reference": "Code du Travail, Art. R4323-55",
                        "rule": "Une distance de sécurité doit être respectée autour des engins en mouvement."
                    },
                    "annotations": [
                        {
                            "type": "box",
                            "x1": excavator['bounding_box_start_x'],
                            "y1": excavator['bounding_box_start_y'],
                            "x2": excavator['bounding_box_end_x'],
                            "y2": excavator['bounding_box_end_y'],
                            "color": "#FF5722"
                        }
                    ] + [
                        {
                            "type": "circle",
                            "x": (p['bounding_box_start_x'] + p['bounding_box_end_x']) / 2,
                            "y": (p['bounding_box_start_y'] + p['bounding_box_end_y']) / 2,
                            "radius": 0.025,
                            "color": "#D32F2F"
                        } for p in proximity_persons
                    ]
                })
    
    return risks

def get_weather_for_date(date_str, weather_data):
    """Get weather information for a specific date"""
    # Simple weather simulation based on date
    import random
    random.seed(hash(date_str))
    
    conditions = ["Ensoleillé", "Nuageux", "Pluie légère", "Vent fort"]
    condition = random.choice(conditions)
    wind_speed = random.randint(5, 40)
    
    if condition == "Pluie légère":
        visibility = "Réduite"
    elif condition == "Vent fort":
        visibility = "Bonne"
    else:
        visibility = "Excellente"
    
    return {
        "condition": condition,
        "wind": f"{wind_speed} km/h",
        "visibility": visibility
    }

# Load real data on startup
try:
    REAL_IMAGES_DATA, WEATHER_DATA = load_real_data()
    REAL_RISKS = analyze_real_risks(REAL_IMAGES_DATA, WEATHER_DATA)
    print("🔍 Données chargées:")
    print(f"  • {len(REAL_IMAGES_DATA)} images analysées")
    print(f"  • {len(REAL_RISKS)} risques détectés")
    print(f"  • Sources: EST-1, EST-2")
except Exception as e:
    print(f"❌ Erreur lors du chargement des données: {e}")
    REAL_IMAGES_DATA, WEATHER_DATA = {}, {}
    REAL_RISKS = []

@app.route('/')
def dashboard():
    """Dashboard page showing risk overview"""
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Filter risks by date
    filtered_risks = [r for r in REAL_RISKS if r['timestamp'].startswith(selected_date)]
    
    # Calculate global risk score
    if filtered_risks:
        global_score = sum(r['severity'] for r in filtered_risks) / len(filtered_risks)
        risk_level = "RISQUE ÉLEVÉ" if global_score >= 7 else "RISQUE MODÉRÉ" if global_score >= 5 else "RISQUE FAIBLE"
        risk_color = "#D32F2F" if global_score >= 7 else "#F57C00" if global_score >= 5 else "#388E3C"
    else:
        global_score = 2.0  # Default low risk
        risk_level = "AUCUN RISQUE"
        risk_color = "#388E3C"
    
    # Format date display
    try:
        current_date_display = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d %B %Y")
    except:
        current_date_display = selected_date
    
    return render_template('dashboard.html', 
                         risks=filtered_risks,
                         risk_score=round(global_score, 1),
                         risk_level=risk_level,
                         risk_color=risk_color,
                         selected_date=selected_date,
                         current_date_display=current_date_display,
                         current_date=selected_date)

@app.route('/risk/<risk_id>')
def risk_detail(risk_id):
    """Risk detail page"""
    # Find the specific risk
    risk = None
    for r in REAL_RISKS:
        if r['id'] == risk_id:
            risk = r
            break
    
    if not risk:
        return "Risk not found", 404
    
    return render_template('risk_detail.html', risk=risk)

@app.route('/api/images/<image_name>')
def serve_image(image_name):
    """Serve images from assets folder"""
    # Try EST-1 first, then EST-2
    for camera in ['EST-1', 'EST-2']:
        image_path = project_root / "assets" / f"images_{camera}" / image_name
        if image_path.exists():
            return send_file(str(image_path))
    
    return "Image not found", 404

@app.route('/api/report/latest')
def latest_report():
    """API endpoint for latest risk report"""
    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    filtered_risks = [r for r in REAL_RISKS if r['timestamp'].startswith(selected_date)]
    
    if filtered_risks:
        global_score = sum(r['severity'] for r in filtered_risks) / len(filtered_risks)
    else:
        global_score = 2.0
    
    return jsonify({
        "global_score": round(global_score, 1),
        "total_risks": len(filtered_risks),
        "risks": filtered_risks,
        "analysis_date": selected_date
    })

@app.route('/api/risk/<risk_id>')
def api_risk_detail(risk_id):
    """API endpoint for risk details"""
    risk = next((r for r in REAL_RISKS if r['id'] == risk_id), None)
    if not risk:
        return jsonify({"error": "Risk not found"}), 404
    return jsonify(risk)

@app.route('/api/risk/<risk_id>/ack', methods=['POST'])
def acknowledge_risk(risk_id):
    """Mark a risk as acknowledged/treated"""
    # In a real system, this would update a database
    return jsonify({"status": "acknowledged", "risk_id": risk_id})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)