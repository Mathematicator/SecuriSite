"""
Performance Evaluation Agent
Evaluates system performance and suggests improvements
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

class PerformanceEvaluator:
    """Agent responsible for evaluating system performance and generating improvement recommendations"""
    
    def __init__(self):
        self.logger = logging.getLogger("PerformanceEvaluator")
        self.baseline_metrics = {
            'detection_accuracy': 0.85,
            'report_quality': 0.80,
            'processing_speed': 2.0,  # images per second
            'regulatory_coverage': 0.75
        }
    
    async def evaluate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive evaluation of the system"""
        self.logger.info("Starting performance evaluation")
        
        metrics = self._calculate_metrics(analysis_data)
        recommendations = self._generate_improvement_suggestions(metrics)
        
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "benchmarks": self.baseline_metrics,
            "improvement_suggestions": recommendations,
            "performance_grade": self._calculate_grade(metrics),
            "optimization_priorities": self._prioritize_improvements(recommendations)
        }
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance metrics from analysis results"""
        
        # Detection confidence analysis
        cv_analysis = data.get('cv_analysis', {})
        if isinstance(cv_analysis, str):
            cv_analysis = {}
        risk_scores = cv_analysis.get('risk_scores', [])
        avg_confidence = 0.8  # Placeholder - would use actual CV model confidence
        
        # Report completeness
        report_data = data.get('report', {})
        report_sections = len(report_data.get('sections', ['summary', 'risks', 'recommendations']))
        report_completeness = min(report_sections / 7.0, 1.0)  # Target 7 sections
        
        # Regulatory coverage
        regulatory_analysis = data.get('regulatory_analysis', {})
        regulatory_matches = len(regulatory_analysis.get('regulatory_analysis', []))
        regulatory_yield = min(regulatory_matches / 5.0, 1.0)  # Target 5 regulations
        
        # Response time (simulated)
        processing_time = 1.5  # Placeholder
        response_time_score = min(5.0 / processing_time, 1.0) if processing_time > 0 else 0
        
        # False positive rate (estimated from summary)
        summary = data.get('report', {}).get('summary', {})
        detected_risks = summary.get('total_risks', 0)
        false_positive_rate = 0.15 if detected_risks > 10 else 0.05
        
        return {
            'detection_accuracy': avg_confidence,
            'report_quality': report_completeness,
            'processing_speed': response_time_score,
            'regulatory_coverage': regulatory_yield,
            'false_positive_rate': false_positive_rate,
            'overall_score': (avg_confidence + report_completeness + regulatory_yield + response_time_score) / 4
        }
    
    def _generate_improvement_suggestions(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate specific improvement recommendations"""
        suggestions = []
        
        # Detection accuracy improvements
        if metrics['detection_accuracy'] < 0.9:
            suggestions.append({
                "category": "computer_vision",
                "priority": "high",
                "suggestion": "Faire revue manuelle sur 20% d'échantillons et ajuster seuils",
                "impact": "+15% de précision",
                "effort": 4  # 1-5 scale
            })
            suggestions.append({
                "category": "computer_vision",
                "priority": "medium",
                "suggestion": "Entraîner modèle sur données spécifiques construction française",
                "impact": "+25% de détection EPI",
                "effort": 5
            })
        
        # Report quality improvements
        if metrics['report_quality'] < 0.85:
            suggestions.append({
                "category": "report_generation",
                "priority": "medium",
                "suggestion": "Ajouter visualisations avec bounding boxes colorés",
                "impact": "+20% lisibilité",
                "effort": 3
            })
            suggestions.append({
                "category": "report_generation",
                "priority": "low",
                "suggestion": "Inclure tendances temporelles et analyses comparatives",
                "impact": "+30% valeur rétrospective",
                "effort": 4
            })
        
        # Regulatory coverage improvements
        if metrics['regulatory_coverage'] < 0.8:
            suggestions.append({
                "category": "regulations",
                "priority": "high",
                "suggestion": "Intégrer scraping automatisé Code du Travail",
                "impact": "+40% couverture réglementaire",
                "effort": 3
            })
            suggestions.append({
                "category": "regulations",
                "priority": "low",
                "suggestion": "Surveillance quotidienne des mises à jour juridiques",
                "impact": "+10% fraîcheur réglementaire",
                "effort": 2
            })
        
        # Processing speed improvements
        if metrics['processing_speed'] < 0.8:
            suggestions.append({
                "category": "performance",
                "priority": "medium",
                "suggestion": "Cache temporel pour données météo pour éviter requêtes redondantes",
                "impact": "-50% temps réponse",
                "effort": 2
            })
            suggestions.append({
                "category": "performance",
                "priority": "low",
                "suggestion": "Utilisation plus efficace des agents LangChain (streaming) ",
                "impact": "-30% latence",
                "effort": 3
            })
        
        return suggestions
    
    def _calculate_grade(self, metrics: Dict[str, float]) -> str:
        """Calculate overall performance grade"""
        overall_score = metrics.get('overall_score', 0)
        
        if overall_score >= 0.9:
            return "A - Excellence"
        elif overall_score >= 0.8:
            return "B - Bon niveau"
        elif overall_score >= 0.7:
            return "C - Satisfaisant"
        elif overall_score >= 0.6:
            return "D - A améliorer"
        else:
            return "E - Refactorisation nécessaire"
    
    def _prioritize_improvements(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize improvements by impact/effort ratio"""
        scored_suggestions = []
        
        for suggestion in suggestions:
            impact = suggestion.get('impact', '').replace('%', '')
            if '+' in impact:
                impact_value = int(impact.replace('+', '').split(' ')[0])
            else:
                impact_value = 10
            
            effort = suggestion.get('effort', 3)
            priority_score = (impact_value / 100) / effort
            
            scored_suggestion = suggestion.copy()
            scored_suggestion['priority_score'] = priority_score
            scored_suggestion['roi'] = f"{(priority_score * 100):.1f}x"
            
            scored_suggestions.append(scored_suggestion)
        
        return sorted(scored_suggestions, key=lambda x: x['priority_score'], reverse=True)
    
    def save_evaluation_report(self, evaluation: Dict[str, Any], filename: str = None):
        """Save evaluation results to file"""
        if filename is None:
            filename = f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        path = Path(f"src/securisite/evaluation/") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Evaluation saved to {path}")