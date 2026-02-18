# ==============================================================================
# Script d'installation des dépendances R - CARIS MEAL Pipeline
# Ce script prépare l'environnement pour Quarto + Python (reticulate)
# ==============================================================================

# Liste exhaustive des packages utilisés dans votre rapport
packages <- c(
  "dplyr", "RMySQL", "odbc", "DBI", "viridis", "ggplot2", 
  "ggrepel", "ggthemes", "plotly", "stringr", "RColorBrewer", 
  "tidytext", "purrr", "lubridate", "tidyr", "scales", 
  "extrafont", "forcats", "DT", "data.table", "readxl", 
  "writexl", "reticulate", "knitr", "rmarkdown"
)

# Fonction d'installation intelligente
install_if_missing <- function(p) {
  if (!require(p, character.only = TRUE)) {
    message(paste("📦 Installation du package :", p))
    install.packages(p, dependencies = TRUE, repos = "https://cloud.r-project.org")
  }
}

# 1. Installation des packages de base
invisible(sapply(packages, install_if_missing))

# 2. Configuration spécifique pour RETICULATE (Le pont R-Python)
# Indispensable pour que Quarto ne cherche pas un .venv inexistant sur GitHub
if (require(reticulate)) {
  message("🐍 Configuration de reticulate...")
  # On force l'installation de miniconda uniquement si nécessaire, 
  # mais sur GitHub Actions, on préfère utiliser le Python système.
  reticulate::configure_environment()
}

# 3. Gestion des polices pour extrafont (Optionnel mais évite des erreurs de rendu)
if (require(extrafont)) {
  # Sur Linux (GitHub Actions), l'importation peut échouer sans polices système
  # On tente une initialisation silencieuse
  try(extrafont::font_import(prompt = FALSE), silent = TRUE)
}

message("✅ Toutes les dépendances R ont été installées avec succès.")