.PHONY: run demo build docker-run install clean lint test

# Default target
all: install

# Install dependencies
install:
	@echo "📦 Installation des dépendances..."
	pip install -r requirements.txt

# Run the main application
run:
	@echo "🚀 Démarrage de SecuriSite-IA..."
	python src/main.py

# Run demo analysis
demo:
	@echo "🎯 Lancement de la démonstration..."
	python src/final_test.py

# Build Docker image
build:
	@echo "🐳 Construction de l'image Docker..."
	docker build -t securisite .

# Run in Docker
docker-run: build
	@echo "🌐 Exécution dans Docker..."
	docker run --rm -v $(PWD)/reports:/app/reports securisite

# Quick test with sample data
test:
	@echo "✅ Test rapide du système..."
	python3 -c "import sys; sys.path.insert(0, 'src'); from securisite.orchestrator import main; import asyncio; asyncio.run(main())"

# Lint code
lint:
	@echo "🔍 Analyse du code..."
	python -m flake8 src/ --max-line-length=100 --ignore=E203,W503

# Clean generated files
clean:
	@echo "🧹 Nettoyage des fichiers générés..."
	rm -f *.md *.json securisite_*.md
	rm -rf reports/ __pycache__/

# Format code
format:
	@echo "🎨 Formatage du code..."
	python -m black src/

# Interactive development
interactive:
	@echo "🎯 Mode interactif - accès aux données..."
	python -c "import sys; sys.path.insert(0, 'src'); from securisite.orchestrator import SecuriSiteOrchestrator; import asyncio; orch = SecuriSiteOrchestrator(); print('✅ Système prêt. Utilisez orch.analyze_site_risks()')

# Help
help:
	@echo "🎯 SecuriSite-IA - Système Multi-Agent"
	@echo ""
	@echo "Usage:"
	@echo "  make install     - Installer dépendances"
	@echo "  make run         - Lancer analyse complète"
	@echo "  make demo        - Démonstration simple"
	@echo "  make build       - Construire Docker"
	@echo "  make docker-run  - Lancer dans Docker"
	@echo "  make test        - Test rapide"
	@echo "  make clean       - Nettoyer fichiers"
	@echo "  make help        - Afficher cette aide"