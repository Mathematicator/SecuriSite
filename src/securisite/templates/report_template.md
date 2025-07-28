# Rapport d'Analyse des Risques sur le Lieu de Travail
Date: {{timestamp}}

## 1. Résumé Éxécutif
**Analyse complète des risques détectés** sur le chantier.

**Statistiques globales**:
- Images analysées: {{images_analyzed}}
- Risques détectés: {{total_risks}}
- Score de conformité: {{compliance_score}}%

{% if critical_violations %}
## ⚠️ Alertes Critiques
{% for violation in critical_violations %}\n### Violation Critique: {{violation.risk_type}}
- **Article réglementaire**: {{violation.articles|join(', ')}}
- **Délai de mise en conformité**: {{violation.adjusted_itv}}h
- **Référent**: {{violation.referent}}
- **Pénalité prévue**: {{violation.penalty}}

{% endfor %}
{% endif %}

## 2. Analyse Détaillée des Risques

### 2.1 Risques liés au Personnel
{% for risk_data in personnel_risks %}
#### {{risk_data.image_id}} - {{risk_data.timestamp}}
{% for person in risk_data.person_detections %}
{% if person.no_ppe > 0.8 %}
- **Personnel sans EPI**:
  - Absence de casque: {{"%.1f" % (person.no_ppe * 100)}}%
  - Score de risque: {{risk_data.risk_score}}
  - **Actions requises**: Équipement obligatoire avant poursuite des travaux
{% endif %}
{% endfor %}
{% endfor %}

### 2.2 Risques Matériels
{% for risk in structural_risks %}
#### {{risk.risk_type}}
- **Équipement concerné**: {{risk.equipment_involved|join(', ')}}
- **Zone d'impact**: {{risk.area}}
- **Sévérité**: {{'⭐' * risk.severity}}
- **Facteur météo**: {{risk.weather_modifier or "Aucune contrainte"}}

{% endfor %}

## 3. Complément Météorologique

### Conditions Actuelles
{% for weather_key, weather_value in weather_conditions.items() %}
- **{{weather_key.replace('_', ' ').title()}}**: {{weather_value}}{% if weather_key == 'temperature' %}°C{% endif %}
{% endfor %}

### Facteurs Météo-Risque
{% for risk_modifier in weather_modifiers %}
- **{{risk_modifier.weather_factor.title()}}**:
  - Multiplicateur: {{risk_modifier.risk_multiplier}}x
  - Équipements affectés: {{risk_modifier.affected_equipment|join(', ')}}
  - Sévérité ajustée: {{risk_modifier.severity}}
{% endfor %}

## 4. Cadre Réglementaire Applicable

### Références Légales
{% for analysis in regulatory_analysis %}
#### {{analysis.original_risk}}
- **Articles**: {{analysis.articles|join(', ')}}
- **Gravité**: {{analysis.severity}}
- **Échéance**: {{analysis.deadline}}
- **Référent**: {{analysis.referent}}
{% if analysis.weather_modifier %}
- **Note météo**: {{analysis.weather_modifier}}
{% endif %}
{% endfor %}

## 5. Recommandations Prioritaires

### Actions Immédiates (24h)
{% for rec in immediate_recommendations %}
- ✅ {{rec}}
{% endfor %}

### Actions à Court Terme (48h)
{% for rec in short_term_recommendations %}
- 🔄 {{rec}}
{% endfor %}

### Actions à Moyen Terme (1 semaine)
{% for rec in medium_term_recommendations %}
- 📅 {{rec}}
{% endfor %}

## 6. Plan de Suivi

### Prochaine Inspection
**Date prévue**: {{next_inspection_date}}

### Points de Contrôle
- [ ] Vérification des EPI sur l'ensemble du personnel
- [ ] Inspection des équipements lourds
- [ ] Contrôle des zones d'accès
- [ ] Mise à jour de la formation sécurité

## 7. Contacts</n
### Ressources externes
- **Inspection du Travail**: 0800 000 100
- **CNAMTS**: www.cnamts.fr
- **CARSAT**: [numéro régional]

---

*Ce rapport a été généré automatiquement par le système SecuriSite-IA.*
*Pour toute question technique: support@securisite.ai*