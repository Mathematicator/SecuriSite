"""Simple test without external dependencies"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_system():
    from securisite.agents.cv_risk_detector import ComputerVisionRiskDetector
    from securisite.agents.weather_context_agent import WeatherContextAgent
    from securisite.agents.regulation_agent import RegulationAgent
    
    print("🧪 Test SecuriSite-IA - Mode simple")
    print("="*40)
    
    # Test basic JSON parsing
    cv_agent = ComputerVisionRiskDetector()
    weather_agent = WeatherContextAgent()
    regulation_agent = RegulationAgent()
    
    # Simulate CV analysis without image files
    demo_data = {
        "663221474_0e31e9a6-d027-402f-babd-bb5a194f9980.jpg": {
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
                        "has_high_vis_pants": 0.0,
                        "has_hard_hat": 0.001,
                        "has_high_vis_vest": 0.005,
                        "no_ppe": 0.995,
                        "two_or_more": 0.0
                    }
                }
            ]
        }
    }
    
    results = [await agent.process({"image_path": "663221474_0e31e9a6-d027-402f-babd-bb5a194f9980.jpg"}) for agent in [cv_agent, weather_agent, regulation_agent]]
    
    print("✅ Tous les agents fonctionnent!")
    print(f"   CV Agent: {len(results[0].get('risk_scores', []))} risques détectés")
    print(f"   Weather Agent: {len(results[1].get('risk_modifiers', []))} facteurs météo")
    print(f"   Regulation Agent: {results[2].get('compliance_score', 0)}% conformité")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_system())