"""
Risk analysis models for SecuriSite-IA
"""
from typing import List, Dict, Optional
from pydantic import BaseModel

class PersonDetection(BaseModel):
    bbox_start_x: float
    bbox_end_x: float
    bbox_start_y: float
    bbox_end_y: float
    has_hard_hat: float
    has_high_vis_vest: float
    has_high_vis_pants: float
    no_ppe: float
    two_or_more: float

class EquipmentDetection(BaseModel):
    label: str
    score: float
    bbox_start_x: float
    bbox_end_x: float
    bbox_start_y: float
    bbox_end_y: float

class ImageAnalysis(BaseModel):
    image_id: str
    timestamp: str
    detections: List[EquipmentDetection]
    person_detections: List[PersonDetection]
    weather_conditions: Optional[Dict] = None

class RiskScore(BaseModel):
    risk_type: str
    severity: int  # 1-10
    area: str
    equipment_involved: List[str]
    person_at_risk: Optional[str] = None
    weather_modifier: Optional[float] = None

class ConstructionRiskReport(BaseModel):
    images_analyzed: int
    total_risks: int
    risk_scores: List[RiskScore]
    recommendations: List[str]
    regulatory_citations: List[str]
    timestamp: str