"""
Demo script for testing SecuriSite-IA functionality
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from securisite.agents.cv_risk_detector import ComputerVisionRiskDetector
from securisite.agents.weather_context_agent import WeatherContextAgent
from securisite.agents.regulation_agent import RegulationAgent
from securisite.agents.report_agent import ReportGenerationAgent

async def demo_analysis():
    """Demonstrate basic functionality of the multi-agent system"""
    
    print("🎯 DÉMO SecuriSite-IA")
    print("=" * 50)
    
    # Initialize agents
    cv_agent = ComputerVisionRiskDetector()
    weather_agent = WeatherContextAgent()
    regulation_agent = RegulationAgent()
    report_agent = ReportGenerationAgent()
    
    # Simulate demo data based on actual assets
    # Using first image from EST-2 as sample
    sample_detection = {
        "photo_id": 663221474,
        "image_shooting": "2025:06:29 16:30:07",
        "detections": [
            {
                "score": 0.95,
                "label": "person",
                "bounding_box_start_x": 0.395,
                "bounding_box_end_x": 0.398,
                "bounding_box_start_y": 0.555,
                "bounding_box_end_y": 0.564,
                "attributes": {
                    "has_hard_hat": 0.001,
                    "has_high_vis_vest": 0.005,
                    "no_ppe": 0.995
                }
            },
            {
                "score": 0.83,
                "label": "tower_crane",
                "bounding_box_start_x": 0.567,
                "bounding_box_end_x": 0.863,
                "bounding_box_start_y": 0.157,
                "bounding_box_end_y": 0.231
            },
            {
                "score": 0.91,
                "label": "container",
                "bounding_box_start_x": 0.297,
                "bounding_box_end_x": 0.320,
                "bounding_box_start_y": 0.528,
                "bounding_box_end_y": 0.581
            }
        ]
    }
    
    # Test CV Risk Detector
    print("🔍 1. Détection des risques CV...")
    cv_result = await cv_agent.process({"image_path": "663221474_0e31e9a6-d027-402f-babd-bb5a194f9980.jpg"})
    print(f"   ✅ Risques détectés: {len(cv_result.get('risk_scores', []))}")
    
    # Test Weather Context Agent
    print("🌦️  2. Contexte météorologique...")
    weather_result = await weather_agent.process({
        "timestamp": "2025:06:29 16:30:07"
    })
    print(f"   ✅ Conditions: {weather_result.get('weather_conditions', {}).get('temperature', 'N/A')}°C")
    
    # Test Regulation Agent
    print("📋 3. Analyse réglementaire...")
    regulatory_result = await regulation_agent.process({
        "risks": cv_result.get('risk_scores', []),
        "weather_conditions": weather_result.get('weather_conditions', {})
    })
    print(f"   ✅ Score conformité: {regulatory_result.get('compliance_score', 0)}%")
    
    # Test Report Generation
    print("📄 4. Génération rapport...")
    report_result = await report_agent.process({
        "cv_analysis": cv_result,
        "weather_context": weather_result,
        "regulatory_analysis": regulatory_result
    })
    
    # Save demo report
    demo_report_path = "securisite_demo_report.md"
    with open(demo_report_path, 'w', encoding='utf-8') as f:
        f.write(report_result['report'])
    
    print("\n" + "=" * 50)
    print(f"🏁 DÉMO COMPLÉTE!")
    print(f"📊 Rapport sauvegardé: {demo_report_path}")
    print(f"🎯 Next step: `python src/main.py` pour analyse complète")
    
    return {
        "cv_analysis": cv_result,
        "weather_context": weather_result, 
        "regulatory_analysis": regulatory_result,
        "report": report_result
    }

if __name__ == "__main__":
    asyncio.run(demo_analysis())