"""
Main orchestrator for SecuriSite-IA multi-agent system
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, Any

# Import agents
from securisite.agents.cv_risk_detector import ComputerVisionRiskDetector
from securisite.agents.weather_context_agent import WeatherContextAgent
from securisite.agents.regulation_agent import RegulationAgent
from securisite.agents.report_agent import ReportGenerationAgent
from securisite.evaluation.evaluator import PerformanceEvaluator

class SecuriSiteOrchestrator:
    """
    Main orchestrator that coordinates all agents for construction risk analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SecuriSiteOrchestrator")
        self.logger.setLevel(logging.INFO)
        
        # Initialize agents
        self.cv_agent = ComputerVisionRiskDetector()
        self.weather_agent = WeatherContextAgent()
        self.regulation_agent = RegulationAgent()
        self.report_agent = ReportGenerationAgent()
        self.evaluator = PerformanceEvaluator()
    
    async def analyze_site_risks(self, image_id: str = None) -> Dict[str, Any]:
        """
        Complete multi-agent risk analysis for construction site
        """
        self.logger.info("Starting comprehensive site risk analysis")
        
        # Step 1: Computer Vision Analysis
        cv_result = await self._run_cv_analysis(image_id)
        
        # Step 2: Weather Context Analysis
        weather_result = await self._run_weather_analysis(cv_result)
        
        # Step 3: Regulatory Compliance Analysis
        regulatory_result = await self._run_regulatory_analysis(cv_result, weather_result)
        
        # Step 4: Generate Report
        report_result = await self._generate_report(cv_result, weather_result, regulatory_result)
        
        # Step 5: Performance Evaluation
        evaluation_result = await self._evaluate_performance(report_result)
        
        return {
            "analysis": {
                "cv_analysis": cv_result,
                "weather_context": weather_result,
                "regulatory_analysis": regulatory_result,
                "report": report_result,
                "performance_evaluation": evaluation_result
            },
            "summary": {
                "total_risks": len(cv_result.get('risk_scores', [])),
                "compliance_score": regulatory_result.get('compliance_score', 0),
                "critical_violations": len(regulatory_result.get('critical_violations', [])),
                "generated_at": datetime.now().isoformat()
            }
        }
    
    async def _run_cv_analysis(self, image_id: str) -> Dict[str, Any]:
        """Run computer vision risk detection"""
        data = {"image_path": image_id}
        return await self.cv_agent.process(data)
    
    async def _run_weather_analysis(self, cv_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run weather context analysis"""
        image_data = cv_result.get('image_analysis', {})
        data = {"timestamp": image_data.get('timestamp', datetime.now().isoformat())}
        return await self.weather_agent.process(data)
    
    async def _run_regulatory_analysis(self, cv_result: Dict[str, Any], weather_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run regulatory compliance analysis"""
        data = {
            "risks": cv_result.get('risk_scores', []),
            "weather_conditions": weather_result.get('weather_conditions', {})
        }
        return await self.regulation_agent.process(data)
    
    async def _generate_report(self, cv_result: Dict[str, Any], weather_result: Dict[str, Any], regulatory_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        data = {
            "cv_analysis": cv_result,
            "weather_context": weather_result,
            "regulatory_analysis": regulatory_result
        }
        return await self.report_agent.process(data)
    
    async def _evaluate_performance(self, report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate system performance"""
        data = {
            "cv_analysis": report_result.get('report', {}),
            "weather_context": report_result.get('weather_context', {}),
            "regulatory_analysis": report_result.get('regulatory_analysis', {})
        }
        return await self.evaluator.evaluate(data)
    
    def save_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save the generated report to file"""
        if filename is None:
            filename = f"securisite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_path = Path(filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(results['analysis']['report']['report'])
        
        self.logger.info(f"Report saved to {report_path}")
        return str(report_path)
    
    def save_full_analysis(self, results: Dict[str, Any]) -> str:
        """Save complete analysis results to JSON file"""
        filename = f"full_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filename

# Global orchestrator instance
orchestrator = SecuriSiteOrchestrator()

async def main():
    """Main execution function"""
    print("🚀 Démarrage du système SecuriSite-IA...")
    
    # Run complete analysis
    results = await orchestrator.analyze_site_risks()
    
    # Display summary
    print("\n📊 Résumé Analyse:")
    print(f"Images analysées: {results['summary']['total_risks']}")
    print(f"Score conformité: {results['summary']['compliance_score']}%")
    print(f"Violations critiques: {results['summary']['critical_violations']}")
    
    # Save results
    report_path = orchestrator.save_report(results)
    analysis_path = orchestrator.save_full_analysis(results)
    
    print(f"\n✅ Rapport enregistré: {report_path}")
    print(f"✅ Analyse complète enregistrée: {analysis_path}")
    
    return results

if __name__ == "__main__":
    # Handle imports and run
    try:
        results = asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Analyse interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")