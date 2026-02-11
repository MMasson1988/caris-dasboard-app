#!/bin/bash
echo "🚀 Activation environnement caris-dashboard-app..."

# Créer alias python pour Windows si nécessaire
if command -v py &> /dev/null && ! command -v python &> /dev/null; then
    alias python='py'
    echo "📝 Alias python='py' créé pour Windows"
fi

source venv/bin/activate
echo "✅ Environnement Python activé!"
echo "📊 Pour R, utilisez RStudio ou R console"  
echo "💡 Pour désactiver: deactivate"
exec bash
