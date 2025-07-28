"""
Regulation Research Agent
Searches and applies French construction safety regulations
"""

import logging
from typing import Dict, Any, List
from .base_agent import BaseSecuriSiteAgent

class RegulationAgent(BaseSecuriSiteAgent):
    """Agent responsible for construction safety regulation research and compliance"""
    
    def __init__(self):
        super().__init__("RegulationAgent")
        self.french_regulations = {
            'person_without_ppe': {
                'articles': ['R4534-15', 'R4312-1', 'R4312-2'],
                'severity': 'URGENTE',
                'itv': 24,  # hours
                'penalty': 'Amende 1 500€ par personne',
                'referent': 'CNAMTS'
            },
            'tower_crane_operation': {
                'articles': ['R4534-26', 'R4534-27', 'R4534-28'],
                'severity': 'HAUTE',
                'itv': 12,  # hours
                'penalty': 'Arrêt du chantier',
                'referent': 'CARSAT'
            },
            'equipment_positioning': {
                'articles': ['R4215-1', 'R4215-2', 'R4215-3'],
                'severity': 'MODÉRÉE',
                'itv': 48,  # hours
                'penalty': 'Mise en conformité',
                'referent': 'Inspection Travail'
            },
            'container_obstruction': {
                'articles': ['R4215-11', 'R4215-12'],
                'severity': 'MAJEURE',
                'itv': 24,  # hours
                'penalty': 'Remplacement/relivraison',
                'referent': 'Inspection Travail'
            }
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process risk findings and provide regulatory context"""
        self.log_info("Analyzing regulatory compliance for construction risks")
        
        risks = data.get('risks', [])
        weather_conditions = data.get('weather_conditions', {})
        
        regulatory_analysis = []
        total_penalty_score = 0
        
        for risk in risks:
            reg_info = self._match_regulation(risk)
            modified_reg = self._apply_weather_modifiers(reg_info, weather_conditions)
            regulatory_analysis.append(modified_reg)
            total_penalty_score += self._calculate_penalty_score(modified_reg)
        
        return {
            "regulatory_analysis": regulatory_analysis,
            "compliance_score": max(100 - total_penalty_score, 0),
            "total_penalty_score": total_penalty_score,
            "critical_violations": [r for r in regulatory_analysis if r['severity'] == 'URGENTE'],
            "recommendations": self._generate_compliance_recommendations(regulatory_analysis),
            "next_inspection_schedule": self._schedule_inspection(regulatory_analysis)
        }
    
    def _match_regulation(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """Match risk with appropriate French regulations"""
        risk_type = risk.get('risk_type', 'unknown')
        severity = risk.get('severity', 0)
        
        # Map to closest regulation category
        regulation_key = self._categorize_risk(risk_type)
        regulation_info = self.french_regulations.get(regulation_key, {
            'articles': ['Code général'],
            'severity': 'INCONNUE',
            'itv': 72,
            'penalty': 'Évaluation au cas par cas',
            'referent': 'Inspection Travail'
        })
        
        # Scale ITV based on severity
        scaled_itv = int(regulation_info['itv'] * (1 - (severity - 1) / 20))
        
        return {
            **regulation_info,
            'original_risk': risk_type,
            'risk_severity': severity,
            'scaled_itv_hours': scaled_itv,
            'deadline': f"{scaled_itv}h maximum"
        }
    
    def _categorize_risk(self, risk_type: str) -> str:
        """Categorize risk type for regulation matching"""
        risk_mapping = {
            'person_without_ppe': 'person_without_ppe',
            'person_missing_equipment': 'person_without_ppe',
            'tower_crane_operation': 'tower_crane_operation',
            'crane_near_people': 'tower_crane_operation',
            'container_obstruction': 'container_obstruction',
            'equipment_positioning': 'equipment_positioning',
            'scaffolding_unstable': 'equipment_positioning',
            'vehicle_placement': 'container_obstruction'
        }
        return risk_mapping.get(risk_type, 'equipment_positioning')
    
    def _apply_weather_modifiers(self, regulation: Dict[str, Any], weather: Dict[str, Any]) -> Dict[str, Any]:
        """Apply weather-based modifiers to regulatory recommendations"""
        modified_reg = regulation.copy()
        
        wind_speed = weather.get('wind_speed', 0)
        precipitation = weather.get('precipitation', 0)
        temperature = weather.get('temperature', 20)
        
        # Weather can increase urgency
        urgency_multiplier = 1.0
        weather_conditions = []
        
        if wind_speed > 25:
            urgency_multiplier *= 0.7  # Reduce ITV by 30%
            weather_conditions.append("vent fort")
        
        if precipitation > 5:
            urgency_multiplier *= 0.8  # Reduce ITV by 20%
            weather_conditions.append("pluie"),
        
        if temperature > 35 or temperature < 0:
            urgency_multiplier *= 0.9  # Reduce ITV by 10%
            weather_conditions.append("température extrême")
        
        new_itv = int(modified_reg['scaled_itv_hours'] * urgency_multiplier)
        
        modified_reg.update({
            'weather_modifier': f"Réduction ITV pour conditions météo: {', '.join(weather_conditions)}",
            'adjusted_itv': max(new_itv, 2),  # Minimum 2 hours
            'weather_conditions': weather_conditions
        })
        
        return modified_reg
    
    def _calculate_penalty_score(self, regulation: Dict[str, Any]) -> int:
        """Calculate penalty score based on regulation severity"""
        severity_mult = {
            'URGENTE': 20,
            'HAUTE': 15,
            'MAJEURE': 10,
            'MODÉRÉE': 5,
            'INCONNUE': 8
        }
        return severity_mult.get(regulation['severity'], 8)
    
    def _generate_compliance_recommendations(self, regulatory_analysis: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for reg in regulatory_analysis:
            recommendations.extend([
                f"Organiser la formation sur {reg['original_risk']}",
                f"Mettre en conformité dans {reg['adjusted_itv']}h maximum",
                f"Contacter {reg['referent']} pour inspection",
                f"Étudier les alternatives temporaires en attendant la garantie"
            ])
        
        # Add weather-specific recommendations
        weather_warnings = [r for r in regulatory_analysis if r.get('weather_conditions')]
        for warning in weather_warnings:
            if 'vent fort' in warning['weather_conditions']:
                recommendations.append("Interdire travaux en hauteur temps fort vent")
            if 'pluie' in warning['weather_conditions']:
                recommendations.append("Reporter travaux électriques extérieurs")
        
        return list(set(recommendations))
    
    def _schedule_inspection(self, regulatory_analysis: List[Dict[str, Any]]) -> str:
        """Schedule next inspection based on violations"""
        if not regulatory_analysis:
            return "Inspection sans préavis"
        
        urgent_violations = [r for r in regulatory_analysis if r['severity'] == 'URGENTE']
        high_violations = [r for r in regulatory_analysis if r['severity'] == 'HAUTE']
        
        if urgent_violations:
            return "Inspection urgente dans 24h"
        elif high_violations:
            return "Inspection dans 48h"
        else:
            return "Inspection programmée dans 1 semaine"