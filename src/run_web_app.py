#!/usr/bin/env python3
"""
Lanceur de l'interface web SecuriSite-IA
Point d'entrée pour l'application web destinée au responsables sécurité
"""

import os
import sys
from pathlib import Path

# Ensure we can find our modules
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

# Change working directory to project root for asset access
os.chdir(project_root)

from securisite.web_app import app

if __name__ == '__main__':
    print("🚀 Démarrage de SecuriSite-IA - Interface Web")
    print("=" * 60)
    print("👤 Interface conçue pour: Responsable Sécurité")
    print("📱 Optimisée pour: Tablette de chantier")
    print("🎯 Objectif: De la Donnée à la Décision en moins d'1 minute")
    print("=" * 60)
    
    # Configuration pour environnement de production/développement
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', int(os.getenv('PORT', 5000))))
    
    # Production settings for Cloud Run
    if os.getenv('FLASK_ENV') == 'production':
        debug_mode = False
        print("🌐 Mode: Production (Google Cloud Run)")
        print(f"🌐 Port: {port}")
    else:
        print("🌐 Accès local: http://localhost:5000")
        print("🌐 Accès réseau: http://0.0.0.0:5000")
    
    print("=" * 60)
    print("📋 Fonctionnalités disponibles:")
    print("  • Tableau de bord avec score de risque global")
    print("  • Vue détaillée des risques avec images annotées")
    print("  • Informations météo et réglementaires contextuelles")
    print("  • Actions: Marquer comme traité, Export PDF")
    print("  • Interface tactile optimisée pour tablettes")
    print("  • Système d'authentification sécurisé")
    print("=" * 60)
    
    try:
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n❌ Application interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        sys.exit(1)