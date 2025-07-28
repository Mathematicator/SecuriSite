"""
Report Generation Agent
Generates comprehensive security reports in French
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import jinja2
from pathlib import Path
from .base_agent import BaseSecuriSiteAgent

class ReportGenerationAgent(BaseSecuriSiteAgent):
    """Agent responsible for generating comprehensive French security reports"""
    
    def __init__(self):
        super().__init__("ReportGenerationAgent")
        self.template_env = jinja2.Environment()
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process all agent results and generate final report"""
        self.log_info("Generating security analysis report")
        
        # Prepare data for report template
        report_data = self._prepare_report_data(data)
        
        # Load template
        template = await self._load_template()
        
        # Generate report
        report = template.render(**report_data)
        
        return {
            "report": report,
            "report_type": "markdown",
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_summary(report_data),
            "executable_sections": self._identify_actions(report_data)
        }
    
    def _prepare_report_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data for report generation"""
        cv_analysis = data.get('cv_analysis', {})
        weather_context = data.get('weather_context', {})
        regulatory_analysis = data.get('regulatory_analysis', {})
        
        # Extract risks by type
        risk_scores = cv_analysis.get('risk_scores', [])
        
        personnel_risks = []
        structural_risks = []
        
        for risk in risk_scores:
            if 'person' in risk.get('risk_type', '').lower():
                personnel_risks.append(risk)
            else:
                structural_risks.append(risk)
        
        # Get compliance info
        regulatory_results = regulatory_analysis.get('regulatory_analysis', [])
        
        # Organize recommendations by timeline
        all_recommendations = regulatory_analysis.get('recommendations', [])
        immediate_rec = [r for r in all_recommendations if '24h' in r or 'immédiate' in r.lower()]
        short_rec = [r for r in all_recommendations if '48h' in r or 'court terme' in r.lower()]
        medium_rec = [r for r in all_recommendations if '1 semaine' in r or 'moyen terme' in r.lower()]
        
        return {
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'images_analyzed': len(cv_analysis.get('image_analysis', {})),
            'total_risks': len(risk_scores),
            'compliance_score': regulatory_analysis.get('compliance_score', 0),
            'personnel_risks': personnel_risks,
            'structural_risks': structural_risks,
            'weather_conditions': weather_context.get('weather_conditions', {}),
            'weather_modifiers': weather_context.get('risk_modifiers', []),
            'regulatory_analysis': regulatory_results,
            'critical_violations': regulatory_analysis.get('critical_violations', []),
            'immediate_recommendations': immediate_rec,
            'short_term_recommendations': short_rec,
            'medium_term_recommendations': medium_rec,
            'next_inspection_date': regulatory_analysis.get('next_inspection_schedule', 'À déterminer')
        }
    
    async def _load_template(self) -> jinja2.Template:
        """Load the Jinja2 template for report generation"""
        template_path = Path("src/securisite/templates/report_template.md")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return self.template_env.from_string(template_content)
        except Exception as e:
            self.log_error(f"Error loading template: {e}")
            return self._create_default_template()
    
    def _create_default_template(self) -> jinja2.Template:
        """Create a default template if file template is not found"""
        default_template = """# Rapport SecuriSite

## Résumé
- Images analysées: {{images_analyzed}}
- Risques détectés: {{total_risks}}
- Score de conformité: {{compliance_score}}%

## Risques Identifiés
{% for risk in personnel_risks %}
- {{risk.risk_type}}: Sévérité {{risk.severity}}/10
{% endfor %}

## Recommandations
{% for rec in immediate_recommendations %}
- {{rec}}
{% endfor %}

Généré le: {{timestamp}}
"""
        return self.template_env.from_string(default_template)
    
    def _generate_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a machine-readable summary"""
        return {
            "total_images": report_data['images_analyzed'],
            "total_risks": report_data['total_risks'],
            "compliance_score": report_data['compliance_score'],
            "critical_violations": len(report_data['critical_violations']),
            "immediate_actions": len(report_data['immediate_recommendations']),
            "risk_categories": list(set([
                r.get('risk_type', 'unknown') 
                for r in report_data.get('personnel_risks', []) + 
                report_data.get('structural_risks', [])
            ]))
        }
    
    def _identify_actions(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify executable actions from the report"""
        actions = []
        
        # From critical violations
        for violation in report_data.get('critical_violations', []):
            actions.append({
                "action": "Immediate_correction",
                "type": violation.get('risk_type'),
                "deadline": violation.get('adjusted_itv', 24),
                "priority": "critical"
            })
        
        # From recommendations
        for rec in report_data.get('immediate_recommendations', []):
            actions.append({
                "action": "follow_recommendation",
                "description": rec,
                "deadline": 24,
                "priority": "high"
            })
        
        return actions