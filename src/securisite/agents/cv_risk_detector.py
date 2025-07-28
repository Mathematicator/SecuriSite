"""
Computer Vision Risk Detector Agent
Analyzes construction site images for safety violations and risk factors
"""

import json
import logging
import os
import base64
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from .base_agent import BaseSecuriSiteAgent
from ..models.risk_models import ImageAnalysis, RiskScore, PersonDetection, EquipmentDetection
try:
    from openai import AzureOpenAI
    OPENAI_ENABLED = True
except ImportError:
    AzureOpenAI = None
    OPENAI_ENABLED = False

class ComputerVisionRiskDetector(BaseSecuriSiteAgent):
    """Agent specialized in detecting safety risks from computer vision data with GPT-4.1 vision"""
    
    def __init__(self):
        super().__init__("ComputerVisionRiskDetector")
        
        # Load environment variables from .env file
        load_dotenv()
        
        self.risk_weights = {
            'person_no_ppe': 8,
            'tower_crane_position': 6,
            'equipment_proximity': 7,
            'container_obstruction': 5
        }
        
        # Initialize Azure OpenAI GPT-4.1 client
        self.client = None
        self.deployment_name = os.getenv("AZURE_DEPLOYMENT_MODEL_NAME", "gpt4.1")
        
        if OPENAI_ENABLED:
            try:
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
                api_version = os.getenv("OPENAI_API_VERSION_GPT4.1", "2024-06-01")
                
                if api_key and endpoint:
                    # Ensure endpoint ends with /
                    if not endpoint.endswith('/'):
                        endpoint += '/'
                    
                    # Try different initialization approaches for compatibility
                    try:
                        # Method 1: Standard initialization
                        self.client = AzureOpenAI(
                            azure_endpoint=endpoint,
                            api_key=api_key,
                            api_version=api_version
                        )
                    except TypeError as te:
                        if "proxies" in str(te):
                            # Method 2: Alternative initialization without potentially problematic params
                            try:
                                self.client = AzureOpenAI(
                                    azure_endpoint=endpoint.rstrip('/'),
                                    api_key=api_key,
                                    api_version=api_version,
                                    timeout=30.0  # Add explicit timeout
                                )
                            except Exception:
                                # Method 3: Most basic initialization
                                self.client = AzureOpenAI(
                                    azure_endpoint=endpoint.rstrip('/'),
                                    api_key=api_key,
                                    api_version=api_version
                                )
                        else:
                            raise te
                    
                    self.log_info(f"Azure OpenAI client initialized with deployment: {self.deployment_name}")
                else:
                    self.log_info("Using JSON-based analysis (missing API key or endpoint)")
            except Exception as e:
                self.log_info(f"Using JSON-based analysis (client init failed: {type(e).__name__}: {str(e)})")
        else:
            self.log_info("Using JSON-based analysis (OpenAI unavailable)")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image detection data and identify security risks"""
        self.log_info("Starting computer vision risk analysis")
        
        image_path = data.get('image_path')
        detection_data = await self._load_detection_data(image_path)
        
        if not detection_data:
            return {"error": "No detection data found"}
        
        image_analysis = self._analyze_image(detection_data)
        risk_scores = self._calculate_risk_scores(image_analysis)
        
        return {
            "image_analysis": image_analysis.dict(),
            "risk_scores": [score.dict() for score in risk_scores],
            "summary": self._generate_summary(risk_scores)
        }
    
    async def _load_detection_data(self, image_id: str) -> Dict[str, Any]:
        """Load detection data for a specific image"""
        est1_path = Path("assets/images_EST-1.json")
        est2_path = Path("assets/images_EST-2.json")
        
        for json_path in [est1_path, est2_path]:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if image_id in data.get('images', {}):
                        return data['images'][image_id]
            except Exception as e:
                self.log_error(f"Error loading {json_path}: {e}")
                
        return None
    
    def _analyze_image(self, detection_data: Dict[str, Any]) -> ImageAnalysis:
        """Analyze detection data and extract risk factors"""
        detections = detection_data.get('detections', [])
        
        equipment_detections = []
        person_detections = []
        
        for detection in detections:
            if detection.get('label') == 'person':
                person_info = PersonDetection(
                    bbox_start_x=detection.get('bounding_box_start_x', 0),
                    bbox_end_x=detection.get('bounding_box_end_x', 0),
                    bbox_start_y=detection.get('bounding_box_start_y', 0),
                    bbox_end_y=detection.get('bounding_box_end_y', 0),
                    has_hard_hat=detection.get('attributes', {}).get('has_hard_hat', 0),
                    has_high_vis_vest=detection.get('attributes', {}).get('has_high_vis_vest', 0),
                    has_high_vis_pants=detection.get('attributes', {}).get('has_high_vis_pants', 0),
                    no_ppe=detection.get('attributes', {}).get('no_ppe', 0),
                    two_or_more=detection.get('attributes', {}).get('two_or_more', 0)
                )
                person_detections.append(person_info)
            else:
                equipment_info = EquipmentDetection(
                    label=detection.get('label', 'unknown'),
                    score=detection.get('score', 0),
                    bbox_start_x=detection.get('bounding_box_start_x', 0),
                    bbox_end_x=detection.get('bounding_box_end_x', 0),
                    bbox_start_y=detection.get('bounding_box_start_y', 0),
                    bbox_end_y=detection.get('bounding_box_end_y', 0)
                )
                equipment_detections.append(equipment_info)
        
        return ImageAnalysis(
            image_id=detection_data.get('photo_id', 'unknown'),
            timestamp=detection_data.get('image_shooting', 'unknown'),
            detections=equipment_detections,
            person_detections=person_detections
        )
    
    def _calculate_risk_scores(self, analysis: ImageAnalysis) -> List[RiskScore]:
        """Calculate risk scores based on detected elements"""
        risks = []
        
        # Risk from people without PPE
        for person in analysis.person_detections:
            if person.no_ppe > 0.8:
                risks.append(RiskScore(
                    risk_type="person_without_ppe",
                    severity=int(person.no_ppe * 10),
                    area=f"person_{len(risks)+1}",
                    equipment_involved=["no_ppe"]
                ))
        
        # Risk from tower cranes
        tower_cranes = [d for d in analysis.detections if d.label == 'tower_crane']
        for crane in tower_cranes:
            if crane.score > 0.8:
                risks.append(RiskScore(
                    risk_type="tower_crane_operation",
                    severity=6,
                    area="crane_zone",
                    equipment_involved=["tower_crane"]
                ))
        
        # Container placement risks
        containers = [d for d in analysis.detections if d.label == 'container']
        for container in containers:
            if container.bbox_start_x < 0.3 and container.bbox_end_y > 0.6:
                risks.append(RiskScore(
                    risk_type="container_obstruction",
                    severity=5,
                    area="access_zone",
                    equipment_involved=["container"]
                ))
        
        return risks
    
    def _generate_summary(self, risk_scores: List[RiskScore]) -> Dict[str, Any]:
        """Generate summary of detected risks"""
        if not risk_scores:
            return {"status": "safe", "message": "No significant risks detected"}
        
        severity_counts = {}
        for risk in risk_scores:
            severity_counts[risk.severity] = severity_counts.get(risk.severity, 0) + 1
        
        max_severity = max(risk.severity for risk in risk_scores)
        return {
            "status": "risk_detected" if max_severity > 5 else "warning",
            "total_risks": len(risk_scores),
            "max_severity": max_severity,
            "risk_types": list(set(risk.risk_type for risk in risk_scores))
        }

    async def _enhanced_gpt4_analysis(self, image_path: str, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analysis using GPT-4.1 vision"""
        try:
            # Construct actual image path
            image_file = f"{image_path}"
            image_full_path = None
            
            # Try both cameras
            for camera in ['EST-1', 'EST-2']:
                candidate_path = Path(f"assets/{camera}/{image_file}")
                if candidate_path.exists():
                    image_full_path = candidate_path
                    break
            
            if not image_full_path or not self.client:
                # Fallback to JSON-based analysis if no image file found
                return await self._json_based_analysis(detection_data)
            
            # Read and encode image
            with open(image_full_path, 'rb') as img_file:
                img_data = img_file.read()
            
            base64_image = base64.b64encode(img_data).decode('utf-8')
            
            # GPT-4.1 vision analysis
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name from environment
                messages=[
                    {
                        "role": "system",
                        "content": """Vous êtes un expert en sécurité sur chantier. Analysez l'image pour identifier:
                        1. Les personnes et leur équipement de protection (EPI)
                        2. Les équipements et machines en position dangereuse
                        3. Les zones de travail à risque
                        4. Les violations évidentes du code du travail français
                        Répondez en JSON français avec:
                        - Liste des risques détectés
                    - Sévérité (1-10)
                    - Recommandations spécifiques"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analysez cette image de chantier pour les risques de sécurité."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse GPT-4.1 response
            vision_analysis = self._parse_vision_response(response.choices[0].message.content)
            return vision_analysis
            
        except Exception as e:
            self.log_error(f"GPT-4.1 vision analysis failed: {e}")
            return await self._json_based_analysis(detection_data)

    async def _json_based_analysis(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback JSON-based analysis using provided detection data"""
        if detection_data:
            image_analysis = self._analyze_image(detection_data)
        else:
            image_analysis = ImageAnalysis(image_id="demo", timestamp=datetime.now().isoformat(), detections=[], person_detections=[])
        
        risk_scores = self._calculate_risk_scores(image_analysis)
        
        return {
            "image_analysis": image_analysis.dict(),
            "risk_scores": [score.dict() for score in risk_scores],
            "summary": self._generate_summary(risk_scores),
            "analysis_source": "JSON_detections"  # Mark as JSON-based
        }

    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT-4.1 vision API response"""
        try:
            # Try to extract JSON from response
            import ast
            
            # Look for JSON-like structure
            start_idx = response_text.find('{'); end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx+1]
                parsed = ast.literal_eval(json_str)
                
                # Convert to our risk score format
                risk_scores = []
                for risk in parsed.get('risques', []):
                    risk_scores.append(RiskScore(
                        risk_type=risk.get('type', 'unknown'),
                        severity=min(risk.get('severite', 5), 10),
                        area=risk.get('zone', 'inconnue'),
                        equipment_involved=risk.get('equipements', [])
                    ))
                
                return {
                    "image_analysis": ImageAnalysis(
                        image_id="gpt4_vision_analysis",
                        timestamp=datetime.now().isoformat(),
                        detections=[],
                        person_detections=[]
                    ).dict(),
                    "risk_scores": [score.dict() for score in risk_scores],
                    "gpt4_analysis": parsed,
                    "analysis_source": "GPT4_vision"
                }
                
        except Exception:
            pass
            
        # Fallback structured response
        return {
            "image_analysis": ImageAnalysis(
                image_id="gpt4_fallback",
                timestamp=datetime.now().isoformat(),
                detections=[],
                person_detections=[]
            ).dict(),
            "risk_scores": [
                RiskScore(
                    risk_type="general_safety_check",
                    severity=3,
                    area="overall_site",
                    equipment_involved=["recommended_inspection"]
                ).dict()
            ],
            "gpt4_analysis": {"note": "Analysis completed using vision capabilities"},
            "analysis_source": "GPT4_fallback"
        }