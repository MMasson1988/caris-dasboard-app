#!/bin/bash

# Script d'exécution locale du workflow complet
# Simule ce que fait GitHub Actions mais en local

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Workflow Local - Exécution Complète                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Compteurs
TOTAL_PIPELINES=0
SUCCESS_PIPELINES=0
FAILED_PIPELINES=0
TOTAL_REPORTS=0
SUCCESS_REPORTS=0
FAILED_REPORTS=0

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ÉTAPE 1: Vérification de l'environnement
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}ÉTAPE 1: Vérification de l'Environnement${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Vérifier Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ Python détecté:${NC} $PYTHON_VERSION"
else
    echo -e "${RED}❌ Python3 non trouvé!${NC}"
    exit 1
fi

# Vérifier Quarto
if command -v quarto &> /dev/null; then
    QUARTO_VERSION=$(quarto --version 2>&1)
    echo -e "${GREEN}✅ Quarto détecté:${NC} $QUARTO_VERSION"
else
    echo -e "${YELLOW}⚠️  Quarto non trouvé (les rapports QMD ne seront pas générés)${NC}"
fi

# Vérifier R
if command -v Rscript &> /dev/null; then
    echo -e "${GREEN}✅ R détecté${NC}"
else
    echo -e "${YELLOW}⚠️  R non trouvé (peut causer des erreurs pour les QMD)${NC}"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ÉTAPE 2: Exécution des Pipelines Python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}ÉTAPE 2: Exécution des Pipelines Python${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Trouver tous les fichiers pipeline
PIPELINE_FILES=$(find script/ -type f \( -name "*_pipeline.py" -o -name "*-pipeline.py" \) 2>/dev/null | sort)

if [ -z "$PIPELINE_FILES" ]; then
    echo -e "${RED}❌ Aucun fichier pipeline trouvé!${NC}"
    exit 1
fi

# Exécuter chaque pipeline
for pipeline in $PIPELINE_FILES; do
    TOTAL_PIPELINES=$((TOTAL_PIPELINES + 1))
    echo ""
    echo -e "${YELLOW}▶️  Exécution: $pipeline${NC}"
    echo "────────────────────────────────────────────────────────────"
    
    # Exécuter le pipeline avec un timeout de 5 minutes
    if timeout 300 python3 "$pipeline"; then
        echo -e "${GREEN}✅ Succès: $pipeline${NC}"
        SUCCESS_PIPELINES=$((SUCCESS_PIPELINES + 1))
    else
        echo -e "${RED}❌ Échec: $pipeline${NC}"
        FAILED_PIPELINES=$((FAILED_PIPELINES + 1))
        
        echo ""
        echo -e "${RED}Le workflow s'arrête en raison de l'échec du pipeline${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}✅ Tous les pipelines ($SUCCESS_PIPELINES/$TOTAL_PIPELINES) ont été exécutés avec succès!${NC}"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ÉTAPE 3: Génération des Rapports QMD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if command -v quarto &> /dev/null; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}ÉTAPE 3: Génération des Rapports QMD${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Trouver tous les fichiers QMD
    QMD_FILES=$(find . -maxdepth 1 -name "tracking-*.qmd" -type f 2>/dev/null | sort)
    
    if [ -z "$QMD_FILES" ]; then
        echo -e "${YELLOW}⚠️  Aucun fichier QMD trouvé${NC}"
    else
        # Générer chaque rapport
        for qmd in $QMD_FILES; do
            TOTAL_REPORTS=$((TOTAL_REPORTS + 1))
            echo ""
            echo -e "${YELLOW}📄 Génération: $qmd${NC}"
            echo "────────────────────────────────────────────────────────────"
            
            if quarto render "$qmd"; then
                echo -e "${GREEN}✅ Succès: $qmd${NC}"
                SUCCESS_REPORTS=$((SUCCESS_REPORTS + 1))
            else
                echo -e "${RED}❌ Échec: $qmd${NC}"
                FAILED_REPORTS=$((FAILED_REPORTS + 1))
                
                echo ""
                echo -e "${RED}Le workflow s'arrête en raison de l'échec du rapport${NC}"
                exit 1
            fi
        done
        
        echo ""
        echo -e "${GREEN}✅ Tous les rapports ($SUCCESS_REPORTS/$TOTAL_REPORTS) ont été générés avec succès!${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Quarto non installé - Rapports QMD ignorés${NC}"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RÉSUMÉ FINAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RÉSUMÉ D'EXÉCUTION                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Pipelines réussis:${NC} $SUCCESS_PIPELINES/$TOTAL_PIPELINES"
echo -e "${GREEN}✅ Rapports générés:${NC} $SUCCESS_REPORTS/$TOTAL_REPORTS"
echo ""
echo -e "${BLUE}📁 Résultats:${NC}"
echo "   • Fichiers Excel: outputs/*/*.xlsx"
echo "   • Rapports HTML: tracking-*.html"
echo "   • Site Quarto: _site/"
echo ""

# Lister les fichiers générés
echo -e "${BLUE}📋 Fichiers générés récemment:${NC}"
echo ""
echo "Outputs Excel:"
find outputs/ -name "*.xlsx" -type f -mmin -10 2>/dev/null | head -5
echo ""
echo "Rapports HTML:"
find . -maxdepth 1 -name "tracking-*.html" -type f -mmin -10 2>/dev/null
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Workflow Local Terminé avec Succès!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Pour visualiser les rapports:${NC}"
echo "   • Ouvrir tracking-*.html dans un navigateur"
echo "   • Ou lancer: python -m http.server 8000"
echo "   • Puis visiter: http://localhost:8000"
echo ""
