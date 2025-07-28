"""
Weather Context Agent
Correlates weather conditions with construction safety risks
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from .base_agent import BaseSecuriSiteAgent

class WeatherContextAgent(BaseSecuriSiteAgent):
    """Agent correlating weather data with construction site safety"""
    
    def __init__(self):
        super().__init__("WeatherContextAgent")
        self.weather_risk_factors = {
            'high_wind': {'threshold': 25, 'risk_multiplier': 1.5, 'affects': ['crane', 'scaffolding']},
            'heavy_rain': {'threshold': 5, 'risk_multiplier': 2.0, 'affects': ['electrical', 'slipping']},
            'low_visibility': {'threshold': 1000, 'risk_multiplier': 1.8, 'affects': ['vehicle', 'communication']},
            'extreme_heat': {'threshold': 35, 'risk_multiplier': 1.3, 'affects': ['fatigue', 'ppe']},
            'cold': {'threshold': 5, 'risk_multiplier': 1.2, 'affects': ['manual_dexterity', 'ppe']}
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather data against construction schedule and risks"""
        self.log_info("Analyzing weather context for construction risks")
        
        image_timestamp = data.get('timestamp')
        weather_data = await self._load_weather_data()
        
        if not image_timestamp or not weather_data:
            return {"error": "Missing required data for weather analysis"}
        
        relevant_weather = self._get_weather_for_time(image_timestamp, weather_data)
        risk_context = self._assess_weather_risks(relevant_weather)
        
        return {
            "weather_conditions": relevant_weather,
            "risk_modifiers": risk_context,
            "recommendations": self._generate_weather_recommendations(risk_context),
            "api_status": "loaded"
        }
    
    async def _load_weather_data(self) -> Dict[str, Any]:
        """Load weather data from JSON files"""
        weather_file = Path("assets/weather_info.json")
        try:
            with open(weather_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log_error(f"Error loading weather data: {e}")
            return {}
    
    def _get_weather_for_time(self, timestamp: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find weather data for specific timestamp"""
        # For now, return latest weather data as placeholder
        if 'weather_by_date' in weather_data:
            if weather_data['weather_by_date']:
                latest_date = max(weather_data['weather_by_date'].keys())
                return weather_data['weather_by_date'][latest_date]
        
        return {
            'temperature': 25,
            'humidity': 60,
            'wind_speed': 10,
            'visibility': 8000,
            'precipitation': 0,
            'uv_index': 7,
            'air_quality_index': 50
        }
    
    def _assess_weather_risks(self, weather: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess weather-based risk factors"""
        risks = []
        
        # Wind risk
        wind_speed = weather.get('wind_speed', 0)
        if wind_speed > self.weather_risk_factors['high_wind']['threshold']:
            risks.append({
                "weather_factor": "high_wind",
                "severity": min(int(wind_speed / 5), 10),
                "affected_equipment": self.weather_risk_factors['high_wind']['affects'],
                "risk_multiplier": self.weather_risk_factors['high_wind']['risk_multiplier']
            })
        
        # Rain risk
        precipitation = weather.get('precipitation', 0)
        if precipitation > self.weather_risk_factors['heavy_rain']['threshold']:
            risks.append({
                "weather_factor": "heavy_rain",
                "severity": min(int(precipitation * 2), 10),
                "affected_equipment": self.weather_risk_factors['heavy_rain']['affects'],
                "risk_multiplier": self.weather_risk_factors['heavy_rain']['risk_multiplier']
            })
        
        # Visibility risk
        visibility = weather.get('visibility', 10000)
        if visibility < self.weather_risk_factors['low_visibility']['threshold']:
            risks.append({
                "weather_factor": "low_visibility",
                "severity": min(int(1000 / visibility * 10), 10),
                "affected_equipment": self.weather_risk_factors['low_visibility']['affects'],
                "risk_multiplier": self.weather_risk_factors['low_visibility']['risk_multiplier']
            })
        
        # Temperature risks
        temperature = weather.get('temperature', 20)
        if temperature > self.weather_risk_factors['extreme_heat']['threshold']:
            risks.append({
                "weather_factor": "extreme_heat",
                "severity": min(int((temperature - 35) * 2), 10),
                "affected_equipment": self.weather_risk_factors['extreme_heat']['affects'],
                "risk_multiplier": self.weather_risk_factors['extreme_heat']['risk_multiplier']
            })
        elif temperature < self.weather_risk_factors['cold']['threshold']:
            risks.append({
                "weather_factor": "cold",
                "severity": min(int((5 - temperature) * 2), 10),
                "affected_equipment": self.weather_risk_factors['cold']['affects'],
                "risk_multiplier": self.weather_risk_factors['cold']['risk_multiplier']
            })
        
        return risks
    
    def _generate_weather_recommendations(self, risk_context: List[Dict[str, Any]]) -> List[str]:
        """Generate weather-related safety recommendations"""
        recommendations = []
        
        for risk in risk_context:
            factor = risk["weather_factor"]
            
            if factor == "high_wind":
                recommendations.append("Suspension des opérations de grue, vérifier sécurité des échafaudages")
            elif factor == "heavy_rain":
                recommendations.append("Report des travaux électriques, vérification anti-dérapage")
            elif factor == "low_visibility":
                recommendations.append("Amélioration de l'éclairage, signaux lumineux additionnels")
            elif factor == "extreme_heat":
                recommendations.append("Augmentation des pauses, vérification des équipements de protection")
            elif factor == "cold":
                recommendations.append("Protection contre l'humidité, vérification des outils manuels")
        
        return list(set(recommendations))  # Remove duplicates